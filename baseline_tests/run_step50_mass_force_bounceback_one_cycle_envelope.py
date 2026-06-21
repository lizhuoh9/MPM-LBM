import os

from step50_common import ROOT, one_cycle_envelope_rows, write_csv_rows, write_json, write_log


FIELDS = [
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
    from src.runtime_geometry_wall_velocity_one_cycle_diagnostics import mass_force_bounceback_one_cycle_envelope

    rows, summary = mass_force_bounceback_one_cycle_envelope(one_cycle_envelope_rows())
    if not summary["envelope_pass"]:
        raise RuntimeError(f"Step 50 mass force bounce-back one-cycle envelope failed: {summary}")
    out_dir = ROOT / "outputs" / "step50_mass_force_bounceback_one_cycle_envelope"
    write_csv_rows(out_dir / "mass_force_bounceback_one_cycle_envelope.csv", rows, FIELDS)
    write_json(out_dir / "mass_force_bounceback_one_cycle_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 50 mass force bounce-back one-cycle envelope finished"
    write_log("logs/step50_mass_force_bounceback_one_cycle_envelope.log", [marker, f"row_count={summary['row_count']}", f"envelope_pass={summary['envelope_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
