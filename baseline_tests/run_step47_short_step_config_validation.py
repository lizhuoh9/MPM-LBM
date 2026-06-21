import os

from step47_common import ROOT, STEP47_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_envelope_config import (
        RuntimeGeometryWallVelocityShortStepEnvelopeConfig,
        summarize_short_step_envelope_config_validation,
        validate_short_step_envelope_config,
    )

    config = RuntimeGeometryWallVelocityShortStepEnvelopeConfig.from_json(STEP47_CONFIG_PATH)
    rows = validate_short_step_envelope_config(config, root=ROOT)
    summary = summarize_short_step_envelope_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 47 short-step config validation failed: {summary}")
    out_dir = ROOT / "outputs" / "step47_short_step_config_validation"
    write_csv_rows(out_dir / "short_step_config_validation.csv", rows, ["check", "pass", "value", "notes"])
    write_json(out_dir / "short_step_config_validation.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "short_step_config_summary.csv", summary_rows(summary), ["metric", "value"])
    marker = "[OK] Step 47 short-step config validation finished"
    write_log("logs/step47_short_step_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
