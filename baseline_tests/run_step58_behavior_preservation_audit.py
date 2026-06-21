import os

from step58_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.fsidriver_behavior_preservation_audit import (
    build_fsidriver_behavior_preservation_audit,
)


FIELDS = ["check", "expected", "actual", "pass", "notes"]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_fsidriver_behavior_preservation_audit(ROOT)
    if not summary["fsidriver_behavior_preservation_audit_pass"]:
        raise RuntimeError(f"Step 58 behavior preservation audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step58_behavior_preservation_audit"
    write_csv_rows(out_dir / "behavior_preservation_audit.csv", rows, FIELDS)
    write_csv_rows(out_dir / "behavior_preservation_audit_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "behavior_preservation_audit.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 58 behavior preservation audit finished"
    write_log("logs/step58_behavior_preservation_audit.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
