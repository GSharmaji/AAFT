# Hand-off prompt for the Claude session on the DRR laptop

Paste this whole file into a Claude Code session opened in `D:\YT Channel\DRR-Automation` (or `claude remote-control` there).

---

DRR Oct'26 update — please do this end to end on this PC without asking me anything unless something is unsafe. (Garvit asked for this from a cloud session; the code and tests were written there. Branch with the same files: GSharmaji/AAFT `claude/zen-meitner-ekmuby`, folder `drr-automation/oct26-update/`.)

Project: `D:\YT Channel\DRR-Automation`. Python: `"$LOCALAPPDATA/Programs/Python/Python312/python.exe"` (not on PATH). Safety rule unchanged: only ever write to the DRR LSQ Test sheet, never production.

## What the update does
1. New course "Diploma in Advanced Filmmaking" -> canonical `HO - Film Making`, appended at the END of ORDER/ACTIVE_ORDER and of the frozen `_daywise_layout_2026-10.json` (October Daywise gets a new last block; nothing else moves).
2. CRM renames: "Diploma in Ayurvedic Nutrition & Lifestyle" -> HO - Ayurveda, "Diploma in Applied Nutrition" -> GS - Nutrition (old names stay mapped).
3. `course_from_program()`: check "ayurved" BEFORE "nutrition" (else Ayurvedic Nutrition enrolments land in Nutrition) + map Advanced Filmmaking.
4. New `build_churn.py` -> "Churn Status" tab (Status by Course + Lead Stage by Course, Active Leads / Churn % / Long PDE %, roll-up row), hooked into run_drr.cmd after build_daywise.
5. Website leads = Source Category 'Website' OR Lead Source 'Website'/'Intelliticks' (wrapper on transform.build_formatted; Intelliticks used to be Google Ads). Same rule in `to_source()` for Sales-Ops enrolments.

## Steps
1. Get `apply_oct26.py`, `build_churn.py`, `test_build_churn.py` from GSharmaji/AAFT branch `claude/zen-meitner-ekmuby`, folder `drr-automation/oct26-update/`, into `D:\YT Channel\DRR-Automation\_oct26\`. Run `python _oct26/test_build_churn.py` (must print OK).
2. Read the current `src/course_map.py`, `src/transform.py`, `build_daywise.py`, `build_history.py` (and any file with `course_from_program` / `to_source`) and confirm the patcher's assumptions hold (names `_GGN`, `GGN_COURSES`, `ekey`, `ORDER`, `ACTIVE_ORDER`, `map_course`, `location_for`; top-level `build_formatted` returning the formatted DataFrame with a `Channel` column whose website value is "Website"; Formatted_Raw has "Source Category" and "Lead Source" columns; Formatted_Raw has a lead Status column (Status / mx_Status) and a "Lead Stage" column — build_churn.py looks for those names in STATUS_COLS / STAGE_COLS; adjust the lists if the real names differ).
3. Run `python _oct26/apply_oct26.py "D:\YT Channel\DRR-Automation" --no-run`. Every step must print OK, verify must show `map_course: all OK`, `ACTIVE_ORDER ends with: HO - Film Making`, `location_for('HO - Film Making'): Gurgaon`, `Website rule: OK`, and real Source columns found. If any step prints STOP, make the equivalent edit by hand (same intent, minimal change) — backups are in `backups/oct26_<time>/`.
4. Check the exact CRM spelling of the new course in this month's `exports/months/fmt_2026-10.csv` / `_course_values.json` (anything with "film" in Course Interested). If the real value isn't one of the 4 variants in the patch, add it to `_OCT26_ADD["HO - Film Making"]` in course_map.py. Don't map Mumbai film courses (only the Advanced Filmmaking diploma).
5. If PAUSE.flag exists, stop and tell me. Don't start within ~10 min of a scheduled slot (odd hours 9–21h) so two runs don't overlap. Then run the full job ONCE: `cmd.exe /c call "D:\YT Channel\DRR-Automation\run_drr.cmd"` and read the new part of `logs/run.log`.
6. Verify in DRR LSQ Test (service account, read-only): `October Daywise` ends with a `HO - Film Making` block of 12 cols and the other courses' cells did not move; `Churn Status` tab exists (table 1 at A1:Q12, table 2 at A14:N25, roll-up rows 27-28, Updated stamp A30); no WARN about unknown statuses/stages (if there are, add them to STATUSES/STAGES at the END). Report: MTD leads / QL / EL per course incl. Film Making, Churn % per course, and how many October leads moved from Google to Website because of Intelliticks.
7. Commit the changes in the DRR-Automation git repo (local commit only, message "Oct'26: Film Making, CRM renames, Churn Status tab, Intelliticks=Website"). Don't commit secrets or exports.
8. Add a short dated note to your memory file `drr-automation-project.md` (new course, renames, Website rule, Churn Status tab + its fixed layout, Intelliticks moved from Google to Website from Oct'26 — Jan–Sep caches still on the old rule).
9. Still needed from Garvit (just list them in your summary, don't block): Film Making Meta campaign code for `src/meta_map.py`, and Film Making Meta/Google targets in `config/targets/2026-10.csv`.
