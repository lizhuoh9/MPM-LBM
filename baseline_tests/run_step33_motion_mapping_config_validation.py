import os

from step33_common import ROOT, STEP33_MOTION_MAPPING_CONFIG_PATH, load_motion_mapping_config, summary_rows, write_csv_rows, write_json, write_log
from src.squid_motion_mapping_config import summarize_motion_mapping_config_validation, validate_motion_mapping_config


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = load_motion_mapping_config()
    rows = validate_motion_mapping_config(config, root=ROOT)
    summary = summarize_motion_mapping_config_validation(rows)
    if not bool(summary["validation_pass"]):
        raise RuntimeError(f"Step 33 motion mapping config validation failed: {summary}")

    out_dir = ROOT / "outputs" / "step33_motion_mapping_config_validation"
    write_csv_rows(out_dir / "motion_mapping_config_validation.csv", rows, FIELDS)
    write_csv_rows(out_dir / "motion_mapping_config_validation_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "motion_mapping_config_validation.json", {"config_path": STEP33_MOTION_MAPPING_CONFIG_PATH, "summary": summary, "rows": rows})
    marker = "[OK] Step 33 motion mapping config validation finished"
    write_log(
        "logs/step33_motion_mapping_config_validation.log",
        [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
