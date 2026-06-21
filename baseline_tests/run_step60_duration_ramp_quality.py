import os

from step60_common import ROOT, summary_rows, write_csv_rows, write_json, write_log
from src.mpm_lbm.evidence.canonical_driver_duration_ramp_audit import (
    build_canonical_driver_duration_ramp_audit,
)


FIELDS = [
    "row_name",
    "coupling_mode",
    "reaction_transfer_mode",
    "driver_run_called",
    "stable",
    "runtime_warning",
    "canonical_driver_module",
    "legacy_driver_module_used_as_implementation",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "diagnostics_row_count",
    "rho_min_min",
    "rho_max_max",
    "lbm_max_v_max",
    "mpm_min_J_min",
    "elapsed_seconds",
    "has_nan",
    "has_inf",
    "pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = build_canonical_driver_duration_ramp_audit(ROOT)
    if not summary["duration_ramp_audit_pass"]:
        raise RuntimeError(f"Step 60 duration ramp quality failed: {summary}")
    out_dir = ROOT / "outputs" / "step60_duration_ramp_quality"
    write_csv_rows(out_dir / "duration_ramp_quality.csv", rows, FIELDS)
    write_csv_rows(out_dir / "duration_ramp_quality_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "duration_ramp_quality.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 60 duration ramp quality finished"
    write_log("logs/step60_duration_ramp_quality.log", [marker, f"row_count={summary['row_count']}"])
    print(marker)


if __name__ == "__main__":
    main()
