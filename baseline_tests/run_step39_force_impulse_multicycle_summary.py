import os

from step39_common import CYCLE_PERIOD_STEPS, ROOT, fieldnames_from_rows, read_diagnostics_rows, read_driver_rows, write_csv_rows, write_json, write_log
from src.multicycle_proxy_diagnostics import force_impulse_proxy_rows_by_cycle, summarize_impulse_drift


def main():
    os.chdir(ROOT)
    rows = []
    for driver_row in read_driver_rows():
        rows.extend(force_impulse_proxy_rows_by_cycle(driver_row, read_diagnostics_rows(driver_row), CYCLE_PERIOD_STEPS))
    drift_summary = summarize_impulse_drift(rows)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["impulse_proxy_finite_pass"]),
        "impulse_proxy_summary_pass": all(row["impulse_proxy_finite_pass"] for row in rows),
    }
    summary.update(drift_summary)
    if not summary["impulse_proxy_summary_pass"] or int(summary["row_count"]) != 8:
        raise RuntimeError(f"Step 39 force impulse multicycle summary failed: {summary}")

    out_dir = ROOT / "outputs" / "step39_force_impulse_multicycle_summary"
    write_csv_rows(out_dir / "force_impulse_multicycle_summary.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "force_impulse_multicycle_summary.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 39 force impulse multicycle summary finished"
    write_log("logs/step39_force_impulse_multicycle_summary.log", [marker, f"row_count={summary['row_count']}"])
    print(f"impulse_proxy_summary_pass={summary['impulse_proxy_summary_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
