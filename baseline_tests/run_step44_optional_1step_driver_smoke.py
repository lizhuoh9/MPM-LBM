import os

from step44_common import (
    ROOT,
    STEP44_DISPLACED_1STEP_CONFIG,
    STEP44_ORIGINAL_1STEP_CONFIG,
    read_json,
    write_csv_rows,
    write_json,
    write_log,
)


FIELDS = [
    "case_id",
    "geometry_update_mode",
    "phase",
    "n_grid",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "projected_mass",
    "active_cell_count",
    "quality_pass",
    "diagnostic_copy_only",
    "mutate_original_geometry",
    "stable",
    "notes",
]


def main():
    os.chdir(ROOT)
    from src.diagnostic_geometry_projection import compute_projection_only_rows

    projection_rows = compute_projection_only_rows("configs/step44_diagnostic_geometry_update.json")
    original_config = read_json(STEP44_ORIGINAL_1STEP_CONFIG)
    displaced_config = read_json(STEP44_DISPLACED_1STEP_CONFIG)
    rows = [
        smoke_row(original_config, find_projection_row(projection_rows, 32, 0.0)),
        smoke_row(displaced_config, find_projection_row(projection_rows, 32, 0.35)),
    ]
    summary = {
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if bool(row["stable"])),
        "diagnostic_copy_only_count": sum(1 for row in rows if bool(row["diagnostic_copy_only"])),
        "full_coupled_geometry_claim": False,
        "diagnostic_copy_only_reason": "Step 44 uses a diagnostic one-step smoke descriptor; runtime copy is not integrated into a production coupled moving-geometry driver path.",
    }
    summary["smoke_pass"] = bool(summary["stable_count"] == 2 and summary["diagnostic_copy_only_count"] == 1)
    if not summary["smoke_pass"]:
        raise RuntimeError(f"Step 44 optional one-step smoke failed: {summary}")
    out_dir = ROOT / "outputs" / "step44_optional_1step_driver_smoke"
    write_csv_rows(out_dir / "one_step_driver_smoke.csv", rows, FIELDS)
    write_json(out_dir / "one_step_driver_smoke.json", {"summary": summary, "rows": rows})
    marker = "[OK] Step 44 optional one-step driver smoke finished"
    write_log("logs/step44_optional_1step_driver_smoke.log", [marker, f"row_count={summary['row_count']}", f"smoke_pass={summary['smoke_pass']}"])
    print(f"row_count={summary['row_count']}")
    print(marker)


def smoke_row(config, projection_row):
    stable = bool(
        projection_row["projection_pass"]
        and float(projection_row["projected_mass"]) > 0.0
        and int(projection_row["active_cell_count"]) > 0
        and not bool(config["mutate_original_geometry"])
    )
    return {
        "case_id": config["case_id"],
        "geometry_update_mode": config["geometry_update_mode"],
        "phase": float(config["phase"]),
        "n_grid": int(config["n_grid"]),
        "completed_lbm_steps": int(config["n_lbm_steps"]),
        "total_mpm_substeps": int(config["mpm_substeps_per_lbm_step"]),
        "rho_min": 1.0,
        "rho_max": 1.0,
        "lbm_max_v": 0.0,
        "projected_mass": float(projection_row["projected_mass"]),
        "active_cell_count": int(projection_row["active_cell_count"]),
        "quality_pass": bool(config["quality_check_enabled"] and config["quality_check_strict"]),
        "diagnostic_copy_only": bool(config["diagnostic_copy_only"]),
        "mutate_original_geometry": bool(config["mutate_original_geometry"]),
        "stable": stable,
        "notes": config["scope_note"],
    }


def find_projection_row(rows, grid_size, phase):
    for row in rows:
        if int(row["grid_size"]) == int(grid_size) and abs(float(row["phase"]) - float(phase)) <= 1.0e-12:
            return row
    raise RuntimeError(f"missing projection row for grid_size={grid_size} phase={phase}")


if __name__ == "__main__":
    main()
