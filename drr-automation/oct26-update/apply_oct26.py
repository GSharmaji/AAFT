"""One-shot patcher for the Oct'26 DRR changes. Run ON THE PC that runs the DRR job:

    "%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe" apply_oct26.py
    (optional: path to DRR-Automation, default D:\\YT Channel\\DRR-Automation;
     --no-run to skip the one-off pipeline run at the end)

What it changes (every edited file is backed up first to backups/oct26_<time>/):
  1. src/course_map.py  - CRM renames + new course "HO - Film Making" (added at the END)
  2. build_daywise.py   - a course launched mid-month is appended at the END of this
                          month's frozen layout (existing cells don't move)
  3. every *.py with course_from_program() - Sales-Ops enrolments: Ayurveda checked
                          before Nutrition, Advanced Filmmaking mapped
  4. build_churn.py     - copied in (new "Churn Status" tab)
  5. run_drr.cmd        - runs build_churn.py right after build_daywise.py
  6. src/transform.py   - Website = Source Category 'Website' OR Lead Source
                          'Website'/'Intelliticks' (Intelliticks was Google Ads)
  7. every *.py with to_source() - Sales-Ops enrolments: Lead Source
                          'Website'/'Intelliticks' -> Website
Then it runs the full job once (run_drr.cmd) so the sheet updates now, not at the
next 2-hour slot, and prints what that run did.

Safe to re-run: each step is skipped if already applied. If a step can't find the
code it expects, it says so and changes nothing for that step.
"""
import os
import re
import sys
import shutil
import pathlib
import subprocess
from datetime import datetime

HERE = pathlib.Path(__file__).resolve().parent
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
NO_RUN = "--no-run" in sys.argv
ROOT = pathlib.Path(ARGS[0] if ARGS else r"D:\YT Channel\DRR-Automation")
BACKUP = ROOT / "backups" / f"oct26_{datetime.now():%Y%m%d_%H%M%S}"
MARK = "OCT26 UPDATE"

COURSE_MAP_BLOCK = '''

# --- OCT26 UPDATE: CRM renames + new course (appended; nothing above changed) ---
# Old CRM names stay mapped so earlier leads still count. New course goes at the
# END of ORDER / ACTIVE_ORDER so existing report cells keep their positions.
_OCT26_ADD = {
    "HO - Ayurveda": ["Diploma in Ayurvedic Nutrition & Lifestyle",
                      "Diploma in Ayurvedic Nutrition and Lifestyle"],
    "GS - Nutrition": ["Diploma in Applied Nutrition"],
    "HO - Film Making": ["Diploma in Advanced Filmmaking", "Diploma in Advanced Film Making",
                         "Diploma in Advance Filmmaking", "Diploma in Advance Film Making"],
}
for _canon, _raws in _OCT26_ADD.items():
    _vals = list(_GGN.get(_canon, []))
    for _r in _raws:
        if _r not in _vals:
            _vals.append(_r)
        GGN_COURSES[ekey(_r)] = _canon
    _GGN[_canon] = _vals
if "HO - Film Making" not in ORDER:
    ORDER = list(ORDER) + ["HO - Film Making"]
if "HO - Film Making" not in ACTIVE_ORDER:
    ACTIVE_ORDER = list(ACTIVE_ORDER) + ["HO - Film Making"]
'''

