import os

from step33_common import make_motion_rows
from step42_common import ROOT, make_displacement_rows, write_csv_rows, write_json, write_log
from src.geometry_displacement_consistency import CONSISTENCY_FIELDS, assert_consistency, compare_displacement_to_motion_mapping


def main():
    os.chdir(ROOT)
    motion_rows = make_motion_rows()
    displacement_rows = make_displacement_rows()
    rows, summary = compare_displacement_to_motion_mapping(motion_rows, displacement_rows)
    assert_consistency(summary, "Step 42 motion-displacement consistency")

    out_dir = ROOT / "outputs" / "step42_motion_displacement_consistency"
    write_csv_rows(out_dir / "motion_displacement_consistency.csv", rows, CONSISTENCY_FIELDS)
    write_json(out_dir / "motion_displacement_consistency.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 42 motion-displacement consistency finished"
    write_log("logs/step42_motion_displacement_consistency.log", [marker, f"row_count={summary['row_count']}", f"consistency_pass={summary['consistency_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
