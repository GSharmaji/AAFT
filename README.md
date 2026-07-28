# LinkedIn Automation & Scheduling

A lightweight, zero-server scheduler that publishes first-party content to a
LinkedIn **Company Page** or **personal profile** on a set calendar, using
LinkedIn's official [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api).

It ships with **10 ready-to-post pieces** and runs itself daily via GitHub
Actions — no manual posting, no scraping, no fake engagement.

> This publishes **your own** content to accounts you control. It does not
> auto-connect, auto-like, auto-DM, or scrape — all of which violate LinkedIn's
> terms and can get your account banned.

---

## How it works

```
content/posts.yaml   ->  your 10 posts + a schedule (edit this)
src/scheduler.py     ->  finds posts that are "due" and not yet published
src/linkedin_client.py -> talks to the LinkedIn Posts API
state/posted.json    ->  ledger of what's already gone out (prevents duplicates)
.github/workflows/   ->  runs the scheduler every day automatically
```

Each day the scheduler looks for posts whose `date` is today-or-earlier and that
aren't already in the ledger, publishes them, and records the result. Because
publishing is recorded per-post, a post never goes out twice.

---

## Setup (one time, ~15 minutes)

### 1. Create a LinkedIn app & get credentials
1. Go to <https://www.linkedin.com/developers/apps> and create an app, linking it
   to your Company Page.
2. Under **Products**, request **Community Management API** (for a Company Page)
   or **Share on LinkedIn** (for a personal profile).
3. Generate an **access token** with:
   - `w_organization_social` — to post as a Company Page, **or**
   - `w_member_social` — to post as yourself.
4. Get your **author URN**:
   - Company Page: `urn:li:organization:<org_id>` (the org id is in your Page admin URL).
   - Personal: `urn:li:person:<member_id>` (call the `/v2/userinfo` endpoint).

### 2. Run it automatically with GitHub Actions (recommended)
In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**, add:

| Secret name | Value |
|---|---|
| `LINKEDIN_ACCESS_TOKEN` | your access token |
| `LINKEDIN_AUTHOR_URN` | e.g. `urn:li:organization:12345678` |
| `LINKEDIN_VERSION` | *(optional)* e.g. `202409` |

That's it. The workflow in `.github/workflows/linkedin-scheduler.yml` runs daily
at 09:00 UTC (~14:30 IST). Change the `cron:` line to post at a different time,
or trigger a manual/dry run from the **Actions** tab.

### 3. (Optional) Run it locally
```bash
pip install -r requirements.txt
cp .env.example .env      # then fill in your token + URN
export $(grep -v '^#' .env | xargs)

python src/scheduler.py --dry-run     # preview, nothing is posted
python src/scheduler.py               # publish everything due today
python src/scheduler.py --id 2026-08-launch-01   # force one post now
```

---

## Editing your content

Open `content/posts.yaml`:

- Set your details once in the `brand:` block — `{{brand_name}}`, `{{website}}`,
  `{{phone}}`, `{{email}}` are substituted into any post that uses them.
- Add/change posts under `posts:`. **Never reuse an `id`** — the ledger uses it to
  know what's already published.
- To attach an image, drop the file in `assets/` and set `image: assets/mypost.png`
  plus an `alt_text:` for accessibility. Text-only posts just omit those fields.

To add more than 10 posts, keep appending entries with future `date`s — the
scheduler handles any number.

---

## Access token expiry

LinkedIn access tokens expire (typically 60 days). When posts stop going out,
regenerate the token and update the `LINKEDIN_ACCESS_TOKEN` secret. For a fully
hands-off setup, implement the OAuth **refresh token** flow and store the refresh
token instead — a good next step once the basics are running.
