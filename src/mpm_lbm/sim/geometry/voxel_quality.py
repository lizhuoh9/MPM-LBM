from collections import deque

import numpy as np


def analyze_voxel_occupancy(occupancy, metadata=None) -> dict:
    """
    Diagnostic-only voxel occupancy quality report for small fixtures.

    Empty occupancy is reported deterministically instead of repaired.
    """
    occ = np.asarray(occupancy)
    if occ.ndim != 3:
        raise ValueError("occupancy must be a 3D array")
    if not np.all(np.isfinite(occ)):
        raise ValueError("occupancy must be finite")

    mask = occ.astype(bool)
    shape = mask.shape
    occupied = np.argwhere(mask)
    occupied_count = int(len(occupied))
    occupied_fraction = float(occupied_count / mask.size)
    empty = occupied_count == 0

    if empty:
        bounds_min = np.array([-1, -1, -1], dtype=np.int64)
        bounds_max = np.array([-1, -1, -1], dtype=np.int64)
        bbox_size = np.array([0, 0, 0], dtype=np.int64)
        touches_domain_boundary = False
        component_count = 0
        largest_component_size = 0
        largest_component_fraction = 0.0
        surface_voxel_count = 0
        interior_voxel_count = 0
    else:
        bounds_min = occupied.min(axis=0)
        bounds_max = occupied.max(axis=0)
        bbox_size = bounds_max - bounds_min + 1
        touches_domain_boundary = bool(np.any(bounds_min == 0) or np.any(bounds_max == (np.asarray(shape) - 1)))
        components = _component_sizes(mask)
        component_count = int(len(components))
        largest_component_size = int(max(components)) if components else 0
        largest_component_fraction = float(largest_component_size / occupied_count)
        surface_voxel_count, interior_voxel_count = _surface_and_interior_counts(mask)

    return {
        "shape_x": int(shape[0]),
        "shape_y": int(shape[1]),
        "shape_z": int(shape[2]),
        "occupied_count": occupied_count,
        "occupied_fraction": occupied_fraction,
        "empty": bool(empty),
        "bounds_index_min_x": int(bounds_min[0]),
        "bounds_index_min_y": int(bounds_min[1]),
        "bounds_index_min_z": int(bounds_min[2]),
        "bounds_index_max_x": int(bounds_max[0]),
        "bounds_index_max_y": int(bounds_max[1]),
        "bounds_index_max_z": int(bounds_max[2]),
        "bbox_size_x": int(bbox_size[0]),
        "bbox_size_y": int(bbox_size[1]),
        "bbox_size_z": int(bbox_size[2]),
        "touches_domain_boundary": touches_domain_boundary,
        "connected_component_count": component_count,
        "largest_component_size": largest_component_size,
        "largest_component_fraction": largest_component_fraction,
        "surface_voxel_count": int(surface_voxel_count),
        "interior_voxel_count": int(interior_voxel_count),
        "stable": bool(not empty and component_count >= 1),
        "notes": "diagnostic voxel occupancy report",
    }


def _component_sizes(mask):
    visited = np.zeros(mask.shape, dtype=bool)
    sizes = []
    for start in np.argwhere(mask):
        start_key = tuple(int(v) for v in start)
        if visited[start_key]:
            continue
        queue = deque([start_key])
        visited[start_key] = True
        size = 0
        while queue:
            index = queue.popleft()
            size += 1
            for neighbor in _neighbors(index, mask.shape):
                if mask[neighbor] and not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)
        sizes.append(size)
    return sizes


def _surface_and_interior_counts(mask):
    surface_count = 0
    interior_count = 0
    for index_arr in np.argwhere(mask):
        index = tuple(int(v) for v in index_arr)
        if _is_surface_voxel(mask, index):
            surface_count += 1
        else:
            interior_count += 1
    return surface_count, interior_count


def _is_surface_voxel(mask, index):
    for neighbor in _neighbors(index, mask.shape, include_outside=True):
        if neighbor is None or not mask[neighbor]:
            return True
    return False


def _neighbors(index, shape, include_outside=False):
    i, j, k = index
    for di, dj, dk in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        ni, nj, nk = i + di, j + dj, k + dk
        if 0 <= ni < shape[0] and 0 <= nj < shape[1] and 0 <= nk < shape[2]:
            yield (ni, nj, nk)
        elif include_outside:
            yield None
