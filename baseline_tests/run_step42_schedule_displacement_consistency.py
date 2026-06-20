import os

from step42_common import ROOT, load_displacement_inputs, write_csv_rows, write_json, write_log
from src.geometry_displacement_consistency import CONSISTENCY_FIELDS, assert_consistency, compare_displacement_to_schedule
from src.geometry_displacement_field import compute_geometry_displacement_rows


def main():
    os.chdir(ROOT)
    inputs = load_displacement_inputs()
    displacement_rows = compute_geometry_displacement_rows(
        inputs["config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["points"],
        inputs["masks"],
    )
    rows, summary = compare_displacement_to_schedule(inputs["schedule_rows"], displacement_rows)
    assert_consistency(summary, "Step 42 schedule-displacement consistency")

    out_dir = ROOT / "outputs" / "step42_schedule_displacement_consistency"
    write_csv_rows(out_dir / "schedule_displacement_consistency.csv", rows, CONSISTENCY_FIELDS)
    write_json(out_dir / "schedule_displacement_consistency.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 42 schedule-displacement consistency finished"
    write_log("logs/step42_schedule_displacement_consistency.log", [marker, f"row_count={summary['row_count']}", f"consistency_pass={summary['consistency_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
