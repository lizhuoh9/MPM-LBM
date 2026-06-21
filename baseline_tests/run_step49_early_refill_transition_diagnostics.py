import os

from step49_common import ROOT, twenty_step_envelope_rows, write_csv_rows, write_json, write_log


TRANSITION_FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "transition_phases",
    "transition_phase_count",
    "rho_min_transition",
    "rho_max_transition",
    "active_cell_count_min_transition",
    "active_cell_count_max_transition",
    "active_cell_count_delta_transition",
    "applied_cell_count_max_transition",
    "max_applied_velocity_norm_transition",
    "wall_velocity_cap_lbm",
    "bb_link_count_min_transition",
    "has_nan",
    "has_inf",
    "transition_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_20step_diagnostics import summarize_early_refill_transition

    rows, summary = summarize_early_refill_transition(twenty_step_envelope_rows())
    if not summary["transition_pass"]:
        raise RuntimeError(f"Step 49 early refill transition diagnostics failed: {summary}")
    out_dir = ROOT / "outputs" / "step49_early_refill_transition_diagnostics"
    write_csv_rows(out_dir / "early_refill_transition_diagnostics.csv", rows, TRANSITION_FIELDS)
    write_json(out_dir / "early_refill_transition_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 49 early refill transition diagnostics finished"
    write_log("logs/step49_early_refill_transition_diagnostics.log", [marker, f"transition_phase_count={summary['transition_phase_count']}", f"transition_pass={summary['transition_pass']}"])
    print(f"transition_phase_count={summary['transition_phase_count']}")
    print(marker)


if __name__ == "__main__":
    main()
