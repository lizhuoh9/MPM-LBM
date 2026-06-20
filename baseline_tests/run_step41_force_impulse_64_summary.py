import os

from step41_common import ROOT, read_diagnostics_rows, read_driver_rows, write_log
from src.selected_parameter_64_feasibility import force_impulse_64_row, summarize_force_impulse_64_rows, write_selected_parameter_outputs


def main():
    os.chdir(ROOT)
    rows = [force_impulse_64_row(row, read_diagnostics_rows(row)) for row in read_driver_rows()]
    summary = summarize_force_impulse_64_rows(rows)
    if not summary["force_impulse_64_pass"]:
        raise RuntimeError(f"Step 41 force impulse 64 summary failed: {summary}")

    out_dir = ROOT / "outputs" / "step41_force_impulse_64_summary"
    write_selected_parameter_outputs(rows, out_dir / "force_impulse_64_summary.csv", out_dir / "force_impulse_64_summary.json", summary)
    marker = "[OK] Step 41 force impulse 64 summary finished"
    write_log("logs/step41_force_impulse_64_summary.log", [marker, f"row_count={summary['row_count']}"])
    print(f"force_impulse_64_pass={summary['force_impulse_64_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
