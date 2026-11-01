"""Posting. Two modes:

manual (default) — builds an upload kit: video, thumbnails, captions, Shorts and
    a metadata sheet to paste into YouTube Studio. Use this until your Google
    Cloud project passes YouTube's API audit: uploads from an unverified project
    (created after 28 July 2020) are locked to private and can't be made public.

api — uploads through the YouTube Data API v3 as private with a scheduled
    publish time (status.publishAt), sets the thumbnail and uploads captions.
"""
from __future__ import annotations

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml

from .config import Config, Episode, PipelineError

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # thumbnails + captions
]


def _ready(ep: Episode) -> dict:
    gate = ep.state().get("approvals", {}).get("final", {})
    build = ep.build().get("render", {})
    if not gate.get("approved"):
        raise PipelineError(f"Final cut not approved. Watch it, then: python -m yt approve {ep.id} final")
    if build.get("script_digest") != gate.get("script_digest") or build.get("dry_run"):
        raise PipelineError("The render changed since final approval (or was a dry run). Re-approve the final cut.")
    return build


def description(cfg: Config, ep: Episode, chapters: list[str]) -> str:
    pack = yaml.safe_load(ep.file("packaging.yaml").read_text()) or {}
    text = pack.get("description", "").strip()
    block = "Chapters:\n" + "\n".join(chapters)
    text = text.replace("{CHAPTERS}", block) if "{CHAPTERS}" in text else f"{text}\n\n{block}"
    footer = cfg.get("channel.description_footer", "")
    return f"{text}\n\n{footer}".strip() if footer else text


def publish(cfg: Config, ep: Episode, *, mode: str | None = None, at: str | None = None) -> str:
    build = _ready(ep)
    mode = mode or cfg.get("upload.mode", "manual")
    pack = yaml.safe_load(ep.file("packaging.yaml").read_text()) or {}
    title = (pack.get("titles") or [ep.title])[0]
    if len(title) > 100:
        raise PipelineError(f"Title is {len(title)} characters; YouTube allows 100.")
    publish_at = at or ep.meta.get("publish_at")
    desc = description(cfg, ep, build.get("chapters", []))
    render_dir = ep.work / "render"
    thumbs = sorted((ep.work / "thumbnails").glob("thumb-*.jpg"))
    if mode == "manual":
        return _kit(ep, title, desc, pack, publish_at, render_dir, thumbs)
    if mode == "api":
        return _api_upload(cfg, ep, title, desc, pack, publish_at, render_dir, thumbs)
    raise PipelineError("upload mode must be 'manual' or 'api'")


