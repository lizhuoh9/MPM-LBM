import os

from step38_common import (
    ROOT,
    STEP38_GEOMETRY_CONFIG_PATH,
    STEP38_SCHEDULE_CONFIG_PATH,
    STEP38_SCHEDULE_OUTPUT_PATH,
    fieldnames_from_rows,
    read_driver_rows,
    read_timeseries_rows,
    write_csv_rows,
    write_json,
    write_log,
)
from src.jet_cycle_proxy_diagnostics import load_schedule_config, load_step32_schedule, summarize_cycle_proxy


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    application_rows = []
    for row in driver_rows:
        if row["mode_class"] == "experimental":
            application_rows.extend(read_timeseries_rows(row))
    schedule_config = load_schedule_config(STEP38_SCHEDULE_CONFIG_PATH)
    schedule_rows = load_step32_schedule(STEP38_SCHEDULE_OUTPUT_PATH)
    summary = summarize_cycle_proxy(schedule_config, schedule_rows, driver_rows, application_rows, STEP38_GEOMETRY_CONFIG_PATH)
    assert_summary(summary)

    rows = [summary]
    out_dir = ROOT / "outputs" / "step38_cycle_proxy_diagnostics"
    write_csv_rows(out_dir / "cycle_proxy_diagnostics.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "cycle_proxy_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 38 cycle proxy diagnostics finished"
    write_log("logs/step38_cycle_proxy_diagnostics.log", [marker, f"cycle_period_steps={summary['cycle_period_steps']}"])
    print(f"phase_alignment_pass={summary['phase_alignment_pass']}")
    print(marker)


def assert_summary(summary):
    if int(summary["cycle_period_steps"]) != 40 or int(summary["schedule_row_count"]) != 81:
        raise RuntimeError(f"Step 38 cycle proxy schedule mismatch: {summary}")
    required = ("phase_alignment_pass", "cavity_volume_cycle_pass", "funnel_aperture_cycle_pass")
    if not all(bool(summary[name]) for name in required):
        raise RuntimeError(f"Step 38 cycle proxy checks failed: {summary}")
    if float(summary["expelled_volume_proxy"]) <= 0.0 or float(summary["refill_volume_proxy"]) <= 0.0:
        raise RuntimeError(f"Step 38 cavity proxy volume is invalid: {summary}")


if __name__ == "__main__":
    main()
