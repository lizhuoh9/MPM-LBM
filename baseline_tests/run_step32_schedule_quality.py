import os

from step32_common import ROOT, load_schedule_config, make_schedule_rows, write_csv_rows, write_json, write_log
from src.squid_kinematics_quality import QUALITY_FIELDS, analyze_kinematics_schedule, assert_kinematics_schedule_quality, quality_rows_from_analysis


def main():
    os.chdir(ROOT)
    config = load_schedule_config()
    schedule = make_schedule_rows()
    analysis = analyze_kinematics_schedule(schedule, config)
    assert_kinematics_schedule_quality(analysis)
    rows = quality_rows_from_analysis(analysis)

    out_dir = ROOT / "outputs" / "step32_schedule_quality"
    write_csv_rows(out_dir / "schedule_quality.csv", rows, QUALITY_FIELDS)
    write_json(out_dir / "schedule_quality.json", {"summary": analysis, "rows": rows})
    marker = "[OK] Step 32 schedule quality finished"
    write_log(
        "logs/step32_schedule_quality.log",
        [marker, f"row_count={analysis['row_count']}", f"quality_pass={analysis['quality_pass']}"],
    )
    print(f"row_count={analysis['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
