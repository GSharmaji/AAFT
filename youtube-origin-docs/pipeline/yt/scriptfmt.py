"""Parse the script markup described in strategy/03-style-bible.md §6.

    ## 3. Chapter title [4:00-8:00]
    [METER: shaky]
    [VIS: picture for this scene] [LABEL: "186 packages"]
    Narration... [VERIFY: note]

A *section* is one story part (and one YouTube chapter). A *scene* starts at
every [VIS: ...] tag and owns the narration that follows it, up to the next
[VIS: ...] or section heading.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

METER_STATES = ("safe", "shaky", "near-death", "off")
TAG_RE = re.compile(r"\[(VIS|LABEL|METER|VERIFY):\s*(.*?)\]", re.S)
HEADING_RE = re.compile(r"^##\s*(\d+)\.\s*(.+?)\s*(?:\[([^\]]*)\])?\s*$")
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.S)

# Target story shape from playbook §7 (words at ~150 wpm).
TARGET_WORDS = {1: 150, 2: 450, 3: 600, 4: 600, 5: 750, 6: 450}


@dataclass
class Scene:
    id: str
    section: int
    vis: str
    label: str | None
    meter: str
    narration: str
    verify: list[str] = field(default_factory=list)

    @property
    def words(self) -> int:
        return len(self.narration.split())


@dataclass
class Section:
    num: int
    title: str
    planned: str
    scenes: list[Scene] = field(default_factory=list)

    @property
    def words(self) -> int:
        return sum(s.words for s in self.scenes)


def _clean_label(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value.strip()


def parse(text: str) -> list[Section]:
    text = FRONTMATTER_RE.sub("", text)
    text = COMMENT_RE.sub("", text)
    sections: list[Section] = []
    meter = "off"
    scene: Scene | None = None
    pending_label: str | None = None

    def close_scene() -> None:
        nonlocal scene
        if scene is not None:
            scene.narration = " ".join(scene.narration.split())
            sections[-1].scenes.append(scene)
        scene = None

    for line in text.splitlines():
        heading = HEADING_RE.match(line.strip())
        if heading:
            close_scene()
            sections.append(Section(int(heading.group(1)), heading.group(2).strip(), (heading.group(3) or "").strip()))
            continue
        if not sections or not line.strip():
            continue

        vis = label = None
        verify: list[str] = []
        for tag, value in TAG_RE.findall(line):
            value = " ".join(value.split())
            if tag == "VIS":
                vis = value
            elif tag == "LABEL":
                label = _clean_label(value)
            elif tag == "METER":
                state = value.lower()
                if state not in METER_STATES:
                    raise ValueError(f"Unknown meter state {value!r} (use one of {METER_STATES})")
                meter = state
                if scene is not None and vis is None:
                    # A meter change inside narration applies from the next scene.
                    pass
            elif tag == "VERIFY":
                verify.append(value)
        prose = " ".join(TAG_RE.sub(" ", line).split())

        if vis is not None:
            close_scene()
            sec = sections[-1]
            scene = Scene(
                id=f"s{sec.num}-{len(sec.scenes) + 1:02d}",
                section=sec.num,
                vis=vis,
                label=label or pending_label,
                meter=meter,
                narration="",
            )
            pending_label = None
        elif label is not None:
            if scene is None:
                pending_label = label
            elif scene.label is None:
                scene.label = label

        if scene is None:
            if prose:
                raise ValueError(f"Narration before any [VIS: ...] in section {sections[-1].num}: {prose[:60]!r}")
            continue
        scene.verify.extend(verify)
        if prose:
            scene.narration += " " + prose
    close_scene()
    return sections


def all_scenes(sections: list[Section]) -> list[Scene]:
    return [s for sec in sections for s in sec.scenes]


def verify_tags(text: str) -> list[tuple[int, str]]:
    """Every [VERIFY: ...] left in the script, with its line number."""
    text = COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for tag, value in TAG_RE.findall(line):
            if tag == "VERIFY":
                out.append((i, " ".join(value.split())))
    return out


def lint(sections: list[Section]) -> list[str]:
    """Warnings about the script's shape. Not fatal — a human decides."""
    warnings: list[str] = []
    total = sum(s.words for s in sections)
    if len(sections) != 6:
        warnings.append(f"Expected 6 story parts (playbook §7), found {len(sections)}.")
    if not 2600 <= total <= 3400:
        warnings.append(f"Script is {total} words; target is ~3,000 (2,600–3,400) for ~20 minutes.")
    for sec in sections:
        target = TARGET_WORDS.get(sec.num)
        if target and not 0.6 * target <= sec.words <= 1.5 * target:
            warnings.append(f"Part {sec.num} '{sec.title}' is {sec.words} words; target ~{target}.")
        for sc in sec.scenes:
            if not sc.narration:
                warnings.append(f"{sc.id}: scene has a picture but no narration.")
            if sc.label and len(sc.label.split()) > 5:
                warnings.append(f"{sc.id}: label '{sc.label}' is over 5 words.")
            if sc.words > 90:
                warnings.append(f"{sc.id}: {sc.words} words under one picture cue — split it so visuals keep up.")
    meters = [sc.meter for sc in all_scenes(sections)]
    if "near-death" not in meters:
        warnings.append("The Near-Death Meter never reaches 'near-death'. Every episode needs its peak.")
    return warnings


def split_shots(narration: str, min_words: int = 8, max_words: int = 18) -> list[str]:
    """Split a scene's narration into shot-sized chunks (~3-7 seconds each).

    The playbook asks for a new visual every 3-5 seconds; at ~150 wpm that is
    roughly 8-13 words. Sentences are kept whole where possible.
    """
    sentences = [s for s in re.split(r"(?<=[.!?])\s+(?=[\"'A-Z0-9])", narration.strip()) if s]
    pieces: list[str] = []
    for sent in sentences:
        words = sent.split()
        if len(words) <= max_words + 4:
            pieces.append(sent)
            continue
        # Long sentence: break at commas / semicolons / dashes into ~max_words chunks.
        parts = re.split(r"(?<=[,;:])\s+|\s+(?=—)", sent)
        buf: list[str] = []
        for part in parts:
            if buf and len(" ".join(buf + [part]).split()) > max_words:
                pieces.append(" ".join(buf))
                buf = []
            buf.append(part)
        if buf:
            pieces.append(" ".join(buf))

    shots: list[str] = []
    buf = ""
    for piece in pieces:
        candidate = f"{buf} {piece}".strip()
        if buf and len(candidate.split()) > max_words:
            shots.append(buf)
            buf = piece
        else:
            buf = candidate
        if len(buf.split()) >= min_words:
            shots.append(buf)
            buf = ""
    if buf:
        if shots and len(buf.split()) < min_words // 2 + 1:
            shots[-1] = f"{shots[-1]} {buf}"
        else:
            shots.append(buf)
    return shots
