import os

from step56_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.canonical_runtime_migration_audit import build_canonical_runtime_migration_audit


FIELDS = [
    "canonical_path",
    "legacy_path",
    "migration_status",
    "canonical_contains_real_implementation",
    "canonical_uses_legacy_getattr",
    "legacy_is_shim",
    "legacy_imports_canonical",
    "forbidden_reverse_dependency",
    "pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_canonical_runtime_migration_audit(ROOT)
    if not summary["canonical_runtime_migration_audit_pass"]:
        raise RuntimeError(f"Step 56 canonical runtime migration audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step56_canonical_runtime_migration_audit"
    write_csv_rows(out_dir / "canonical_runtime_migration_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "canonical_runtime_migration_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "canonical_runtime_migration_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 56 canonical runtime migration audit finished"
    write_log("logs/step56_canonical_runtime_migration_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
