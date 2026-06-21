import os

from step50_common import ROOT, one_cycle_envelope_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "phase_sequence",
    "active_cell_count_phase0",
    "active_cell_count_phase035",
    "active_cell_count_phase0975",
    "active_cell_count_delta_phase0_to_phase035",
    "active_cell_count_delta_phase035_to_phase0975",
    "max_applied_velocity_phase0",
    "max_applied_velocity_phase0975",
    "max_applied_velocity_delta_phase0_to_phase0975",
    "progression_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_one_cycle_diagnostics import summarize_one_cycle_phase_progression

    rows, summary = summarize_one_cycle_phase_progression(one_cycle_envelope_rows())
    if not summary["phase_progression_pass"]:
        raise RuntimeError(f"Step 50 phase progression one-cycle diagnostics failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_phase_progression_one_cycle_diagnostics"
    write_csv_rows(out_dir / "phase_progression_one_cycle_diagnostics.csv", rows, FIELDS)
    write_json(out_dir / "phase_progression_one_cycle_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 phase progression one-cycle diagnostics finished"
    write_log("logs/step50_phase_progression_one_cycle_diagnostics.log", [marker, f"phase_count={summary['phase_count']}", f"phase_progression_pass={summary['phase_progression_pass']}"])
    print(f"phase_count={summary['phase_count']}")
    print(marker)


if __name__ == "__main__":
    main()
