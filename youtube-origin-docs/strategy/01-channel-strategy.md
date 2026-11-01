# Channel Strategy — Company Origin Documentaries (Playbook 1)

Working channel name: **Almost Didn't Exist** (check the handle is free before you commit — I could not check it).
Model channel from the playbook: Built On You (@BuiltonYou).

Confidence tags used below:
- **[Certain]** = hard evidence (official docs, filings, the playbook itself)
- **[Likely]** = strong inference from several sources
- **[Guessing]** = my judgment to fill a gap. Treat as a starting assumption to test.

---

## 0. Bottom line (read this first)

- **The demand is proven. The format is not.** [Likely] Four big channels already live off company stories (table in §3). That proves people watch this. It does **not** prove that a new AI-sketch channel can win. The model channel has only 5 videos and 1 flop. The playbook itself says that is too early to judge.
- **Copying Built On You 1:1 is the weak move.** [Likely] Everyone who bought this playbook got the same model channel, the same title formula and the same examples (IKEA, Samsung, Visa, McDonald's). Those topics will be crowded within weeks. So we keep the proven parts (title formula, sketch style, 6-part story) and add one owned asset: the **Near-Death Meter** (see §2).
- **Automation cuts production time, not research time.** [Certain] The playbook says the niche is 70% research and story. The pipeline in `../pipeline` removes the editing grind. It does not remove the human fact-check. If you skip that gate, one wrong number in the comments will cost you more than a week of saved time.
- **Expect $0 for the first ~3 months.** [Guessing] This is a 6–12 month bet. Plan time and money for that.

---

## 1. What we are building

- **One giant company per video, told as a survival story.** Founder → first win → the moment it almost died → how it took over your daily life → where it is going.
- **Promise to the viewer:** "Every giant you use today almost didn't exist. Here's the night it nearly ended."
- **Length:** 18–22 minutes, ~3,000 words. Same as the model channel.
- **Cadence:** 1 long video per week + 3 Shorts cut from it. The playbook says 1/week is realistic; research is the bottleneck. [Certain — playbook §8]

## 2. How we are different from the model channel

| What | Built On You (model) | Us |
|---|---|---|
| Title formula | "The ENTIRE History of X in N Minutes" | Same for ~70% of uploads. Test 3 other playbook frameworks in the first 10. |
| Visual style | Hand-drawn sketch, muted earthy palette | Same family. One locked style prompt (see `03-style-bible.md`). |
| Story spine | Founder → takeover | Same 6 parts, but the **near-death moment is the brand**. |
| Signature device | None | **Near-Death Meter**: a hand-drawn gauge in the corner (SAFE → SHAKY → NEAR-DEATH). It climbs as the story builds and peaks at minute 8–12. |
| Topic choice | Mixed, includes a fandom brand (Nintendo flopped) | Business-curious adults only. Avoid the playbook's own examples in the first 10. |

Why the meter:
- It makes the retention peak (minute 8–12) **visible and anticipated**. Viewers see the needle moving and stay to see it hit red.
- It is cheap. The pipeline draws it automatically from one tag in the script (`[METER: shaky]`).
- It never shows a fake number. It is a mood gauge, not a "survival odds %" claim. That protects us on accuracy.

---

## 3. Step 4 — "Prove it's consistent" (the step most people skip)

What the playbook asks: find 3–5 other channels in this format, list their top 5 videos and 10 steady videos, and check that most videos get solid views.

### 3a. What I could verify (channel level)

| Channel | Subscribers (2026) | Format | Source quality |
|---|---|---|---|
| MagnatesMedia | ~1.86M (Aug 2026) | Business/founder documentaries | [Likely] third-party tracker |
| Company Man | ~1.8M (Aug 2026), 486 uploads | One company, one problem per video | [Likely] trackers agree on subs; **average views disagree: ~115K vs ~653K** |
| Business Casual | ~1.15M (Oct 2026), only 91 videos | Animated, narrated business history | [Likely] |
| Modern MBA | ~800K (Jul 2026) | Company deep-dives | [Likely] |
| Built On You (model) | 4.64K, 5 videos, avg ~53K views | AI sketch animation | [Certain] — from the playbook |

What this proves:
- [Likely] Company stories support several million-subscriber channels. Demand is real and lasting, not a fad.
- [Likely] Business Casual reached ~1.15M subs with only 91 videos. That means each video carries a lot of weight, which matches a slow, research-heavy, 1-per-week model.

What it does **not** prove:
- Whether an AI-voice + AI-sketch channel keeps viewers as well as these hand-made channels. Only Built On You tests that, and 5 videos is too few. [Certain]

### 3b. What you still need to do (20 minutes, from your own browser)

My environment could not open YouTube directly, so I could not list each channel's top videos. Do this before you publish episode 2:

1. Open each channel above → Videos → sort by **Popular**. Write down the top 5.
2. Sort by **Latest**. Skip the last 2 weeks. Write down the next 10 and their views.
3. Fill this table. If 7+ of the 10 "steady" videos on 3+ channels clear 50K views, the niche is consistent. If most are under 10K and a few hits carry the channel, be careful.

| Channel | Top 5 (title — views) | 10 steady videos: how many > 50K? | Topics that flopped |
|---|---|---|---|
| Company Man | | /10 | |
| MagnatesMedia | | /10 | |
| Business Casual | | /10 | |
| Modern MBA | | /10 | |
| Built On You | | /5 | Nintendo (3.8K) |

Also check: did any of them already do a strong 20-minute version of our first 3 topics (FedEx, 7-Eleven, Heinz)? If yes, change the angle or swap the topic. That is the "Fresh" score.

---

## 4. Audience and geography — a decision you need to make now

- [Certain — playbook §9] Built On You's top audience country is India. RPM is much lower for Indian views than US/UK views.
- [Guessing] If you are based in India and share early videos with your own network, you will teach the algorithm that your audience is Indian. That pulls RPM down for the life of the channel.

Decision for the first 20 videos:
- Pick companies a US/UK adult uses daily (logistics, food, retail, tech). No India-only companies until the channel has a stable audience.
- US-English documentary voice.
- Publish **Thursday 15:00 UTC** (10:00 New York, 15:00 London, 20:30 India).
- Do **not** post links in Indian WhatsApp groups for the first 10 videos. Seed in Reddit threads and communities where the topic is discussed (r/business, r/logistics for FedEx, etc.) and only where self-promotion is allowed.
- Later option: an Indian-giants series (Tata, Reliance, Amul) could be a second lane or a Hindi channel (see Playbook 3). Do it on purpose, not by accident.

---

## 5. Choosing topics (our version of "Pick your lane")

A company must score **18+ out of 25** on the playbook's 5 tests. Full scored list in `02-idea-bank.md`.

| Test | Question |
|---|---|
| Daily-life hook | Did the viewer touch this company today? |
| Drama | Is there a near-collapse or a crazy gamble? |
| Visual numbers | Can we show scale on screen? |
| Audience fit | Business-curious adults, not one fandom? |
| Fresh | No great 20-minute version already crushing it? |

Extra rules from the model channel's data:
- No fandom brands (gaming, anime, sports teams). Nintendo got 3.8K vs Amazon 141K. [Certain — playbook]
- Avoid the playbook's examples (IKEA, Samsung, Visa, McDonald's) in the first 10. [Guessing — classmates will flood them]
- Avoid companies in an active legal fight or safety story (e.g. Boeing right now). The facts change weekly and errors are costly.

