import os

from step40_common import ROOT, read_driver_rows, read_timeseries_rows, write_log
from src.jet_cycle_parameter_sensitivity import summarize_cap_saturation, write_parameter_sensitivity_outputs


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    application_rows_by_case = {row["case"]: read_timeseries_rows(row) for row in driver_rows if row["mode_class"] == "experimental"}
    rows, summary = summarize_cap_saturation(application_rows_by_case, driver_rows)
    if not summary["cap_saturation_diagnostics_pass"]:
        raise RuntimeError(f"Step 40 cap saturation diagnostics failed: {summary}")

    out_dir = ROOT / "outputs" / "step40_cap_saturation_diagnostics"
    write_parameter_sensitivity_outputs(
        rows,
        out_dir / "cap_saturation_diagnostics.csv",
        out_dir / "cap_saturation_diagnostics.json",
        summary,
    )
    marker = "[OK] Step 40 cap saturation diagnostics finished"
    write_log("logs/step40_cap_saturation_diagnostics.log", [marker, f"cap_pass={summary['cap_pass']}"])
    print(f"cap_saturation_diagnostics_pass={summary['cap_saturation_diagnostics_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
