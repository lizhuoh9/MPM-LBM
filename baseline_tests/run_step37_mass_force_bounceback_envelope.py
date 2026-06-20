import os

from step37_common import ROOT, fieldnames_from_rows, read_json, write_csv_rows, write_json, write_log


def main():
    os.chdir(ROOT)
    source_rows = read_json("outputs/step37_application_window_driver/application_window_results.json")["rows"]
    rows = [envelope_row(row) for row in source_rows]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["envelope_pass"]),
        "envelope_pass": all(row["envelope_pass"] for row in rows),
        "min_rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "max_rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "max_bb_correction_max": max(float(row["bb_max_correction_max"]) for row in rows),
        "max_hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in rows),
        "max_applied_velocity_norm": max(float(row["max_applied_velocity_norm"]) for row in rows),
    }
    if not summary["envelope_pass"]:
        raise RuntimeError(f"Step 37 mass/force/bounceback envelope failed: {summary}")

    out_dir = ROOT / "outputs" / "step37_mass_force_bounceback_envelope"
    write_csv_rows(out_dir / "mass_force_bounceback_envelope.csv", rows, fieldnames_from_rows(rows))
    write_json(out_dir / "mass_force_bounceback_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 37 mass force bounceback envelope finished"
    write_log("logs/step37_mass_force_bounceback_envelope.log", [marker, f"row_count={summary['row_count']}"])
    print(f"envelope_pass={summary['envelope_pass']}")
    print(marker)


def envelope_row(row):
    result = {
        "case": row["case"],
        "mode_class": row["mode_class"],
        "reaction_transfer_mode": row["reaction_transfer_mode"],
        "rho_min_global": float(row["rho_min_global"]),
        "rho_max_global": float(row["rho_max_global"]),
        "lbm_max_v_global": float(row["lbm_max_v_global"]),
        "mpm_min_J_global": float(row["mpm_min_J_global"]),
        "mpm_max_speed_global": float(row["mpm_max_speed_global"]),
        "projected_mass_min": float(row["projected_mass_min"]),
        "projected_mass_max": float(row["projected_mass_max"]),
        "hydro_force_max_norm": float(row["hydro_force_max_norm"]),
        "bb_link_count_min": int(row["bb_link_count_min"]),
        "bb_link_count_max": int(row["bb_link_count_max"]),
        "bb_max_correction_max": float(row["bb_max_correction_max"]),
        "max_grid_reaction_norm": float(row["max_grid_reaction_norm"]),
        "max_applied_velocity_norm": float(row["max_applied_velocity_norm"]),
        "wall_velocity_cap_lbm": float(row["wall_velocity_cap_lbm"]),
        "has_nan": bool(row["has_nan"]),
        "has_inf": bool(row["has_inf"]),
    }
    applied_ok = result["max_applied_velocity_norm"] <= result["wall_velocity_cap_lbm"] + 1.0e-12 if row["mode_class"] == "experimental" else result["max_applied_velocity_norm"] == 0.0
    result["envelope_pass"] = bool(
        result["rho_min_global"] > 0.95
        and result["rho_max_global"] < 1.05
        and result["lbm_max_v_global"] < 0.1
        and result["mpm_min_J_global"] > 0.0
        and result["projected_mass_min"] > 0.0
        and result["projected_mass_max"] > 0.0
        and result["bb_link_count_max"] > 0
        and result["bb_max_correction_max"] >= 0.0
        and result["hydro_force_max_norm"] >= 0.0
        and result["max_grid_reaction_norm"] >= 0.0
        and applied_ok
        and not result["has_nan"]
        and not result["has_inf"]
    )
    return result


if __name__ == "__main__":
    main()
