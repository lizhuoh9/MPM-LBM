import os

from step55_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.import_boundary_audit import build_import_boundary_audit


FIELDS = [
    "path",
    "forbidden_import_count",
    "forbidden_path_count",
    "forbidden_step_constant_count",
    "pass",
    "forbidden_import_hits",
    "forbidden_path_hits",
    "forbidden_step_hits",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_import_boundary_audit(ROOT)
    if not summary["import_boundary_audit_pass"]:
        raise RuntimeError(f"Step 55 import boundary audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step55_import_boundary_audit"
    write_csv_rows(out_dir / "import_boundary_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "import_boundary_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "import_boundary_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 55 import boundary audit finished"
    write_log("logs/step55_import_boundary_audit.log", [marker, f"scanned_sim_file_count={summary['scanned_sim_file_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
