from __future__ import annotations

import numpy as np


def official_point_like_displacement(
    initial_positions,
    current_positions,
    target_point_norm,
    nearest_count: int,
    scale_m: float,
    radius_norm: float | None = None,
) -> dict:
    initial = _as_points(initial_positions, "initial_positions")
    current = _as_points(current_positions, "current_positions")
    target = np.asarray(target_point_norm, dtype=np.float64)
    if target.shape != (3,) or not np.all(np.isfinite(target)):
        raise ValueError("target_point_norm must be a finite 3-vector")
    if initial.shape != current.shape:
        raise ValueError("initial_positions and current_positions must have the same shape")
    if nearest_count <= 0:
        raise ValueError("nearest_count must be positive")
    if scale_m <= 0.0:
        raise ValueError("scale_m must be positive")
    if radius_norm is not None and radius_norm <= 0.0:
        raise ValueError("radius_norm must be positive when provided")

    distances = np.linalg.norm(initial - target[None, :], axis=1)
    order = np.argsort(distances, kind="stable")
    if radius_norm is not None:
        selected = order[distances[order] <= float(radius_norm)]
        if len(selected) == 0:
            selected = order[: min(int(nearest_count), len(order))]
    else:
        selected = order[: min(int(nearest_count), len(order))]

    displacement_norm = current[selected] - initial[selected]
    displacement_m = np.mean(displacement_norm, axis=0) * float(scale_m)
    return {
        "selected_particle_count": int(len(selected)),
        "selected_particle_indices": [int(i) for i in selected.tolist()],
        "target_point_norm": [float(v) for v in target.tolist()],
        "nearest_distance_norm_min": float(np.min(distances[selected])) if len(selected) else float("nan"),
        "nearest_distance_norm_max": float(np.max(distances[selected])) if len(selected) else float("nan"),
        "official_point_like_total_displacement_m": float(np.linalg.norm(displacement_m)),
        "official_point_like_x_displacement_m": float(displacement_m[0]),
        "official_point_like_y_displacement_m": float(displacement_m[1]),
        "official_point_like_z_displacement_m": float(displacement_m[2]),
        "monitor_is_direct_fluent_equivalent": False,
        "monitor_scope": "nearest-particle proxy for Fluent structural point surface displacement",
    }


def _as_points(values, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"{name} must have shape (n, 3)")
    if len(array) == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be finite")
    return array
