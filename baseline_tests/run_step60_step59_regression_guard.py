import os

from step60_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.step60_regression_guard import build_step60_step59_regression_guard


FIELDS = ["check", "pass", "details"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_step60_step59_regression_guard(ROOT)
    if not summary["step59_regression_guard_pass"]:
        raise RuntimeError(f"Step 60 Step 59 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step60_step59_regression_guard"
    write_csv_rows(out_dir / "step59_regression_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "step59_regression_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "step59_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 60 Step 59 regression guard finished"
    write_log("logs/step60_step59_regression_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
