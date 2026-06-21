import os

from step50_common import ROOT, STEP50_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_config import (
        RuntimeGeometryWallVelocityOneCycleEnvelopeConfig,
        summarize_one_cycle_envelope_config_validation,
        validate_one_cycle_envelope_config,
    )

    config = RuntimeGeometryWallVelocityOneCycleEnvelopeConfig.from_json(STEP50_CONFIG_PATH)
    rows = validate_one_cycle_envelope_config(config, root=ROOT)
    summary = summarize_one_cycle_envelope_config_validation(rows, config)
    if not summary["validation_pass"]:
        raise RuntimeError(f"Step 50 one-cycle config validation failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_one_cycle_config_validation"
    write_csv_rows(out_dir / "one_cycle_config_validation.csv", rows, ["check", "pass", "value", "notes"])
    write_csv_rows(out_dir / "one_cycle_config_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "one_cycle_config_validation.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 one-cycle config validation finished"
    write_log("logs/step50_one_cycle_config_validation.log", [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
