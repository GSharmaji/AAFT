"""Assemble the video with ffmpeg.

Timeline: each scene's narration length (from the audio files) is split across
its shots by word count, so pictures change in sync with what is being said.
Each shot = one still image + a slow camera move (zoom in/out, pan) + optional
pop-up label + the Near-Death Meter. Shots are cached, so a re-render after a
small fix only rebuilds what changed.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import textwrap
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import media, scriptfmt
from .config import Config, Episode, PipelineError

MOVES = ("in", "panr", "out", "panl")
RENDER_VERSION = 4  # bump when shot drawing code changes, so cached shots are rebuilt


def _fmt_time(secs: float, srt: bool = False) -> str:
    ms = int(round(secs * 1000))
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    if srt:
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _esc(path: Path | str) -> str:
    return str(path).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def build_timeline(ep: Episode, fps: int, scene_ids: list[str] | None = None) -> list[dict]:
    plan_path = ep.work / "shots.json"
    if not plan_path.exists():
        raise PipelineError(f"No shot list. Run: python -m yt shots {ep.id}")
    plan = json.loads(plan_path.read_text())
    scenes: list[str] = []
    for p in plan:
        if p["scene"] not in scenes:
            scenes.append(p["scene"])
    if scene_ids is not None:
        scenes = [s for s in scenes if s in scene_ids]
    timeline: list[dict] = []
    t = 0.0
    for sid in scenes:
        meta = ep.work / "audio" / f"{sid}.json"
        if not meta.exists():
            raise PipelineError(f"No narration for scene {sid}. Run: python -m yt voice {ep.id}")
        dur = json.loads(meta.read_text())["duration"]
        f0, f1 = round(t * fps), round((t + dur) * fps)
        shots = [p for p in plan if p["scene"] == sid]
        weights = [max(p["words"], 3) for p in shots]
        total_frames = f1 - f0
        raw = [total_frames * w / sum(weights) for w in weights]
        frames = [int(x) for x in raw]
        for i in sorted(range(len(raw)), key=lambda i: raw[i] - frames[i], reverse=True)[: total_frames - sum(frames)]:
            frames[i] += 1
        start = f0
        for p, n in zip(shots, frames):
            timeline.append({**p, "frames": max(n, 1), "start": start / fps, "end": (start + n) / fps,
                             "wav": str(ep.work / "audio" / f"{sid}.wav")})
            start += n
        t += dur
    return timeline


def _zoompan(move: str, zoom: float, frames: int, w: int, h: int, fps: int) -> str:
    den = max(frames - 1, 1)
    dz = zoom - 1
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    z, x, y = {
        "in": (f"1+{dz:.4f}*on/{den}", cx, cy),
        "out": (f"{zoom:.4f}-{dz:.4f}*on/{den}", cx, cy),
        "panr": (f"{zoom:.4f}", f"(iw-iw/zoom)*on/{den}", cy),
        "panl": (f"{zoom:.4f}", f"(iw-iw/zoom)*(1-on/{den})", cy),
    }[move]
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps}"


def render_shot(cfg: Config, shot: dict, out: Path, *, w: int, h: int, fps: int, scale: int, crf: int,
                preset: str, move: str, meter: Path | None, vertical: bool = False, top_text: str = "") -> Path:
    img = Path(shot["image"])
    label = f"“{shot['label']}”" if shot.get("label") else ""
    font = cfg.resolve(cfg.get("labels.font", media.FONT_FALLBACK))
    if not font.exists():
        font = Path(media.FONT_FALLBACK)
    zoom = float(cfg.get("video.zoom", 1.10))
    key = hashlib.sha256(json.dumps([
        media.file_sha(img), shot["frames"], w, h, fps, scale, crf, move, zoom, label, str(meter), vertical,
        top_text, str(font), RENDER_VERSION,
    ]).encode()).hexdigest()[:16]
    meta = out.with_suffix(".json")
    if out.exists() and meta.exists() and json.loads(meta.read_text()).get("key") == key:
        return out

    pic_w, pic_h = (w, int(w * 9 / 16) // 2 * 2) if vertical else (w, h)
    inputs = ["-i", str(img)]
    chain = [f"[0:v]scale={pic_w * scale}:{pic_h * scale}:force_original_aspect_ratio=increase,"
             f"crop={pic_w * scale}:{pic_h * scale},setsar=1,"
             f"{_zoompan(move, zoom, shot['frames'], pic_w, pic_h, fps)}[pic]"]
    cur = "pic"
    pic_top = (h - pic_h) // 2 - int(h * 0.04) if vertical else 0
    if vertical:
        chain.append(f"[{cur}]pad={w}:{h}:0:{pic_top}:color=0xF3EBDD[pad]")
        cur = "pad"
    if meter is not None:
        inputs += ["-i", str(meter)]
        margin = int(w * 0.025)
        y = pic_top + margin if vertical else margin
        chain.append(f"[{cur}][1:v]overlay=x=W-w-{margin}:y={y}[met]")
        cur = "met"
    texts = []
    tmp_files = []
    if label:
        tf = out.with_suffix(".label.txt")
        tf.write_text(label)
        tmp_files.append(tf)
        fs = int(h * (0.032 if vertical else 0.056))
        y = f"{pic_top + pic_h + int(h * 0.03)}" if vertical else "h*0.80-text_h/2"
        texts.append(
            f"drawtext=fontfile='{_esc(font)}':textfile='{_esc(tf)}':expansion=none:fontsize={fs}:"
            f"fontcolor=0x3A3028:box=1:boxcolor=0xF6EFE2@0.95:boxborderw={int(fs * 0.45)}:"
            f"x=(w-text_w)/2:y={y}:alpha='if(lt(t,0.35),0,min(1,(t-0.35)/0.25))'"
        )
    if vertical and top_text:
        fs = int(h * 0.042)
        for n, line in enumerate(textwrap.wrap(top_text, 20)[:4]):  # one drawtext per line = centred lines
            tf = out.with_suffix(f".top{n}.txt")
            tf.write_text(line)
            tmp_files.append(tf)
            texts.append(
                f"drawtext=fontfile='{_esc(font)}':textfile='{_esc(tf)}':expansion=none:fontsize={fs}:"
                f"fontcolor=0x3A3028:x=(w-text_w)/2:y={int(h * 0.10 + n * fs * 1.3)}"
            )
    if texts:
        chain.append(f"[{cur}]{','.join(texts)}[txt]")
        cur = "txt"
    chain.append(f"[{cur}]format=yuv420p[vout]")
    cmd = ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chain), "-map", "[vout]",
           "-frames:v", str(shot["frames"]), "-r", str(fps), "-c:v", "libx264", "-preset", preset,
           "-crf", str(crf), "-g", str(fps * 2), "-pix_fmt", "yuv420p", "-an", str(out)]
    media._run(cmd)
    for tf in tmp_files:
        tf.unlink(missing_ok=True)
    meta.write_text(json.dumps({"key": key}))
    return out


def _render_video(cfg: Config, ep: Episode, timeline: list[dict], out_dir: Path, *, w: int, h: int, fps: int,
                  scale: int, crf: int, preset: str, vertical: bool = False, top_text: str = "") -> Path:
    shots_dir = out_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    meter_w = int(w * (0.20 if vertical else 0.13))
    meters = {s: media.meter_png(cfg, s, out_dir / f"meter-{s}.png", meter_w) for s in ("safe", "shaky", "near-death")}

    jobs = []
    for i, shot in enumerate(timeline):
        shot["image"] = str(ep.work / "images" / f"{shot['id']}.png")
        if not Path(shot["image"]).exists():
            raise PipelineError(f"Missing image for {shot['id']}. Run: python -m yt images {ep.id}")
        meter = meters.get(shot["meter"]) if shot["meter"] != "off" else None
        jobs.append((shot, shots_dir / f"{shot['id']}.mp4", MOVES[i % len(MOVES)], meter))

    def run(job):
        shot, path, move, meter = job
        return render_shot(cfg, shot, path, w=w, h=h, fps=fps, scale=scale, crf=crf, preset=preset,
                           move=move, meter=meter, vertical=vertical,
                           top_text=top_text if vertical else "")

    with ThreadPoolExecutor(max_workers=int(cfg.get("video.parallel", 3))) as pool:
        for n, _ in enumerate(pool.map(run, jobs), 1):
            if n % 20 == 0 or n == len(jobs):
                print(f"  shots rendered: {n}/{len(jobs)}")

    vlist = out_dir / "video.txt"
    vlist.write_text("".join(f"file '{p.resolve()}'\n" for _, p, _, _ in jobs))
    video = out_dir / "video.mp4"
    media._run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(vlist), "-c", "copy", str(video)])

    wavs: list[str] = []
    for shot in timeline:
        if shot["wav"] not in wavs:
            wavs.append(shot["wav"])
    alist = out_dir / "audio.txt"
    alist.write_text("".join(f"file '{Path(p).resolve()}'\n" for p in wavs))
    narration = out_dir / "narration.wav"
    media._run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(alist), "-c", "copy", str(narration)])
    return _mux(cfg, video, narration, out_dir / "out.mp4")


def _mux(cfg: Config, video: Path, narration: Path, out: Path) -> Path:
    music = cfg.get("video.music")
    music_path = cfg.resolve(music) if music else None
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(narration)]
    norm = "loudnorm=I=-16:TP=-1.5:LRA=11"
    if music_path and music_path.exists():
        vol = float(cfg.get("video.music_volume", 0.10))
        cmd += ["-stream_loop", "-1", "-i", str(music_path)]
        graph = (f"[1:a]{norm},asplit=2[n1][n2];[2:a]volume={vol}[m];"
                 f"[m][n1]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];"
                 f"[n2][duck]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        graph = f"[1:a]{norm}[a]"
    cmd += ["-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-shortest", "-movflags", "+faststart", str(out)]
    media._run(cmd)
    return out


def _settings(cfg: Config, preview: bool) -> dict:
    if preview:
        return dict(w=854, h=480, fps=24, scale=1, crf=28, preset="ultrafast")
    return dict(w=int(cfg.get("video.width", 1920)), h=int(cfg.get("video.height", 1080)),
                fps=int(cfg.get("video.fps", 30)), scale=int(cfg.get("video.prescale", 2)),
                crf=int(cfg.get("video.crf", 20)), preset=cfg.get("video.preset", "medium"))


def render(cfg: Config, ep: Episode, *, preview: bool = False, sections: list[int] | None = None) -> Path:
    s = _settings(cfg, preview)
    script_text = ep.file("script.md").read_text()
    parsed = scriptfmt.parse(script_text)
    scene_ids = None
    if sections:
        scene_ids = [sc.id for sec in parsed if sec.num in sections for sc in sec.scenes]
    timeline = build_timeline(ep, s["fps"], scene_ids)
    out_dir = ep.dir("render/preview" if preview else "render/full")
    tmp = _render_video(cfg, ep, timeline, out_dir, **s)
    name = "preview.mp4" if preview else ("partial.mp4" if sections else "final.mp4")
    final = ep.dir("render") / name
    shutil.move(str(tmp), final)

    total = timeline[-1]["end"] if timeline else 0
    _write_captions(timeline, ep.dir("render") / ("preview.srt" if preview else "captions.srt"))
    chapters = _write_chapters(parsed, timeline, ep.dir("render") / "chapters.txt")

    placeholders = sum(media.is_placeholder(Path(t["image"])) for t in timeline)
    silent = any(json.loads((ep.work / "audio" / f"{t['scene']}.json").read_text()).get("provider") == "silent"
                 for t in timeline)
    dry = bool(cfg.dry_run or placeholders or silent)
    if not preview and not sections:
        from .writing import _digest
        ep.save_build(render={
            "final": str(final), "duration": round(total, 2), "dry_run": dry,
            "placeholder_images": placeholders, "silent_voice": silent,
            "script_digest": _digest(script_text), "chapters": chapters,
        })
    print(f"Rendered {final} — {_fmt_time(total)} ({len(timeline)} shots)")
    if dry:
        print(f"  This is an ANIMATIC (silent voice: {silent}, placeholder images: {placeholders}). Not publishable.")
    if not sections:
        _title_check(ep.title, total)
    return final


def _title_check(title: str, secs: float) -> None:
    m = re.search(r"in (\d+) Minutes", title, re.I)
    if m and secs > 60:
        claimed, actual = int(m.group(1)), round(secs / 60)
        if claimed != actual:
            print(f"  TITLE CHECK: title says {claimed} minutes, video is ~{actual}. Update the title in calendar.yaml.")


def _write_captions(timeline: list[dict], path: Path) -> None:
    lines = []
    for i, t in enumerate(timeline, 1):
        text = "\n".join(textwrap.wrap(t["text"], 42))
        lines.append(f"{i}\n{_fmt_time(t['start'], True)} --> {_fmt_time(t['end'], True)}\n{text}\n")
    path.write_text("\n".join(lines))


def _write_chapters(parsed: list[scriptfmt.Section], timeline: list[dict], path: Path) -> list[str]:
    starts: dict[int, float] = {}
    for t in timeline:
        starts.setdefault(t["section"], t["start"])
    names = {sec.num: sec.title.strip('"') for sec in parsed}
    chapters = [f"{_fmt_time(starts[n])} {names.get(n, f'Part {n}')}" for n in sorted(starts)]
    path.write_text("\n".join(chapters) + "\n")
    return chapters


# ------------------------------------------------------------------- shorts
def shorts(cfg: Config, ep: Episode, *, preview: bool = False) -> list[Path]:
    import yaml

    pack = ep.file("packaging.yaml")
    if not pack.exists():
        raise PipelineError(f"No packaging.yaml for {ep.id}")
    specs = (yaml.safe_load(pack.read_text()) or {}).get("shorts", [])
    order = [sc.id for sc in scriptfmt.all_scenes(scriptfmt.parse(ep.file("script.md").read_text()))]
    made = []
    for spec in specs:
        first, last = spec["scenes"]
        if first not in order or last not in order:
            raise PipelineError(f"Short '{spec['id']}': unknown scene id(s) {first}..{last}")
        ids = order[order.index(first): order.index(last) + 1]
        s = _settings(cfg, preview)
        w, h = (540, 960) if preview else (1080, 1920)
        timeline = build_timeline(ep, s["fps"], ids)
        out_dir = ep.dir(f"render/shorts/{spec['id']}")
        tmp = _render_video(cfg, ep, timeline, out_dir, w=w, h=h, fps=s["fps"], scale=s["scale"], crf=s["crf"],
                            preset=s["preset"], vertical=True, top_text=spec.get("hook_text", ""))
        final = ep.dir("render/shorts") / f"{spec['id']}.mp4"
        shutil.move(str(tmp), final)
        secs = timeline[-1]["end"]
        warn = "  (over 60s: still allowed as a Short up to 3 min, but shorter usually performs better)" if secs > 60 else ""
        if secs > 180:
            raise PipelineError(f"Short '{spec['id']}' is {secs:.0f}s; Shorts must be 3 minutes or less.")
        print(f"Short {final.name}: {_fmt_time(secs)}{warn}")
        made.append(final)
    return made


def probe(path: Path) -> str:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                          "-of", "compact", str(path)], capture_output=True, text=True)
    return out.stdout.strip()
