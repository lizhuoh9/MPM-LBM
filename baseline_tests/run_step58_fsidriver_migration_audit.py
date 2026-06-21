import os

from step58_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.fsidriver_migration_audit import build_fsidriver_migration_audit


FIELDS = [
    "canonical_path",
    "legacy_path",
    "migration_status",
    "canonical_path_exists",
    "legacy_path_exists",
    "canonical_contains_real_implementation",
    "canonical_has_forbidden_tokens",
    "canonical_forbidden_tokens",
    "canonical_imports_legacy_root",
    "legacy_is_shim",
    "legacy_imports_canonical",
    "forbidden_reverse_dependency",
    "pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_fsidriver_migration_audit(ROOT)
    if not summary["fsidriver_migration_audit_pass"]:
        raise RuntimeError(f"Step 58 FSIDriver migration audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step58_fsidriver_migration_audit"
    write_csv_rows(out_dir / "fsidriver_migration_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "fsidriver_migration_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "fsidriver_migration_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 58 FSIDriver migration audit finished"
    write_log("logs/step58_fsidriver_migration_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
