import os

from step35_common import (
    ROOT,
    STEP35_WALL_VELOCITY_CONFIG_PATH,
    summary_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.wall_velocity_config import (
    summarize_wall_velocity_config_validation,
    validate_wall_velocity_config,
    WallVelocityFieldConfig,
)


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = WallVelocityFieldConfig.from_json(STEP35_WALL_VELOCITY_CONFIG_PATH)
    rows = validate_wall_velocity_config(config, root=ROOT)
    summary = summarize_wall_velocity_config_validation(rows, config=config)
    assert_summary(summary)

    out_dir = ROOT / "outputs" / "step35_wall_velocity_config_validation"
    write_csv_rows(out_dir / "wall_velocity_config_validation.csv", rows, FIELDS)
    write_csv_rows(out_dir / "wall_velocity_config_validation_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "wall_velocity_config_validation.json", {"summary": summary, "rows": rows, "config": config.to_dict()})
    marker = "[OK] Step 35 wall velocity config validation finished"
    write_log(
        "logs/step35_wall_velocity_config_validation.log",
        [
            marker,
            f"row_count={summary['row_count']}",
            f"pass_count={summary['pass_count']}",
            f"validation_pass={summary['validation_pass']}",
        ],
    )
    print(f"validation_pass={summary['validation_pass']}")
    print(marker)


def assert_summary(summary: dict) -> None:
    if not bool(summary["validation_pass"]):
        raise RuntimeError(f"Step 35 wall velocity config validation failed: {summary}")
    if int(summary["grid_size_count"]) != 3 or int(summary["phase_sample_count"]) != 7 or int(summary["tracked_region_count"]) != 3:
        raise RuntimeError(f"Step 35 config sample dimensions are wrong: {summary}")
    for field in (
        "write_dense_field",
        "write_sparse_samples",
        "apply_to_lbm",
        "lbm_population_update_enabled",
        "moving_bounceback_update_enabled",
        "driver_integration_enabled",
        "jet_model_enabled",
        "actuation_enabled",
    ):
        if bool(summary[field]):
            raise RuntimeError(f"Step 35 config enabled forbidden flag {field}: {summary}")
    if int(summary["execution_flag_enabled_count"]) != 0:
        raise RuntimeError(f"Step 35 config has enabled execution flags: {summary}")


if __name__ == "__main__":
    main()
