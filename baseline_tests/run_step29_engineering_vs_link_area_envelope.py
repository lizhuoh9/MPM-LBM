import math
import os

from step29_common import ROOT, read_csv_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "candidate_id",
    "geometry_type",
    "rho_min_delta",
    "rho_max_delta",
    "lbm_max_v_delta",
    "mpm_min_J_delta",
    "projected_mass_delta",
    "hydro_force_max_norm_delta",
    "active_cell_count_delta",
    "bb_link_count_delta",
    "link_area_area_scale_final",
    "comparison_pass",
]


def main():
    os.chdir(ROOT)
    envelope_rows = read_csv_rows("outputs/step29_stability_envelope_summary/stability_envelope.csv")
    driver_rows = read_csv_rows("outputs/step29_64_stability_driver/stability_driver_results.csv")
    rows = _comparison_rows(envelope_rows, driver_rows)
    summary = {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["comparison_pass"])}
    if int(summary["row_count"]) != 2 or int(summary["pass_count"]) != 2:
        raise RuntimeError(f"Step 29 engineering/link-area envelope comparison failed: {rows}")

    out_dir = ROOT / "outputs" / "step29_engineering_vs_link_area_envelope"
    write_csv_rows(out_dir / "engineering_vs_link_area_envelope.csv", rows, FIELDS)
    write_json(out_dir / "engineering_vs_link_area_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 29 engineering vs link-area envelope finished"
    write_log("logs/step29_engineering_vs_link_area_envelope.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _comparison_rows(envelope_rows, driver_rows):
    by_candidate = {}
    for row in envelope_rows:
        by_candidate.setdefault(row["candidate_id"], {})[row["reaction_transfer_mode"]] = row
    driver_by_key = {(row["candidate_id"], row["reaction_transfer_mode"]): row for row in driver_rows}

    rows = []
    for candidate_id, pair in sorted(by_candidate.items()):
        engineering = pair.get("engineering")
        link_area = pair.get("link_area_experimental")
        if engineering is None or link_area is None:
            raise RuntimeError(f"missing Step 29 transfer pair for {candidate_id}")
        link_driver = driver_by_key[(candidate_id, "link_area_experimental")]
        row = {
            "candidate_id": candidate_id,
            "geometry_type": engineering["geometry_type"],
            "rho_min_delta": float(link_area["rho_min_observed"]) - float(engineering["rho_min_observed"]),
            "rho_max_delta": float(link_area["rho_max_observed"]) - float(engineering["rho_max_observed"]),
            "lbm_max_v_delta": float(link_area["lbm_max_v_observed"]) - float(engineering["lbm_max_v_observed"]),
            "mpm_min_J_delta": float(link_area["mpm_min_J_observed"]) - float(engineering["mpm_min_J_observed"]),
            "projected_mass_delta": float(link_area["projected_mass_max"]) - float(engineering["projected_mass_max"]),
            "hydro_force_max_norm_delta": float(link_area["hydro_force_max_norm_max"])
            - float(engineering["hydro_force_max_norm_max"]),
            "active_cell_count_delta": int(float(link_area["active_cell_count_max"]))
            - int(float(engineering["active_cell_count_max"])),
            "bb_link_count_delta": int(float(link_area["bb_link_count_max"])) - int(float(engineering["bb_link_count_max"])),
            "link_area_area_scale_final": float(link_driver["area_scale_final"]),
        }
        row["comparison_pass"] = bool(
            abs(row["rho_min_delta"]) <= 1.0e-3
            and abs(row["rho_max_delta"]) <= 1.0e-3
            and abs(row["lbm_max_v_delta"]) <= 1.0e-3
            and abs(row["mpm_min_J_delta"]) <= 1.0e-3
            and abs(row["projected_mass_delta"]) <= 1.0e-4
            and row["active_cell_count_delta"] == 0
            and abs(row["bb_link_count_delta"]) <= 512
            and math.isfinite(row["link_area_area_scale_final"])
            and 0.25 <= row["link_area_area_scale_final"] <= 2.0
        )
        rows.append(row)
    return rows


if __name__ == "__main__":
    main()