def _kit(ep: Episode, title: str, desc: str, pack: dict, publish_at: str | None, render_dir: Path, thumbs: list[Path]) -> str:
    kit = ep.dir("upload-kit")
    shutil.copy2(render_dir / "final.mp4", kit / f"{ep.id}.mp4")
    if (render_dir / "captions.srt").exists():
        shutil.copy2(render_dir / "captions.srt", kit / f"{ep.id}.en.srt")
    for t in thumbs:
        shutil.copy2(t, kit / t.name)
    shorts = sorted((render_dir / "shorts").glob("*.mp4")) if (render_dir / "shorts").exists() else []
    for s in shorts:
        shutil.copy2(s, kit / f"short-{s.name}")
    when = publish_at or "(not set — see calendar.yaml)"
    alt = "\n".join(f"- {t}" for t in (pack.get("titles") or [])[1:])
    short_lines = "\n".join(f"- short-{s['id']}.mp4 — title: {s['title']}" for s in pack.get("shorts", []))
    sheet = f"""# Upload sheet — {ep.id}

## Main video: `{ep.id}.mp4`
**Title:** {title}

**Alternate titles (for Test & Compare):**
{alt or '- none'}

**Schedule:** {when} (Visibility → Schedule)

**Description:**
```
{desc}
```

**Tags:** {', '.join(pack.get('tags', []))}

**Thumbnail:** thumb-A.jpg. Add thumb-B / thumb-C under "Test & compare".
**Subtitles:** upload `{ep.id}.en.srt` (Subtitles → Upload file → With timing).
**Category:** Education · Made for kids: No · Altered or synthetic content: see note below.
**End screen:** next episode + subscribe. **Playlist:** Almost Didn't Exist.

**Pinned comment:**
> {pack.get('pinned_comment', '')}

## Shorts
{short_lines or '- none'}
In each Short: set "Related video" to the main video.

## Checklist before you press Schedule
- [ ] Watched the full video once at 1x, with sound
- [ ] Title length matches the video (the "in N Minutes" number)
- [ ] Chapters show in the description preview
- [ ] AI disclosure: hand-drawn sketch style is clearly not real → normally "No". If any image looks
      like a real photo of a real person or event, answer "Yes".
- [ ] No company logos or ripped footage in the video or thumbnail
"""
    (kit / "UPLOAD.md").write_text(sheet)
    st = ep.state()
    st["published"] = {"mode": "manual-kit", "kit": str(kit), "prepared_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    ep.save_state(st)
    return f"Upload kit ready: {kit} (open UPLOAD.md)"


def _credentials():
    try:
        from google.oauth2.credentials import Credentials
    except ImportError as e:
        raise PipelineError("Install the Google client: pip install -r requirements.txt") from e
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if missing:
        raise PipelineError(f"Missing {', '.join(missing)}. Run `python -m yt auth` once to get a refresh token.")
    return Credentials(
        None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"], scopes=SCOPES,
    )


def _api_upload(cfg: Config, ep: Episode, title: str, desc: str, pack: dict, publish_at: str | None,
                render_dir: Path, thumbs: list[Path]) -> str:
    from googleapiclient.discovery import build as gbuild
    from googleapiclient.http import MediaFileUpload

    if not publish_at:
        raise PipelineError("No publish time. Set publish_at in calendar.yaml or pass --at 2026-11-12T15:00:00Z")
    when = datetime.fromisoformat(publish_at.replace("Z", "+00:00"))
    if when <= datetime.now(timezone.utc):
        raise PipelineError(f"publish_at {publish_at} is in the past.")
    status = {
        "privacyStatus": "private",  # required for a scheduled publish
        "publishAt": when.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "selfDeclaredMadeForKids": bool(cfg.get("channel.made_for_kids", False)),
    }
    synthetic = cfg.get("upload.contains_synthetic_media")
    if synthetic is not None:
        status["containsSyntheticMedia"] = bool(synthetic)
    yt = gbuild("youtube", "v3", credentials=_credentials(), cache_discovery=False)
    body = {
        "snippet": {
            "title": title, "description": desc[:5000], "tags": pack.get("tags", []),
            "categoryId": str(cfg.get("channel.category_id", "27")),
            "defaultLanguage": cfg.get("channel.language", "en"),
            "defaultAudioLanguage": cfg.get("channel.language", "en"),
        },
        "status": status,
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(render_dir / "final.mp4"), chunksize=-1, resumable=True))
    response = None
    while response is None:
        progress, response = req.next_chunk()
        if progress:
            print(f"  uploading… {int(progress.progress() * 100)}%")
    video_id = response["id"]
    if thumbs:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbs[0]))).execute()
    srt = render_dir / "captions.srt"
    if srt.exists():
        yt.captions().insert(
            part="snippet",
            body={"snippet": {"videoId": video_id, "language": cfg.get("channel.language", "en"), "name": "English"}},
            media_body=MediaFileUpload(str(srt)),
        ).execute()
    st = ep.state()
    st["published"] = {"mode": "api", "video_id": video_id, "publish_at": status["publishAt"],
                       "uploaded_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    ep.save_state(st)
    status_now = yt.videos().list(part="status", id=video_id).execute()["items"][0]["status"]
    note = ""
    if status_now.get("privacyStatus") == "private" and not status_now.get("publishAt"):
        note = ("\n  WARNING: YouTube kept the video private with no schedule. Your API project is probably "
                "unverified (uploads locked to private). Use manual mode until the audit passes.")
    return f"Uploaded https://youtu.be/{video_id} — scheduled for {status['publishAt']}.{note}"


def auth(client_secret: str) -> str:
    """One-time: opens a browser to authorise your channel and prints a refresh token."""
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(client_secret, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    return (
        "Add these to your .env (and to GitHub secrets if you use the workflow):\n"
        f"YT_CLIENT_ID={creds.client_id}\nYT_CLIENT_SECRET={creds.client_secret}\nYT_REFRESH_TOKEN={creds.refresh_token}"
    )