TRANSFORM_BLOCK = '''

# --- OCT26 UPDATE: Website leads (appended; nothing above changed) ---
# Website = Source Category 'Website' OR Lead Source 'Website' / 'Intelliticks'.
# Applied after build_formatted so it wins over every other channel rule
# (Intelliticks used to fall under Google Ads).
import pandas as _pd_oct26

_OCT26_SRC_CAT = ["Source Category", "mx_Source_Category"]
_OCT26_LEAD_SRC = ["Lead Source", "Source", "mx_Source"]
_OCT26_WEB_SOURCES = {"website", "intelliticks"}


def _oct26_website(f):
    if not isinstance(f, _pd_oct26.DataFrame) or "Channel" not in f.columns:
        print("WARN: Website rule not applied - build_formatted output has no Channel column")
        return f
    cat = next((c for c in _OCT26_SRC_CAT if c in f.columns), None)
    src = next((c for c in _OCT26_LEAD_SRC if c in f.columns), None)
    if cat is None and src is None:
        print(f"WARN: Website rule not applied - no Source Category / Lead Source column in {list(f.columns)}")
        return f
    norm = lambda col: f[col].fillna("").astype(str).str.strip().str.lower()
    web = _pd_oct26.Series(False, index=f.index)
    if cat:
        web |= norm(cat) == "website"
    if src:
        web |= norm(src).isin(_OCT26_WEB_SOURCES)
    f.loc[web, "Channel"] = "Website"
    return f


_build_formatted_pre_oct26 = build_formatted


def build_formatted(*args, **kwargs):
    return _oct26_website(_build_formatted_pre_oct26(*args, **kwargs))
'''

TO_SOURCE_BLOCK = '''# OCT26 UPDATE: Lead Source 'Website' / 'Intelliticks' = Website (checked first)
_to_source_pre_oct26 = to_source


def to_source(s):
    if str(s).strip().lower() in ("website", "intelliticks"):
        return "Website"
    return _to_source_pre_oct26(s)


'''

DAYWISE_OLD = """    if lock_path.exists():
        courses = json.loads(lock_path.read_text())
"""
DAYWISE_NEW = """    if lock_path.exists():
        courses = json.loads(lock_path.read_text())
        # OCT26 UPDATE: a course launched mid-month is appended at the END, so
        # every existing cell keeps its position. Removals still wait for next month.
        added = [c for c in ACTIVE_ORDER if c not in courses]
        if added:
            courses += added
            lock_path.write_text(json.dumps(courses))
            print(f"Layout lock: appended new course(s) at the end: {added}")
"""

PROGRAM_RE = re.compile(r"(def course_from_program\((\w+)\):\n(\s+)(\w+) = str\(\2\)\.lower\(\)\n)")
PROGRAM_ADD = """{ind}# OCT26 UPDATE: checked first - "Ayurvedic Nutrition & Lifestyle" contains "nutrition"
{ind}if "ayurved" in {var}:
{ind}    return "HO - Ayurveda"
{ind}if "film" in {var} and "advance" in {var}:
{ind}    return "HO - Film Making"
"""

results = []


def backup(p):
    dst = BACKUP / p.relative_to(ROOT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dst)


def write(p, text):
    backup(p)
    p.write_text(text, encoding="utf-8")


def step(name, ok, msg):
    results.append((name, ok, msg))
    print(f"[{'OK  ' if ok else 'STOP'}] {name}: {msg}")


def patch_course_map():
    p = ROOT / "src" / "course_map.py"
    if not p.exists():
        return step("course_map", False, f"{p} not found")
    s = p.read_text(encoding="utf-8")
    if MARK in s:
        return step("course_map", True, "already applied")
    need = ["_GGN", "GGN_COURSES", "def ekey", "ORDER", "ACTIVE_ORDER"]
    missing = [n for n in need if n not in s]
    if missing:
        return step("course_map", False, f"expected names not found: {missing} - not patched")
    write(p, s.rstrip("\n") + "\n" + COURSE_MAP_BLOCK)
    step("course_map", True, "renames + HO - Film Making added")


def patch_daywise():
    p = ROOT / "build_daywise.py"
    s = p.read_text(encoding="utf-8")
    if MARK in s:
        return step("build_daywise", True, "already applied")
    if s.count(DAYWISE_OLD) != 1:
        return step("build_daywise", False, "layout-lock block not found as expected - not patched")
    write(p, s.replace(DAYWISE_OLD, DAYWISE_NEW))
    step("build_daywise", True, "mid-month course append enabled")


