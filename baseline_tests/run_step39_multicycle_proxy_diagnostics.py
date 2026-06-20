import os

from step39_common import (
    CYCLE_COUNT,
    CYCLE_PERIOD_STEPS,
    ROOT,
    STEP39_GEOMETRY_CONFIG_PATH,
    STEP39_SCHEDULE_OUTPUT_PATH,
    fieldnames_from_rows,
    read_driver_rows,
    read_timeseries_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.jet_cycle_proxy_diagnostics import load_step32_schedule
from src.multicycle_proxy_diagnostics import (
    summarize_cavity_proxy_by_cycle,
    summarize_funnel_proxy_by_cycle,
    wall_velocity_proxy_by_cycle,
)


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    schedule_rows = load_step32_schedule(STEP39_SCHEDULE_OUTPUT_PATH)
    rows = []
    rows.extend(summarize_cavity_proxy_by_cycle(schedule_rows, CYCLE_COUNT, CYCLE_PERIOD_STEPS, STEP39_GEOMETRY_CONFIG_PATH))
    rows.extend(summarize_funnel_proxy_by_cycle(schedule_rows, CYCLE_COUNT, CYCLE_PERIOD_STEPS))
    for row in driver_rows:
        if row["mode_class"] == "experimental":
            rows.extend(wall_velocity_proxy_by_cycle(row, read_timeseries_rows(row), CYCLE_PERIOD_STEPS, CYCLE_COUNT))
    summary = {
        "cycle_count": CYCLE_COUNT,
        "cycle_period_steps": CYCLE_PERIOD_STEPS,
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["cycle_pass"]),
        "multicycle_proxy_pass": all(row["cycle_pass"] for row in rows),
    }
    if not summary["multicycle_proxy_pass"]:
        raise RuntimeError(f"Step 39 multicycle proxy diagnostics failed: {summary}")

    out_dir = ROOT / "outputs" / "step39_multicycle_proxy_diagnostics"
    write_csv_rows(out_dir / "multicycle_proxy_diagnostics.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "multicycle_proxy_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 39 multicycle proxy diagnostics finished"
    write_log("logs/step39_multicycle_proxy_diagnostics.log", [marker, f"row_count={summary['row_count']}"])
    print(f"multicycle_proxy_pass={summary['multicycle_proxy_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
