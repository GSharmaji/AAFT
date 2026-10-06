"""Build "Churn Status": Status by Course + Lead Stage by Course, current month.

Replaces the manual LSQ-export -> Excel pivot -> paste step for the DRR
workbook's "Churn Status" tab. Writes ONE tab into the DRR LSQ Test sheet:

  Table 1 (row 1)  Status by Course     : Row Labels | <statuses> | (blank) | Other |
                                          Grand Total | Active Leads | Churn % | Long PDE %
  Table 2          Lead Stage by Course : Row Labels | <stages> | (blank) | Other | Grand Total
  Funnel row       the 7 roll-ups the DRR sheet shows under the two pivots
  Updated stamp

Population = Gurgaon (GGN) leads CREATED this month (same base as Daily_Master /
Daywise), read from exports/months/fmt_YYYY-MM.csv. DRR_MONTH=YYYY-MM finalizes
a past month (writes "<Month> Churn Status" so the live tab is untouched).

Layout is FIXED so linked cells never move: course rows and status/stage columns
are hard-coded below. A status/stage value not in the list lands in "Other" and
is printed as a WARN, so add it to the list (at the END) if it should get its
own column. Never writes a production DRR.
"""
import os
import re
import sys
import pathlib
from datetime import datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EXPORTS = pathlib.Path(__file__).resolve().parent / "exports"
PROD_BLOCKLIST = ["ggn courses", "media plan"]

# Row order = the DRR "Churn Status" tab order; new courses go at the END.
# (canonical course from course_map, label shown in the sheet = current CRM name)
COURSE_ROWS = [
    ("HO - 3D Animation and Vfx", "Diploma in 3D Animation and Visual Effects"),
    ("HO - Ayurveda",             "Diploma in Ayurvedic Nutrition & Lifestyle"),
    ("GS - Event Management",     "Diploma in Event Management"),
    ("HO - Fashion Design",       "Diploma in Fashion Design"),
    ("GS - Interior Design",      "Diploma in Interior Design"),
    ("HO - Music Production",     "Diploma in Music Production"),
    ("GS - Naturopathy",          "Diploma in Naturopathy"),
    ("GS - Nutrition",            "Diploma in Applied Nutrition"),
    ("GS - Psychology",           "Diploma in Psychology"),
    ("HO - Film Making",          "Diploma in Advanced Filmmaking"),
]

STATUSES = ["Application on Hold", "Call Back Later", "Could Not Connect", "Interview Done",
            "Interview Scheduled", "Long PDE (>10 mins)", "Not Interested", "Offer on Hold",
            "Offer Released", "Short PDE (<10 mins)"]
STAGES = ["Enrolled", "Lead", "Lead Called", "Lead Reactivated", "Marketing Applicant",
          "Offered", "Rejected", "Rejected - CNC", "Sales Applicant", "Selected"]

# Column names tried in Formatted_Raw (first match wins)
STATUS_COLS = ["Status", "mx_Status", "Lead Status"]
STAGE_COLS = ["Lead Stage", "ProspectStage", "Stage"]

# Active Leads, exactly as the DRR sheet formula does it:
#   Total - Long PDE - Short PDE - (Rejected, Rejected - CNC, Sales Applicant,
#   Selected, Offered, Enrolled stages)
# Status and stage are subtracted separately, so a lead that is e.g. Long PDE AND
# Sales Applicant is subtracted twice. Set True to count each lead once instead.
ACTIVE_DEDUP = False
ACTIVE_MINUS_STATUSES = ["Long PDE (>10 mins)", "Short PDE (<10 mins)"]
ACTIVE_MINUS_STAGES = ["Rejected", "Rejected - CNC", "Sales Applicant", "Selected",
                       "Offered", "Enrolled"]

BLANK, OTHER, TOTAL = "(blank)", "Other", "Grand Total"


def vkey(s):
    """Match key for CRM values: case/space-insensitive, 'Rejected-CNC' == 'Rejected - CNC'."""
    s = re.sub(r"\s*-\s*", "-", str(s).strip().lower())
    return re.sub(r"\s+", " ", s)


def bucket(series, known):
    """Map raw CRM values onto the fixed column list; returns (bucketed, unknown counts)."""
    lookup = {vkey(k): k for k in known}
    raw = series.fillna("").astype(str).str.strip()
    out = raw.map(lambda v: BLANK if v == "" else lookup.get(vkey(v), OTHER))
    unknown = raw[(out == OTHER)].value_counts()
    return out, unknown


def pick_col(df, candidates, what):
    for c in candidates:
        if c in df.columns:
            return c
    sys.exit(f"ERROR: no {what} column in Formatted_Raw (tried {candidates}). "
             f"Columns are: {list(df.columns)}")