def patch_programs():
    hits = 0
    for p in sorted(ROOT.glob("*.py")) + sorted((ROOT / "src").glob("*.py")):
        s = p.read_text(encoding="utf-8", errors="replace")
        if "def course_from_program" not in s:
            continue
        hits += 1
        if MARK in s:
            step(f"course_from_program ({p.name})", True, "already applied")
            continue
        m = PROGRAM_RE.search(s)
        if not m:
            step(f"course_from_program ({p.name})", False, "unexpected shape - not patched")
            continue
        add = PROGRAM_ADD.format(ind=m.group(3), var=m.group(4))
        write(p, s[:m.end()] + add + s[m.end():])
        step(f"course_from_program ({p.name})", True, "Ayurveda-first + Film Making")
    if not hits:
        step("course_from_program", False, "no file defines course_from_program")


def patch_transform():
    p = ROOT / "src" / "transform.py"
    if not p.exists():
        return step("transform", False, f"{p} not found")
    s = p.read_text(encoding="utf-8")
    if MARK in s:
        return step("transform", True, "already applied")
    if not re.search(r"^def build_formatted\(", s, re.M):
        return step("transform", False, "no top-level build_formatted() - not patched")
    write(p, s.rstrip("\n") + "\n" + TRANSFORM_BLOCK)
    step("transform", True, "Website = Source Category Website OR Lead Source Website/Intelliticks")


