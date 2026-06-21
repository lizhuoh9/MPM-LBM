import os

from step46_common import ROOT, coupling_smoke_rows, write_csv_rows, write_json, write_log


DIAGNOSTIC_FIELDS = [
    "row_name",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "bb_link_count",
    "bb_max_correction",
    "hydro_force_max_norm",
    "max_applied_velocity_norm",
    "wall_velocity_cap_lbm",
    "has_nan",
    "has_inf",
    "diagnostics_pass",
]


def main():
    os.chdir(ROOT)
    from src.runtime_geometry_wall_velocity_diagnostics import mass_force_bounceback_diagnostics

    rows, summary = mass_force_bounceback_diagnostics(coupling_smoke_rows())
    if not summary["diagnostics_pass"]:
        raise RuntimeError(f"Step 46 mass/force/bounce-back diagnostics failed: {summary}")
    out_dir = ROOT / "outputs" / "step46_mass_force_bounceback_diagnostics"
    write_csv_rows(out_dir / "mass_force_bounceback_diagnostics.csv", rows, DIAGNOSTIC_FIELDS)
    write_json(out_dir / "mass_force_bounceback_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 46 mass force bounce-back diagnostics finished"
    write_log("logs/step46_mass_force_bounceback_diagnostics.log", [marker, f"row_count={summary['row_count']}", f"diagnostics_pass_count={summary['diagnostics_pass_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


if __name__ == "__main__":
    main()