---

## 6. Growth system

**Per long video (weekly):**
- 1 title chosen from 3 drafts. Upload with thumbnail A, run YouTube **Test & Compare** with thumbnails B and C. [Certain that thumbnail testing exists; title testing — Likely, check your Studio]
- Chapters from the 6 story parts (the pipeline writes them from real timings).
- Sources listed in the description. This builds trust and heads off "wrong date" comments.
- Pinned comment = the open question from the last section of the script.
- End screen → next video in the series + subscribe.

**Shorts (3 per long video):**
- Cut from the same assets: the near-death moment, the jaw-drop number, the founder twist.
- Each Short links to the full video using the "related video" option.
- [Likely] Shorts pay very little. Their job is discovery and subscribers, not money.

**Series and playlists:**
- "Almost Didn't Exist" (all episodes), "Logistics Giants", "Food Empires". Playlists keep binge sessions going.
- Rival pairs drive the second video: FedEx → "The Real Reason UPS Beat FedEx at Ground" (episode 9).

**Community:**
- Read every comment on the first 10 videos. Fix real errors with a pinned correction. Accuracy is our moat.
- Ask in the pinned comment which company to cover next. Use the replies to fill the idea bank.

---

## 7. Money — honest numbers

**Cost per video (with the pipeline):**

| Item | Cost | Confidence |
|---|---|---|
| Claude (research, script, fact-check, shot list, packaging) | ~$3–8 | [Guessing] — depends on how many web searches |
| AI voice (ElevenLabs, ~18,000 characters) | ~$5 (Creator plan covers ~5 videos/month) | [Likely] |
| Images (~200–250 shots) | ~$5–20 | [Likely] — depends on image model and quality |
| Music | $0 (YouTube Audio Library) to ~$15/month | [Likely] |
| **Total cash** | **~$15–45 per video** | |
| **Your time** | **~8–10 hours per video** (research check 3–4h, script edit 2–3h, review 1h, packaging 1h) | [Guessing] |

