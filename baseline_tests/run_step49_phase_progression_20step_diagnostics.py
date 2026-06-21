import os

from step49_common import ROOT, twenty_step_envelope_rows, write_csv_rows, write_json, write_log


PHASE_FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "phase_sequence",
    "active_cell_count_phase0",
    "active_cell_count_phase035",
    "active_cell_count_delta_phase0_to_phase035",
    "max_applied_velocity_phase0",
    "max_applied_velocity_phase05",
    "max_applied_velocity_delta_phase0_to_phase05",
    "progression_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_20step_diagnostics import summarize_twenty_step_phase_progression

    rows, summary = summarize_twenty_step_phase_progression(twenty_step_envelope_rows())
    if not summary["phase_progression_pass"]:
        raise RuntimeError(f"Step 49 phase progression 20-step diagnostics failed: {summary}")
    out_dir = ROOT / "outputs" / "step49_phase_progression_20step_diagnostics"
    write_csv_rows(out_dir / "phase_progression_20step_diagnostics.csv", rows, PHASE_FIELDS)
    write_json(out_dir / "phase_progression_20step_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 49 phase progression 20-step diagnostics finished"
    write_log("logs/step49_phase_progression_20step_diagnostics.log", [marker, f"phase_count={summary['phase_count']}", f"phase_progression_pass={summary['phase_progression_pass']}"])
    print(f"phase_count={summary['phase_count']}")
    print(marker)


if __name__ == "__main__":
    main()
