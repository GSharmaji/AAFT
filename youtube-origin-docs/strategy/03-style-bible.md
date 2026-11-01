# Style Bible — lock these once, reuse every episode

The playbook's rule: "lock ONE sketch style with your AI image tool, using the same style prompt every time, so the channel looks like a brand." This file is that lock. The pipeline reads the same values from `../pipeline/config.yaml`.

---

## 1. Visual style

**Style prompt (prepended to every image prompt — do not edit per episode):**

> Hand-drawn pencil and ink sketch illustration on warm off-white paper, loose confident linework, light watercolor wash in a muted earthy palette (warm browns, slate greys, sage greens, faded ochre), one small accent of brick red, simple round-headed cartoon people with dot eyes and no detailed faces, generous empty paper space, no text, no letters, no logos, no photorealism, 16:9 composition.

Rules:
- **People are round-headed figures.** No realistic faces of real founders. This keeps us clear of likeness problems and AI-disclosure questions.
- **No logos, no readable text in images.** Text comes from the pipeline's labels (crisp, never misspelled).
- **Brand colours are allowed** (FedEx purple/orange on a sketch plane) but not the logo itself.
- **Scale shots** every 2–3 minutes: tiny figure next to a huge object (warehouse, fleet, pile of packages).
- **Accent red** only for danger moments (near-death section, warnings).

How to lock it (week 0):
1. Generate 20 test images from the same 5 prompts with your image model (`python -m yt images ep01-fedex --only s1-01,s3-09,s4-06,s5-15,s6-07`).
2. Keep the best one as your **style reference**. If your image tool accepts reference images, use it every time.
3. Never change the style prompt after episode 1. If you must, change it between seasons, not mid-season.

## 2. On-screen labels

- Handwritten-style quote labels that pop in: `"Out For Delivery"`, `"$5,000 left"`, `"186 packages"`.
- Max **5 words**. Numbers beat words.
- One label per scene at most. Not every scene needs one — use them to stress the key points.
- Script tag: `[LABEL: "186 packages"]`.

## 3. The Near-Death Meter (our signature device)

- A hand-drawn gauge, top-right corner, with three zones: **SAFE** (sage green) → **SHAKY** (ochre) → **NEAR-DEATH** (brick red).
- Script tag: `[METER: safe]`, `[METER: shaky]`, `[METER: near-death]`, `[METER: off]`.
- It is a **mood gauge, never a number**. Don't say "a 3% chance of survival" unless a source says it.
- Pattern: SAFE in the hook → SHAKY during the first win → NEAR-DEATH at minute 8–12 → back to SAFE in the takeover → off for the ending (or SHAKY if a new threat is the open question).

## 4. Voice

- Calm, warm, mature documentary voice. Unhurried. ~140–150 words per minute.
- US English (audience decision in strategy §4).
- Test 5 voices on the same 60-second hook. Pick the one that sounds like it is telling a story, not reading a list.
- Same voice forever. Changing voice = changing brand.

## 5. Writing rules

Structure (playbook §7, ~20 min, ~3,000 words):

| Part | Time | Words | Job |
|---|---|---|---|
| 1. Hook | 0:00–1:00 | ~150 | Everyday moment → the hidden machine behind it → jaw-drop number |
| 2. The founder before the company | 1:00–4:00 | ~450 | Who they were, what problem they saw |
| 3. The first win | 4:00–8:00 | ~600 | The early idea that worked |
| 4. The near-death moment | 8:00–12:00 | ~600 | Crisis, scandal or bet-the-company decision. **Slow down here.** |
| 5. The takeover | 12:00–17:00 | ~750 | How it became unavoidable in daily life |
| 6. Where it's going | 17:00–20:00 | ~450 | Today's numbers + one open question for the comments |

Sentence rules:
- Short sentences. Spoken English. Read it out loud.
- **Every part ends on a cliffhanger line.** ("The idea worked. The maths didn't.")
- One "wait, what?" fact per minute.
- Numbers get a comparison the viewer can picture ("more packages than there are people in Netherlands").
- Myths are labelled as myths. "Legend says…", "As his early executive told it…". Never present a legend as fact.
- Every number and date carries a `[VERIFY: ...]` tag in the draft. The tag is removed only after 2 independent sources confirm it.

## 6. Script markup (what the pipeline reads)

```
## 3. Fourteen jets, 186 packages [4:00-8:00]
[METER: shaky]
[VIS: a small cargo jet on a dark runway, one tiny figure loading a box] [LABEL: "186 packages"]
Narration for this scene. Two to four sentences. The pipeline splits it into
shots of ~4 seconds each and writes a matching image for every shot.

[VIS: next scene's picture]
Next narration paragraph.
```

- `## N. Chapter title [start-end]` = a story part. The title is the YouTube chapter name viewers see, so make it intriguing ("$5,000 and a night in Las Vegas"), not a label ("Near-death moment").
- `[VIS: ...]` = the picture for this scene. Describe subject and composition only. The style prompt is added automatically.
- `[LABEL: "..."]` = optional on-screen label for the scene.
- `[METER: ...]` = Near-Death Meter state from this scene onwards.
- `[VERIFY: ...]` = a fact to double-source. Removed from narration automatically. Blocks approval while present.
- `<!-- ... -->` = notes to yourself. Ignored.

## 7. Thumbnails

- The company's world drawn in the same sketch style. **One strong focal image.** Tiny figure + huge object works best.
- Text: none, or max 3 words / 1 number (e.g. `$5,000`).
- Paper background, high contrast linework, one accent colour.
- Make 3 versions per video for YouTube Test & Compare: (A) scale shot, (B) the near-death object, (C) the founder figure in the key moment.

## 8. Titles

- Main formula (use for ~70% of uploads): **The ENTIRE History of [Company] in [N] Minutes** — N must match the real length.
- Alternates (test in episodes 5, 9, 10):
  - How [Company] Quietly Took Over Your [Kitchen / Phone / Street]
  - [Company] Was 1 Mistake Away From Dying
  - The Real Reason [Company] Beat [Rival]
