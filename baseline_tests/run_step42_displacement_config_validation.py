import os

from step42_common import ROOT, STEP42_DISPLACEMENT_CONFIG_PATH, load_displacement_config, summary_rows, write_csv_rows, write_json, write_log
from src.geometry_displacement_config import summarize_geometry_displacement_config_validation, validate_geometry_displacement_config


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = load_displacement_config()
    rows = validate_geometry_displacement_config(config, root=ROOT)
    summary = summarize_geometry_displacement_config_validation(rows, config)
    if not bool(summary["validation_pass"]):
        raise RuntimeError(f"Step 42 displacement config validation failed: {summary}")

    out_dir = ROOT / "outputs" / "step42_displacement_config_validation"
    write_csv_rows(out_dir / "displacement_config_validation.csv", rows, FIELDS)
    write_csv_rows(out_dir / "displacement_config_validation_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "displacement_config_validation.json", {"config_path": STEP42_DISPLACEMENT_CONFIG_PATH, "summary": summary, "rows": rows})
    marker = "[OK] Step 42 displacement config validation finished"
    write_log("logs/step42_displacement_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
