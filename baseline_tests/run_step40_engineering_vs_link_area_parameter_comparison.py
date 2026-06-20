import os

from step40_common import ROOT, read_driver_rows, write_log
from src.jet_cycle_parameter_sensitivity import (
    compare_transfer_modes_by_scale,
    summarize_response_rows,
    write_parameter_sensitivity_outputs,
)


def main():
    os.chdir(ROOT)
    rows = compare_transfer_modes_by_scale([row for row in read_driver_rows() if row["mode_class"] == "experimental"])
    summary = summarize_response_rows(rows, "comparison_pass")
    if int(summary["row_count"]) != 3 or not summary["comparison_pass"]:
        raise RuntimeError(f"Step 40 engineering vs link-area comparison failed: {summary}")

    out_dir = ROOT / "outputs" / "step40_engineering_vs_link_area_parameter_comparison"
    write_parameter_sensitivity_outputs(
        rows,
        out_dir / "engineering_vs_link_area_parameter.csv",
        out_dir / "engineering_vs_link_area_parameter.json",
        summary,
    )
    marker = "[OK] Step 40 engineering vs link-area parameter comparison finished"
    write_log("logs/step40_engineering_vs_link_area_parameter_comparison.log", [marker, f"row_count={summary['row_count']}"])
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
