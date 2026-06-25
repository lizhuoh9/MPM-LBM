import os

from step110_common import ROOT
from src.mpm_lbm.evidence.step109_common import summary_rows, write_csv_rows, write_json
from src.mpm_lbm.evidence.step112_common import write_log
from src.mpm_lbm.evidence.step112_output_guard import build_step112_output_guard


def main():
    os.chdir(ROOT)
    rows, summary = build_step112_output_guard(ROOT)
    if not summary["output_guard_pass"]:
        raise RuntimeError(f"Step112 output guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step112_output_guard"
    write_json(out_dir / "output_guard_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "output_guard_report.csv", rows)
    write_csv_rows(out_dir / "output_guard_summary.csv", summary_rows(summary), ["metric", "value"])
    marker = "[OK] Step112 output guard finished"
    write_log(ROOT, "logs/step112_output_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
