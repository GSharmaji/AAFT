"""Voice and image generation. Both are cached by content hash, so re-running
after a script fix only regenerates the scenes/shots that changed."""
from __future__ import annotations

import base64
import csv
import hashlib
import json
import os
import subprocess
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from . import scriptfmt
from .config import Config, Episode, PipelineError

PAPER = (243, 235, 221)
INK = (58, 48, 40)
FONT_FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _hash(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def is_placeholder(png: Path) -> bool:
    """True if this image is still a storyboard card (not real art)."""
    meta_path = png.with_suffix(".json")
    if not meta_path.exists():
        return False  # a file dropped in by hand
    sha = json.loads(meta_path.read_text()).get("placeholder_sha")
    return bool(sha) and sha == file_sha(png)


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise PipelineError(f"Command failed: {' '.join(cmd[:6])} ...\n{proc.stderr[-1500:]}")


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError as e:
        raise PipelineError(f"Could not read duration of {path}") from e


def font(cfg: Config, key: str, size: int) -> ImageFont.FreeTypeFont:
    path = cfg.resolve(cfg.get(key, FONT_FALLBACK))
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.truetype(FONT_FALLBACK, size)


# ======================================================================= voice
def voice(cfg: Config, ep: Episode) -> list[dict]:
    """One narration file per scene -> work/<ep>/audio/<scene>.wav (48 kHz mono PCM, exact length)."""
    scenes = scriptfmt.all_scenes(scriptfmt.parse(ep.file("script.md").read_text()))
    out_dir = ep.dir("audio")
    provider = cfg.voice_provider
    voice_id = cfg.get("voice.voice_id") or os.environ.get("ELEVENLABS_VOICE_ID", "")
    model_id = cfg.get("voice.model_id", "eleven_multilingual_v2")
    wpm = float(cfg.get("voice.words_per_minute", 145))
    if provider == "elevenlabs" and not (os.environ.get("ELEVENLABS_API_KEY") and voice_id):
        raise PipelineError("ElevenLabs needs ELEVENLABS_API_KEY and voice.voice_id (or ELEVENLABS_VOICE_ID).")

    manifest = []
    for i, sc in enumerate(scenes):
        key = _hash(provider, voice_id, model_id, sc.narration, str(wpm) if provider == "silent" else "")
        wav = out_dir / f"{sc.id}.wav"
        meta_path = out_dir / f"{sc.id}.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        if not (wav.exists() and meta.get("key") == key):
            if provider == "elevenlabs":
                raw = out_dir / f"{sc.id}.mp3"
                _elevenlabs(
                    sc.narration, raw, voice_id, model_id,
                    prev=scenes[i - 1].narration if i else "",
                    nxt=scenes[i + 1].narration if i + 1 < len(scenes) else "",
                    settings=cfg.get("voice.settings", {}) or {},
                )
                _run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", str(wav)])
            elif provider == "silent":
                secs = max(1.5, sc.words / wpm * 60 + 0.4)
                _run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                      "-t", f"{secs:.3f}", "-c:a", "pcm_s16le", str(wav)])
            else:
                raise PipelineError(f"Unknown voice provider '{provider}' (use elevenlabs or silent).")
            meta = {"key": key, "duration": duration(wav), "provider": provider}
            meta_path.write_text(json.dumps(meta))
            print(f"  voice {sc.id}: {meta['duration']:.1f}s")
        manifest.append({"scene": sc.id, "wav": str(wav), "duration": meta["duration"]})
    total = sum(m["duration"] for m in manifest)
    print(f"Narration: {len(manifest)} scenes, {total / 60:.1f} min ({provider})")
    return manifest


def _elevenlabs(text: str, out: Path, voice_id: str, model_id: str, *, prev: str, nxt: str, settings: dict) -> None:
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": model_id,
            "previous_text": prev[-600:] or None,  # keeps intonation continuous across scenes
            "next_text": nxt[:600] or None,
            "voice_settings": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, **settings},
        },
        timeout=180,
    )
    if resp.status_code != 200:
        raise PipelineError(f"ElevenLabs error {resp.status_code}: {resp.text[:300]}")
    out.write_bytes(resp.content)


