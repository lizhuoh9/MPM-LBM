import os

from step58_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.optional_bridge_audit import build_optional_bridge_audit


FIELDS = [
    "canonical_path",
    "canonical_module",
    "legacy_module",
    "symbol_count",
    "bridge_file_exists",
    "temporary_marker_present",
    "uses_legacy_getattr",
    "legacy_module_declared",
    "all_symbols_listed",
    "canonical_import_pass",
    "legacy_import_pass",
    "resolved_symbol_count",
    "same_object_symbol_count",
    "pass",
    "error",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_optional_bridge_audit(ROOT)
    if not summary["optional_bridge_audit_pass"]:
        raise RuntimeError(f"Step 58 optional bridge audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step58_optional_bridge_audit"
    write_csv_rows(out_dir / "optional_bridge_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "optional_bridge_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "optional_bridge_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 58 optional bridge audit finished"
    write_log("logs/step58_optional_bridge_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
