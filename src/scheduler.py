#!/usr/bin/env python3
"""
LinkedIn post scheduler.

Reads content/posts.yaml, figures out which posts are due (date <= today) and
haven't been published yet (tracked in state/posted.json), and publishes them
via the official LinkedIn Posts API.

Designed to be run once a day (locally via cron, or via GitHub Actions).

Usage:
    python src/scheduler.py --dry-run          # show what WOULD post, call no API
    python src/scheduler.py                     # publish everything due
    python src/scheduler.py --id 2026-08-launch-01   # force a single post now
    python src/scheduler.py --all               # publish every post, ignore dates
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

import yaml

# Make `import linkedin_client` work whether run from repo root or src/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linkedin_client import LinkedInClient, LinkedInError  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS_FILE = os.path.join(REPO_ROOT, "content", "posts.yaml")
STATE_FILE = os.path.join(REPO_ROOT, "state", "posted.json")


def load_calendar() -> dict:
    with open(POSTS_FILE, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_state() -> dict:
    if os.path.isfile(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_state(state: dict) -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def render_text(post: dict, brand: dict) -> str:
    """Fill {{placeholders}}, append hashtags."""
    text = post.get("text", "").rstrip()
    for key, val in (brand or {}).items():
        text = text.replace("{{" + key + "}}", str(val))
    hashtags = post.get("hashtags") or []
    if hashtags:
        text = text + "\n\n" + " ".join(hashtags)
    return text


def select_due(posts: list, state: dict, today: dt.date, args) -> list:
    if args.id:
        chosen = [p for p in posts if p.get("id") == args.id]
        if not chosen:
            print(f"No post found with id '{args.id}'", file=sys.stderr)
        return chosen

    due = []
    for p in posts:
        pid = p.get("id")
        if not pid:
            print("Skipping a post with no 'id' field", file=sys.stderr)
            continue
        if pid in state:
            continue  # already published
        if args.all:
            due.append(p)
            continue
        post_date = dt.date.fromisoformat(str(p["date"]))
        if post_date <= today:
            due.append(p)
    return due


def main() -> int:
    parser = argparse.ArgumentParser(description="LinkedIn post scheduler")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be posted without calling the API")
    parser.add_argument("--id", help="Publish one specific post id now (ignores date)")
    parser.add_argument("--all", action="store_true",
                        help="Publish every not-yet-posted item, ignoring dates")
    args = parser.parse_args()

    calendar = load_calendar()
    brand = calendar.get("brand", {})
    posts = calendar.get("posts", [])
    state = load_state()
    today = dt.date.today()

    due = select_due(posts, state, today, args)

    if not due:
        print(f"Nothing due as of {today}. Up to date ✔")
        return 0

    print(f"{len(due)} post(s) to publish as of {today}:\n")

    client = None
    if not args.dry_run:
        try:
            client = LinkedInClient()
        except LinkedInError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    published = 0
    for post in due:
        pid = post["id"]
        text = render_text(post, brand)
        image = post.get("image")

        print("-" * 60)
        print(f"[{pid}]  scheduled {post.get('date', 'n/a')}")
        print(text)
        if image:
            print(f"(image: {image})")

        if args.dry_run:
            print("DRY RUN — not published")
            continue

        try:
            image_urn = None
            if image:
                img_path = image if os.path.isabs(image) else os.path.join(REPO_ROOT, image)
                image_urn = client.upload_image(img_path)
            urn = client.create_post(text, image_urn=image_urn,
                                     alt_text=post.get("alt_text", ""))
            state[pid] = {
                "posted_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "urn": urn,
            }
            save_state(state)  # save after each success so a crash never double-posts
            published += 1
            print(f"PUBLISHED ✔  {urn}")
        except LinkedInError as e:
            print(f"FAILED ✘  {e}", file=sys.stderr)

    print("-" * 60)
    if args.dry_run:
        print(f"Dry run complete. {len(due)} post(s) would be published.")
    else:
        print(f"Done. {published}/{len(due)} published.")
        if published < len(due):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
