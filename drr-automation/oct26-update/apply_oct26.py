"""One-shot patcher for the Oct'26 DRR changes. Run ON THE PC that runs the DRR job:

    "%LOCALAPPDATA%\\Programs\\Python\\Python312\\python.exe" apply_oct26.py
    (optional arg: path to DRR-Automation, default D:\\YT Channel\\DRR-Automation)

What it changes (every edited file is backed up first to backups/oct26_<time>/):
  1. src/course_map.py  - CRM renames + new course "HO - Film Making" (added at the END)
  2. build_daywise.py   - a course launched mid-month is appended at the END of this
                          month's frozen layout (existing cells don't move)
  3. every *.py with course_from_program() - Sales-Ops enrolments: Ayurveda checked
                          before Nutrition, Advanced Filmmaking mapped
  4. build_churn.py     - copied in (new "Churn Status" tab)
  5. run_drr.cmd        - runs build_churn.py right after build_daywise.py

Safe to re-run: each step is skipped if already applied. If a step can't find the
code it expects, it says so and changes nothing for that step.
"""
import re
import sys
import shutil
import pathlib
import subprocess
from datetime import datetime

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\YT Channel\DRR-Automation")
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
    for f in ["build_daywise.py", "build_churn.py", "build_history.py"]:
        r = subprocess.run([sys.executable, "-m", "py_compile", f], cwd=ROOT, capture_output=True, text=True)
        print(f"compile {f}: {'OK' if r.returncode == 0 else r.stderr.strip()}")


def main():
    if not ROOT.exists():
        sys.exit(f"ERROR: {ROOT} not found - pass the DRR-Automation path as the first argument.")
    print(f"DRR-Automation: {ROOT}\nBackups:        {BACKUP}\n")
    patch_course_map()
    patch_daywise()
    patch_programs()
    copy_churn()
    patch_runner()
    verify()
    stops = [n for n, ok, _ in results if not ok]
    print("\nDONE." if not stops else f"\nDONE WITH {len(stops)} STEP(S) NEEDING A HAND FIX: {stops}")


if __name__ == "__main__":
    main()
