import os

from step28_common import (
    ROOT,
    as_bool,
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
    "n_grid",
    "rho_min_delta",
    "rho_max_delta",
    "lbm_max_v_delta",
    "mpm_min_J_delta",
    "projected_mass_delta",
    "active_cell_count_delta",
    "bb_link_count_delta",
    "step27_source",
    "step28_source",
    "prefix_pass",
]


def main():
    os.chdir(ROOT)
    step27_rows = _step27_rows()
    step28_rows = read_csv_rows("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv")
    rows = [_prefix_row(row, step27_rows) for row in step28_rows]
    rows.sort(key=lambda row: (row["candidate_id"], row["reaction_transfer_mode"]))
    summary = {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["prefix_pass"])}
    if int(summary["row_count"]) != 4 or int(summary["pass_count"]) != 4:
        raise RuntimeError(f"Step 28 Step 27 prefix regression failed: {rows}")

    out_dir = ROOT / "outputs" / "step28_step27_prefix_regression"
    write_csv_rows(out_dir / "step27_prefix_regression.csv", rows, FIELDS)
    write_json(out_dir / "step27_prefix_regression.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 28 Step 27 prefix regression finished"
    write_log("logs/step28_step27_prefix_regression.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _step27_rows():
    rows = []
    for path in [
        "outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv",
        "outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv",
    ]:
        for row in read_csv_rows(path):
            if row["mode"] == "moving_boundary":
                rows.append((row, path))
    return {(row["candidate_id"], row["reaction_transfer_mode"]): (row, path) for row, path in rows}


def _prefix_row(step28_row, step27_rows):
    key = (step28_row["candidate_id"], step28_row["reaction_transfer_mode"])
    if key not in step27_rows:
        raise RuntimeError(f"missing Step 27 row for Step 28 prefix comparison: {key}")
    step27_row, step27_path = step27_rows[key]
    diagnostics_path = diagnostics_path_from_driver_row(step28_row)
    step5 = _step5_row(read_csv_rows(diagnostics_path))
    row = {
        "candidate_id": step28_row["candidate_id"],
        "geometry_type": step28_row["geometry_type"],
        "reaction_transfer_mode": step28_row["reaction_transfer_mode"],
        "n_grid": int(float(step28_row["n_grid"])),
        "rho_min_delta": float(step5["rho_min"]) - float(step27_row["rho_min_global"]),
        "rho_max_delta": float(step5["rho_max"]) - float(step27_row["rho_max_global"]),
        "lbm_max_v_delta": float(step5["lbm_max_v"]) - float(step27_row["lbm_max_v_global"]),
        "mpm_min_J_delta": float(step5["mpm_min_J"]) - float(step27_row["mpm_min_J_global"]),
        "projected_mass_delta": float(step5["projected_mass"]) - float(step27_row["projected_mass"]),
        "active_cell_count_delta": int(float(step5["active_cell_count"])) - int(float(step27_row["active_cell_count"])),
        "bb_link_count_delta": int(float(step5["bb_link_count"])) - int(float(step27_row["bb_link_count_max"])),
        "step27_source": step27_path,
        "step28_source": diagnostics_path,
    }
    row["prefix_pass"] = bool(
        as_bool(step28_row["stable"])
        and abs(row["rho_min_delta"]) <= 1.0e-5
        and abs(row["rho_max_delta"]) <= 1.0e-5
        and abs(row["lbm_max_v_delta"]) <= 1.0e-5
        and abs(row["mpm_min_J_delta"]) <= 1.0e-5
        and abs(row["projected_mass_delta"]) <= 5.0e-5
        and row["active_cell_count_delta"] == 0
        and row["bb_link_count_delta"] == 0
    )
    return row


def _step5_row(rows):
    for row in rows:
        if int(float(row["step"])) == 5:
            return row
    raise RuntimeError("missing Step 28 step=5 time-series row")


if __name__ == "__main__":
    main()
