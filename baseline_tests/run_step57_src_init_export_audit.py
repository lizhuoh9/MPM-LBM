import os

from step57_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.src_init_export_audit import build_src_init_export_audit


FIELDS = [
    "check",
    "symbol",
    "expected_module",
    "actual_module",
    "module_import_pass",
    "symbol_resolve_pass",
    "pass",
    "error",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_src_init_export_audit(ROOT)
    if not summary["src_init_export_audit_pass"]:
        raise RuntimeError(f"Step 57 src.__init__ export audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step57_src_init_export_audit"
    write_csv_rows(out_dir / "src_init_export_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "src_init_export_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "src_init_export_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 57 src.__init__ export audit finished"
    write_log("logs/step57_src_init_export_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