# ====================================================================== images
def images(cfg: Config, ep: Episode, *, only: list[str] | None = None) -> None:
    """One image per shot -> work/<ep>/images/<shot>.png"""
    shots_path = ep.work / "shots.json"
    if not shots_path.exists():
        raise PipelineError(f"No shot list. Run: python -m yt shots {ep.id}")
    plan = json.loads(shots_path.read_text())
    out_dir = ep.dir("images")
    provider = cfg.image_provider
    style = " ".join(str(cfg.get("images.style_prompt", "")).split())

    with open(out_dir / "prompts.csv", "w", newline="") as f:  # handy for manual tools (e.g. Midjourney)
        w = csv.writer(f)
        w.writerow(["shot_id", "file", "prompt"])
        for p in plan:
            w.writerow([p["id"], f"{p['id']}.png", f"{style} {p['prompt']}".strip()])
    if only:
        plan = [p for p in plan if p["id"] in only or p["scene"] in only]

    todo = []
    for p in plan:
        png = out_dir / f"{p['id']}.png"
        meta_path = out_dir / f"{p['id']}.json"
        key = _hash(provider, style, p["prompt"])
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        if png.exists() and (meta.get("key") == key or meta.get("locked") or provider == "manual"):
            continue  # cached, hand-locked, or (manual mode) never overwrite an existing file
        todo.append((p, png, meta_path, key))

    if provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        raise PipelineError("images.provider is 'openai' but OPENAI_API_KEY is not set.")

    def make(item: tuple) -> str:
        p, png, meta_path, key = item
        if provider == "openai":
            _openai_image(cfg, f"{style} {p['prompt']}", png)
        elif provider in ("placeholder", "manual"):
            placeholder(p["prompt"], p["id"], png)
        else:
            raise PipelineError(f"Unknown image provider '{provider}' (openai | placeholder | manual).")
        meta = {"key": key, "provider": provider, "prompt": p["prompt"]}
        if provider != "openai":
            meta["placeholder_sha"] = file_sha(png)  # lets render tell a storyboard card from real art
        meta_path.write_text(json.dumps(meta))
        return p["id"]

    workers = int(cfg.get("images.parallel", 4)) if provider == "openai" else 8
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for n, shot_id in enumerate(pool.map(make, todo), 1):
            if provider == "openai" or n % 25 == 0:
                print(f"  image {n}/{len(todo)}: {shot_id}")
    print(f"Images: {len(plan)} shots, {len(todo)} generated ({provider}). Prompts: {out_dir / 'prompts.csv'}")
    if provider == "manual":
        print("  Manual mode: drop your own PNGs into that folder with the same file names, then re-render.")


def _openai_image(cfg: Config, prompt: str, out: Path, size: str | None = None) -> None:
    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        json={
            "model": cfg.get("images.model", "gpt-image-1"),
            "prompt": prompt,
            "size": size or cfg.get("images.size", "1536x1024"),
            "quality": cfg.get("images.quality", "medium"),
            "n": 1,
        },
        timeout=300,
    )
    if resp.status_code != 200:
        raise PipelineError(f"Image API error {resp.status_code}: {resp.text[:300]}")
    out.write_bytes(base64.b64decode(resp.json()["data"][0]["b64_json"]))


def placeholder(prompt: str, label: str, out: Path, size: tuple[int, int] = (1536, 1024)) -> None:
    """A storyboard card: lets you check pacing and the cut before paying for art."""
    img = Image.new("RGB", size, PAPER)
    d = ImageDraw.Draw(img)
    w, h = size
    for inset, width in ((28, 5), (40, 2)):
        d.rounded_rectangle([inset, inset, w - inset, h - inset], radius=26, outline=INK, width=width)
    big = ImageFont.truetype(FONT_FALLBACK, int(h * 0.045))
    small = ImageFont.truetype(FONT_FALLBACK, int(h * 0.028))
    d.text((70, 62), f"STORYBOARD  {label}", font=small, fill=(140, 120, 100))
    y = int(h * 0.30)
    for line in textwrap.wrap(prompt, 46)[:8]:
        tw = d.textlength(line, font=big)
        d.text(((w - tw) / 2, y), line, font=big, fill=INK)
        y += int(h * 0.065)
    # a little round-headed figure, so the card reads as "sketch"
    cx, cy = int(w * 0.88), int(h * 0.80)
    d.ellipse([cx - 24, cy - 90, cx + 24, cy - 42], outline=INK, width=4)
    d.line([cx, cy - 42, cx, cy + 10], fill=INK, width=4)
    d.line([cx - 30, cy - 20, cx + 30, cy - 20], fill=INK, width=4)
    d.line([cx, cy + 10, cx - 22, cy + 60], fill=INK, width=4)
    d.line([cx, cy + 10, cx + 22, cy + 60], fill=INK, width=4)
    img.save(out)


