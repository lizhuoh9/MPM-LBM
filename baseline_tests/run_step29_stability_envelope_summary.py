import os

from step29_common import ROOT, diagnostics_path_from_driver_row, read_csv_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "candidate_id",
    "geometry_type",
    "reaction_transfer_mode",
    "diagnostic_row_count",
    "step_min",
    "step_max",
    "rho_min_observed",
    "rho_max_observed",
    "lbm_max_v_observed",
    "mpm_min_J_observed",
    "mpm_max_speed_observed",
    "projected_mass_min",
    "projected_mass_max",
    "active_cell_count_min",
    "active_cell_count_max",
    "hydro_force_max_norm_max",
    "bb_link_count_min",
    "bb_link_count_max",
    "stable_envelope_pass",
]


def main():
    os.chdir(ROOT)
    driver_rows = read_csv_rows("outputs/step29_64_stability_driver/stability_driver_results.csv")
    rows = [_envelope_row(row) for row in driver_rows]
    rows.sort(key=lambda row: (row["candidate_id"], row["reaction_transfer_mode"]))
    summary = {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["stable_envelope_pass"])}
    if int(summary["row_count"]) != 4 or int(summary["pass_count"]) != 4:
        raise RuntimeError(f"Step 29 stability envelope summary failed: {rows}")

    out_dir = ROOT / "outputs" / "step29_stability_envelope_summary"
    write_csv_rows(out_dir / "stability_envelope.csv", rows, FIELDS)
    write_json(out_dir / "stability_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 29 stability envelope summary finished"
    write_log("logs/step29_stability_envelope_summary.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _envelope_row(driver_row):
    time_rows = read_csv_rows(diagnostics_path_from_driver_row(driver_row))
    post_rows = [row for row in time_rows if int(float(row["step"])) > 0]
    if not post_rows:
        raise RuntimeError(f"missing Step 29 post-step rows: {driver_row}")
    steps = [int(float(row["step"])) for row in time_rows]
    row = {
        "candidate_id": driver_row["candidate_id"],
        "geometry_type": driver_row["geometry_type"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "diagnostic_row_count": len(time_rows),
        "step_min": min(steps),
        "step_max": max(steps),
        "rho_min_observed": min(float(item["rho_min"]) for item in time_rows),
        "rho_max_observed": max(float(item["rho_max"]) for item in time_rows),
        "lbm_max_v_observed": max(float(item["lbm_max_v"]) for item in time_rows),
        "mpm_min_J_observed": min(float(item["mpm_min_J"]) for item in time_rows),
        "mpm_max_speed_observed": max(float(item["mpm_max_speed"]) for item in time_rows),
        "projected_mass_min": min(float(item["projected_mass"]) for item in post_rows),
        "projected_mass_max": max(float(item["projected_mass"]) for item in post_rows),
        "active_cell_count_min": min(int(float(item["active_cell_count"])) for item in post_rows),
        "active_cell_count_max": max(int(float(item["active_cell_count"])) for item in post_rows),
        "hydro_force_max_norm_max": max(float(item["hydro_force_max_norm"]) for item in post_rows),
        "bb_link_count_min": min(int(float(item["bb_link_count"])) for item in post_rows),
        "bb_link_count_max": max(int(float(item["bb_link_count"])) for item in post_rows),
    }
    row["stable_envelope_pass"] = bool(
        row["diagnostic_row_count"] >= 21
        and row["step_min"] == 0
        and row["step_max"] == 20
        and row["rho_min_observed"] > 0.95
        and row["rho_max_observed"] < 1.05
        and row["lbm_max_v_observed"] < 0.1
        and row["mpm_min_J_observed"] > 0.0
        and row["mpm_max_speed_observed"] < 10.0
        and row["projected_mass_min"] > 0.0
        and row["active_cell_count_min"] > 0
        and row["hydro_force_max_norm_max"] > 0.0
        and row["bb_link_count_min"] > 0
    )
    return row


if __name__ == "__main__":
    main()
