import os

from step49_common import ROOT, STEP49_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_20step_config import (
        RuntimeGeometryWallVelocityTwentyStepEnvelopeConfig,
        summarize_twenty_step_envelope_config_validation,
        validate_twenty_step_envelope_config,
    )

    config = RuntimeGeometryWallVelocityTwentyStepEnvelopeConfig.from_json(STEP49_CONFIG_PATH)
    rows = validate_twenty_step_envelope_config(config, root=ROOT)
    summary = summarize_twenty_step_envelope_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 49 twenty-step config validation failed: {summary}")
    out_dir = ROOT / "outputs" / "step49_20step_config_validation"
    write_csv_rows(out_dir / "twenty_step_config_validation.csv", rows, ["check", "pass", "value", "notes"])
    write_json(out_dir / "twenty_step_config_validation.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "twenty_step_config_summary.csv", summary_rows(summary), ["metric", "value"])
    marker = "[OK] Step 49 20-step config validation finished"
    write_log("logs/step49_20step_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
