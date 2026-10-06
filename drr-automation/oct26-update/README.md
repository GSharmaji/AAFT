# DRR automation — Oct'26 update

Changes for the local `D:\YT Channel\DRR-Automation` job that feeds the **DRR LSQ Test** sheet.

## What it does

| # | Change | File(s) |
|---|---|---|
| 1 | **New course: Diploma in Advanced Filmmaking** → canonical `HO - Film Making`. It is added at the **end** of every course list, so no existing column moves. In `October Daywise` it gets the same 12 columns as the other courses (Total Leads / Adwords / Meta / Website × Total Leads / Qualified Lead / Enrolments). | `src/course_map.py`, `build_daywise.py` |
| 2 | **CRM renames:** "Diploma in Ayurvedic Nutrition & Lifestyle" → `HO - Ayurveda`, and "Diploma in Applied Nutrition" → `GS - Nutrition`. The old names stay mapped, so earlier leads still count. | `src/course_map.py` |
| 3 | **Enrolment fix:** `course_from_program()` checked "nutrition" before "ayurved". That meant every *Ayurvedic **Nutrition** & Lifestyle* enrolment would have been counted as **Nutrition**. Ayurveda is now checked first, and Advanced Filmmaking enrolments are mapped too. | every `*.py` that has `course_from_program` |
| 4 | **New tab `Churn Status`** with two tables: Status by Course and Lead Stage by Course. It also has Active Leads, Churn %, Long PDE %, and the roll-up row (Lead + Lead Called … Enrolled). The numbers come from the same Gurgaon month-to-date leads as Daywise. | `build_churn.py` (new) |
| 5 | The scheduled job runs `build_churn.py` right after `build_daywise.py`. | `run_drr.cmd` |
| 6 | **Website leads = Source Category "Website" OR Lead Source "Website" / "Intelliticks".** This rule wins over every other channel rule. Intelliticks used to count as **Google Ads**, so from now on Adwords numbers drop and Website numbers rise by the same amount. | `src/transform.py` |
| 7 | The same rule for Sales-Ops enrolments (Lead Source "Website" / "Intelliticks" → Website). | every `*.py` that has `to_source` |

October Daywise is already locked with 9 courses. On the next run, `build_daywise` adds Film Making as the last block. Nothing else moves.

## How to apply (on the PC)

1. Copy this `oct26-update` folder anywhere on the PC.
2. Run:
   ```
   "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" apply_oct26.py
   ```
   If the project isn't at `D:\YT Channel\DRR-Automation`, pass its path as the first argument.
   - Every file is backed up to `backups\oct26_<time>\` before it is edited.
   - The script is safe to run again. Each step is skipped if it was already applied.
   - Any step that can't find the code it expects prints `STOP` and leaves that file untouched.
3. Check the `--- verify ---` lines. All mappings should say `all OK`, and `ACTIVE_ORDER ends with: HO - Film Making`.
4. **The script then runs the full job once** (`run_drr.cmd`), so the sheet updates now instead of at the next 2-hour slot. It prints the key lines from that run. To skip this, add `--no-run`. If `PAUSE.flag` exists, the run is skipped. Avoid starting the script right at a scheduled slot (9, 11, 13 … 21h), or two runs will write to the sheet at once.
5. Check the DRR LSQ Test sheet: `October Daywise` should end with the Film Making block, and a new `Churn Status` tab should appear.

Optional offline test (no Google or LSQ needed): `python test_build_churn.py`. It rebuilds the manual Oct'26 pivots and checks every number against them.

## Things the script cannot do for you

- **Check the exact CRM spelling of the new course.** Course matching is exact (case-insensitive). The script covers "Advanced/Advance" + "Filmmaking/Film Making". If the CRM uses anything else, the Health tab flags it as a NEW COURSE VALUE, and Film Making will show zeros.
- **Meta spend for Film Making.** `src/meta_map.py` matches campaign names by course code. Add the Film Making campaign code there, or its Meta spend lands in OTHER.
- **Past months.** The Website rule only applies to months pulled after the patch. October is re-pulled on every run, so it is fully on the new rule. Jan–Sep in the year-to-date Formatted_Raw stay on the old rule (Intelliticks = Google) unless you re-pull each month with `DRR_MONTH=YYYY-MM`.
- **Targets.** `config/targets/2026-10.csv` has no Film Making rows. Pacing stays without it until you add the Overall/Meta/Google targets. The DRR shows ₹3L spend and 651 leads; the Meta/Google split is your call.

## Pulling into the DRR workbook

Use lookups by course name instead of fixed cell references. That way a new row or column can't silently break a link. For example, Overall Performance → Churn %:

```
=IFERROR(INDEX(IMPORTRANGE("15HpH5px6KabWSKLtMUoiYP4yIVp4RYJ6yW3hi7xuIvA","Churn Status!A1:Q12"),
   MATCH("Diploma in Applied Nutrition", IMPORTRANGE("15HpH5px6KabWSKLtMUoiYP4yIVp4RYJ6yW3hi7xuIvA","Churn Status!A1:A12"),0),
   16),"-")
```

Tab layout (fixed): table 1 at `A1:Q12` (header, 10 courses, Grand Total). Table 2 at `A14:N25`. Roll-up labels in row 27, values in row 28. Update time in `A30`.

## Errors found in the current manual Oct'26 DRR file

- **The roll-up row under the Churn pivots (row 27) points at the wrong columns.** "Enrolled" shows 724, which is actually *Lead Called*. "Interview Scheduled" shows 237, which is *Not Interested*. "Lead+Lead Called" shows 14 instead of 1,329. The new tab computes these correctly.
- **Overall Performance → Churn % (column AI) links to the wrong course in 4 of 10 rows:**

  | Row | Course | Links to (wrong) | Should link to |
  |---|---|---|---|
  | AI2 | Nutrition | U10 (Psychology) | U9 |
  | AI4 | Naturopathy | U9 (Nutrition) | U8 |
  | AI7 | Music | U8 (Naturopathy) | U7 |
  | AI9 | 3D Animation | U3 (Ayurveda) | U2 |

- **The "Active Leads" formula subtracts status and stage separately.** A lead that is, say, *Long PDE* **and** *Sales Applicant* gets subtracted twice, so Active Leads and Churn % come out too low. `build_churn.py` copies your formula exactly, so its numbers match yours. To count each lead only once, set `ACTIVE_DEDUP = True`.
