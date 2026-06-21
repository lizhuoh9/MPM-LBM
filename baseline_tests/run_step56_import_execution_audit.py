import os

from step56_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.import_execution_audit import build_import_execution_audit


FIELDS = [
    "canonical_module",
    "legacy_module",
    "symbol",
    "canonical_import_pass",
    "legacy_import_pass",
    "same_object",
    "pass",
    "error",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_import_execution_audit(ROOT)
    if not summary["import_execution_audit_pass"]:
        raise RuntimeError(f"Step 56 import execution audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step56_import_execution_audit"
    write_csv_rows(out_dir / "import_execution_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "import_execution_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "import_execution_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 56 import execution audit finished"
    write_log("logs/step56_import_execution_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
