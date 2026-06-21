import math


def analyze_runtime_projection_quality(rows: list[dict], config) -> dict:
    phases = sorted({float(row["phase"]) for row in rows})
    grids = sorted({int(row["grid_size"]) for row in rows})
    row_count_pass = len(rows) == len(config.selected_phases) * len(config.grid_sizes)
    finite_pass = all(_finite_row(row) for row in rows)
    bounds_pass = all(
        int(row["active_cell_count"]) > 0
        and 0.0 <= float(row["solid_phi_min"]) <= float(row["solid_phi_max"]) <= 1.0
        and int(row["bbox_cell_min_x"]) <= int(row["bbox_cell_max_x"])
        and int(row["bbox_cell_min_y"]) <= int(row["bbox_cell_max_y"])
        and int(row["bbox_cell_min_z"]) <= int(row["bbox_cell_max_z"])
        for row in rows
    )
    active_cell_pass = all(int(row["active_cell_count"]) > 0 for row in rows)
    projected_mass_pass = all(float(row["projected_mass"]) > 0.0 for row in rows)
    solid_phi_bounds_pass = all(0.0 <= float(row["solid_phi_min"]) <= float(row["solid_phi_max"]) <= 1.0 for row in rows)
    phase_coverage_pass = phases == list(config.selected_phases)
    grid_coverage_pass = grids == list(config.grid_sizes)
    transient_only_pass = all(bool(row["transient_only"]) for row in rows)
    no_persistent_state_pass = all(
        not bool(row["persist_projected_state"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["apply_to_driver_state"])
        and not bool(row["apply_to_default_lbm_state"])
        and not bool(row["apply_to_default_mpm_state"])
        and not bool(row["apply_to_default_projection_state"])
        and not bool(row["update_dynamic_solid"])
        for row in rows
    )
    return {
        "row_count": len(rows),
        "row_count_pass": bool(row_count_pass),
        "finite_pass": bool(finite_pass),
        "bounds_pass": bool(bounds_pass),
        "active_cell_pass": bool(active_cell_pass),
        "projected_mass_pass": bool(projected_mass_pass),
        "solid_phi_bounds_pass": bool(solid_phi_bounds_pass),
        "phase_coverage_pass": bool(phase_coverage_pass),
        "grid_coverage_pass": bool(grid_coverage_pass),
        "transient_only_pass": bool(transient_only_pass),
        "no_persistent_state_pass": bool(no_persistent_state_pass),
        "quality_pass": bool(
            row_count_pass
            and finite_pass
            and bounds_pass
            and active_cell_pass
            and projected_mass_pass
            and solid_phi_bounds_pass
            and phase_coverage_pass
            and grid_coverage_pass
            and transient_only_pass
            and no_persistent_state_pass
        ),
    }


def _finite_row(row: dict) -> bool:
    excluded = {"source_kind", "occupancy_hash", "notes"}
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True
