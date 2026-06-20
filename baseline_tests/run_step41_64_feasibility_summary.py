import os

from step41_common import ROOT, read_driver_rows, write_log, write_summary_csv
from src.selected_parameter_64_feasibility import summarize_selected_parameter_feasibility, write_json


def main():
    os.chdir(ROOT)
    summary = summarize_selected_parameter_feasibility(read_driver_rows())
    if not summary["feasibility_pass"]:
        raise RuntimeError(f"Step 41 64 feasibility summary failed: {summary}")

    out_dir = ROOT / "outputs" / "step41_64_feasibility_summary"
    write_summary_csv(out_dir / "feasibility_summary.csv", summary)
    write_json(out_dir / "feasibility_summary.json", {"summary": summary, "rows": []})
    marker = "[OK] Step 41 64 feasibility summary finished"
    write_log("logs/step41_64_feasibility_summary.log", [marker, f"feasibility_pass={summary['feasibility_pass']}"])
    print(f"feasibility_pass={summary['feasibility_pass']}")
    print(marker)


if __name__ == "__main__":
    main()
