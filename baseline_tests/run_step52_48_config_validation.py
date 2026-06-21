import os

from step52_common import ROOT, STEP52_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_48_feasibility_config import (
        RuntimeGeometryWallVelocity48FeasibilityConfig,
        summarize_48_feasibility_config_validation,
        validate_48_feasibility_config,
    )

    config = RuntimeGeometryWallVelocity48FeasibilityConfig.from_json(STEP52_CONFIG_PATH)
    rows = validate_48_feasibility_config(config, root=ROOT)
    summary = summarize_48_feasibility_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 52 48 config validation failed: {summary}")
    out_dir = ROOT / "outputs" / "step52_48_config_validation"
    write_csv_rows(out_dir / "config_validation.csv", rows, ["check", "pass", "value", "notes"])
    write_csv_rows(out_dir / "config_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "config_validation.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 52 48 config validation finished"
    write_log("logs/step52_48_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
