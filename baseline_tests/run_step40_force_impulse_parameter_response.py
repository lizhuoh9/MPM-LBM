import os

from step40_common import ROOT, read_diagnostics_rows, read_driver_rows, write_log
from src.jet_cycle_parameter_sensitivity import (
    force_impulse_parameter_response_row,
    summarize_response_rows,
    write_parameter_sensitivity_outputs,
)


def main():
    os.chdir(ROOT)
    rows = [force_impulse_parameter_response_row(row, read_diagnostics_rows(row)) for row in read_driver_rows()]
    summary = summarize_response_rows(rows, "response_finite_pass")
    if int(summary["row_count"]) != 8 or not summary["force_impulse_parameter_response_pass"]:
        raise RuntimeError(f"Step 40 force impulse parameter response failed: {summary}")

    out_dir = ROOT / "outputs" / "step40_force_impulse_parameter_response"
    write_parameter_sensitivity_outputs(
        rows,
        out_dir / "force_impulse_parameter_response.csv",
        out_dir / "force_impulse_parameter_response.json",
        summary,
    )
    marker = "[OK] Step 40 force impulse parameter response finished"
    write_log("logs/step40_force_impulse_parameter_response.log", [marker, f"row_count={summary['row_count']}"])
    print(f"force_impulse_parameter_response_pass={summary['force_impulse_parameter_response_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
