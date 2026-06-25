import os

from step107_common import ROOT, write_log
from src.mpm_lbm.evidence.step107_common import summary_rows, write_csv_rows, write_json
from src.mpm_lbm.evidence.step107_output_guard import build_step107_output_guard


def main():
    os.chdir(ROOT)
    rows, summary = build_step107_output_guard(ROOT)
    if not summary["output_guard_pass"]:
        raise RuntimeError(f"Step107 output guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step107_output_guard"
    write_csv_rows(out_dir / "output_guard_report.csv", rows)
    write_csv_rows(out_dir / "output_guard_summary.csv", summary_rows(summary), ["metric", "value"])
    write_json(out_dir / "output_guard_report.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step107 output guard finished"
    write_log("logs/step107_output_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
