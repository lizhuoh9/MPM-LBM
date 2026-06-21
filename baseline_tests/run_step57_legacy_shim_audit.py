import os

from step57_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.driver_support_legacy_shim_audit import build_driver_support_legacy_shim_audit


FIELDS = [
    "legacy_path",
    "canonical_path",
    "legacy_file_exists",
    "legacy_is_shim",
    "legacy_imports_canonical",
    "legacy_contains_implementation_body",
    "nonblank_line_count",
    "pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_driver_support_legacy_shim_audit(ROOT)
    if not summary["driver_support_legacy_shim_audit_pass"]:
        raise RuntimeError(f"Step 57 legacy shim audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step57_legacy_shim_audit"
    write_csv_rows(out_dir / "legacy_shim_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "legacy_shim_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "legacy_shim_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 57 legacy shim audit finished"
    write_log("logs/step57_legacy_shim_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
