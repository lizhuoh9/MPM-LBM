import os

from step36_common import (
    ROOT,
    STEP36_APPLICATION_CONFIG_PATH,
    summary_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.wall_velocity_application_config import (
    WallVelocityApplicationConfig,
    summarize_wall_velocity_application_config_validation,
    validate_wall_velocity_application_config,
)


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = WallVelocityApplicationConfig.from_json(STEP36_APPLICATION_CONFIG_PATH)
    rows = validate_wall_velocity_application_config(config, root=ROOT)
    summary = summarize_wall_velocity_application_config_validation(rows, config=config)
    assert_summary(summary)

    out_dir = ROOT / "outputs" / "step36_wall_velocity_application_config_validation"
    write_csv_rows(out_dir / "application_config_validation.csv", rows, FIELDS)
    write_csv_rows(out_dir / "application_config_validation_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "application_config_validation.json", {"summary": summary, "rows": rows, "config": config.to_dict()})
    marker = "[OK] Step 36 wall velocity application config validation finished"
    write_log(
        "logs/step36_wall_velocity_application_config_validation.log",
        [marker, f"row_count={summary['row_count']}", f"pass_count={summary['pass_count']}", f"validation_pass={summary['validation_pass']}"],
    )
    print(f"validation_pass={summary['validation_pass']}")
    print(marker)


def assert_summary(summary: dict) -> None:
    if not bool(summary["validation_pass"]):
        raise RuntimeError(f"Step 36 application config validation failed: {summary}")
    if summary["application_mode"] != "solid_vel_experimental":
        raise RuntimeError(f"Step 36 config mode is wrong: {summary}")
    if summary["target_lbm_field"] != "solid_vel":
        raise RuntimeError(f"Step 36 target field is wrong: {summary}")
    if not bool(summary["apply_to_lbm_solid_vel"]):
        raise RuntimeError(f"Step 36 must apply only to lbm.solid_vel: {summary}")
    for field in ("apply_to_lbm_populations", "apply_to_mpm", "apply_to_projector", "modify_bounceback_formula", "jet_model_enabled", "actuation_claim_enabled"):
        if bool(summary[field]):
            raise RuntimeError(f"Step 36 config enabled forbidden flag {field}: {summary}")
    if float(summary["wall_velocity_cap_lbm"]) > 0.01:
        raise RuntimeError(f"Step 36 cap must be conservative: {summary}")


if __name__ == "__main__":
    main()
