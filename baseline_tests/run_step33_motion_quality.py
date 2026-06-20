import os

from step33_common import ROOT, load_motion_mapping_config, make_motion_rows, write_csv_rows, write_json, write_log
from src.squid_motion_quality import QUALITY_FIELDS, analyze_motion_mapping, assert_motion_mapping_quality, quality_rows_from_motion_analysis


def main():
    os.chdir(ROOT)
    config = load_motion_mapping_config()
    rows = make_motion_rows()
    analysis = analyze_motion_mapping(rows, config)
    assert_motion_mapping_quality(analysis)
    quality_rows = quality_rows_from_motion_analysis(analysis)

    out_dir = ROOT / "outputs" / "step33_motion_quality"
    write_csv_rows(out_dir / "motion_quality.csv", quality_rows, QUALITY_FIELDS)
    write_json(out_dir / "motion_quality.json", {"summary": analysis, "rows": quality_rows})
    marker = "[OK] Step 33 motion quality finished"
    write_log("logs/step33_motion_quality.log", [marker, f"row_count={analysis['row_count']}", f"quality_pass={analysis['quality_pass']}"])
    print(f"row_count={analysis['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
