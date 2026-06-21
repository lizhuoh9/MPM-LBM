import math


def compare_original_vs_runtime_projection(original_rows: list[dict], runtime_rows: list[dict]) -> list[dict]:
    original_by_key = _by_grid_phase(original_rows)
    rows = []
    for runtime in runtime_rows:
        key = (int(runtime["grid_size"]), float(runtime["phase"]))
        original = original_by_key[key]
        projected_mass_delta = abs(float(runtime["projected_mass"]) - float(original["projected_mass"]))
        active_cell_delta = abs(int(runtime["active_cell_count"]) - int(original["active_cell_count"]))
        bbox_delta = _bbox_delta(runtime, original)
        occupancy_changed = runtime["occupancy_hash"] != original["occupancy_hash"]
        is_rest = math.isclose(float(runtime["phase"]), 0.0, abs_tol=1.0e-12) or math.isclose(float(runtime["phase"]), 1.0, abs_tol=1.0e-12)
        close_to_original = bool(projected_mass_delta <= 1.0e-12 and active_cell_delta <= 1 and bbox_delta <= 1.0)
        projection_delta_nonzero = bool(occupancy_changed or active_cell_delta > 0 or bbox_delta > 0.0)
        rows.append(
            {
                "grid_size": int(runtime["grid_size"]),
                "phase": float(runtime["phase"]),
                "projected_mass_delta": float(projected_mass_delta),
                "active_cell_delta": float(active_cell_delta),
                "bbox_delta": float(bbox_delta),
                "occupancy_changed": bool(occupancy_changed),
                "is_rest_phase": bool(is_rest),
                "close_to_original": bool(close_to_original),
                "projection_delta_nonzero": bool(projection_delta_nonzero),
                "comparison_pass": bool(close_to_original if is_rest else math.isfinite(projected_mass_delta) and math.isfinite(bbox_delta)),
            }
        )
    return rows


def summarize_original_vs_runtime_projection(rows: list[dict]) -> dict:
    phase0 = [row for row in rows if math.isclose(float(row["phase"]), 0.0, abs_tol=1.0e-12)]
    phase1 = [row for row in rows if math.isclose(float(row["phase"]), 1.0, abs_tol=1.0e-12)]
    midcycle = [row for row in rows if not bool(row["is_rest_phase"])]
    return {
        "row_count": len(rows),
        "comparison_pass_count": sum(1 for row in rows if bool(row["comparison_pass"])),
        "comparison_pass": all(bool(row["comparison_pass"]) for row in rows),
        "phase0_close_to_original": all(bool(row["close_to_original"]) for row in phase0),
        "phase1_close_to_original": all(bool(row["close_to_original"]) for row in phase1),
        "midcycle_projection_delta_nonzero": any(bool(row["projection_delta_nonzero"]) for row in midcycle),
        "max_projected_mass_delta": max(float(row["projected_mass_delta"]) for row in rows) if rows else 0.0,
        "max_active_cell_delta": max(float(row["active_cell_delta"]) for row in rows) if rows else 0.0,
        "max_bbox_delta": max(float(row["bbox_delta"]) for row in rows) if rows else 0.0,
    }


def projection_phase_closure_rows(runtime_rows: list[dict]) -> list[dict]:
    by_key = _by_grid_phase(runtime_rows)
    grids = sorted({int(row["grid_size"]) for row in runtime_rows})
    rows = []
    for grid in grids:
        phase0 = by_key[(grid, 0.0)]
        phase1 = by_key[(grid, 1.0)]
        projected_mass_delta = abs(float(phase1["projected_mass"]) - float(phase0["projected_mass"]))
        active_cell_delta = abs(int(phase1["active_cell_count"]) - int(phase0["active_cell_count"]))
        bbox_delta = _bbox_delta(phase1, phase0)
        rows.append(
            {
                "grid_size": int(grid),
                "phase0_phase1_projected_mass_delta": float(projected_mass_delta),
                "phase0_phase1_active_cell_delta": int(active_cell_delta),
                "phase0_phase1_bbox_delta": float(bbox_delta),
                "occupancy_hash_equal": phase0["occupancy_hash"] == phase1["occupancy_hash"],
                "closure_pass": bool(projected_mass_delta <= 1.0e-8 and active_cell_delta <= 1 and bbox_delta <= 1.0),
            }
        )
    return rows


def summarize_projection_phase_closure(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "closure_pass_count": sum(1 for row in rows if bool(row["closure_pass"])),
        "closure_pass": all(bool(row["closure_pass"]) for row in rows),
        "max_projected_mass_delta": max(float(row["phase0_phase1_projected_mass_delta"]) for row in rows) if rows else 0.0,
        "max_active_cell_delta": max(int(row["phase0_phase1_active_cell_delta"]) for row in rows) if rows else 0,
        "max_bbox_delta": max(float(row["phase0_phase1_bbox_delta"]) for row in rows) if rows else 0.0,
    }


def compare_step44_projection_smoke(step44_rows: list[dict], step45_rows: list[dict]) -> list[dict]:
    step44_by_key = _by_grid_phase(step44_rows)
    rows = []
    for step45 in step45_rows:
        key = (int(step45["grid_size"]), float(step45["phase"]))
        step44 = step44_by_key[key]
        projected_mass_delta = abs(float(step45["projected_mass"]) - float(step44["projected_mass"]))
        active_cell_count_delta = abs(int(step45["active_cell_count"]) - int(step44["active_cell_count"]))
        solid_phi_min_delta = abs(float(step45["solid_phi_min"]) - float(step44["solid_phi_min"]))
        solid_phi_max_delta = abs(float(step45["solid_phi_max"]) - float(step44["solid_phi_max"]))
        rows.append(
            {
                "grid_size": int(step45["grid_size"]),
                "phase": float(step45["phase"]),
                "projected_mass_delta": float(projected_mass_delta),
                "active_cell_count_delta": float(active_cell_count_delta),
                "solid_phi_min_delta": float(solid_phi_min_delta),
                "solid_phi_max_delta": float(solid_phi_max_delta),
                "alignment_pass": bool(
                    projected_mass_delta <= 1.0e-6
                    and active_cell_count_delta <= 0
                    and solid_phi_min_delta <= 0.0
                    and solid_phi_max_delta <= 0.0
                ),
            }
        )
    return rows


def summarize_step44_projection_alignment(rows: list[dict]) -> dict:
    return {
        "row_count": len(rows),
        "alignment_pass_count": sum(1 for row in rows if bool(row["alignment_pass"])),
        "alignment_pass": all(bool(row["alignment_pass"]) for row in rows),
        "max_projected_mass_delta": max(float(row["projected_mass_delta"]) for row in rows) if rows else 0.0,
        "max_active_cell_count_delta": max(float(row["active_cell_count_delta"]) for row in rows) if rows else 0.0,
        "max_solid_phi_min_delta": max(float(row["solid_phi_min_delta"]) for row in rows) if rows else 0.0,
        "max_solid_phi_max_delta": max(float(row["solid_phi_max_delta"]) for row in rows) if rows else 0.0,
    }


def _by_grid_phase(rows: list[dict]) -> dict:
    return {(int(row["grid_size"]), float(row["phase"])): row for row in rows}


def _bbox_delta(left: dict, right: dict) -> float:
    total = 0.0
    for key in (
        "bbox_cell_min_x",
        "bbox_cell_min_y",
        "bbox_cell_min_z",
        "bbox_cell_max_x",
        "bbox_cell_max_y",
        "bbox_cell_max_z",
    ):
        total += (float(left[key]) - float(right[key])) ** 2
    return math.sqrt(total)
