import math
import os

from step28_common import ROOT, as_bool, read_csv_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "candidate_id",
    "geometry_type",
    "n_grid",
    "engineering_rho_min",
    "link_area_rho_min",
    "rho_min_delta",
    "engineering_rho_max",
    "link_area_rho_max",
    "rho_max_delta",
    "engineering_lbm_max_v",
    "link_area_lbm_max_v",
    "lbm_max_v_delta",
    "engineering_mpm_min_J",
    "link_area_mpm_min_J",
    "mpm_min_J_delta",
    "engineering_projected_mass",
    "link_area_projected_mass",
    "projected_mass_delta",
    "engineering_hydro_force_max_norm",
    "link_area_hydro_force_max_norm",
    "hydro_force_max_norm_delta",
    "link_area_area_scale_final",
    "comparison_pass",
]


def main():
    os.chdir(ROOT)
    rows = read_csv_rows("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv")
    comparison_rows = _comparison_rows(rows)
    summary = {"row_count": len(comparison_rows), "pass_count": sum(1 for row in comparison_rows if row["comparison_pass"])}
    if int(summary["row_count"]) != 2 or int(summary["pass_count"]) != 2:
        raise RuntimeError(f"Step 28 engineering/link-area comparison failed: {comparison_rows}")

    out_dir = ROOT / "outputs" / "step28_engineering_vs_link_area_comparison"
    write_csv_rows(out_dir / "engineering_vs_link_area.csv", comparison_rows, FIELDS)
    write_json(out_dir / "engineering_vs_link_area.json", {"summary": summary, "rows": comparison_rows})
    marker = "[OK] Step 28 engineering vs link-area comparison finished"
    write_log("logs/step28_engineering_vs_link_area_comparison.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _comparison_rows(rows):
    by_candidate = {}
    for row in rows:
        by_candidate.setdefault(row["candidate_id"], {})[row["reaction_transfer_mode"]] = row

    comparison_rows = []
    for candidate_id, pair in sorted(by_candidate.items()):
        engineering = pair.get("engineering")
        link_area = pair.get("link_area_experimental")
        if engineering is None or link_area is None:
            raise RuntimeError(f"missing Step 28 transfer pair for {candidate_id}")
        row = {
            "candidate_id": candidate_id,
            "geometry_type": engineering["geometry_type"],
            "n_grid": int(float(engineering["n_grid"])),
            "engineering_rho_min": float(engineering["rho_min_global"]),
            "link_area_rho_min": float(link_area["rho_min_global"]),
            "engineering_rho_max": float(engineering["rho_max_global"]),
            "link_area_rho_max": float(link_area["rho_max_global"]),
            "engineering_lbm_max_v": float(engineering["lbm_max_v_global"]),
            "link_area_lbm_max_v": float(link_area["lbm_max_v_global"]),
            "engineering_mpm_min_J": float(engineering["mpm_min_J_global"]),
            "link_area_mpm_min_J": float(link_area["mpm_min_J_global"]),
            "engineering_projected_mass": float(engineering["projected_mass"]),
            "link_area_projected_mass": float(link_area["projected_mass"]),
            "engineering_hydro_force_max_norm": float(engineering["hydro_force_max_norm"]),
            "link_area_hydro_force_max_norm": float(link_area["hydro_force_max_norm"]),
            "link_area_area_scale_final": float(link_area["area_scale_final"]),
        }
        row["rho_min_delta"] = row["link_area_rho_min"] - row["engineering_rho_min"]
        row["rho_max_delta"] = row["link_area_rho_max"] - row["engineering_rho_max"]
        row["lbm_max_v_delta"] = row["link_area_lbm_max_v"] - row["engineering_lbm_max_v"]
        row["mpm_min_J_delta"] = row["link_area_mpm_min_J"] - row["engineering_mpm_min_J"]
        row["projected_mass_delta"] = row["link_area_projected_mass"] - row["engineering_projected_mass"]
        row["hydro_force_max_norm_delta"] = (
            row["link_area_hydro_force_max_norm"] - row["engineering_hydro_force_max_norm"]
        )
        row["comparison_pass"] = bool(
            as_bool(engineering["stable"])
            and as_bool(link_area["stable"])
            and abs(row["rho_min_delta"]) <= 5.0e-4
            and abs(row["rho_max_delta"]) <= 5.0e-4
            and abs(row["lbm_max_v_delta"]) <= 5.0e-4
            and abs(row["mpm_min_J_delta"]) <= 5.0e-4
            and abs(row["projected_mass_delta"]) <= 5.0e-5
            and math.isfinite(row["link_area_area_scale_final"])
            and 0.25 <= row["link_area_area_scale_final"] <= 2.0
        )
        comparison_rows.append(row)
    return comparison_rows


if __name__ == "__main__":
    main()