# ================================================================== the meter
METER_ZONES = [("SAFE", (122, 150, 112)), ("SHAKY", (205, 160, 70)), ("NEAR-DEATH", (170, 62, 48))]
NEEDLE = {"safe": 0.17, "shaky": 0.5, "near-death": 0.86}


def meter_png(cfg: Config, state: str, out: Path, width: int) -> Path:
    """Hand-drawn style gauge: three zones and a needle. A mood gauge, never a number."""
    import math

    scale = 3  # draw big, downsample for smooth lines
    W = width * scale
    H = int(W * 0.72)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=W // 12, fill=PAPER + (238,), outline=INK + (255,), width=3 * scale)
    cx, cy, r = W // 2, int(H * 0.80), int(W * 0.38)
    for i, (_, color) in enumerate(METER_ZONES):
        a0, a1 = 180 + i * 60, 180 + (i + 1) * 60
        d.arc([cx - r, cy - r, cx + r, cy + r], a0 + 2, a1 - 2, fill=color + (255,), width=int(r * 0.26))
    frac = NEEDLE.get(state, 0.17)
    ang = math.radians(180 + 180 * frac)
    tip = (cx + int(r * 0.92 * math.cos(ang)), cy + int(r * 0.92 * math.sin(ang)))
    d.line([cx, cy, *tip], fill=INK + (255,), width=5 * scale)
    d.ellipse([cx - 9 * scale, cy - 9 * scale, cx + 9 * scale, cy + 9 * scale], fill=INK + (255,))
    f = font(cfg, "labels.font", int(H * 0.15))
    name = dict(zip(NEEDLE, [z[0] for z in METER_ZONES])).get(state, "SAFE")
    color = dict(zip(NEEDLE, [z[1] for z in METER_ZONES])).get(state, INK)
    tw = d.textlength(name, font=f)
    d.text(((W - tw) / 2, int(H * 0.06)), name, font=f, fill=color + (255,))
    img = img.resize((width, int(width * 0.72)), Image.LANCZOS)
    img.save(out)
    return out


# ================================================================= thumbnails
def thumbnails(cfg: Config, ep: Episode) -> list[Path]:
    import yaml

    pack_path = ep.file("packaging.yaml")
    if not pack_path.exists():
        raise PipelineError(f"No packaging.yaml. Write one or run: python -m yt package {ep.id}")
    concepts = (yaml.safe_load(pack_path.read_text()) or {}).get("thumbnails", [])
    out_dir = ep.dir("thumbnails")
    style = " ".join(str(cfg.get("images.style_prompt", "")).split())
    provider = cfg.image_provider
    made = []
    for c in concepts:
        raw = out_dir / f"raw-{c['id']}.png"
        meta_path = out_dir / f"raw-{c['id']}.json"
        key = _hash(provider, style, c["prompt"])
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        if not (raw.exists() and (meta.get("key") == key or meta.get("locked"))):
            if provider == "openai":
                _openai_image(cfg, f"{style} {c['prompt']} Strong single focal point, readable at small size.", raw)
            else:
                placeholder(c["prompt"], f"THUMB {c['id']}", raw)
            meta_path.write_text(json.dumps({"key": key}))
        img = Image.open(raw).convert("RGB")
        img = _crop_16x9(img).resize((1280, 720), Image.LANCZOS)
        if c.get("text"):
            _overlay_text(cfg, img, c["text"])
        jpg = out_dir / f"thumb-{c['id']}.jpg"
        img.save(jpg, "JPEG", quality=90, optimize=True)
        made.append(jpg)
    print(f"Thumbnails: {', '.join(p.name for p in made)}")
    return made


def _crop_16x9(img: Image.Image) -> Image.Image:
    w, h = img.size
    target_h = int(w * 9 / 16)
    if target_h <= h:
        top = (h - target_h) // 2
        return img.crop((0, top, w, top + target_h))
    target_w = int(h * 16 / 9)
    left = (w - target_w) // 2
    return img.crop((left, 0, left + target_w, h))


def _overlay_text(cfg: Config, img: Image.Image, text: str) -> None:
    d = ImageDraw.Draw(img)
    f = font(cfg, "thumbnails.font", 150)
    tw = d.textlength(text, font=f)
    x, y = 60, img.height - 210
    if tw > img.width - 120:
        f = font(cfg, "thumbnails.font", int(150 * (img.width - 120) / tw))
    d.text((x, y), text, font=f, fill=(250, 245, 235), stroke_width=10, stroke_fill=INK)
