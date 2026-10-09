# Job-specific resume process

One master profile → one tailored resume per job description (JD).

> **This repo is public.** Personal data (contact details, employer numbers, tailored
> resumes, master profile) lives only in `resume/private/` (gitignored) and in the
> "Job Applications" folder in Google Drive. Only this method and the template are committed.

## Inputs
- **Master profile:** `resume/private/master-profile.md` (copy in Google Drive → "Job Applications").
  It's the only source of facts. A new session starts by pulling it from Drive.
- **JD:** pasted by the user.

## Steps

### 1. Break down the JD
- List the minimum qualifications (MQs), preferred qualifications (PQs), and responsibilities.
- Pull the 10–15 keywords the screener will look for (tools, skills, metrics, domain words).
- Note what the role is *really* about in one line (e.g. "B2B content team lead + subscriber growth").

### 2. MQ gate (do this before writing anything)
- Check every MQ against the master profile: **Met / Partly / Not met**, with the evidence.
- Years are counted from real dates. Don't count the MBA, and don't count overlapping roles twice.
- If any MQ is **Not met**, say so plainly and recommend skip or apply. Some employers cap
  applications (Google: 3 per 30 days), so a weak-fit application has a real cost.
- The user decides. Never stretch a fact to clear an MQ.

### 3. Map evidence to the JD
- For each MQ, PQ and key responsibility, pick the 1–2 strongest facts from the profile.
- Order roles and bullets by relevance to this JD, not by habit.
- Drop anything that doesn't support this JD.

### 4. Write
- **Bullets follow:** "Accomplished [X], measured by [Y], by doing [Z]". Numbers in every bullet where they exist.
- **Use the JD's own words** where they truthfully describe the work (e.g. "lead-generation funnels" over "lead gen").
- **Leadership:** state team size, functions, and scope (budget, markets, product lines).
- **Projects:** add a Projects or Education line only if it shows a skill the JD asks for that your jobs don't already prove.
- **Summary:** 2–3 lines, built from the JD's top 3 needs.
- **Length:** 1 page unless the JD is senior and the evidence earns page 2.
- **Format:** single column, no tables, icons, or images, so applicant tracking systems (ATS) can read it.

### 5. Check before sending
- Every number traces to the master profile. Titles and dates match the profile exactly.
- Each MQ is visibly covered in the first half of page 1.
- Keyword check: each top JD keyword appears at least once, naturally.
- Read it as a skeptical recruiter: what would make them reject it in 10 seconds?

### 6. Output
- File name: **`Garvit Sharma Resume [Company Name].pdf`** (e.g. `Garvit Sharma Resume Lyxel&Flamingo.pdf`).
- Working files: `resume/private/jobs/<company>-<role>/` (HTML source + PDF). The container is temporary,
  so the PDF is sent in chat and the user saves it to Drive → "Job Applications".
- Fit notes (MQ check, risks) go in the chat reply, not in the resume.
- Render: `NODE_PATH=/opt/node22/lib/node_modules node resume/render.js <path/to/resume.html>`

## Rules
- No invented facts, numbers, titles, or dates. If a fact is missing, ask for it.
- Every version must use the same titles and dates. Background checks compare them.
- Flag fit problems honestly, even if the user wants to apply anyway.
