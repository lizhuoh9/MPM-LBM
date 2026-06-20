import math

import numpy as np


GRID_FIELDS = [
    "grid_size",
    "region_id",
    "active_cell_count",
    "sample_point_count",
    "max_velocity_norm",
    "mean_velocity_norm",
    "max_displacement_norm",
    "coverage_pass",
    "finite_pass",
]


def summarize_motion_on_grids(points: np.ndarray, masks: dict[str, np.ndarray], motion_rows: list[dict], grid_sizes) -> list[dict]:
    pts = _as_points(points)
    rows = []
    tracked_regions = sorted({row["region_id"] for row in motion_rows})
    for grid_size in tuple(int(value) for value in grid_sizes):
        if grid_size <= 0:
            raise ValueError("grid_size must be positive")
        for region_id in tracked_regions:
            mask = np.asarray(masks[region_id], dtype=bool)
            selected = pts[mask]
            active_cell_count = _active_cell_count(selected, grid_size)
            region_motion = [row for row in motion_rows if row["region_id"] == region_id]
            row = {
                "grid_size": grid_size,
                "region_id": region_id,
                "active_cell_count": active_cell_count,
                "sample_point_count": int(len(selected)),
                "max_velocity_norm": max(float(item["velocity_norm_max"]) for item in region_motion),
                "mean_velocity_norm": float(np.mean([float(item["velocity_norm_mean"]) for item in region_motion])),
                "max_displacement_norm": max(float(item["displacement_norm_max"]) for item in region_motion),
            }
            row["finite_pass"] = _finite_grid_row(row)
            row["coverage_pass"] = bool(active_cell_count > 0 and row["sample_point_count"] > 0 and row["finite_pass"])
            rows.append(row)
    return rows


def summarize_motion_grid_rows(rows: list[dict]) -> dict:
    if not rows:
        return {"row_count": 0, "coverage_pass": False}
    return {
        "row_count": len(rows),
        "grid_size_count": len({int(row["grid_size"]) for row in rows}),
        "tracked_region_count": len({row["region_id"] for row in rows}),
        "min_active_cell_count": min(int(row["active_cell_count"]) for row in rows),
        "min_sample_point_count": min(int(row["sample_point_count"]) for row in rows),
        "max_velocity_norm": max(float(row["max_velocity_norm"]) for row in rows),
        "max_displacement_norm": max(float(row["max_displacement_norm"]) for row in rows),
        "finite_pass": all(bool(row["finite_pass"]) for row in rows),
        "coverage_pass": all(bool(row["coverage_pass"]) for row in rows),
    }


def assert_motion_grid_diagnostics(summary: dict) -> None:
    if not (
        int(summary.get("row_count", 0)) == 9
        and int(summary.get("grid_size_count", 0)) == 3
        and int(summary.get("tracked_region_count", 0)) == 3
        and int(summary.get("min_active_cell_count", 0)) > 0
        and bool(summary.get("finite_pass", False))
        and bool(summary.get("coverage_pass", False))
    ):
        raise RuntimeError(f"Step 33 motion grid diagnostics failed: {summary}")


def _active_cell_count(points: np.ndarray, grid_size: int) -> int:
    if len(points) == 0:
        return 0
    indices = np.floor(np.clip(points, 0.0, np.nextafter(1.0, 0.0)) * float(grid_size)).astype(np.int64)
    linear = indices[:, 0] * grid_size * grid_size + indices[:, 1] * grid_size + indices[:, 2]
    return int(len(np.unique(linear)))


def _finite_grid_row(row: dict) -> bool:
    return all(
        math.isfinite(float(row[field]))
        for field in (
            "active_cell_count",
            "sample_point_count",
            "max_velocity_norm",
            "mean_velocity_norm",
            "max_displacement_norm",
        )
    )


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array
