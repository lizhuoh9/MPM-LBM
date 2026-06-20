import os

from step43_common import ROOT, STEP43_GEOMETRY_MOTION_CONFIG_PATH, load_geometry_motion_config, summary_rows, write_csv_rows, write_json, write_log
from src.geometry_motion_config import summarize_geometry_motion_config_validation, validate_geometry_motion_interface_config


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = load_geometry_motion_config()
    rows = validate_geometry_motion_interface_config(config, root=ROOT)
    summary = summarize_geometry_motion_config_validation(rows, config, root=ROOT)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 43 geometry motion config validation failed: {summary}")

    out_dir = ROOT / "outputs" / "step43_geometry_motion_config_validation"
    write_csv_rows(out_dir / "geometry_motion_config_validation.csv", rows, FIELDS)
    write_csv_rows(out_dir / "geometry_motion_config_validation_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "geometry_motion_config_validation.json", {"config_path": STEP43_GEOMETRY_MOTION_CONFIG_PATH, "summary": summary, "rows": rows})
    marker = "[OK] Step 43 geometry motion config validation finished"
    write_log("logs/step43_geometry_motion_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
