import math
import os

from step29_common import ROOT, diagnostics_path_from_driver_row, read_csv_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "candidate_id",
    "geometry_type",
    "reaction_transfer_mode",
    "post_step_row_count",
    "hydro_force_min",
    "hydro_force_max",
    "hydro_force_final",
    "max_grid_reaction_norm_min",
    "max_grid_reaction_norm_max",
    "max_grid_reaction_norm_final",
    "active_reaction_particle_count_min",
    "active_reaction_particle_count_max",
    "bb_link_count_min",
    "bb_link_count_max",
    "bb_max_correction_max",
    "finite_pass",
    "positive_post_step_pass",
]


def main():
    os.chdir(ROOT)
    driver_rows = read_csv_rows("outputs/step29_64_stability_driver/stability_driver_results.csv")
    rows = [_envelope_row(row) for row in driver_rows]
    rows.sort(key=lambda row: (row["candidate_id"], row["reaction_transfer_mode"]))
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["finite_pass"] and row["positive_post_step_pass"]),
    }
    if int(summary["row_count"]) != 4 or int(summary["pass_count"]) != 4:
        raise RuntimeError(f"Step 29 force/reaction envelope failed: {rows}")

    out_dir = ROOT / "outputs" / "step29_force_reaction_envelope"
    write_csv_rows(out_dir / "force_reaction_envelope.csv", rows, FIELDS)
    write_json(out_dir / "force_reaction_envelope.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 29 force reaction envelope finished"
    write_log("logs/step29_force_reaction_envelope.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _envelope_row(driver_row):
    time_rows = read_csv_rows(diagnostics_path_from_driver_row(driver_row))
    post_rows = [row for row in time_rows if int(float(row["step"])) > 0]
    if not post_rows:
        raise RuntimeError(f"missing Step 29 post-step diagnostics: {driver_row}")
    hydro_values = [float(row["hydro_force_max_norm"]) for row in post_rows]
    reaction_values = [float(row["max_grid_reaction_norm"]) for row in post_rows]
    active_counts = [int(float(row["active_reaction_particle_count"])) for row in post_rows]
    link_counts = [int(float(row["bb_link_count"])) for row in post_rows]
    correction_values = [float(row["bb_max_correction"]) for row in post_rows]
    finite_pass = _finite_time_series(time_rows)
    positive_post_step_pass = all(
        float(row["hydro_force_max_norm"]) > 0.0
        and float(row["max_grid_reaction_norm"]) > 0.0
        and int(float(row["active_reaction_particle_count"])) > 0
        and int(float(row["bb_link_count"])) > 0
        for row in post_rows
    )
    return {
        "candidate_id": driver_row["candidate_id"],
        "geometry_type": driver_row["geometry_type"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "post_step_row_count": len(post_rows),
        "hydro_force_min": min(hydro_values),
        "hydro_force_max": max(hydro_values),
        "hydro_force_final": hydro_values[-1],
        "max_grid_reaction_norm_min": min(reaction_values),
        "max_grid_reaction_norm_max": max(reaction_values),
        "max_grid_reaction_norm_final": reaction_values[-1],
        "active_reaction_particle_count_min": min(active_counts),
        "active_reaction_particle_count_max": max(active_counts),
        "bb_link_count_min": min(link_counts),
        "bb_link_count_max": max(link_counts),
        "bb_max_correction_max": max(correction_values),
        "finite_pass": finite_pass,
        "positive_post_step_pass": bool(
            len(post_rows) >= 20
            and positive_post_step_pass
            and max(hydro_values) > 0.0
            and max(reaction_values) > 0.0
            and max(active_counts) > 0
            and min(link_counts) > 0
        ),
    }


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
