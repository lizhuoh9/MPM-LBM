import os

from step34_common import (
    ROOT,
    STEP34_BOUNDARY_MOTION_CONFIG_PATH,
    summary_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.boundary_motion_config import (
    BoundaryMotionInterfaceConfig,
    summarize_boundary_motion_config_validation,
    validate_boundary_motion_interface_config,
)


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = BoundaryMotionInterfaceConfig.from_json(STEP34_BOUNDARY_MOTION_CONFIG_PATH)
    rows = validate_boundary_motion_interface_config(config, root=ROOT)
    summary = summarize_boundary_motion_config_validation(rows)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 34 boundary-motion config validation failed: {rows}")

    out_dir = ROOT / "outputs" / "step34_boundary_motion_config_validation"
    write_csv_rows(out_dir / "boundary_motion_config_validation.csv", rows, FIELDS)
    write_json(out_dir / "boundary_motion_config_validation.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "boundary_motion_config_validation_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    marker = "[OK] Step 34 boundary motion config validation finished"
    write_log(
        "logs/step34_boundary_motion_config_validation.log",
        [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"],
    )
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
