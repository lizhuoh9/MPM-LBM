import os

from step53_common import ROOT, STEP53_CONFIG_PATH, summary_rows, write_csv_rows, write_json, write_log
from src.runtime_geometry_wall_velocity_support_scaling_audit import phasewise_support_scaling_rows


SUMMARY_FIELDS = ["metric", "value"]
FIELDS = [
    "phase",
    "active_cell_count_32",
    "active_cell_count_48",
    "active_cell_count_ratio_48_vs_32",
    "active_cell_count_delta_48_minus_32",
    "applied_cell_count_32",
    "applied_cell_count_48",
    "applied_cell_count_ratio_48_vs_32",
    "applied_cell_count_delta_48_minus_32",
    "bb_link_count_32",
    "bb_link_count_48",
    "bb_link_count_ratio_48_vs_32",
    "bb_link_count_delta_48_minus_32",
    "projected_mass_32",
    "projected_mass_48",
    "projected_mass_delta_48_minus_32",
    "rho_min_32",
    "rho_min_48",
    "rho_max_32",
    "rho_max_48",
    "lbm_max_v_32",
    "lbm_max_v_48",
    "hydro_force_norm_32",
    "hydro_force_norm_48",
    "hydro_force_ratio_48_vs_32",
    "impulse_proxy_32",
    "impulse_proxy_48",
    "impulse_proxy_ratio_48_vs_32",
    "all_values_finite",
    "all_ratios_finite",
]


def main():
    os.chdir(ROOT)
    rows, summary = phasewise_support_scaling_rows(ROOT, STEP53_CONFIG_PATH)
    if not summary["phasewise_audit_pass"]:
        raise RuntimeError(f"Step 53 phasewise support scaling audit failed: {summary}")
    out_dir = ROOT / "outputs" / "step53_phasewise_support_scaling_audit"
    write_csv_rows(out_dir / "phasewise_support_scaling.csv", rows, FIELDS)
    write_csv_rows(out_dir / "phasewise_support_scaling_summary.csv", summary_rows(summary), SUMMARY_FIELDS)
    write_json(out_dir / "phasewise_support_scaling.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 53 phasewise support scaling audit finished"
    write_log("logs/step53_phasewise_support_scaling_audit.log", [marker, f"matched_phase_count={summary['matched_phase_count']}"])
    print(f"matched_phase_count={summary['matched_phase_count']}")
    print(marker)


if __name__ == "__main__":
    main()
