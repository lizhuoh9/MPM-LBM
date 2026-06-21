import os

from step53_common import ROOT, STEP53_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log
from src.runtime_geometry_wall_velocity_support_scaling_audit import applied_wall_support_rows


FIELDS = [
    "metric",
    "applied_cell_count_32",
    "applied_cell_count_48",
    "applied_cell_count_ratio_48_vs_32",
    "applied_cell_count_growth_observed",
    "applied_cell_support_growth_pass",
    "applied_cell_fraction_32",
    "applied_cell_fraction_48",
    "applied_cell_fraction_ratio",
    "applied_cell_count_per_active_cell_32",
    "applied_cell_count_per_active_cell_48",
    "applied_cell_growth_is_physical_validation",
    "wall_support_growth_claim",
    "audit_pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = applied_wall_support_rows(ROOT, STEP53_CONFIG_PATH)
    if not summary["applied_wall_support_audit_pass"]:
        raise RuntimeError(f"Step 53 applied wall support audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step53_applied_wall_support_scaling_audit"
    write_csv_rows(out_dir / "applied_wall_support_scaling.csv", rows, FIELDS)
    write_csv_rows(out_dir / "applied_wall_support_scaling_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "applied_wall_support_scaling.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 53 applied wall support scaling audit finished"
    write_log("logs/step53_applied_wall_support_scaling_audit.log", [marker, f"applied_cell_count_ratio_48_vs_32={summary['applied_cell_count_ratio_48_vs_32']}"])
    print(marker)


if __name__ == "__main__":
    main()
