import time


BYTES_PER_MB = 1024.0 * 1024.0
LBM_FLOATS_PER_CELL = 53
LBM_INT8_FIELDS_PER_CELL = 4
MPM_PARTICLE_FLOATS = 27
MPM_GRID_FLOATS_PER_NODE = 7


def _validate_positive_int(value, name):
    if int(value) != value or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def _validate_positive_number(value, name):
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _mb(num_bytes):
    return float(num_bytes) / BYTES_PER_MB


class PerformanceTimer:
    def __init__(self):
        self._starts = {}
        self._elapsed = {}

    def start(self, name: str):
        self._starts[name] = time.perf_counter()

    def stop(self, name: str):
        if name not in self._starts:
            raise KeyError(f"timer '{name}' was not started")
        elapsed = time.perf_counter() - self._starts.pop(name)
        self._elapsed[name] = self._elapsed.get(name, 0.0) + elapsed
        return elapsed

    def row(self) -> dict:
        return dict(sorted(self._elapsed.items()))


def estimate_lbm_memory_bytes(n_grid: int, dtype_bytes: int = 4) -> dict:
    n_grid = _validate_positive_int(n_grid, "n_grid")
    dtype_bytes = _validate_positive_int(dtype_bytes, "dtype_bytes")
    n_cells = n_grid**3
    float_bytes = n_cells * LBM_FLOATS_PER_CELL * dtype_bytes
    int8_bytes = n_cells * LBM_INT8_FIELDS_PER_CELL
    total_bytes = int(float_bytes + int8_bytes)
    return {
        "n_grid": n_grid,
        "n_cells": n_cells,
        "float_fields_per_cell": LBM_FLOATS_PER_CELL,
        "int8_fields_per_cell": LBM_INT8_FIELDS_PER_CELL,
        "float_bytes": int(float_bytes),
        "int8_bytes": int(int8_bytes),
        "lbm_estimated_bytes": total_bytes,
        "lbm_estimated_mb": _mb(total_bytes),
        "assumptions": (
            "Dense LBM lower-bound estimate; excludes Taichi runtime overhead, "
            "allocator overhead, scalar fields, and MRT matrices."
        ),
    }


def estimate_mpm_memory_bytes(n_grid: int, n_particles: int, dtype_bytes: int = 4) -> dict:
    n_grid = _validate_positive_int(n_grid, "n_grid")
    n_particles = _validate_positive_int(n_particles, "n_particles")
    dtype_bytes = _validate_positive_int(dtype_bytes, "dtype_bytes")
    n_cells = n_grid**3
    particle_bytes = int(n_particles * MPM_PARTICLE_FLOATS * dtype_bytes)
    grid_bytes = int(n_cells * MPM_GRID_FLOATS_PER_NODE * dtype_bytes)
    total_bytes = particle_bytes + grid_bytes
    return {
        "n_grid": n_grid,
        "n_cells": n_cells,
        "n_particles": n_particles,
        "particle_floats": MPM_PARTICLE_FLOATS,
        "grid_floats_per_node": MPM_GRID_FLOATS_PER_NODE,
        "mpm_particle_estimated_bytes": particle_bytes,
        "mpm_grid_estimated_bytes": grid_bytes,
        "mpm_estimated_bytes": total_bytes,
        "mpm_particle_estimated_mb": _mb(particle_bytes),
        "mpm_grid_estimated_mb": _mb(grid_bytes),
        "mpm_estimated_mb": _mb(total_bytes),
        "assumptions": (
            "MPM lower-bound estimate for particle state and grid_v/grid_m/grid_f_ext; "
            "excludes Taichi runtime and allocator overhead."
        ),
    }


def estimate_coupling_memory_bytes(n_grid: int, dtype_bytes: int = 4) -> dict:
    n_grid = _validate_positive_int(n_grid, "n_grid")
    dtype_bytes = _validate_positive_int(dtype_bytes, "dtype_bytes")
    _validate_positive_number(dtype_bytes, "dtype_bytes")
    return {
        "n_grid": n_grid,
        "n_cells": n_grid**3,
        "coupling_estimated_bytes": 0,
        "coupling_estimated_mb": 0.0,
        "assumptions": (
            "Projection fields are counted in the LBM estimate. Coupling scalar "
            "diagnostics are negligible compared with dense LBM/MPM grid fields."
        ),
    }


def estimate_total_memory_bytes(n_grid: int, n_particles: int, dtype_bytes: int = 4) -> dict:
    lbm = estimate_lbm_memory_bytes(n_grid, dtype_bytes)
    mpm = estimate_mpm_memory_bytes(n_grid, n_particles, dtype_bytes)
    coupling = estimate_coupling_memory_bytes(n_grid, dtype_bytes)
    total_bytes = (
        lbm["lbm_estimated_bytes"]
        + mpm["mpm_particle_estimated_bytes"]
        + mpm["mpm_grid_estimated_bytes"]
        + coupling["coupling_estimated_bytes"]
    )
    return {
        "n_grid": int(n_grid),
        "n_cells": int(n_grid) ** 3,
        "n_particles": int(n_particles),
        "lbm_estimated_bytes": lbm["lbm_estimated_bytes"],
        "mpm_particle_estimated_bytes": mpm["mpm_particle_estimated_bytes"],
        "mpm_grid_estimated_bytes": mpm["mpm_grid_estimated_bytes"],
        "coupling_estimated_bytes": coupling["coupling_estimated_bytes"],
        "total_estimated_bytes": int(total_bytes),
        "lbm_estimated_mb": lbm["lbm_estimated_mb"],
        "mpm_particle_estimated_mb": mpm["mpm_particle_estimated_mb"],
        "mpm_grid_estimated_mb": mpm["mpm_grid_estimated_mb"],
        "coupling_estimated_mb": coupling["coupling_estimated_mb"],
        "total_estimated_mb": _mb(total_bytes),
        "assumptions": "Lower-bound dense-field estimate; not measured GPU allocation.",
    }
