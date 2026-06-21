import os

from step54_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.repository_test_strength_audit import build_repository_test_strength_audit


FIELDS = [
    "test_file",
    "step",
    "checks_file_existence",
    "checks_log_marker",
    "checks_report_text",
    "checks_committed_artifact_json",
    "checks_source_string",
    "reruns_runner",
    "reruns_solver",
    "validates_formula",
    "validates_numerical_benchmark",
    "test_strength_level",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_repository_test_strength_audit(ROOT)
    if not summary["test_strength_audit_pass"]:
        raise RuntimeError(f"Step 54 test strength audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step54_test_strength_audit"
    write_csv_rows(out_dir / "test_strength_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "test_strength_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "test_strength_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 54 test strength audit finished"
    write_log("logs/step54_test_strength_audit.log", [marker, f"audited_file_count={summary['audited_file_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
