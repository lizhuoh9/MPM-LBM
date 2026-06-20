import os

from step32_common import ROOT, STEP32_SCHEDULE_CONFIG_PATH, load_schedule_config, summary_rows, write_csv_rows, write_json, write_log
from src.squid_kinematics_config import summarize_config_validation, validate_kinematics_schedule_config


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = load_schedule_config()
    rows = validate_kinematics_schedule_config(config, root=ROOT)
    summary = summarize_config_validation(rows)
    if not bool(summary["validation_pass"]):
        raise RuntimeError(f"Step 32 schedule config validation failed: {summary}")

    out_dir = ROOT / "outputs" / "step32_schedule_config_validation"
    write_csv_rows(out_dir / "schedule_config_validation.csv", rows, FIELDS)
    write_csv_rows(out_dir / "schedule_config_validation_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "schedule_config_validation.json", {"config_path": STEP32_SCHEDULE_CONFIG_PATH, "summary": summary, "rows": rows})
    marker = "[OK] Step 32 schedule config validation finished"
    write_log(
        "logs/step32_schedule_config_validation.log",
        [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
