import os

from step58_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.fsidriver_import_execution_audit import (
    build_fsidriver_import_execution_audit,
)


FIELDS = [
    "row_kind",
    "canonical_module",
    "legacy_module",
    "symbol",
    "comparison",
    "canonical_import_pass",
    "legacy_import_pass",
    "same_object",
    "equal_value",
    "pass",
    "error",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_fsidriver_import_execution_audit(ROOT)
    if not summary["fsidriver_import_execution_audit_pass"]:
        raise RuntimeError(f"Step 58 import execution audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step58_import_execution_audit"
    write_csv_rows(out_dir / "import_execution_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "import_execution_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "import_execution_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 58 import execution audit finished"
    write_log("logs/step58_import_execution_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
