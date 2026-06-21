import os

from step55_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.compatibility_shim_audit import build_compatibility_shim_audit


FIELDS = [
    "old_path",
    "new_path",
    "symbol",
    "old_path_exists",
    "new_path_exists",
    "old_symbol_present",
    "new_symbol_or_lazy_export_present",
    "source_text_check_only",
    "pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_compatibility_shim_audit(ROOT)
    if not summary["compatibility_shim_audit_pass"]:
        raise RuntimeError(f"Step 55 compatibility shim audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step55_compatibility_shim_audit"
    write_csv_rows(out_dir / "compatibility_shim_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "compatibility_shim_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "compatibility_shim_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 55 compatibility shim audit finished"
    write_log("logs/step55_compatibility_shim_audit.log", [marker, f"surface_count={summary['surface_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
