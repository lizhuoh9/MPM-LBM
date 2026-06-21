import os

from step59_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.geo_path_naming_audit import build_geo_path_naming_audit


FIELDS = [
    "n_grid",
    "expected_filename",
    "actual_filename",
    "geo_path",
    "output_dir_exists_before",
    "output_dir_exists_after",
    "pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_geo_path_naming_audit(ROOT)
    if not summary["geo_path_naming_audit_pass"]:
        raise RuntimeError(f"Step 59 geo path naming audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step59_geo_path_naming_audit"
    write_csv_rows(out_dir / "geo_path_naming_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "geo_path_naming_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "geo_path_naming_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 59 geo path naming audit finished"
    write_log("logs/step59_geo_path_naming_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
