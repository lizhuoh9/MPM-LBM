import os

from step29_common import (
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
    "step28_source",
    "step29_source",
    "prefix_pass",
]


def main():
    os.chdir(ROOT)
    step28_rows = _step28_rows()
    step29_rows = read_csv_rows("outputs/step29_64_stability_driver/stability_driver_results.csv")
    rows = [_prefix_row(row, step28_rows) for row in step29_rows]
    rows.sort(key=lambda row: (row["candidate_id"], row["reaction_transfer_mode"]))
    summary = {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["prefix_pass"])}
    if int(summary["row_count"]) != 4 or int(summary["pass_count"]) != 4:
        raise RuntimeError(f"Step 29 Step 28 prefix regression failed: {rows}")

    out_dir = ROOT / "outputs" / "step29_step28_prefix_regression"
    write_csv_rows(out_dir / "step28_prefix_regression.csv", rows, FIELDS)
    write_json(out_dir / "step28_prefix_regression.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 29 Step 28 prefix regression finished"
    write_log("logs/step29_step28_prefix_regression.log", [marker, f"row_count={summary['row_count']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def _step28_rows():
    rows = read_csv_rows("outputs/step28_64_transfer_pair_driver/transfer_pair_driver_results.csv")
    return {(row["candidate_id"], row["reaction_transfer_mode"]): row for row in rows}


def _prefix_row(step29_row, step28_rows):
    key = (step29_row["candidate_id"], step29_row["reaction_transfer_mode"])
    if key not in step28_rows:
        raise RuntimeError(f"missing Step 28 row for Step 29 prefix comparison: {key}")
    step28_row = step28_rows[key]
    step28_path = diagnostics_path_from_driver_row(step28_row)
    step29_path = diagnostics_path_from_driver_row(step29_row)
    step28_step10 = _step_row(read_csv_rows(step28_path), 10)
    step29_step10 = _step_row(read_csv_rows(step29_path), 10)
    row = {
        "candidate_id": step29_row["candidate_id"],
        "geometry_type": step29_row["geometry_type"],
        "reaction_transfer_mode": step29_row["reaction_transfer_mode"],
        "n_grid": int(float(step29_row["n_grid"])),
        "rho_min_delta": float(step29_step10["rho_min"]) - float(step28_step10["rho_min"]),
        "rho_max_delta": float(step29_step10["rho_max"]) - float(step28_step10["rho_max"]),
        "lbm_max_v_delta": float(step29_step10["lbm_max_v"]) - float(step28_step10["lbm_max_v"]),
        "mpm_min_J_delta": float(step29_step10["mpm_min_J"]) - float(step28_step10["mpm_min_J"]),
        "projected_mass_delta": float(step29_step10["projected_mass"]) - float(step28_step10["projected_mass"]),
        "active_cell_count_delta": int(float(step29_step10["active_cell_count"]))
        - int(float(step28_step10["active_cell_count"])),
        "bb_link_count_delta": int(float(step29_step10["bb_link_count"])) - int(float(step28_step10["bb_link_count"])),
        "step28_source": step28_path,
        "step29_source": step29_path,
    }
    row["prefix_pass"] = bool(
        as_bool(step29_row["stable"])
        and abs(row["rho_min_delta"]) <= 1.0e-5
        and abs(row["rho_max_delta"]) <= 1.0e-5
        and abs(row["lbm_max_v_delta"]) <= 1.0e-5
        and abs(row["mpm_min_J_delta"]) <= 1.0e-5
        and abs(row["projected_mass_delta"]) <= 5.0e-5
        and row["active_cell_count_delta"] == 0
        and row["bb_link_count_delta"] == 0
    )
    return row


def _step_row(rows, step):
    for row in rows:
        if int(float(row["step"])) == int(step):
            return row
    raise RuntimeError(f"missing time-series row for step={step}")


if __name__ == "__main__":
    main()
