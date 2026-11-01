"""Writing stages: ideate -> research -> write -> factcheck -> (human approval) -> shots -> package."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import yaml

from . import prompts, scriptfmt
from .config import Config, Episode, PipelineError
from .llm import Claude


def _style_bible(cfg: Config) -> str:
    path = cfg.resolve(cfg.get("paths.style_bible", "../strategy/03-style-bible.md"))
    return path.read_text() if path.exists() else ""


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------- ideate
IDEA_SCHEMA = {
    "type": "object",
    "properties": {
        "ideas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "daily_life": {"type": "integer"},
                    "drama": {"type": "integer"},
                    "visual_numbers": {"type": "integer"},
                    "audience_fit": {"type": "integer"},
                    "fresh": {"type": "integer"},
                    "near_death": {"type": "string"},
                    "title": {"type": "string"},
                    "why": {"type": "string"},
                },
                "required": ["company", "daily_life", "drama", "visual_numbers", "audience_fit",
                             "fresh", "near_death", "title", "why"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["ideas"],
    "additionalProperties": False,
}


def ideate(cfg: Config, companies: list[str]) -> list[dict]:
    claude = Claude(cfg)
    notes = claude.ask(
        prompts.IDEATE,
        "Research these companies for a 20-minute origin documentary. For each: the strongest "
        "near-death moment (with a source), the everyday hook, scale numbers, and what already "
        "exists on YouTube (search for '<company> history' and 'entire history of <company>' "
        "videos and note their views and age).\n\n" + "\n".join(f"- {c}" for c in companies),
        effort=cfg.get("llm.effort_research", "high"),
        web=min(40, 4 * len(companies)),
    )
    scored = claude.ask(
        prompts.IDEATE,
        "Score each company from these research notes. Title: use 'The ENTIRE History of "
        "[Company] in [N] Minutes' unless another playbook framework clearly fits better.\n\n"
        + notes.text,
        effort=cfg.get("llm.effort_light", "medium"),
        schema=IDEA_SCHEMA,
    ).json()["ideas"]
    for idea in scored:
        idea["total"] = sum(idea[k] for k in ("daily_life", "drama", "visual_numbers", "audience_fit", "fresh"))
    scored.sort(key=lambda i: -i["total"])
    out = cfg.resolve(cfg.get("paths.ideas", "../content/ideas-scored.yaml"))
    existing = (yaml.safe_load(out.read_text()) or {}).get("ideas", []) if out.exists() else []
    keep = [i for i in existing if i["company"].lower() not in {s["company"].lower() for s in scored}]
    out.write_text(yaml.safe_dump({"scored_on": _today(), "ideas": scored + keep}, sort_keys=False, allow_unicode=True))
    return scored


# ---------------------------------------------------------------- research
def research(cfg: Config, ep: Episode, *, force: bool = False) -> str:
    path = ep.file("research.md")
    if path.exists() and not force:
        raise PipelineError(f"{path} exists. Use --force to redo the research.")
    claude = Claude(cfg)
    hint = ep.meta.get("near_death", "")
    answer = claude.ask(
        prompts.RESEARCH,
        f"Company: {ep.company}\nToday's date: {_today()}\n"
        + (f"Near-death moment we expect to build around (check it): {hint}\n" if hint else ""),
        effort=cfg.get("llm.effort_research", "high"),
        web=int(cfg.get("llm.max_web_searches", 25)),
    )
    ep.src.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Research brief — {ep.company}\n\n_Generated {_today()} by {answer.model}. "
                    "Check every claim before it reaches the script._\n\n" + answer.with_sources())
    return str(path)


# ---------------------------------------------------------------- write
def write(cfg: Config, ep: Episode, *, force: bool = False, next_episode: str = "") -> str:
    path = ep.file("script.md")
    if path.exists() and not force:
        raise PipelineError(f"{path} exists. Use --force to overwrite (your edits would be lost).")
    brief = ep.file("research.md")
    if not brief.exists():
        raise PipelineError(f"No research brief yet. Run: python -m yt research {ep.id}")
    example = cfg.resolve(cfg.get("paths.example_script", "../content/episodes/ep01-fedex/script.md"))
    parts = [
        f"<style_bible>\n{_style_bible(cfg)}\n</style_bible>",
        f"<research_brief>\n{brief.read_text()}\n</research_brief>",
    ]
    if example.exists() and example.resolve() != path.resolve():
        parts.append(f"<example_script note='format and tone reference only; do not reuse its facts'>\n"
                     f"{example.read_text()}\n</example_script>")
    parts.append(
        f"Write the script for episode '{ep.id}' about {ep.company}. Working title: {ep.title}.\n"
        f"Front-matter fields: episode: {ep.id}, company: {ep.company}, title: {ep.title}, "
        "status: draft — resolve every [VERIFY] tag before approval.\n"
        + (f"Next episode to tease at the very end: {next_episode}\n" if next_episode else "")
    )
    answer = Claude(cfg).ask(prompts.WRITE, "\n\n".join(parts), effort=cfg.get("llm.effort_write", "high"))
    text = answer.text.strip()
    text = re.sub(r"^```(?:markdown)?\n|\n```$", "", text)  # tolerate a fenced reply
    sections = scriptfmt.parse(text)  # raises on malformed markup
    path.write_text(text + "\n")
    _reset_approval(ep, "script")
    return _script_report(sections, text)


def _script_report(sections: list[scriptfmt.Section], text: str) -> str:
    total = sum(s.words for s in sections)
    lines = [f"{s.num}. {s.title}: {len(s.scenes)} scenes, {s.words} words" for s in sections]
    lines.append(f"Total: {total} words (~{total / 145:.1f} min at a calm 145 wpm)")
    lines.append(f"[VERIFY] tags to resolve: {len(scriptfmt.verify_tags(text))}")
    lines += [f"WARNING: {w}" for w in scriptfmt.lint(sections)]
    return "\n".join(lines)


def check(ep: Episode) -> str:
    path = ep.file("script.md")
    if not path.exists():
        raise PipelineError(f"No script at {path}")
    text = path.read_text()
    return _script_report(scriptfmt.parse(text), text)


# ---------------------------------------------------------------- factcheck
CLAIM_RE = re.compile(r"\d|\$|percent|million|billion|first|largest|only|never|said|told")


def claims(text: str) -> list[str]:
    """Sentences worth checking: anything with numbers/dates/superlatives/quotes, plus VERIFY notes."""
    out: list[str] = []
    for sc in scriptfmt.all_scenes(scriptfmt.parse(text)):
        sentences = re.split(r"(?<=[.!?])\s+", sc.narration)
        for s in sentences:
            if CLAIM_RE.search(s.lower()) or '"' in s:
                out.append(f"[{sc.id}] {s}")
        out += [f"[{sc.id}] (note) {v}" for v in sc.verify]
    return out


def factcheck(cfg: Config, ep: Episode) -> str:
    script = ep.file("script.md")
    if not script.exists():
        raise PipelineError(f"No script yet. Run: python -m yt write {ep.id}")
    items = claims(script.read_text())
    numbered = "\n".join(f"{i}. {c}" for i, c in enumerate(items, 1))
    brief = ep.file("research.md")
    context = f"<research_brief>\n{brief.read_text()}\n</research_brief>\n\n" if brief.exists() else ""
    answer = Claude(cfg).ask(
        prompts.FACTCHECK,
        f"{context}Company: {ep.company}. Today's date: {_today()}.\n\nClaims to check:\n{numbered}",
        effort=cfg.get("llm.effort_research", "high"),
        web=int(cfg.get("llm.max_web_searches_factcheck", 40)),
    )
    out = ep.file("factcheck.md")
    if out.exists():  # keep the previous check (and any notes you added to it)
        out.replace(ep.file("factcheck.previous.md"))
    out.write_text(f"<!-- script_digest: {_digest(script.read_text())} -->\n"
                   f"# Fact-check — {ep.id}\n\n_Generated {_today()} by {answer.model}. A human must "
                   "still apply the fixes and remove each [VERIFY] tag._\n\n" + answer.with_sources())
    return str(out)


def factcheck_is_current(ep: Episode) -> bool:
    """True if factcheck.md was made from the script exactly as it is now."""
    out, script = ep.file("factcheck.md"), ep.file("script.md")
    if not (out.exists() and script.exists()):
        return False
    first = out.read_text().split("\n", 1)[0]
    m = re.match(r"<!-- script_digest: (\w+) -->", first)
    return bool(m) and m.group(1) == _digest(script.read_text())


# ---------------------------------------------------------------- approvals
def _reset_approval(ep: Episode, gate: str) -> None:
    st = ep.state()
    if st.get("approvals", {}).get(gate, {}).get("approved"):
        st["approvals"][gate] = {"approved": False, "reset": f"script rewritten {_today()}"}
        ep.save_state(st)


def approve(cfg: Config, ep: Episode, gate: str, *, by: str, force: bool = False) -> str:
    if gate == "script":
        text = ep.file("script.md").read_text()
        open_tags = scriptfmt.verify_tags(text)
        if open_tags and not force:
            preview = "\n".join(f"  line {n}: {note}" for n, note in open_tags[:10])
            raise PipelineError(
                f"{len(open_tags)} [VERIFY] tag(s) still open. Double-source each fact, fix the wording, "
                f"then delete the tag.\n{preview}" + ("\n  ..." if len(open_tags) > 10 else "")
            )
        scriptfmt.parse(text)
        digest = _digest(text)
    elif gate == "final":
        build = ep.build()
        if not build.get("render", {}).get("final"):
            raise PipelineError(f"No full render yet. Run: python -m yt produce {ep.id}")
        if build["render"].get("dry_run"):
            raise PipelineError("The last render was a dry run (silent voice, placeholder art). Render for real first.")
        if build["render"].get("script_digest") != _digest(ep.file("script.md").read_text()):
            raise PipelineError("The script changed after the last render. Re-run produce first.")
        digest = build["render"]["script_digest"]
    else:
        raise PipelineError("Gate must be 'script' or 'final'.")
    st = ep.state()
    st.setdefault("approvals", {})[gate] = {
        "approved": True, "by": by, "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "script_digest": digest,
    }
    ep.save_state(st)
    return f"{ep.id}: '{gate}' approved by {by}."


def require_script_approval(ep: Episode, *, dry_run: bool) -> None:
    text = ep.file("script.md").read_text()
    gate = ep.state().get("approvals", {}).get("script", {})
    if gate.get("approved") and gate.get("script_digest") == _digest(text):
        return
    if dry_run:
        print("NOTE: script not approved — continuing because this is a dry run (animatic only, never publishable).")
        return
    reason = "changed since it was approved" if gate.get("approved") else "not approved yet"
    raise PipelineError(f"Script is {reason}. Resolve [VERIFY] tags, then: python -m yt approve {ep.id} script")


def _digest(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# ---------------------------------------------------------------- shots
SHOT_SCHEMA = {
    "type": "object",
    "properties": {
        "shots": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "prompt": {"type": "string"}},
                "required": ["id", "prompt"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["shots"],
    "additionalProperties": False,
}


def shots(cfg: Config, ep: Episode) -> list[dict]:
    """Split every scene into ~4-second shots and write an image prompt for each."""
    sections = scriptfmt.parse(ep.file("script.md").read_text())
    min_w, max_w = int(cfg.get("shots.min_words", 8)), int(cfg.get("shots.max_words", 18))
    plan: list[dict] = []
    for sc in scriptfmt.all_scenes(sections):
        for i, text in enumerate(scriptfmt.split_shots(sc.narration, min_w, max_w), 1):
            plan.append({
                "id": f"{sc.id}-{i:02d}", "scene": sc.id, "section": sc.section, "text": text,
                "words": len(text.split()), "vis": sc.vis,
                "label": sc.label if i == 1 else None, "meter": sc.meter,
                "prompt": sc.vis if i == 1 else f"{sc.vis} — a different angle or close-up detail",
            })

    result = None
    if cfg.llm_enabled:
        listing = "\n".join(
            f'{p["id"]} | scene cue: {p["vis"]} | narration: {p["text"]}' for p in plan
        )
        try:
            result = Claude(cfg).ask(
                prompts.SHOTS,
                f"Company: {ep.company}. Write one image prompt per shot id below.\n\n{listing}",
                effort=cfg.get("llm.effort_light", "medium"),
                schema=SHOT_SCHEMA,
            ).json()["shots"]
        except PipelineError as e:
            # Shot prompts improve variety but are not essential: fall back instead of stopping production.
            print(f"WARNING: Claude shot prompts failed ({e}). Using each scene's [VIS] cue instead.")
    if result is not None:
        by_id = {s["id"]: s["prompt"].strip() for s in result if s.get("prompt")}
        missing = [p["id"] for p in plan if p["id"] not in by_id]
        for p in plan:
            p["prompt"] = by_id.get(p["id"], p["prompt"])
        if missing:
            print(f"NOTE: {len(missing)} shot(s) kept the default prompt: {', '.join(missing[:8])}")
    elif not cfg.llm_enabled:
        print("NOTE: no Claude key (or dry run) — shots reuse each scene's [VIS] cue.")

    out = ep.dir(".") / "shots.json"
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False))
    return plan


# ---------------------------------------------------------------- packaging
PACKAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "titles": {"type": "array", "items": {"type": "string"}},
        "description": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "pinned_comment": {"type": "string"},
        "thumbnails": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "prompt": {"type": "string"}, "text": {"type": "string"}},
                "required": ["id", "prompt", "text"], "additionalProperties": False,
            },
        },
        "shorts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "title": {"type": "string"}, "hook_text": {"type": "string"},
                    "first_scene": {"type": "string"}, "last_scene": {"type": "string"},
                },
                "required": ["id", "title", "hook_text", "first_scene", "last_scene"], "additionalProperties": False,
            },
        },
    },
    "required": ["titles", "description", "tags", "pinned_comment", "thumbnails", "shorts"],
    "additionalProperties": False,
}


def package(cfg: Config, ep: Episode, *, force: bool = False) -> str:
    path = ep.file("packaging.yaml")
    if path.exists() and not force:
        raise PipelineError(f"{path} exists. Use --force to regenerate.")
    script = ep.file("script.md").read_text()
    scenes = "\n".join(f"{s.id}: {s.narration[:140]}" for s in scriptfmt.all_scenes(scriptfmt.parse(script)))
    data = Claude(cfg).ask(
        prompts.PACKAGE,
        f"<style_bible>\n{_style_bible(cfg)}\n</style_bible>\n<script>\n{script}\n</script>\n"
        f"<scene_ids>\n{scenes}\n</scene_ids>\nWorking title: {ep.title}",
        effort=cfg.get("llm.effort_light", "medium"),
        schema=PACKAGE_SCHEMA,
    ).json()
    data["shorts"] = [
        {"id": s["id"], "title": s["title"], "hook_text": s["hook_text"], "scenes": [s["first_scene"], s["last_scene"]]}
        for s in data["shorts"]
    ]
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100))
    return str(path)
