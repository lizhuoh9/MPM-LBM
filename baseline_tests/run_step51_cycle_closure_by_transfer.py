import os

from step51_common import ROOT, transfer_closure_rows, transfer_comparison_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_transfer_diagnostics import summarize_transfer_cycle_closure

    rows = transfer_comparison_rows()
    closure_rows = transfer_closure_rows()
    closure_rows, summary = summarize_transfer_cycle_closure(rows, closure_rows)
    if not summary["closure_pass"]:
        raise RuntimeError(f"Step 51 cycle closure by transfer failed: {summary}")
    out_dir = ROOT / "outputs" / "step51_cycle_closure_by_transfer"
    write_csv_rows(out_dir / "cycle_closure_by_transfer.csv", closure_rows)
    write_json(out_dir / "cycle_closure_by_transfer.json", {"summary": summary, "rows": closure_rows})
    marker = "[OK] Step 51 cycle closure by transfer finished"
    write_log("logs/step51_cycle_closure_by_transfer.log", [marker, f"row_count={summary['row_count']}", f"closure_pass={summary['closure_pass']}"])
    print(marker)


if __name__ == "__main__":
    main()
