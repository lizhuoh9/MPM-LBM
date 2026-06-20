import os

from step42_common import ROOT, load_displacement_config, make_displacement_rows, write_csv_rows, write_json, write_log
from src.geometry_displacement_quality import QUALITY_FIELDS, analyze_displacement_quality, assert_displacement_quality, quality_rows_from_displacement_analysis


def main():
    os.chdir(ROOT)
    config = load_displacement_config()
    rows = make_displacement_rows()
    analysis = analyze_displacement_quality(rows, config)
    assert_displacement_quality(analysis)
    quality_rows = quality_rows_from_displacement_analysis(analysis)

    out_dir = ROOT / "outputs" / "step42_displacement_quality"
    write_csv_rows(out_dir / "displacement_quality.csv", quality_rows, QUALITY_FIELDS)
    write_json(out_dir / "displacement_quality.json", {"summary": analysis, "rows": quality_rows})
    marker = "[OK] Step 42 displacement quality finished"
    write_log("logs/step42_displacement_quality.log", [marker, f"row_count={analysis['row_count']}", f"quality_pass={analysis['quality_pass']}"])
    print(f"row_count={analysis['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
