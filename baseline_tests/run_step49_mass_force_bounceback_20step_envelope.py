import os

from step49_common import ROOT, twenty_step_envelope_rows, write_csv_rows, write_json, write_log


DIAGNOSTIC_FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "bb_link_count_min",
    "bb_max_correction_global",
    "hydro_force_max_norm_global",
    "max_applied_velocity_norm",
    "wall_velocity_cap_lbm",
    "has_nan",
    "has_inf",
    "envelope_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_20step_diagnostics import mass_force_bounceback_twenty_step_envelope

    rows, summary = mass_force_bounceback_twenty_step_envelope(twenty_step_envelope_rows())
    if not summary["envelope_pass"]:
        raise RuntimeError(f"Step 49 mass/force/bounce-back 20-step envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step49_mass_force_bounceback_20step_envelope"
    write_csv_rows(out_dir / "mass_force_bounceback_20step_envelope.csv", rows, DIAGNOSTIC_FIELDS)
    write_json(out_dir / "mass_force_bounceback_20step_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 49 mass force bounce-back 20-step envelope finished"
    write_log("logs/step49_mass_force_bounceback_20step_envelope.log", [marker, f"row_count={summary['row_count']}", f"envelope_pass_count={summary['envelope_pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
