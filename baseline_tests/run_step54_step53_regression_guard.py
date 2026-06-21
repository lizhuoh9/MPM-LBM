import os

from step54_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.repository_evidence_integrity_regression_guard import step53_regression_rows


FIELDS = ["check", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = step53_regression_rows(ROOT)
    if not summary["step53_regression_pass"]:
        raise RuntimeError(f"Step 54 Step 53 regression guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step54_step53_regression_guard"
    write_csv_rows(out_dir / "step53_regression_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "step53_regression_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "step53_regression_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 54 Step 53 regression guard finished"
    write_log("logs/step54_step53_regression_guard.log", [marker, f"pass_count={summary['pass_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
