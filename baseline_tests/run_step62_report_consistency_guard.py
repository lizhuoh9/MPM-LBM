import os

from step62_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.report_consistency_guard import build_report_consistency_guard


FIELDS = [
    "step",
    "report_path",
    "artifact_path",
    "section",
    "metric",
    "report_value",
    "artifact_value",
    "delta",
    "tolerance",
    "pass",
    "notes",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_report_consistency_guard(ROOT)
    if not summary["report_consistency_guard_pass"]:
        raise RuntimeError(f"Step 62 report consistency guard failed: {summary}")
    out_dir = ROOT / "outputs" / "step62_report_consistency_guard"
    write_csv_rows(out_dir / "report_consistency_guard.csv", rows, FIELDS)
    write_csv_rows(out_dir / "report_consistency_guard_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "report_consistency_guard.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 62 report consistency guard finished"
    write_log("logs/step62_report_consistency_guard.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
