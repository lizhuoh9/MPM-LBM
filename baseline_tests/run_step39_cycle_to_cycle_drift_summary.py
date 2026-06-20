import os

from step39_common import CYCLE_PERIOD_STEPS, ROOT, fieldnames_from_rows, read_diagnostics_rows, read_driver_rows, write_csv_rows, write_json, write_log
from src.multicycle_proxy_diagnostics import summarize_cycle_stability, summarize_cycle_to_cycle_drift


def main():
    os.chdir(ROOT)
    rows = []
    for driver_row in read_driver_rows():
        cycle_rows = summarize_cycle_stability(driver_row, read_diagnostics_rows(driver_row), CYCLE_PERIOD_STEPS)
        rows.append(summarize_cycle_to_cycle_drift(cycle_rows))
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["drift_pass"]),
        "drift_summary_pass": all(row["drift_pass"] for row in rows),
    }
    if not summary["drift_summary_pass"]:
        raise RuntimeError(f"Step 39 cycle-to-cycle drift failed: {summary}")

    out_dir = ROOT / "outputs" / "step39_cycle_to_cycle_drift_summary"
    write_csv_rows(out_dir / "cycle_to_cycle_drift.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "cycle_to_cycle_drift.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 39 cycle-to-cycle drift summary finished"
    write_log("logs/step39_cycle_to_cycle_drift_summary.log", [marker, f"row_count={summary['row_count']}"])
    print(f"drift_summary_pass={summary['drift_summary_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
