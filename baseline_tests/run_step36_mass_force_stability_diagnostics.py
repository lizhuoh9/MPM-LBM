import os

from step36_common import ROOT, fieldnames_from_rows, read_csv_rows, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    source_rows = read_csv_rows("outputs/step36_experimental_application_smoke/experimental_application_results.csv")
    rows = [diagnostic_row(row) for row in source_rows]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["stability_pass"]),
        "stability_pass": all(row["stability_pass"] for row in rows),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "max_bb_correction": max(float(row["bb_max_correction_global"]) for row in rows),
        "max_lbm_population_update_count": max(int(row["lbm_population_update_count"]) for row in rows),
    }
    if not summary["stability_pass"]:
        raise RuntimeError(f"Step 36 mass/force stability failed: {summary}")

    out_dir = ROOT / "outputs" / "step36_mass_force_stability_diagnostics"
    write_csv_rows(out_dir / "mass_force_stability.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "mass_force_stability.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 36 mass force stability diagnostics finished"
    write_log(
        "logs/step36_mass_force_stability_diagnostics.log",
        [marker, f"row_count={summary['row_count']}", f"stability_pass={summary['stability_pass']}"],
    )
    print(f"stability_pass={summary['stability_pass']}")
    print(marker)


def diagnostic_row(row):
    result = {
        "case": row["case"],
        "n_grid": int(float(row["n_grid"])),
        "reaction_transfer_mode": row["reaction_transfer_mode"],
        "rho_min_global": float(row["rho_min_global"]),
        "rho_max_global": float(row["rho_max_global"]),
        "lbm_max_v_global": float(row["lbm_max_v_global"]),
        "mpm_min_J_global": float(row["mpm_min_J_global"]),
        "mpm_max_speed_global": float(row["mpm_max_speed_global"]),
        "hydro_force_max_norm": float(row["hydro_force_max_norm"]),
        "bb_link_count_max": int(float(row["bb_link_count_max"])),
        "bb_max_correction_global": float(row["bb_max_correction_global"]),
        "active_reaction_particle_count_max": int(float(row["active_reaction_particle_count_max"])),
        "applied_cell_count": int(float(row["applied_cell_count"])),
        "max_applied_velocity_norm": float(row["max_applied_velocity_norm"]),
        "wall_velocity_cap_lbm": float(row["wall_velocity_cap_lbm"]),
        "lbm_population_update_count": int(float(row["lbm_population_update_count"])),
    }
    result["stability_pass"] = bool(
        result["rho_min_global"] > 0.95
        and result["rho_max_global"] < 1.05
        and result["lbm_max_v_global"] < 0.1
        and result["mpm_min_J_global"] > 0.0
        and result["mpm_max_speed_global"] < 10.0
        and result["bb_link_count_max"] > 0
        and result["bb_max_correction_global"] > 0.0
        and result["active_reaction_particle_count_max"] > 0
        and result["applied_cell_count"] > 0
        and result["max_applied_velocity_norm"] <= result["wall_velocity_cap_lbm"] + 1.0e-12
        and result["lbm_population_update_count"] == 0
    )
    return result


if __name__ == "__main__":
    main()
