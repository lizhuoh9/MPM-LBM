import os

from step41_common import (
    ROOT,
    STEP41_GEOMETRY_CONFIG_PATH,
    STEP41_SCHEDULE_CONFIG_PATH,
    STEP41_SCHEDULE_ROWS_PATH,
    read_driver_rows,
    read_timeseries_rows,
    write_log,
)
from src.selected_parameter_64_feasibility import summarize_cycle_proxy_64, write_selected_parameter_outputs


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    application_rows = []
    for row in driver_rows:
        if row["mode_class"] == "experimental":
            application_rows.extend(read_timeseries_rows(row))
    rows, summary = summarize_cycle_proxy_64(
        STEP41_SCHEDULE_CONFIG_PATH,
        STEP41_SCHEDULE_ROWS_PATH,
        driver_rows,
        application_rows,
        STEP41_GEOMETRY_CONFIG_PATH,
    )
    if not summary["cycle_proxy_64_pass"]:
        raise RuntimeError(f"Step 41 cycle proxy 64 diagnostics failed: {summary}")

    out_dir = ROOT / "outputs" / "step41_cycle_proxy_64_diagnostics"
    write_selected_parameter_outputs(rows, out_dir / "cycle_proxy_64_diagnostics.csv", out_dir / "cycle_proxy_64_diagnostics.json", summary)
    marker = "[OK] Step 41 cycle proxy 64 diagnostics finished"
    write_log("logs/step41_cycle_proxy_64_diagnostics.log", [marker, f"cycle_proxy_64_pass={summary['cycle_proxy_64_pass']}"])
    print(f"cycle_proxy_64_pass={summary['cycle_proxy_64_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