def pivot(df, col, known):
    cols = known + [BLANK, OTHER]
    rows = []
    for canon, label in COURSE_ROWS:
        counts = df.loc[df["Course"] == canon, col].value_counts()
        vals = [int(counts.get(k, 0)) for k in cols]
        rows.append([label] + vals + [sum(vals)])
    totals = [sum(r[j] for r in rows) for j in range(1, len(cols) + 2)]
    return [["Row Labels"] + cols + [TOTAL]] + rows + [[TOTAL] + totals]


def active_leads(df, s_tab, g_tab):
    """Per course row (+ Grand Total): Active Leads list aligned with the table rows."""
    s_idx = {h: i for i, h in enumerate(s_tab[0])}
    g_idx = {h: i for i, h in enumerate(g_tab[0])}
    out = []
    for i in range(1, len(s_tab)):
        if ACTIVE_DEDUP:
            sub = df if i == len(s_tab) - 1 else df[df["Course"] == COURSE_ROWS[i - 1][0]]
            gone = sub["_status"].isin(ACTIVE_MINUS_STATUSES) | sub["_stage"].isin(ACTIVE_MINUS_STAGES)
            out.append(int((~gone).sum()))
        else:
            v = s_tab[i][s_idx[TOTAL]]
            v -= sum(s_tab[i][s_idx[s]] for s in ACTIVE_MINUS_STATUSES)
            v -= sum(g_tab[i][g_idx[g]] for g in ACTIVE_MINUS_STAGES)
            out.append(v)
    return out


def funnel(s_tab, g_tab):
    """The roll-up row under the pivots in the DRR sheet (Grand Total row of each table)."""
    s = dict(zip(s_tab[0], s_tab[-1]))
    g = dict(zip(g_tab[0], g_tab[-1]))
    return [
        ("Lead + Lead Called", g["Lead"] + g["Lead Called"]),
        ("Call Back Later + Could Not Connect", s["Call Back Later"] + s["Could Not Connect"]),
        ("Marketing Applicant + Sales Applicant", g["Marketing Applicant"] + g["Sales Applicant"]),
        ("Interview Scheduled", s["Interview Scheduled"]),
        ("Interview Done", s["Interview Done"]),
        ("Offered", g["Offered"]),
        ("Enrolled", g["Enrolled"]),
    ]


def build_grid(df, stamp):
    """df needs Course + _status + _stage. Returns (grid, layout info for formatting)."""
    df = df[df["Course"].isin([c for c, _ in COURSE_ROWS])]
    s_tab = pivot(df, "_status", STATUSES)
    g_tab = pivot(df, "_stage", STAGES)

    act = active_leads(df, s_tab, g_tab)
    t_i = s_tab[0].index(TOTAL)
    lp_i = s_tab[0].index("Long PDE (>10 mins)")
    s_tab[0] += ["Active Leads", "Churn %", "Long PDE %"]
    for i in range(1, len(s_tab)):
        tot = s_tab[i][t_i]
        s_tab[i] += [act[i - 1],
                     round(act[i - 1] / tot, 4) if tot else 0,
                     round(s_tab[i][lp_i] / tot, 4) if tot else 0]

    ncols = max(len(s_tab[0]), len(g_tab[0]))
    pad = lambda r: r + [""] * (ncols - len(r))
    grid = [pad(r) for r in s_tab]
    grid.append(pad([]))
    g_start = len(grid)
    grid += [pad(r) for r in g_tab]
    grid.append(pad([]))
    f_start = len(grid)
    f = funnel(s_tab, g_tab)
    grid.append(pad([x[0] for x in f]))
    grid.append(pad([x[1] for x in f]))
    grid.append(pad([]))
    grid.append(pad([f"Updated {stamp}", "", "", ""]))

    layout = {"ncols": ncols, "s_rows": len(s_tab), "g_start": g_start, "g_rows": len(g_tab),
              "f_start": f_start, "pct_cols": [len(s_tab[0]) - 2, len(s_tab[0]) - 1]}
    return grid, layout


