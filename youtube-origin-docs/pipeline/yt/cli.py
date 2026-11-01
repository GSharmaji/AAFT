"""Command line: python -m yt <command> <episode> [options]

Typical week (one episode):
  python -m yt draft ep02-7-eleven          # research -> script -> fact-check (Claude + web search)
  # ... you fix facts, delete [VERIFY] tags ...
  python -m yt approve ep02-7-eleven script # human gate 1
  python -m yt produce ep02-7-eleven        # shots -> voice -> images -> render -> thumbnails -> shorts
  # ... you watch final.mp4 ...
  python -m yt approve ep02-7-eleven final  # human gate 2
  python -m yt publish ep02-7-eleven        # upload kit (manual) or scheduled API upload
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from . import media, render, writing
from .config import PIPELINE_DIR, Config, PipelineError


def _load_env() -> None:
    """Load pipeline/.env if present (KEY=VALUE lines). Real env vars win."""
    path = PIPELINE_DIR / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def main(argv: list[str] | None = None) -> int:
    _load_env()
    p = argparse.ArgumentParser(prog="python -m yt", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, help="path to config.yaml")
    p.add_argument("--dry-run", action="store_true",
                   help="no API calls: silent narration + storyboard cards (an animatic to check pacing)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("ideate", help="score candidate companies with the playbook's 5 tests")
    s.add_argument("companies", nargs="+")

    for name, help_ in [
        ("research", "web research brief -> research.md"),
        ("write", "draft the script from research.md -> script.md"),
        ("factcheck", "check every claim in the script -> factcheck.md"),
        ("draft", "research + write + factcheck"),
        ("check", "lint the script: structure, word counts, open [VERIFY] tags"),
        ("shots", "split scenes into ~4s shots + image prompts"),
        ("voice", "narration per scene"),
        ("images", "one image per shot"),
        ("render", "assemble the video"),
        ("thumbnails", "thumbnails A/B/C from packaging.yaml"),
        ("shorts", "vertical Shorts from packaging.yaml"),
        ("package", "draft packaging.yaml (titles, description, tags, thumbnails, shorts)"),
        ("produce", "shots + voice + images + render + thumbnails + shorts"),
        ("publish", "upload kit (manual) or scheduled upload (api)"),
        ("status", "where this episode is"),
    ]:
        s = sub.add_parser(name, help=help_)
        s.add_argument("episode")
        if name in ("research", "write", "draft", "package"):
            s.add_argument("--force", action="store_true", help="overwrite the existing file")
        if name in ("render", "produce", "shorts"):
            s.add_argument("--preview", action="store_true", help="fast 480p render")
        if name in ("render", "produce"):
            s.add_argument("--sections", help="only these story parts, e.g. 1,4 (preview use)")
        if name == "publish":
            s.add_argument("--mode", choices=["manual", "api"])
            s.add_argument("--at", help="override publish time, e.g. 2026-11-12T15:00:00Z")
        if name == "images":
            s.add_argument("--only", help="comma-separated shot or scene ids to (re)generate")

    s = sub.add_parser("approve", help="human gates: 'script' (facts checked) and 'final' (cut watched)")
    s.add_argument("episode")
    s.add_argument("gate", choices=["script", "final"])
    s.add_argument("--by", default=os.environ.get("YT_REVIEWER") or getpass.getuser())
    s.add_argument("--force", action="store_true", help="approve a script that still has [VERIFY] tags (not recommended)")

    s = sub.add_parser("auth", help="one-time YouTube OAuth; prints a refresh token")
    s.add_argument("client_secret", help="OAuth client JSON downloaded from Google Cloud Console")

    args = p.parse_args(argv)
    try:
        cfg = Config(args.config, dry_run=args.dry_run)
        return _dispatch(cfg, args)
    except PipelineError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def _calendar_next(cfg: Config, ep_id: str) -> str:
    eps = cfg.calendar()
    ids = [e["id"] for e in eps]
    if ep_id in ids and ids.index(ep_id) + 1 < len(ids):
        nxt = eps[ids.index(ep_id) + 1]
        return f"{nxt['company']} — {nxt.get('near_death', '')}"
    return ""


def _dispatch(cfg: Config, a: argparse.Namespace) -> int:
    if a.cmd == "ideate":
        for i in writing.ideate(cfg, a.companies):
            print(f"{i['total']:>2}/25  {i['company']:<20} {i['title']}")
        return 0
    if a.cmd == "auth":
        from .publish import auth
        print(auth(a.client_secret))
        return 0

    ep = cfg.episode(a.episode)
    sections = [int(x) for x in a.sections.split(",")] if getattr(a, "sections", None) else None
    script = ep.file("script.md")

    # `draft` resumes: steps whose file already exists are skipped (never overwrite a
    # paid-for research brief or a script you have edited) unless --force is given.
    resume = a.cmd == "draft" and not a.force
    if a.cmd in ("research", "draft"):
        if resume and ep.file("research.md").exists():
            print("research.md exists — skipping research (use --force to redo it).")
        else:
            print(writing.research(cfg, ep, force=a.force))
    if a.cmd in ("write", "draft"):
        if resume and script.exists():
            print("script.md exists — skipping the script (use --force to overwrite it).")
        else:
            print(writing.write(cfg, ep, force=a.force, next_episode=_calendar_next(cfg, ep.id)))
    if a.cmd in ("factcheck", "draft"):
        print(writing.factcheck(cfg, ep))
        if a.cmd == "draft":
            print(f"\nNext: fix the script using factcheck.md, delete each [VERIFY] tag, then: python -m yt approve {ep.id} script")
        return 0
    if a.cmd in ("research", "write"):
        return 0
    if a.cmd == "check":
        print(writing.check(ep))
        return 0
    if a.cmd == "approve":
        print(writing.approve(cfg, ep, a.gate, by=a.by, force=a.force))
        return 0
    if a.cmd == "package":
        print(writing.package(cfg, ep, force=a.force))
        return 0
    if a.cmd == "status":
        return _status(cfg, ep)
    if a.cmd == "publish":
        from .publish import publish
        print(publish(cfg, ep, mode=a.mode, at=a.at))
        return 0

    if not script.exists():
        raise PipelineError(f"No script for {ep.id}. Run: python -m yt draft {ep.id}")
    # Gate 1 protects the money-spending, at-scale steps. Shot prompts and a few test
    # images (--only, e.g. to lock the visual style) are allowed before approval.
    if a.cmd in ("voice", "render", "produce") or (a.cmd == "images" and not a.only):
        writing.require_script_approval(ep, dry_run=cfg.dry_run or getattr(a, "preview", False))
    if a.cmd in ("shots", "produce"):
        print(f"Shots: {len(writing.shots(cfg, ep))}")
    if a.cmd in ("voice", "produce"):
        media.voice(cfg, ep)
    if a.cmd in ("images", "produce"):
        only = [x.strip() for x in a.only.split(",")] if getattr(a, "only", None) else None
        media.images(cfg, ep, only=only)
    if a.cmd in ("render", "produce"):
        render.render(cfg, ep, preview=a.preview, sections=sections)
    if a.cmd in ("thumbnails", "produce"):
        if ep.file("packaging.yaml").exists():
            media.thumbnails(cfg, ep)
        else:
            print(f"Skipping thumbnails: no packaging.yaml (run: python -m yt package {ep.id})")
    if a.cmd in ("shorts", "produce"):
        if ep.file("packaging.yaml").exists():
            render.shorts(cfg, ep, preview=a.preview)
    if a.cmd == "produce" and not (a.preview or sections):
        print(f"\nNext: watch {ep.work / 'render' / 'final.mp4'} start to finish, then: python -m yt approve {ep.id} final")
    return 0


def _status(cfg: Config, ep) -> int:
    from . import scriptfmt

    print(f"{ep.id} — {ep.company} — {ep.title}")
    print(f"  publish_at: {ep.meta.get('publish_at', '-')}")
    for name in ("research.md", "script.md", "factcheck.md", "packaging.yaml"):
        print(f"  {name:<15} {'yes' if ep.file(name).exists() else '-'}")
    if ep.file("script.md").exists():
        print(f"  open [VERIFY] tags: {len(scriptfmt.verify_tags(ep.file('script.md').read_text()))}")
    from .writing import _digest

    approvals = ep.state().get("approvals", {})
    current = _digest(ep.file("script.md").read_text()) if ep.file("script.md").exists() else None
    for gate in ("script", "final"):
        g = approvals.get(gate, {})
        text = f"APPROVED by {g.get('by', '?')}" if g.get("approved") else "not yet"
        if g.get("approved") and g.get("script_digest") != current:
            text += " — but the script has changed since (re-approve)"
        print(f"  approval {gate:<6} {text}")
    r = ep.build().get("render", {})
    if r:
        kind = "animatic (dry run)" if r.get("dry_run") else "real"
        print(f"  last render: {r.get('duration', 0) / 60:.1f} min, {kind}")
    pub = ep.state().get("published")
    print(f"  published: {pub if pub else '-'}")
    return 0
