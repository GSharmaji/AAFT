"""Offline check: rebuild the Oct'26 DRR "Churn Status" pivots from synthetic leads
and compare with the numbers in the manual sheet (no Google / LSQ access needed).

Run:  python test_build_churn.py
"""
import pandas as pd
import build_churn as bc

# From the manual Oct'26 sheet (9 courses, same row order as COURSE_ROWS).
STATUS = {  # Application on Hold .. Short PDE, (blank)
    "HO - 3D Animation and Vfx": [0, 18, 44, 0, 0, 7, 25, 1, 0, 4, 65],
    "HO - Ayurveda":             [0, 18, 51, 0, 0, 4, 21, 0, 0, 4, 72],
    "GS - Event Management":     [1, 13, 45, 0, 1, 19, 30, 0, 0, 6, 72],
    "HO - Fashion Design":       [3, 21, 63, 1, 0, 12, 37, 0, 0, 10, 80],
    "GS - Interior Design":      [7, 35, 88, 1, 0, 23, 41, 0, 0, 13, 111],
    "HO - Music Production":     [0, 5, 44, 0, 1, 9, 29, 0, 1, 11, 47],
    "GS - Naturopathy":          [0, 16, 33, 0, 1, 7, 22, 0, 0, 5, 59],
    "GS - Nutrition":            [0, 13, 23, 0, 0, 5, 16, 0, 0, 4, 69],
    "GS - Psychology":           [1, 14, 34, 0, 0, 14, 16, 0, 0, 5, 43],
}
STAGE = {  # Enrolled .. Selected
    "HO - 3D Animation and Vfx": [0, 65, 71, 0, 0, 0, 26, 1, 0, 1],
    "HO - Ayurveda":             [0, 72, 76, 0, 0, 0, 22, 0, 0, 0],
    "GS - Event Management":     [0, 71, 83, 0, 1, 0, 30, 0, 2, 0],
    "HO - Fashion Design":       [0, 79, 104, 1, 1, 1, 37, 0, 4, 0],
    "GS - Interior Design":      [0, 102, 154, 0, 9, 1, 41, 0, 12, 0],
    "HO - Music Production":     [1, 46, 65, 1, 0, 1, 31, 0, 2, 0],
    "GS - Naturopathy":          [0, 58, 61, 0, 1, 0, 22, 0, 1, 0],
    "GS - Nutrition":            [0, 69, 44, 0, 0, 0, 17, 0, 0, 0],
    "GS - Psychology":           [0, 43, 66, 0, 0, 0, 16, 0, 2, 0],
}
ACTIVE = [125, 140, 130, 163, 229, 92, 108, 104, 90]   # sheet column T
TOTALS = [164, 170, 187, 227, 319, 147, 143, 130, 127]


def synth():
    rows = []
    for course, sc in STATUS.items():
        statuses = sum(([v] * n for v, n in zip(bc.STATUSES + [""], sc)), [])
        stages = sum(([v] * n for v, n in zip(bc.STAGES, STAGE[course])), [])
        assert len(statuses) == len(stages), course
        for st, sg in zip(statuses, stages):
            rows.append({"Course": course, "Status": st, "Lead Stage": sg})
    # spelling noise the CRM really produces + a value outside the list
    rows.append({"Course": "HO - Film Making", "Status": "could not  connect", "Lead Stage": "Rejected-CNC"})
    rows.append({"Course": "HO - Film Making", "Status": "Brand New Status", "Lead Stage": "lead"})
    rows.append({"Course": "Other (not in DRR)", "Status": "Call Back Later", "Lead Stage": "Lead"})
    df = pd.DataFrame(rows)
    df["_status"], unk_s = bc.bucket(df["Status"], bc.STATUSES)
    df["_stage"], unk_g = bc.bucket(df["Lead Stage"], bc.STAGES)
    assert dict(unk_s) == {"Brand New Status": 1}, dict(unk_s)
    assert dict(unk_g) == {}, dict(unk_g)
    return df


def main():
    grid, lay = bc.build_grid(synth(), "06-10-2026 10:00 IST")
    hdr = grid[0]
    T = hdr.index("Grand Total")
    for i, (canon, label) in enumerate(bc.COURSE_ROWS[:9], start=1):
        row = grid[i]
        assert row[0] == label
        assert row[1:12] == STATUS[canon], (label, row[1:12])
        assert row[T] == TOTALS[i - 1], (label, row[T])
        assert row[hdr.index("Active Leads")] == ACTIVE[i - 1], (label, row[hdr.index("Active Leads")])

    film = grid[10]
    assert film[0] == "Diploma in Advanced Filmmaking"
    assert film[hdr.index("Could Not Connect")] == 1 and film[hdr.index("Other")] == 1, film

    gt = grid[lay["s_rows"] - 1]
    assert gt[0] == "Grand Total" and gt[T] == 1614 + 2, gt[T]      # 'Other (not in DRR)' excluded
    assert gt[hdr.index("Active Leads")] == 1181 + 1, gt[hdr.index("Active Leads")]   # film: 1 Rejected-CNC, 1 active
    assert round(gt[hdr.index("Churn %")], 2) == 0.73

    g0 = lay["g_start"]
    ghdr = grid[g0]
    assert ghdr[ghdr.index("Rejected - CNC")] == "Rejected - CNC"
    assert grid[g0 + 10][ghdr.index("Rejected - CNC")] == 1          # 'Rejected-CNC' matched
    ggt = grid[g0 + lay["g_rows"] - 1]
    assert ggt[ghdr.index("Grand Total")] == 1616

    labels, vals = grid[lay["f_start"]], grid[lay["f_start"] + 1]
    funnel = dict(zip(labels, vals))
    assert funnel["Lead + Lead Called"] == 605 + 1 + 724, funnel     # +1 film 'lead'
    assert funnel["Call Back Later + Could Not Connect"] == 153 + 425 + 1
    assert funnel["Marketing Applicant + Sales Applicant"] == 12 + 23
    assert funnel["Interview Scheduled"] == 3 and funnel["Interview Done"] == 2
    assert funnel["Offered"] == 3 and funnel["Enrolled"] == 1

    bc.ACTIVE_DEDUP = True
    grid2, _ = bc.build_grid(synth(), "x")
    assert all(grid2[i][hdr.index("Active Leads")] >= grid[i][hdr.index("Active Leads")]
               for i in range(1, lay["s_rows"]))
    print("OK — pivots, Active Leads, Churn %, funnel row all match the manual Oct'26 sheet")
    for r in grid:
        print(r)


if __name__ == "__main__":
    main()
