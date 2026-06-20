import os

from step41_common import ROOT, read_driver_rows, write_log
from src.selected_parameter_64_feasibility import (
    compare_engineering_link_area_64_rows,
    summarize_response_rows,
    write_selected_parameter_outputs,
)


def main():
    os.chdir(ROOT)
    rows = compare_engineering_link_area_64_rows([row for row in read_driver_rows() if row["mode_class"] == "experimental"])
    summary = summarize_response_rows(rows, "comparison_pass")
    if int(summary["row_count"]) != 1 or not summary["comparison_pass"]:
        raise RuntimeError(f"Step 41 engineering vs link-area 64 comparison failed: {summary}")

    out_dir = ROOT / "outputs" / "step41_engineering_vs_link_area_64_comparison"
    write_selected_parameter_outputs(rows, out_dir / "engineering_vs_link_area_64.csv", out_dir / "engineering_vs_link_area_64.json", summary)
    marker = "[OK] Step 41 engineering vs link-area 64 comparison finished"
    write_log("logs/step41_engineering_vs_link_area_64_comparison.log", [marker, f"row_count={summary['row_count']}"])
    print(f"comparison_pass={summary['comparison_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
