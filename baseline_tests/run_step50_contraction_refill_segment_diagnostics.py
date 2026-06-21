import os

from step50_common import ROOT, one_cycle_envelope_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "contraction_phase_count",
    "refill_phase_count",
    "contraction_rho_min",
    "contraction_rho_max",
    "refill_rho_min",
    "refill_rho_max",
    "contraction_active_cell_delta",
    "refill_active_cell_delta",
    "contraction_applied_cell_count_max",
    "refill_applied_cell_count_max",
    "contraction_max_applied_velocity_norm",
    "refill_max_applied_velocity_norm",
    "wall_velocity_cap_lbm",
    "contraction_bb_link_count_min",
    "refill_bb_link_count_min",
    "has_nan",
    "has_inf",
    "contraction_segment_pass",
    "refill_segment_pass",
    "segment_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_diagnostics import summarize_contraction_refill_segments

    rows, summary = summarize_contraction_refill_segments(one_cycle_envelope_rows())
    if not summary["segment_pass"]:
        raise RuntimeError(f"Step 50 contraction/refill segment diagnostics failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_contraction_refill_segment_diagnostics"
    write_csv_rows(out_dir / "contraction_refill_segment_diagnostics.csv", rows, FIELDS)
    write_json(out_dir / "contraction_refill_segment_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 contraction refill segment diagnostics finished"
    write_log("logs/step50_contraction_refill_segment_diagnostics.log", [marker, f"contraction_phase_count={summary['contraction_phase_count']}", f"refill_phase_count={summary['refill_phase_count']}"])
    print(f"contraction_phase_count={summary['contraction_phase_count']}")
    print(marker)


if __name__ == "__main__":
    main()
