import os

from step38_common import ROOT, fieldnames_from_rows, read_diagnostics_rows, read_driver_rows, write_csv_rows, write_json, write_log
from src.jet_cycle_proxy_diagnostics import force_impulse_proxy_row


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    rows = [force_impulse_proxy_row(row, read_diagnostics_rows(row)) for row in driver_rows]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["impulse_proxy_finite_pass"]),
        "impulse_proxy_summary_pass": all(row["impulse_proxy_finite_pass"] for row in rows),
    }
    if not summary["impulse_proxy_summary_pass"] or int(summary["row_count"]) != 4:
        raise RuntimeError(f"Step 38 force impulse proxy summary failed: {summary}")

    out_dir = ROOT / "outputs" / "step38_force_impulse_proxy_summary"
    write_csv_rows(out_dir / "force_impulse_proxy_summary.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "force_impulse_proxy_summary.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 38 force impulse proxy summary finished"
    write_log("logs/step38_force_impulse_proxy_summary.log", [marker, f"row_count={summary['row_count']}"])
    print(f"impulse_proxy_summary_pass={summary['impulse_proxy_summary_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
