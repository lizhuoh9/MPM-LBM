import os

from step51_common import ROOT, STEP51_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_config import (
        RuntimeGeometryWallVelocityTransferConfig,
        summarize_transfer_comparison_config_validation,
        validate_transfer_comparison_config,
    )

    config = RuntimeGeometryWallVelocityTransferConfig.from_json(STEP51_CONFIG_PATH)
    rows = validate_transfer_comparison_config(config, root=ROOT)
    summary = summarize_transfer_comparison_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 51 transfer config validation failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_transfer_config_validation"
    write_csv_rows(out_dir / "transfer_config_validation.csv", rows, ["check", "pass", "value", "notes"])
    write_csv_rows(out_dir / "transfer_config_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "transfer_config_validation.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 51 transfer config validation finished"
    write_log("logs/step51_transfer_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
