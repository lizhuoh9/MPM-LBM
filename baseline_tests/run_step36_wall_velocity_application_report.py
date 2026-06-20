import os

from step36_common import (
    ROOT,
    STEP36_APPLICATION_CONFIG_PATH,
    summary_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.wall_velocity_application import build_wall_velocity_application_report
from src.wall_velocity_application_config import WallVelocityApplicationConfig


SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    config = WallVelocityApplicationConfig.from_json(STEP36_APPLICATION_CONFIG_PATH)
    report = build_wall_velocity_application_report(config, n_grid=48, phase=0.1)
    summary = report["summary"]
    assert_summary(summary)

    out_dir = ROOT / "outputs" / "step36_wall_velocity_application_report"
    write_json(out_dir / "application_report.json", report)
    write_csv_rows(out_dir / "application_report_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    marker = "[OK] Step 36 wall velocity application report finished"
    write_log(
        "logs/step36_wall_velocity_application_report.log",
        [marker, f"report_pass={summary['report_pass']}", f"applied_cell_count={summary['applied_cell_count']}"],
    )
    print(f"report_pass={summary['report_pass']}")
    print(marker)


def assert_summary(summary: dict) -> None:
    if not bool(summary["report_pass"]):
        raise RuntimeError(f"Step 36 application report failed: {summary}")
    if int(summary["n_grid"]) != 48:
        raise RuntimeError(f"Step 36 report must use 48^3 smoke sampling: {summary}")
    if int(summary["wall_velocity_row_count"]) != 63:
        raise RuntimeError(f"Step 36 report must consume the Step 35 63-row field: {summary}")
    if int(summary["applied_cell_count"]) <= 0:
        raise RuntimeError(f"Step 36 report has no applied cells: {summary}")
    if float(summary["max_capped_velocity_norm"]) > float(summary["wall_velocity_cap_lbm"]) + 1.0e-12:
        raise RuntimeError(f"Step 36 report exceeds velocity cap: {summary}")
    if bool(summary["lbm_population_update_enabled"]) or bool(summary["modify_bounceback_formula"]):
        raise RuntimeError(f"Step 36 report enables forbidden updates: {summary}")


if __name__ == "__main__":
    main()
