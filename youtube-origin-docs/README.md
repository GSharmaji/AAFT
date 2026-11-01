# Almost Didn't Exist — Company Origin Documentaries

A faceless YouTube channel built on **Playbook 1 (Company Origin Documentaries)** from the
*VIP AI YouTube Accelerator* pack: one giant company per video, ~20 minutes, hand-drawn sketch
style, calm documentary voice, one video a week.

This folder has everything from ideation to posting:

| Part | Where | What it is |
|---|---|---|
| Strategy | [`strategy/01-channel-strategy.md`](strategy/01-channel-strategy.md) | Positioning, Step 4 proof, audience decision, money, KPIs, risks, 90-day plan |
| Idea bank | [`strategy/02-idea-bank.md`](strategy/02-idea-bank.md) | 24 companies scored 0–25; the first 10 episodes |
| Style bible | [`strategy/03-style-bible.md`](strategy/03-style-bible.md) | Locked visual prompt, voice, Near-Death Meter, writing rules, script markup |
| Calendar | [`content/calendar.yaml`](content/calendar.yaml) | Episodes 1–10 with publish slots |
| Episode 1 | [`content/episodes/ep01-fedex/`](content/episodes/ep01-fedex/) | Full script (2,806 words, ~19.8 min), research brief, packaging, 3 Shorts |
| Pipeline | [`pipeline/`](pipeline/) | Python + ffmpeg automation, ideation → upload |

**Episode 1 is not ready to publish yet.** The script has 65 `[VERIFY]` tags. The pipeline will
not approve it until each fact is double-sourced and the tag is deleted. That is on purpose.

---

## How a week works

```
Mon   python -m yt draft ep02-7-eleven          # Claude: web research -> script -> fact-check
Mon–Tue  YOU: fix facts using factcheck.md, edit the story, delete each [VERIFY] tag
Tue   python -m yt approve ep02-7-eleven script # gate 1 — refuses while any [VERIFY] is open
Tue   python -m yt package ep02-7-eleven        # titles, description, tags, thumbnails, Shorts picks
Tue   python -m yt produce ep02-7-eleven        # shots, voice, images, video, thumbnails, Shorts
Wed   YOU: watch the whole video once, with sound
Wed   python -m yt approve ep02-7-eleven final  # gate 2 — refuses a dry run or a stale render
Wed   python -m yt publish ep02-7-eleven        # upload kit (or scheduled API upload)
Thu   15:00 UTC goes live. Shorts on Mon / Wed / Sat.
```

Human time: ~8–10 hours a week, mostly fact-checking and story editing. The pipeline removes
the editing grind, not the research. See strategy §7.

## What the pipeline does

```
calendar.yaml ─► research.md ─► script.md ─► factcheck.md ─► [GATE 1: you] ─► shots.json
   (ideate)     (Claude + web)   (Claude)    (Claude + web)                    (Claude: image prompts)
                                                                                      │
   upload kit / YouTube ◄─ [GATE 2: you] ◄─ final.mp4 + Shorts + thumbnails ◄─ voice + images
       (publish)                               (ffmpeg render)                (ElevenLabs, image API)
```

- **Visual sync.** Each scene's narration length is split across its shots by word count, so a
  new picture appears every ~3–7 seconds, in step with what is being said (playbook §8).
- **Camera moves.** Each still gets a slow zoom or pan, rotating through four moves.
- **Labels.** `[LABEL: "186 packages"]` pops a crisp quote label onto the screen (never AI-misspelled).
- **Near-Death Meter.** `[METER: near-death]` draws the signature gauge in the corner.
- **Chapters and captions.** Built from real timings — chapters go into the description, captions
  into an `.srt` file.
- **Caching.** Change one sentence and re-run: only that scene's voice and shots are rebuilt.
- **Dry run.** `--dry-run` uses silent narration and storyboard cards, so you can check pacing and
  structure for free. A dry-run render can never be approved or published.

## Setup

```bash
cd youtube-origin-docs/pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # plus ffmpeg on your PATH
cp .env.example .env                     # add your keys
```

```bash
python -m yt status ep01-fedex
```

```bash
python -m yt --dry-run produce ep01-fedex --preview
```

That last command makes a free 480p animatic of episode 1 in about a minute
(`pipeline/work/ep01-fedex/render/preview.mp4`).

Keys you need:

| Key | For | Cost |
|---|---|---|
| `YT_ANTHROPIC_API_KEY` (or `ANTHROPIC_API_KEY` outside Claude Code) | research, script, fact-check, shot prompts, packaging, ideation. A key from console.anthropic.com → API Keys; API usage is billed separately from a Claude plan | ~$3–8 per episode |
| `ELEVENLABS_API_KEY` + voice id | narration | ~$5 per episode |
| `OPENAI_API_KEY` | images (`images.provider: openai`) — or use `manual` and drop in your own PNGs | ~$5–20 per episode |
| `YT_CLIENT_ID/SECRET/REFRESH_TOKEN` | API upload only — after your Google project passes YouTube's audit | free |

## Posting: why manual mode is the default

YouTube locks videos uploaded through an **unverified** API project (created after 28 July 2020)
to private, and they cannot be made public later. So `publish` builds an **upload kit** —
video, thumbnails, captions, Shorts and an `UPLOAD.md` sheet with the title, description
(with chapters), tags, schedule and a pre-flight checklist. Uploading it in YouTube Studio takes
about 5 minutes.

Apply for the YouTube API audit in week 0. When it passes, set `upload.mode: api` in
`pipeline/config.yaml`: the pipeline then uploads as private with a scheduled publish time,
sets the thumbnail and uploads captions.

## GitHub Actions

`.github/workflows/yt-origin-docs.yml` (repo root) runs two stages on demand from the Actions tab:
- **draft** → research + script + fact-check, then opens a pull request with the draft for your review.
- **produce** → renders the video, Shorts and thumbnails and attaches them to the run as a download
  (needs the script approval committed in `state.yaml`).

Final approval and publishing stay on your machine, after you have watched the cut. The workflow
never runs on a schedule. Run the first 3 episodes by hand before automating anything.
Repository secrets it reads: `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`, `OPENAI_API_KEY`.
