import os

from step40_common import ROOT, read_driver_rows, write_log
from src.jet_cycle_parameter_sensitivity import (
    compare_static_vs_parameter_rows,
    summarize_response_rows,
    write_parameter_sensitivity_outputs,
)


def main():
    os.chdir(ROOT)
    driver_rows = read_driver_rows()
    rows = compare_static_vs_parameter_rows(
        [row for row in driver_rows if row["mode_class"] == "static"],
        [row for row in driver_rows if row["mode_class"] == "experimental"],
    )
    summary = summarize_response_rows(rows, "comparison_pass")
    if int(summary["row_count"]) != 6 or not summary["comparison_pass"]:
        raise RuntimeError(f"Step 40 static vs parameter comparison failed: {summary}")

    out_dir = ROOT / "outputs" / "step40_static_vs_parameter_comparison"
    write_parameter_sensitivity_outputs(
        rows,
        out_dir / "static_vs_parameter_comparison.csv",
        out_dir / "static_vs_parameter_comparison.json",
        summary,
    )
    marker = "[OK] Step 40 static vs parameter comparison finished"
    write_log("logs/step40_static_vs_parameter_comparison.log", [marker, f"row_count={summary['row_count']}"])
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