def load_month(month):
    p = EXPORTS / "months" / f"fmt_{month}.csv"
    if not p.exists():
        sys.exit(f"ERROR: {p} missing — run drr_lsq.py first.")
    f = pd.read_csv(p, dtype=str, keep_default_na=False)
    f = f[f["Location"] == "Gurgaon"].copy()
    f = f[f["Created On"].str[:7] == month]
    s_col = pick_col(f, STATUS_COLS, "Status")
    g_col = pick_col(f, STAGE_COLS, "Lead Stage")
    f["_status"], s_unknown = bucket(f[s_col], STATUSES)
    f["_stage"], g_unknown = bucket(f[g_col], STAGES)
    for what, unk in (("Status", s_unknown), ("Lead Stage", g_unknown)):
        if len(unk):
            print(f"WARN: {what} values not in the fixed list -> counted in 'Other': "
                  f"{dict(unk)}  (add to the list in build_churn.py if needed)")
    missing = sorted(set(f["Course"]) - {c for c, _ in COURSE_ROWS})
    if missing:
        n = int(f["Course"].isin(missing).sum())
        print(f"WARN: {n} Gurgaon leads in courses without a Churn row: {missing}")
    return f


def push(grid, layout, title):
    import time as _t
    import gspread
    from google.oauth2.service_account import Credentials
    from config import load_secrets, PROJECT_ROOT

    cfg = load_secrets()
    creds = Credentials.from_service_account_file(
        str(PROJECT_ROOT / cfg["GOOGLE_SERVICE_ACCOUNT_JSON"]),
        scopes=["https://www.googleapis.com/auth/spreadsheets"])
    sh = gspread.authorize(creds).open_by_key(cfg["DRR_SHEET_ID"])
    if any(b in sh.title.lower() for b in PROD_BLOCKLIST):
        sys.exit(f"REFUSING: '{sh.title}' looks like production.")

    def _retry(fn, *a, **k):
        for attempt in (1, 2):
            try:
                return fn(*a, **k)
            except gspread.exceptions.APIError as e:
                if "429" in str(e) and attempt == 1:
                    _t.sleep(65)          # write-quota is per minute; wait it out once
                else:
                    raise

    ncols = layout["ncols"]
    try:
        ws = sh.worksheet(title)
        _retry(ws.clear)
        _retry(ws.resize, rows=len(grid) + 1, cols=ncols)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title, rows=len(grid) + 2, cols=ncols)
    _retry(ws.update, values=grid, range_name="A1", value_input_option="RAW")

    sid = ws.id
    hdr_fmt = {"textFormat": {"bold": True}, "horizontalAlignment": "CENTER",
               "wrapStrategy": "WRAP", "backgroundColor": {"red": 0.74, "green": 0.88, "blue": 0.95}}
    rng = lambda r0, r1, c0=0, c1=ncols: {"sheetId": sid, "startRowIndex": r0, "endRowIndex": r1,
                                          "startColumnIndex": c0, "endColumnIndex": c1}
    reqs = []
    # header rows + Grand Total rows of both tables
    s_end, g0, g_end = layout["s_rows"], layout["g_start"], layout["g_start"] + layout["g_rows"]
    for r in (0, s_end - 1, g0, g_end - 1):
        reqs.append({"repeatCell": {"range": rng(r, r + 1), "cell": {"userEnteredFormat": hdr_fmt},
                     "fields": "userEnteredFormat(textFormat,horizontalAlignment,wrapStrategy,backgroundColor)"}})
    f0 = layout["f_start"]
    reqs.append({"repeatCell": {"range": rng(f0, f0 + 1), "cell": {"userEnteredFormat": {
        "textFormat": {"bold": True}, "wrapStrategy": "WRAP"}},
        "fields": "userEnteredFormat(textFormat,wrapStrategy)"}})
    for c in layout["pct_cols"]:
        reqs.append({"repeatCell": {"range": rng(1, s_end, c, c + 1), "cell": {"userEnteredFormat": {
            "numberFormat": {"type": "PERCENT", "pattern": "0%"}}},
            "fields": "userEnteredFormat.numberFormat"}})
    reqs.append({"updateDimensionProperties": {"range": {
        "sheetId": sid, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
        "properties": {"pixelSize": 300}, "fields": "pixelSize"}})
    _retry(sh.batch_update, {"requests": reqs})
    print(f"  pushed '{title}' -> '{sh.title}'")


def main():
    tgt = os.environ.get("DRR_MONTH", "").strip()         # optional "YYYY-MM" to finalize a past month
    now = datetime.now()
    when = datetime.strptime(tgt, "%Y-%m") if tgt else now
    month = when.strftime("%Y-%m")
    title = "Churn Status" if not tgt else f"{when:%B} Churn Status"

    df = load_month(month)
    grid, layout = build_grid(df, now.strftime("%d-%m-%Y %H:%M IST"))
    tot = grid[layout["s_rows"] - 1]
    print(f"{title} ({month}): {len(COURSE_ROWS)} courses | leads {tot[grid[0].index(TOTAL)]} "
          f"| active {tot[grid[0].index('Active Leads')]} | churn {tot[grid[0].index('Churn %')]:.0%}")
    push(grid, layout, title)


if __name__ == "__main__":
    main()
