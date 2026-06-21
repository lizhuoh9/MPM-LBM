import math

import numpy as np

from .diagnostic_geometry_update import (
    _canonical_phase,
    load_step44_inputs,
    selected_schedule_rows,
    write_csv_rows,
    write_json,
)
from .geometry_displacement_field import displacement_vectors_for_region


PROJECTION_FIELDS = [
    "grid_size",
    "phase",
    "sample_index",
    "projected_mass",
    "active_cell_count",
    "solid_phi_min",
    "solid_phi_max",
    "region_coverage",
    "has_nan",
    "has_inf",
    "diagnostic_only",
    "projection_pass",
    "notes",
]


def compute_projection_only_rows(config_path) -> list[dict]:
    inputs = load_step44_inputs(config_path)
    config = inputs["config"]
    rows = []
    for schedule_row in selected_schedule_rows(inputs):
        displaced_points, union_count = runtime_displaced_union_points(inputs, schedule_row)
        for grid_size in config.grid_sizes:
            rows.append(project_runtime_geometry_copy_to_grid(displaced_points, union_count, int(grid_size), schedule_row, config.diagnostic_only))
    return rows


def runtime_displaced_union_points(inputs, schedule_row):
    config = inputs["config"]
    points = np.asarray(inputs["points"], dtype=np.float64)
    masks = inputs["masks"]
    union_mask = np.zeros(len(points), dtype=bool)
    displaced = points.copy()
    for region_id in config.tracked_regions:
        mask = np.asarray(masks[region_id], dtype=bool)
        union_mask |= mask
        selected = points[mask]
        vectors = displacement_vectors_for_region(region_id, selected, inputs["geometry_config"], schedule_row)
        displaced[mask] = selected + vectors
    return displaced[union_mask].copy(), int(np.count_nonzero(union_mask))


def project_runtime_geometry_copy_to_grid(points, union_count: int, grid_size: int, schedule_row, diagnostic_only: bool) -> dict:
    pts = np.asarray(points, dtype=np.float64)
    has_nan = bool(np.isnan(pts).any())
    has_inf = bool(np.isinf(pts).any())
    clipped = np.clip(pts, 0.0, np.nextafter(1.0, 0.0))
    indices = np.floor(clipped * float(grid_size)).astype(np.int64)
    indices = np.clip(indices, 0, grid_size - 1)
    linear = indices[:, 0] * grid_size * grid_size + indices[:, 1] * grid_size + indices[:, 2]
    active_cell_count = int(len(np.unique(linear))) if len(linear) else 0
    projected_mass = float(len(pts)) / float(max(union_count, 1))
    solid_phi_min = 0.0
    solid_phi_max = 1.0 if active_cell_count > 0 else 0.0
    region_coverage = float(active_cell_count) / float(grid_size**3)
    projection_pass = bool(
        grid_size > 0
        and active_cell_count > 0
        and projected_mass > 0.0
        and 0.0 <= solid_phi_min <= solid_phi_max <= 1.0
        and not has_nan
        and not has_inf
        and diagnostic_only
        and math.isfinite(projected_mass)
        and math.isfinite(region_coverage)
    )
    return {
        "grid_size": int(grid_size),
        "phase": _canonical_phase(schedule_row["phase"]),
        "sample_index": int(schedule_row["sample_index"]),
        "projected_mass": projected_mass,
        "active_cell_count": active_cell_count,
        "solid_phi_min": solid_phi_min,
        "solid_phi_max": solid_phi_max,
        "region_coverage": region_coverage,
        "has_nan": has_nan,
        "has_inf": has_inf,
        "diagnostic_only": bool(diagnostic_only),
        "projection_pass": projection_pass,
        "notes": "Step 44 projection-only runtime copy diagnostic; no persistent LBM state update",
    }


def summarize_projection_only_rows(rows: list[dict]) -> dict:
    phases = sorted({float(row["phase"]) for row in rows})
    grids = sorted({int(row["grid_size"]) for row in rows})
    return {
        "row_count": len(rows),
        "grid_size_count": len(grids),
        "grid_sizes": grids,
        "phase_count": len(phases),
        "selected_phases": phases,
        "projection_pass_count": sum(1 for row in rows if bool(row["projection_pass"])),
        "min_projected_mass": min(float(row["projected_mass"]) for row in rows) if rows else 0.0,
        "min_active_cell_count": min(int(row["active_cell_count"]) for row in rows) if rows else 0,
        "max_solid_phi_max": max(float(row["solid_phi_max"]) for row in rows) if rows else 0.0,
        "has_nan_count": sum(1 for row in rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in rows if bool(row["has_inf"])),
        "projection_smoke_pass": bool(rows and all(bool(row["projection_pass"]) for row in rows)),
    }


def write_projection_only_rows(rows: list[dict], csv_path, json_path) -> None:
    write_csv_rows(csv_path, rows, PROJECTION_FIELDS)
    write_json(json_path, {"summary": summarize_projection_only_rows(rows), "rows": rows})
