import os

from step40_common import ROOT, read_driver_rows, write_log
from src.jet_cycle_parameter_sensitivity import summarize_scale_response, write_parameter_sensitivity_outputs


def main():
    os.chdir(ROOT)
    rows, summary = summarize_scale_response(read_driver_rows())
    if not summary["parameter_sensitivity_pass"]:
        raise RuntimeError(f"Step 40 parameter sensitivity summary failed: {summary}")

    out_dir = ROOT / "outputs" / "step40_parameter_sensitivity_summary"
    write_parameter_sensitivity_outputs(
        rows,
        out_dir / "parameter_sensitivity_summary.csv",
        out_dir / "parameter_sensitivity_summary.json",
        summary,
    )
    marker = "[OK] Step 40 parameter sensitivity summary finished"
    write_log("logs/step40_parameter_sensitivity_summary.log", [marker, f"parameter_sensitivity_pass={summary['parameter_sensitivity_pass']}"])
    print(f"parameter_sensitivity_pass={summary['parameter_sensitivity_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
