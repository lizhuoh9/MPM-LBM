import os

from step27_common import ROOT, read_csv_rows, write_csv_rows, write_json, write_log


FIELDS = [
    "candidate_id",
    "geometry_type",
    "mode",
    "reaction_transfer_mode",
    "n_grid",
    "driver_projected_mass",
    "step26_projected_mass",
    "projected_mass_delta",
    "driver_active_cell_count",
    "step26_active_cell_count",
    "active_cell_count_delta",
    "alignment_pass",
]


def main():
    os.chdir(ROOT)
    step26_rows = _step26_projection_rows()
    driver_rows = []
    driver_rows.extend(read_csv_rows("outputs/step27_64_driver_mesh_feasibility/mesh_64_short_driver_results.csv"))
    driver_rows.extend(read_csv_rows("outputs/step27_64_driver_voxel_feasibility/voxel_64_short_driver_results.csv"))
    rows = [_alignment_row(row, step26_rows[row["candidate_id"]]) for row in driver_rows]
    rows.sort(key=lambda row: (row["candidate_id"], row["mode"], row["reaction_transfer_mode"]))
    summary = {"row_count": len(rows), "pass_count": sum(1 for row in rows if row["alignment_pass"]), "rows": rows}
    if int(summary["row_count"]) != 6 or int(summary["pass_count"]) != 6:
        raise RuntimeError(f"Step 27 driver/projection alignment failed: {summary}")

    out_dir = ROOT / "outputs" / "step27_driver_projection_alignment"
    write_csv_rows(out_dir / "driver_projection_alignment.csv", rows, FIELDS)
    write_json(out_dir / "driver_projection_alignment.json", summary)
    marker = "[OK] Step 27 driver projection alignment finished"
    write_log("logs/step27_driver_projection_alignment.log", [marker, f"row_count={len(rows)}", f"pass_count={summary['pass_count']}"])
    print(f"row_count={len(rows)}")
    print(marker)


def _step26_projection_rows():
    payload = _read_json("outputs/step26_projection_scale_diagnostics/projection_scale_results.json")
    return {
        row["candidate_id"]: row
        for row in payload["rows"]
        if int(row["n_grid"]) == 64
    }


def _alignment_row(driver_row, projection_row):
    mass_delta = float(driver_row["projected_mass"]) - float(projection_row["projected_mass"])
    active_delta = int(float(driver_row["active_cell_count"])) - int(float(projection_row["active_cell_count"]))
    row = {
        "candidate_id": driver_row["candidate_id"],
        "geometry_type": driver_row["geometry_type"],
        "mode": driver_row["mode"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "n_grid": int(float(driver_row["n_grid"])),
        "driver_projected_mass": float(driver_row["projected_mass"]),
        "step26_projected_mass": float(projection_row["projected_mass"]),
        "projected_mass_delta": mass_delta,
        "driver_active_cell_count": int(float(driver_row["active_cell_count"])),
        "step26_active_cell_count": int(float(projection_row["active_cell_count"])),
        "active_cell_count_delta": active_delta,
    }
    row["alignment_pass"] = bool(row["n_grid"] == 64 and abs(mass_delta) <= 5.0e-5 and abs(active_delta) <= 32)
    return row


def _read_json(path):
    import json

    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    main()
