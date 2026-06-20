import os

from step41_common import ROOT, read_driver_rows, read_timeseries_rows, write_log
from src.selected_parameter_64_feasibility import summarize_wall_velocity_64_quality, write_selected_parameter_outputs


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    application_rows_by_case = {row["case"]: read_timeseries_rows(row) for row in driver_rows if row["mode_class"] == "experimental"}
    rows, summary = summarize_wall_velocity_64_quality(application_rows_by_case, driver_rows)
    if not summary["quality_pass"]:
        raise RuntimeError(f"Step 41 wall velocity 64 quality failed: {summary}")

    out_dir = ROOT / "outputs" / "step41_wall_velocity_64_quality"
    write_selected_parameter_outputs(rows, out_dir / "wall_velocity_64_quality.csv", out_dir / "wall_velocity_64_quality.json", summary)
    marker = "[OK] Step 41 wall velocity 64 quality finished"
    write_log("logs/step41_wall_velocity_64_quality.log", [marker, f"quality_pass={summary['quality_pass']}"])
    print(f"quality_pass={summary['quality_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
