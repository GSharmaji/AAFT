"""Config + episode paths. Everything is resolved relative to config.yaml."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PIPELINE_DIR = Path(__file__).resolve().parent.parent


class PipelineError(RuntimeError):
    """A clear, user-facing error (bad input, missing approval, missing key)."""


class Config:
    def __init__(self, path: Path | None = None, *, dry_run: bool = False):
        self.path = Path(path or os.environ.get("YT_CONFIG") or PIPELINE_DIR / "config.yaml").resolve()
        if not self.path.exists():
            raise PipelineError(f"Config not found: {self.path}")
        self.data: dict[str, Any] = yaml.safe_load(self.path.read_text()) or {}
        self.base = self.path.parent
        self.dry_run = dry_run

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self.data
        for key in dotted.split("."):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def resolve(self, value: str | Path) -> Path:
        p = Path(value).expanduser()
        return p if p.is_absolute() else (self.base / p).resolve()

    # Providers: dry-run forces the free/offline ones so you can test the whole
    # chain (an "animatic") without any API keys or cost.
    @property
    def voice_provider(self) -> str:
        return "silent" if self.dry_run else os.environ.get("YT_VOICE_PROVIDER") or self.get("voice.provider", "silent")

    @property
    def image_provider(self) -> str:
        return "placeholder" if self.dry_run else os.environ.get("YT_IMAGE_PROVIDER") or self.get("images.provider", "placeholder")

    @property
    def llm_enabled(self) -> bool:
        return not self.dry_run and bool(
            os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_PROFILE")
        )

    @property
    def episodes_dir(self) -> Path:
        return self.resolve(self.get("paths.episodes", "../content/episodes"))

    @property
    def work_dir(self) -> Path:
        return self.resolve(self.get("paths.work", "./work"))

    def calendar(self) -> list[dict]:
        path = self.resolve(self.get("paths.calendar", "../content/calendar.yaml"))
        return (yaml.safe_load(path.read_text()) or {}).get("episodes", []) if path.exists() else []

    def episode(self, ep_id: str) -> "Episode":
        meta = next((e for e in self.calendar() if e.get("id") == ep_id), None)
        src = self.episodes_dir / ep_id
        if meta is None and not src.exists():
            known = ", ".join(e["id"] for e in self.calendar())
            raise PipelineError(f"Unknown episode '{ep_id}'. Add it to calendar.yaml. Known: {known}")
        return Episode(ep_id, src, self.work_dir / ep_id, meta or {"id": ep_id})


@dataclass
class Episode:
    id: str
    src: Path   # committed: script, research, fact-check, packaging, approvals
    work: Path  # generated media (git-ignored)
    meta: dict

    @property
    def company(self) -> str:
        return self.meta.get("company") or self.id

    @property
    def title(self) -> str:
        return self.meta.get("title") or f"The ENTIRE History of {self.company}"

    def file(self, name: str) -> Path:
        return self.src / name

    def dir(self, name: str) -> Path:
        d = self.work / name
        d.mkdir(parents=True, exist_ok=True)
        return d

    # --- approvals (committed, human-controlled) ---
    @property
    def state_path(self) -> Path:
        return self.src / "state.yaml"

    def state(self) -> dict:
        return (yaml.safe_load(self.state_path.read_text()) or {}) if self.state_path.exists() else {}

    def save_state(self, state: dict) -> None:
        self.src.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(yaml.safe_dump(state, sort_keys=False, allow_unicode=True))

    # --- build info (generated) ---
    def build(self) -> dict:
        p = self.work / "build.json"
        return json.loads(p.read_text()) if p.exists() else {}

    def save_build(self, **updates: Any) -> None:
        self.work.mkdir(parents=True, exist_ok=True)
        data = self.build()
        data.update(updates)
        (self.work / "build.json").write_text(json.dumps(data, indent=2))