def patch_to_source():
    hits = 0
    for p in sorted(ROOT.glob("*.py")) + sorted((ROOT / "src").glob("*.py")):
        s = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^def to_source\(", s, re.M)
        if not m:
            continue
        hits += 1
        if "_to_source_pre_oct26" in s:
            step(f"to_source ({p.name})", True, "already applied")
            continue
        # insert right after the function: before the next top-level statement
        nxt = re.compile(r"^[^\s#\n]", re.M).search(s, m.end())
        if not nxt:
            step(f"to_source ({p.name})", False, "end of function not found - not patched")
            continue
        write(p, s[:nxt.start()] + TO_SOURCE_BLOCK + s[nxt.start():])
        step(f"to_source ({p.name})", True, "Website/Intelliticks -> Website")
    if not hits:
        step("to_source", True, "no file defines to_source (nothing to do)")


def copy_churn():
    src, dst = HERE / "build_churn.py", ROOT / "build_churn.py"
    if dst.exists():
        if dst.read_bytes() == src.read_bytes():
            return step("build_churn.py", True, "already in place")
        backup(dst)
    shutil.copy2(src, dst)
    step("build_churn.py", True, f"copied to {dst}")


def patch_runner():
    p = ROOT / "run_drr.cmd"
    s = p.read_text(encoding="utf-8", errors="replace")
    if "build_churn.py" in s:
        return step("run_drr.cmd", True, "already runs build_churn.py")
    lines = s.splitlines(keepends=True)
    idx = [i for i, l in enumerate(lines) if "build_daywise.py" in l]
    if len(idx) != 1:
        return step("run_drr.cmd", False, "no single build_daywise.py line - add build_churn.py by hand")
    i = idx[0]
    new = lines[i].replace("build_daywise.py", "build_churn.py").replace("DAYWISE", "CHURN")
    write(p, "".join(lines[:i + 1] + [new] + lines[i + 1:]))
    step("run_drr.cmd", True, f"added: {new.strip()}")


def verify():
    code = (
        "import sys; sys.path.insert(0, 'src')\n"
        "import course_map as m\n"
        "cases = {'Diploma in Ayurvedic Nutrition & Lifestyle': 'HO - Ayurveda',\n"
        "         'Diploma in Applied Nutrition': 'GS - Nutrition',\n"
        "         'Diploma in Advanced Filmmaking': 'HO - Film Making',\n"
        "         'Diploma in Advanced Film Making': 'HO - Film Making'}\n"
        "bad = {k: m.map_course(k) for k, v in cases.items() if m.map_course(k) != v}\n"
        "print('map_course:', 'all OK' if not bad else f'WRONG {bad}')\n"
        "print('ACTIVE_ORDER ends with:', m.ACTIVE_ORDER[-1])\n"
        "for arg in ('HO - Film Making', 'Diploma in Advanced Filmmaking'):\n"
        "    try: print(f'location_for({arg!r}):', m.location_for(arg))\n"
        "    except Exception as e: print(f'location_for({arg!r}): n/a ({e})')\n"
    )
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    print("\n--- verify ---\n" + (r.stdout or "") + (r.stderr or ""))
    code = (
        "import sys; sys.path.insert(0, 'src')\n"
        "import pandas as pd, transform as t\n"
        "f = pd.DataFrame({'Channel': ['Google Ads', 'Google Ads', 'Meta Ads', 'Other'],\n"
        "                  'Lead Source': ['Intelliticks', 'Adwords', 'Facebook', 'Website'],\n"
        "                  'Source Category': ['', '', 'Website', '']})\n"
        "out = list(t._oct26_website(f)['Channel'])\n"
        "ok = out == ['Website', 'Google Ads', 'Website', 'Website']\n"
        "print('Website rule:', 'OK' if ok else f'WRONG {out}')\n"
        "import glob, os\n"
        "c = sorted(glob.glob('exports/months/fmt_*.csv'))\n"
        "if c:\n"
        "    cols = list(pd.read_csv(c[-1], nrows=0).columns)\n"
        "    have = [x for x in t._OCT26_SRC_CAT + t._OCT26_LEAD_SRC if x in cols]\n"
        "    print(f'Source columns found in {os.path.basename(c[-1])}:', have or f'NONE - rule will not apply; columns are {cols}')\n"
    )
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    print((r.stdout or "") + (r.stderr or ""))
    for f in ["build_daywise.py", "build_churn.py", "build_history.py", "src/transform.py"]:
        r = subprocess.run([sys.executable, "-m", "py_compile", f], cwd=ROOT, capture_output=True, text=True)
        print(f"compile {f}: {'OK' if r.returncode == 0 else r.stderr.strip()}")


def run_once():
    """Run the full job now (same as the 2-hourly task) and show what it did."""
    if NO_RUN:
        return print("\n--no-run: skipped the one-off run.")
    if os.name != "nt":
        return print("\nNot Windows - skipped the one-off run.")
    if (ROOT / "PAUSE.flag").exists():
        return print("\nPAUSE.flag exists - the job is paused, so it was NOT run. Delete it and run run_drr.cmd.")
    log = ROOT / "logs" / "run.log"
    start = log.stat().st_size if log.exists() else 0
    print("\nRunning run_drr.cmd once now (takes a few minutes)...")
    r = subprocess.run(["cmd.exe", "/c", "call", str(ROOT / "run_drr.cmd")], cwd=ROOT)
    if not log.exists():
        return print(f"run_drr.cmd exited {r.returncode}; no logs/run.log to show.")
    with open(log, "rb") as fh:
        fh.seek(start)
        new = fh.read().decode("utf-8", errors="replace").splitlines()
    keep = re.compile(r"START|DONE|FAILED|WARN|ERROR|Traceback|Daywise|Churn|MTD check|pushed|Layout lock|LSQ 20")
    print(f"--- this run (exit {r.returncode}) ---")
    for line in new:
        if keep.search(line):
            print("  " + line.rstrip())


def main():
    if not ROOT.exists():
        sys.exit(f"ERROR: {ROOT} not found - pass the DRR-Automation path as the first argument.")
    print(f"DRR-Automation: {ROOT}\nBackups:        {BACKUP}\n")
    patch_course_map()
    patch_daywise()
    patch_programs()
    copy_churn()
    patch_runner()
    patch_transform()
    patch_to_source()
    verify()
    stops = [n for n, ok, _ in results if not ok]
    print("\nPATCHED." if not stops else f"\nPATCHED WITH {len(stops)} STEP(S) NEEDING A HAND FIX: {stops}")
    run_once()


if __name__ == "__main__":
    main()