**Getting paid (YouTube Partner Program):** 1,000 subscribers + 4,000 public watch hours in 12 months. [Certain]
- A 20-minute video with ~7 minutes average watch time needs ~34,000 views to reach 4,000 hours. [Certain — maths]

**Scenarios for the first 90 days:** [Guessing — use these to set expectations, not as promises]

| Scenario | Median views per video | Monetized by day 90? | Monthly revenue after monetized |
|---|---|---|---|
| Weak | ~1,500 | No | — |
| Base | ~5,000 | Maybe (subs are the bottleneck) | ~$150–300 at $3–6 RPM |
| Strong (one breakout like Amazon's 141K) | ~15,000 + one hit | Yes | ~$1,000–2,000 |

- The $6.5 RPM in the playbook is a third-party estimate for a channel that is **not monetized yet**. With an India-heavy audience, $2–4 is more realistic. [Likely]

---

## 8. What to measure and when to change course

Check in YouTube Studio 48 hours and 7 days after each upload.

| Metric | Target | If below target |
|---|---|---|
| Impressions click-through rate (CTR) | 5%+ | Change the thumbnail first, then the title. |
| Average view duration | 7+ min (35% of 20 min) | Watch the retention graph. Fix the section where it drops. Usually the founder part is too slow. |
| Retention at 1:00 | 65%+ | The hook failed. Rewrite hooks harder: everyday moment → hidden machine → number. |
| Views vs channel median | Track only | Topic signal. Make more of what beats the median. |
| Subscribers per 1,000 views | 5+ | Strengthen the end-of-video promise of the next story. |

All targets are [Guessing] starting points for this niche. Replace them with your own medians after 10 videos.

**Decision rules:**
- After **10 videos**: if the median is under 2,000 views **and** average view duration is under 5 minutes, the problem is the format, not the topic. Change packaging style or voice before making video 11.
- After **20 videos**: if you are not on track for monetization within 6 months, stop or switch to a better-fit playbook. Don't drift for a year.

---

## 9. Risks and how we handle them

| Risk | Why it matters | What we do |
|---|---|---|
| Wrong facts | Fans of companies notice wrong dates and numbers. [Certain — playbook §9] | Every number needs 2 sources. The script carries `[VERIFY]` tags. The pipeline **refuses to approve a script that still has `[VERIFY]` tags**. |
| "Inauthentic content" demonetization | Since 15 July 2025, YouTube's Partner Program targets mass-produced, repetitive content — AI voice over slideshow visuals is the example people quote. [Likely — press coverage of YouTube's update] | 1 video a week, not 1 a day. Original research and script. Human fact-check and human final review. Story structure varies per company. Never batch-publish near-identical videos. |
| YouTube API upload lock | Videos uploaded through an **unverified** API project (created after 28 July 2020) are locked to private and cannot be made public. [Certain — Google's API docs] | The pipeline defaults to **manual mode**: it builds an upload kit (video, thumbnail, captions, copy-paste metadata) and you upload in YouTube Studio. Apply for the API audit in parallel; switch to API mode only after it passes. |
| AI content disclosure | Realistic AI content that could be mistaken for real people or events must be disclosed. [Certain] Hand-drawn sketch style is clearly not real, so it is likely exempt. [Likely] | Keep visuals clearly drawn, never photoreal. No realistic AI faces of real founders. Use simple round-headed figures. |
| Logos and footage | Ripping company ads or news footage gets claims. [Certain — playbook §9] | We draw everything. Brand colours, not logos, in thumbnails. No company ad clips. |
| Classmates flood the same topics | Same playbook, same examples. [Guessing] | First 10 topics avoid the playbook examples. |
| Burnout | 8–10 hours a week on top of your job. | Batch: research 2 episodes ahead. Keep a 2-video buffer before launch. |

---

## 10. 90-day plan

| Week | Do this |
|---|---|
| 0 (now) | Finish Step 4 table (§3b). Lock the style (generate 20 test images, pick one). Pick the voice. Claim the handle. Set up Google Cloud project and apply for the YouTube API audit. |
| 1 | Episode 1 (FedEx): resolve all `[VERIFY]` tags, approve, produce, review. Episode 2 research. |
| 2 | Episode 2 (7-Eleven) script + fact-check. Build a 2-video buffer. **Publish episode 1** on Thursday. |
| 3–4 | Publish weekly. 3 Shorts per video. Read every comment. |
| 5 | First review: CTR, AVD, retention at 1:00 across 3 videos. Change one variable only. |
| 6–9 | Episodes 5–8. Test the 3 alternate title frameworks (episodes 5, 9, 10). |
| 10 | 10-video decision (§8). Update `02-idea-bank.md` with real data: which topics and titles beat the median. |
| 11–13 | Double down on the winning topic type. Plan episodes 11–20. |

---

## Sources

- Playbook: *VIP AI YouTube Accelerator: The Niche Playbooks*, Playbook 1 (data pulled 19 Oct 2026).
- Channel numbers: [creatordb — Modern MBA](https://creatordb.app/creatorstats/modernmba/), [creatordb — MagnatesMedia](https://creatordb.app/creatorstats/magnatesmedia/), [Qoruz — Company Man](https://qoruz.com/Company_Man/youtube), [OutlierKit — Company Man](https://outlierkit.com/channel/companyman114), [SpeakRJ — Business Casual](https://www.speakrj.com/audit/report/UC_E4px0RST-qFwXLJWBav8Q/youtube).
- YouTube "inauthentic content" update: [Plagiarism Today](https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/), [Windows Central](https://www.windowscentral.com/software-apps/youtube-ramps-up-campaign-against-ai-slop-with-stricter-monetization-caveats-on-inauthentic-and-repetitive-videos).
- API upload lock: [YouTube Data API — Videos](https://developers.google.com/youtube/v3/docs/videos), [videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert).
- AI disclosure: [YouTube blog — disclosing altered or synthetic content](https://blog.youtube/news-and-events/disclosing-ai-generated-content).
- RPM ranges (vendor blogs, low quality): [bytecap](https://www.bytecap.io/blog/faceless-youtube-channel-that-makes-money-2026), [easyviral](https://easyviral.ai/blog/how-much-do-faceless-youtube-channels-make-2026).
