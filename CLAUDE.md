# Writing rules for this repo (always apply)

These apply to everything written for the owner: resumes, LinkedIn text, emails, posts, captions, and chat replies.

- Never use the em dash character (U+2014). Use a comma, a full stop, a colon, "and", or a plain hyphen with spaces ( - ) instead.
- Never use the en dash (U+2013) either. Write ranges with a plain hyphen: "Jan 2025 - Present", "8-12".
- Never use arrow characters (U+2192) in text. Write "to" ("Rs 26,000 to Rs 19,000") or use a plain "-" bullet.
- Avoid phrases that read as AI-written: "not X, but Y" slogans, "What I'm known for", "X over Y" taglines, "say hi", "game-changer", "leverage", "seamless", "delve".
- Write in simple, plain English. Short sentences.

# Resume work

- Follow `resume/PROCESS.md`. Facts come only from the master profile (`resume/private/master-profile.md`, also in the owner's Google Drive "Job Applications" folder).
- Before sending any resume, run `python3 resume/audit.py resume/private/master-profile.md "resume/private/jobs/*/*.pdf"`. It checks numbers against the profile and fails on em dashes, en dashes and arrows.
- This repo is public. Never commit anything under `resume/private/`.
