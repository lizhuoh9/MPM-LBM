import os

from step46_common import ROOT, STEP46_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_coupling_config import (
        RuntimeGeometryWallVelocityCouplingSmokeConfig,
        summarize_coupling_smoke_config_validation,
        validate_coupling_smoke_config,
    )

    config = RuntimeGeometryWallVelocityCouplingSmokeConfig.from_json(STEP46_CONFIG_PATH)
    rows = validate_coupling_smoke_config(config, root=ROOT)
    summary = summarize_coupling_smoke_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 46 coupling smoke config validation failed: {summary}")
    out_dir = ROOT / "outputs" / "step46_coupling_smoke_config_validation"
    write_csv_rows(out_dir / "coupling_smoke_config_validation.csv", rows, ["check", "pass", "value", "notes"])
    write_json(out_dir / "coupling_smoke_config_validation.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "coupling_smoke_config_summary.csv", summary_rows(summary), ["metric", "value"])
    marker = "[OK] Step 46 coupling smoke config validation finished"
    write_log("logs/step46_coupling_smoke_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
