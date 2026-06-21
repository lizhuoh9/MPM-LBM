import os

from step47_common import ROOT, short_step_envelope_rows, write_csv_rows, write_json, write_log


PHASE_FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "phase_sequence",
    "active_cell_count_phase0",
    "active_cell_count_phase035",
    "active_cell_count_delta_phase0_to_phase035",
    "max_applied_velocity_phase0",
    "max_applied_velocity_phase035",
    "max_applied_velocity_delta_phase0_to_phase035",
    "progression_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_envelope_diagnostics import summarize_phase_progression

    rows, summary = summarize_phase_progression(short_step_envelope_rows())
    if not summary["phase_progression_pass"]:
        raise RuntimeError(f"Step 47 phase progression diagnostics failed: {summary}")
    out_dir = ROOT / "outputs" / "step47_phase_progression_diagnostics"
    write_csv_rows(out_dir / "phase_progression_diagnostics.csv", rows, PHASE_FIELDS)
    write_json(out_dir / "phase_progression_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 47 phase progression diagnostics finished"
    write_log("logs/step47_phase_progression_diagnostics.log", [marker, f"phase_count={summary['phase_count']}", f"phase_progression_pass={summary['phase_progression_pass']}"])
    print(f"phase_count={summary['phase_count']}")
    print(marker)


if __name__ == "__main__":
    main()
