import json
import os
import time

import numpy as np

from src import FSIDriver3D, FSIDriverConfig
from src.performance import estimate_total_memory_bytes
from src.run_utils import save_csv_rows


RESULT_FIELDS = [
    "mode",
    "geometry_type",
    "stable",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "total_mpm_substeps",
    "target_u_lbm_x",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "projection_zone_ux_final",
    "solid_mean_vx_final",
    "active_cell_count",
    "projected_mass",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
    "estimated_memory_mb",
    "total_time_sec",
    "steps_per_sec",
    "notes",
]


def load_driver_config(root, relative_path):
    return FSIDriverConfig.from_json(os.path.join(root, relative_path))


def _final_row_to_result(config, final, timing, notes):
    total_time = float(timing["total_time"])
    memory = estimate_total_memory_bytes(config.n_grid, config.n_particles)
    return {
        "mode": config.coupling_mode,
        "geometry_type": config.geometry_type,
        "stable": True,
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "total_mpm_substeps": int(config.n_lbm_steps * config.mpm_substeps_per_lbm_step),
        "target_u_lbm_x": float(config.target_u_lbm[0]),
        "rho_min": float(final["rho_min"]),
        "rho_max": float(final["rho_max"]),
        "lbm_max_v": float(final["lbm_max_v"]),
        "mpm_min_J": float(final["mpm_min_J"]),
        "mpm_max_speed": float(final["mpm_max_speed"]),
        "projection_zone_ux_final": float(final["projection_zone_fluid_mean_ux"]),
        "solid_mean_vx_final": float(final["solid_mean_vx_norm"]),
        "active_cell_count": int(final["active_cell_count"]),
        "projected_mass": float(final["projected_mass"]),
        "cell_force_max_norm": float(final["cell_force_max_norm"]),
        "hydro_force_max_norm": float(final["hydro_force_max_norm"]),
        "bb_link_count": int(final["bb_link_count"]),
        "active_reaction_particle_count": int(final["active_reaction_particle_count"]),
        "max_grid_reaction_norm": float(final["max_grid_reaction_norm"]),
        "estimated_memory_mb": float(memory["total_estimated_mb"]),
        "total_time_sec": total_time,
        "steps_per_sec": float(config.n_lbm_steps / total_time) if total_time > 0.0 else 0.0,
        "notes": notes,
    }


def run_config(root, config_path, out_dir, notes):
    config = load_driver_config(root, config_path)
    driver = FSIDriver3D(config, out_dir)
    diagnostics = driver.run()
    final = diagnostics[-1]
    timing = driver.performance_row()
    return _final_row_to_result(config, final, timing, notes)


def validate_rows(rows, required_modes, expected_grid, expected_particles_by_mode=None):
    by_mode = {row["mode"]: row for row in rows}
    if set(by_mode) != set(required_modes):
        raise RuntimeError(f"expected modes {required_modes}, got {sorted(by_mode)}")

    for row in rows:
        numeric = [value for key, value in row.items() if key not in ("mode", "geometry_type", "stable", "notes")]
        if not np.all(np.isfinite(numeric)):
            raise RuntimeError(f"{row['mode']} result contains NaN or Inf")
        if not row["stable"]:
            raise RuntimeError(f"{row['mode']} result is unstable")
        if int(row["n_grid"]) != int(expected_grid):
            raise RuntimeError(f"{row['mode']} n_grid mismatch: {row['n_grid']} != {expected_grid}")
        if expected_particles_by_mode is not None:
            expected_particles = int(expected_particles_by_mode[row["mode"]])
            if int(row["n_particles"]) != expected_particles:
                raise RuntimeError(f"{row['mode']} n_particles mismatch")
        if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
            raise RuntimeError(f"{row['mode']} rho outside accepted range")
        if float(row["lbm_max_v"]) >= 0.1:
            raise RuntimeError(f"{row['mode']} lbm_max_v exceeded threshold")
        if float(row["mpm_min_J"]) <= 0.0:
            raise RuntimeError(f"{row['mode']} mpm_min_J became non-positive")
        if float(row["mpm_max_speed"]) >= 10.0:
            raise RuntimeError(f"{row['mode']} mpm_max_speed exceeded threshold")
        if float(row["total_time_sec"]) <= 0.0:
            raise RuntimeError(f"{row['mode']} total_time_sec must be positive")

    if "penalty" in by_mode and float(by_mode["penalty"]["cell_force_max_norm"]) <= 0.0:
        raise RuntimeError("penalty mode should have nonzero cell_force")
    if "moving_boundary" in by_mode:
        moving = by_mode["moving_boundary"]
        if float(moving["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("moving_boundary mode should keep cell_force zero")
        if int(moving["bb_link_count"]) <= 0:
            raise RuntimeError("moving_boundary mode should have bounce-back links")


def write_result_table(rows, csv_path, npz_path):
    save_csv_rows(rows, csv_path, fieldnames=RESULT_FIELDS)
    np.savez(
        npz_path,
        columns=np.asarray(RESULT_FIELDS),
        modes=np.asarray([row["mode"] for row in rows]),
        rows=np.asarray([[row[field] for field in RESULT_FIELDS[3:-1]] for row in rows], dtype=np.float64),
    )


def write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def print_row(prefix, row):
    print(
        f"{prefix} mode={row['mode']}, stable=True, n_grid={row['n_grid']}, "
        f"n_particles={row['n_particles']}, rho_min={row['rho_min']:.9e}, "
        f"rho_max={row['rho_max']:.9e}, lbm_max_v={row['lbm_max_v']:.9e}, "
        f"mpm_min_J={row['mpm_min_J']:.9e}, mpm_max_speed={row['mpm_max_speed']:.9e}, "
        f"active_cell_count={row['active_cell_count']}, projected_mass={row['projected_mass']:.9e}, "
        f"cell_force_max_norm={row['cell_force_max_norm']:.9e}, "
        f"hydro_force_max_norm={row['hydro_force_max_norm']:.9e}, "
        f"bb_link_count={row['bb_link_count']}, total_time_sec={row['total_time_sec']:.3f}"
    )


def elapsed_label(t0):
    return f"{time.time() - t0:.2f}s"
