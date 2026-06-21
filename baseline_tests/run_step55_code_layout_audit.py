import os

from step55_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.code_layout_audit import build_code_layout_audit


FIELDS = ["check", "path", "category", "pass", "value", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_code_layout_audit(ROOT)
    if not summary["code_layout_audit_pass"]:
        raise RuntimeError(f"Step 55 code layout audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step55_code_layout_audit"
    write_csv_rows(out_dir / "code_layout_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "code_layout_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "code_layout_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 55 code layout audit finished"
    write_log("logs/step55_code_layout_audit.log", [marker, f"root_src_file_count={summary['root_src_file_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
