"""Thin Claude wrapper used by the writing stages (research, script, fact-check,
shot list, packaging, ideation).

- Streams every request (long outputs) and returns the final message.
- Opts into server-side refusal fallbacks (`fallbacks="default"`) by default;
  turn off with `llm.fallbacks: false` in config.yaml.
- Continues `pause_turn` responses from server-side web search.
- Collects web citations so research notes keep their sources.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .config import Config, PipelineError

WEB_SEARCH = "web_search_20260209"
WEB_FETCH = "web_fetch_20260209"
FALLBACK_BETA = "server-side-fallback-2026-07-01"


@dataclass
class Answer:
    text: str
    sources: list[tuple[str, str]] = field(default_factory=list)  # (title, url), de-duplicated, in order
    model: str = ""

    def json(self) -> Any:
        return json.loads(self.text)

    def with_sources(self) -> str:
        if not self.sources:
            return self.text
        lines = [self.text.rstrip(), "", "## Sources cited by the research run", ""]
        lines += [f"{i}. [{title or url}]({url})" for i, (title, url) in enumerate(self.sources, 1)]
        return "\n".join(lines) + "\n"


class Claude:
    def __init__(self, cfg: Config):
        if not cfg.llm_enabled:
            raise PipelineError(
                "This stage needs Claude. Set ANTHROPIC_API_KEY (see pipeline/.env.example). "
                "Note: --dry-run never calls Claude."
            )
        import anthropic  # imported lazily so offline stages don't need it

        self.anthropic = anthropic
        self.client = anthropic.Anthropic()
        self.model = cfg.get("llm.model", "claude-opus-5-5")
        self.fallbacks = bool(cfg.get("llm.fallbacks", True))

    def ask(
        self,
        system: str,
        prompt: str,
        *,
        effort: str = "high",
        web: int = 0,
        schema: dict | None = None,
        max_tokens: int = 64000,
    ) -> Answer:
        """One task, one answer. `web` = max web searches (0 = no web tools)."""
        output_config: dict[str, Any] = {"effort": effort}
        if schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": schema}
        tools: list[dict] = []
        if web:
            tools = [
                {"type": WEB_SEARCH, "name": "web_search", "max_uses": web},
                {"type": WEB_FETCH, "name": "web_fetch", "max_uses": max(5, web // 2)},
            ]

        messages: list[dict] = [{"role": "user", "content": prompt}]
        texts: list[str] = []
        sources: dict[str, str] = {}
        model = self.model
        for _ in range(8):  # pause_turn continuations
            kwargs: dict[str, Any] = dict(
                model=self.model, max_tokens=max_tokens, system=system,
                messages=messages, output_config=output_config,
            )
            if tools:
                kwargs["tools"] = tools
            try:
                if self.fallbacks:
                    stream = self.client.beta.messages.stream(betas=[FALLBACK_BETA], fallbacks="default", **kwargs)
                else:
                    stream = self.client.messages.stream(**kwargs)
                with stream as s:
                    msg = s.get_final_message()
            except self.anthropic.AuthenticationError as e:
                raise PipelineError("Anthropic API key rejected. Check ANTHROPIC_API_KEY.") from e
            except self.anthropic.BadRequestError as e:
                raise PipelineError(f"Claude rejected the request: {e.message}") from e
            except self.anthropic.RateLimitError as e:
                raise PipelineError("Rate limited by the Anthropic API. Wait a minute and re-run this stage.") from e
            except self.anthropic.APIConnectionError as e:
                raise PipelineError("Could not reach the Anthropic API (network).") from e

            model = getattr(msg, "model", model)
            if msg.stop_reason == "refusal":
                details = getattr(msg, "stop_details", None)
                raise PipelineError(f"Claude declined this request: {getattr(details, 'explanation', '') or 'no details'}")
            for block in msg.content:
                if getattr(block, "type", "") != "text":
                    continue
                texts.append(block.text)
                for c in getattr(block, "citations", None) or []:
                    url = getattr(c, "url", None)
                    if url and url not in sources:
                        sources[url] = getattr(c, "title", "") or ""
            if msg.stop_reason == "pause_turn":
                messages.append({"role": "assistant", "content": msg.content})
                continue
            if msg.stop_reason == "max_tokens":
                raise PipelineError("Output hit max_tokens. Raise llm.max_tokens or split the task.")
            break
        else:
            raise PipelineError("Web research did not finish after 8 continuations.")

        text = "".join(texts).strip()
        if schema is not None:
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                raise PipelineError(f"Claude returned invalid JSON: {e}") from e
        return Answer(text, [(t, u) for u, t in sources.items()], model)
