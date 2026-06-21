import os

from step53_common import ROOT, STEP53_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log
from src.runtime_geometry_wall_velocity_support_scaling_audit import active_cell_semantics_rows


FIELDS = [
    "metric",
    "active_cell_count_32",
    "active_cell_count_48",
    "active_cell_count_ratio",
    "active_cell_count_growth_observed",
    "active_cell_count_non_decreasing",
    "active_cell_count_used_as_grid_convergence_metric",
    "active_cell_count_growth_required_for_pass",
    "active_cell_growth_failure_is_step53_failure",
    "active_cell_semantics_status",
    "step54_link_area_allowed",
    "step54_block_reason",
    "grid_convergence_claim",
    "physical_validation_claim",
    "production_readiness_claim",
    "notes",
    "semantics_pass",
]
SUMMARY_FIELDS = ["metric", "value"]


def main():
    os.chdir(ROOT)
    rows, summary = active_cell_semantics_rows(ROOT, STEP53_CONFIG_PATH)
    if not summary["semantics_pass"]:
        raise RuntimeError(f"Step 53 active-cell semantics audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step53_active_cell_semantics_audit"
    write_csv_rows(out_dir / "active_cell_semantics.csv", rows, FIELDS)
    write_csv_rows(out_dir / "active_cell_semantics_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "active_cell_semantics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 53 active-cell semantics audit finished"
    write_log("logs/step53_active_cell_semantics_audit.log", [marker, f"active_cell_count_growth_observed={summary['active_cell_count_growth_observed']}"])
    print(marker)


if __name__ == "__main__":
    main()
