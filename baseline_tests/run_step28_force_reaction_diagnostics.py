import math
import os

from step28_common import (
    ROOT,
    diagnostics_path_from_driver_row,
    read_csv_rows,
    write_csv_rows,
    write_json,
    write_log,
)


FIELDS = [
    "candidate_id",
    "geometry_type",
    "reaction_transfer_mode",
    "row_count",
    "post_step_positive_rows",
    "hydro_force_max_norm_min",
    "hydro_force_max_norm_max",
    "hydro_force_max_norm_final",
    "max_grid_reaction_norm_min",
    "max_grid_reaction_norm_max",
    "max_grid_reaction_norm_final",
    "active_reaction_particle_count_min",
    "active_reaction_particle_count_max",
    "bb_link_count_min",
    "bb_link_count_max",
    "bb_max_correction_max",
    "finite_pass",
    "diagnostic_pass",
]


def main():
    os.chdir(ROOT)
    driver_rows = read_csv_rows("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv")
    rows = [_diagnostic_row(row) for row in driver_rows]
    rows.sort(key=lambda row: (row["candidate_id"], row["reaction_transfer_mode"]))
    summary = {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["diagnostic_pass"])}
    if int(summary["row_count"]) != 4 or int(summary["pass_count"]) != 4:
        raise RuntimeError(f"Step 28 force/reaction diagnostics failed: {rows}")

    out_dir = ROOT / "outputs" / "step28_force_reaction_diagnostics"
    write_csv_rows(out_dir / "force_reaction_diagnostics.csv", rows, FIELDS)
    write_json(out_dir / "force_reaction_diagnostics.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 28 force reaction diagnostics finished"
    write_log("logs/step28_force_reaction_diagnostics.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _diagnostic_row(driver_row):
    path = diagnostics_path_from_driver_row(driver_row)
    time_rows = read_csv_rows(path)
    post_rows = [row for row in time_rows if int(float(row["step"])) > 0]
    if not post_rows:
        raise RuntimeError(f"missing Step 28 post-step diagnostics: {path}")

    hydro_values = [float(row["hydro_force_max_norm"]) for row in post_rows]
    reaction_values = [float(row["max_grid_reaction_norm"]) for row in post_rows]
    active_counts = [int(float(row["active_reaction_particle_count"])) for row in post_rows]
    link_counts = [int(float(row["bb_link_count"])) for row in post_rows]
    correction_values = [float(row["bb_max_correction"]) for row in post_rows]
    finite_pass = _finite_time_series(time_rows)
    positive_rows = sum(
        1
        for row in post_rows
        if float(row["hydro_force_max_norm"]) > 0.0
        and float(row["max_grid_reaction_norm"]) >= 0.0
        and int(float(row["active_reaction_particle_count"])) > 0
        and int(float(row["bb_link_count"])) > 0
    )
    row = {
        "candidate_id": driver_row["candidate_id"],
        "geometry_type": driver_row["geometry_type"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "row_count": len(time_rows),
        "post_step_positive_rows": positive_rows,
        "hydro_force_max_norm_min": min(hydro_values),
        "hydro_force_max_norm_max": max(hydro_values),
        "hydro_force_max_norm_final": hydro_values[-1],
        "max_grid_reaction_norm_min": min(reaction_values),
        "max_grid_reaction_norm_max": max(reaction_values),
        "max_grid_reaction_norm_final": reaction_values[-1],
        "active_reaction_particle_count_min": min(active_counts),
        "active_reaction_particle_count_max": max(active_counts),
        "bb_link_count_min": min(link_counts),
        "bb_link_count_max": max(link_counts),
        "bb_max_correction_max": max(correction_values),
        "finite_pass": finite_pass,
    }
    row["diagnostic_pass"] = bool(
        row["row_count"] >= 10
        and row["post_step_positive_rows"] == len(post_rows)
        and row["hydro_force_max_norm_min"] > 0.0
        and row["hydro_force_max_norm_max"] > 0.0
        and math.isfinite(row["max_grid_reaction_norm_min"])
        and math.isfinite(row["max_grid_reaction_norm_max"])
        and row["active_reaction_particle_count_max"] > 0
        and row["bb_link_count_max"] > 0
        and math.isfinite(row["bb_max_correction_max"])
        and row["finite_pass"]
    )
    return row


def _finite_time_series(rows):
    fields = [
        "rho_min",
        "rho_max",
        "lbm_max_v",
        "mpm_min_J",
        "mpm_max_speed",
        "projected_mass",
        "cell_force_max_norm",
        "hydro_force_max_norm",
        "bb_max_correction",
        "max_grid_reaction_norm",
    ]
    for row in rows:
        for field in fields:
            if not math.isfinite(float(row[field])):
                return False
    return True


if __name__ == "__main__":
    main()
