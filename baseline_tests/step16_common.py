import csv
import json
import math
import os
import time
from dataclasses import replace

import numpy as np

from src import FSIDriver3D, FSIDriverConfig
from src.performance import estimate_total_memory_bytes
from src.run_utils import save_csv_rows


LONG_SUMMARY_FIELDS = [
    "case",
    "mode",
    "geometry_type",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "rho_min_global",
    "rho_max_global",
    "rho_span_global",
    "lbm_max_v_global",
    "mpm_min_J_global",
    "mpm_max_speed_global",
    "solid_vx_initial",
    "solid_vx_final",
    "solid_vx_drift",
    "projection_zone_ux_initial",
    "projection_zone_ux_final",
    "bb_link_count_min",
    "bb_link_count_max",
    "active_reaction_particle_count_min",
    "active_reaction_particle_count_max",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "estimated_memory_mb",
    "stable",
    "well_behaved",
    "elapsed_seconds",
    "notes",
]


MODE_RESULT_FIELDS = LONG_SUMMARY_FIELDS


def load_driver_config(root, relative_path):
    return FSIDriverConfig.from_json(os.path.join(root, relative_path))


def load_mode_matrix(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def config_with(config, **updates):
    return replace(config, **updates)


def _read_timeseries_rows(csv_path):
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _float(row, key):
    return float(row[key])


def _int(row, key):
    return int(float(row[key]))


def _finite_values(summary):
    excluded = {"case", "mode", "geometry_type", "stable", "well_behaved", "notes"}
    values = []
    for key, value in summary.items():
        if key in excluded or value == "":
            continue
        values.append(float(value))
    return values


def _all_finite(summary):
    return bool(np.all(np.isfinite(_finite_values(summary))))


def _min_int(rows, key):
    if not rows:
        return 0
    return min(_int(row, key) for row in rows)


def _max_int(rows, key):
    if not rows:
        return 0
    return max(_int(row, key) for row in rows)


def summarize_driver_timeseries(csv_path):
    rows = _read_timeseries_rows(csv_path)
    if not rows:
        raise RuntimeError(f"empty diagnostics timeseries: {csv_path}")

    mode = rows[-1]["coupling_mode"]
    post_initial_rows = [row for row in rows if _int(row, "step") > 0]
    event_rows = post_initial_rows if post_initial_rows else rows

    rho_min = min(_float(row, "rho_min") for row in rows)
    rho_max = max(_float(row, "rho_max") for row in rows)
    summary = {
        "completed_lbm_steps": max(_int(row, "step") for row in rows),
        "total_mpm_substeps": max(_int(row, "total_mpm_substeps") for row in rows),
        "rho_min_global": rho_min,
        "rho_max_global": rho_max,
        "rho_span_global": rho_max - rho_min,
        "lbm_max_v_global": max(_float(row, "lbm_max_v") for row in rows),
        "mpm_min_J_global": min(_float(row, "mpm_min_J") for row in rows),
        "mpm_max_speed_global": max(_float(row, "mpm_max_speed") for row in rows),
        "solid_vx_initial": _float(rows[0], "solid_mean_vx_norm"),
        "solid_vx_final": _float(rows[-1], "solid_mean_vx_norm"),
        "projection_zone_ux_initial": _float(rows[0], "projection_zone_fluid_mean_ux"),
        "projection_zone_ux_final": _float(rows[-1], "projection_zone_fluid_mean_ux"),
        "bb_link_count_min": _min_int(event_rows, "bb_link_count"),
        "bb_link_count_max": _max_int(event_rows, "bb_link_count"),
        "active_reaction_particle_count_min": _min_int(event_rows, "active_reaction_particle_count"),
        "active_reaction_particle_count_max": _max_int(event_rows, "active_reaction_particle_count"),
        "cell_force_max_norm": max(_float(row, "cell_force_max_norm") for row in rows),
        "hydro_force_max_norm": max(_float(row, "hydro_force_max_norm") for row in rows),
        "elapsed_seconds": _float(rows[-1], "elapsed_seconds"),
    }
    summary["solid_vx_drift"] = summary["solid_vx_final"] - summary["solid_vx_initial"]

    stable = (
        summary["rho_min_global"] > 0.95
        and summary["rho_max_global"] < 1.05
        and summary["lbm_max_v_global"] < 0.1
        and summary["mpm_min_J_global"] > 0.0
        and summary["mpm_max_speed_global"] < 10.0
        and _all_finite(summary)
    )
    if mode == "moving_boundary":
        stable = (
            stable
            and summary["bb_link_count_min"] > 0
            and summary["active_reaction_particle_count_min"] > 0
            and summary["cell_force_max_norm"] == 0.0
            and summary["hydro_force_max_norm"] > 0.0
        )

    summary["stable"] = bool(stable)
    summary["well_behaved"] = bool(stable)
    return summary


def assert_long_run_stable(summary, require_moving_boundary=True):
    if not _all_finite(summary):
        raise RuntimeError(f"summary contains NaN or Inf: {summary}")
    if float(summary["rho_min_global"]) <= 0.95:
        raise RuntimeError("rho_min_global is below the accepted lower bound")
    if float(summary["rho_max_global"]) >= 1.05:
        raise RuntimeError("rho_max_global is above the accepted upper bound")
    if float(summary["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError("lbm_max_v_global exceeded the accepted maximum")
    if float(summary["mpm_min_J_global"]) <= 0.0:
        raise RuntimeError("mpm_min_J_global became non-positive")
    if float(summary["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError("mpm_max_speed_global exceeded the accepted maximum")
    if require_moving_boundary:
        if int(summary["bb_link_count_min"]) <= 0:
            raise RuntimeError("moving_boundary summary has no bounce-back links")
        if int(summary["active_reaction_particle_count_min"]) <= 0:
            raise RuntimeError("moving_boundary summary has no active reaction particles")
        if float(summary["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("moving_boundary summary must keep cell_force_max_norm at zero")
        if float(summary["hydro_force_max_norm"]) <= 0.0:
            raise RuntimeError("moving_boundary summary should have nonzero hydro_force diagnostics")
    if not bool(summary["stable"]):
        raise RuntimeError(f"summary is not stable: {summary}")


def run_driver_case(config, out_dir):
    driver = FSIDriver3D(config, out_dir)
    diagnostics = driver.run()
    return {
        "config": config,
        "driver": driver,
        "diagnostics": diagnostics,
        "timing": driver.performance_row(),
        "out_dir": out_dir,
    }


def load_final_row(driver_out_dir):
    rows = _read_timeseries_rows(os.path.join(driver_out_dir, "diagnostics_timeseries.csv"))
    if not rows:
        raise RuntimeError(f"empty diagnostics timeseries in {driver_out_dir}")
    return rows[-1]


def _summary_with_config(config, summary, case, notes):
    memory = estimate_total_memory_bytes(config.n_grid, config.n_particles)
    row = {
        "case": case,
        "mode": config.coupling_mode,
        "geometry_type": config.geometry_type,
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "estimated_memory_mb": float(memory["total_estimated_mb"]),
        "notes": notes,
    }
    row.update(summary)
    return {field: row.get(field, "") for field in LONG_SUMMARY_FIELDS}


def summarize_driver_result(result, case, notes=""):
    csv_path = os.path.join(result["out_dir"], "diagnostics_timeseries.csv")
    summary = summarize_driver_timeseries(csv_path)
    return _summary_with_config(result["config"], summary, case, notes)


def write_long_run_summary(summary, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")


def write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_summary_csv(rows, path):
    save_csv_rows(rows, path, fieldnames=LONG_SUMMARY_FIELDS)


def _bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().lower()
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    return float(value)


def write_summary_npz(rows, path, fieldnames=LONG_SUMMARY_FIELDS):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"columns": np.asarray(fieldnames)}
    if any("mode" in row for row in rows):
        payload["modes"] = np.asarray([row.get("mode", "") for row in rows])
    for field in fieldnames:
        values = [row.get(field, "") for row in rows]
        if field in {"case", "mode", "geometry_type", "notes"}:
            continue
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue
    np.savez(path, **payload)


def mode_matrix_config(matrix, mode):
    if mode not in matrix["modes"]:
        raise ValueError(f"mode {mode!r} is not present in Step 16 matrix")
    data = {key: value for key, value in matrix.items() if key != "modes"}
    data["coupling_mode"] = mode
    return FSIDriverConfig(**data)


def validate_mode_summary(row):
    assert_long_run_stable(row, require_moving_boundary=row["mode"] == "moving_boundary")
    if row["mode"] == "none":
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("none mode should keep cell_force_max_norm at zero")
        if int(row["bb_link_count_min"]) != 0:
            raise RuntimeError("none mode should not have moving bounce-back links")
    elif row["mode"] == "penalty":
        if float(row["cell_force_max_norm"]) <= 0.0:
            raise RuntimeError("penalty mode should have nonzero cell_force_max_norm")
        if int(row["bb_link_count_min"]) != 0:
            raise RuntimeError("penalty mode should not have moving bounce-back links")
    elif row["mode"] == "moving_boundary":
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("moving_boundary mode should keep cell_force_max_norm at zero")
        if int(row["bb_link_count_min"]) <= 0:
            raise RuntimeError("moving_boundary mode should have bounce-back links")
    else:
        raise RuntimeError(f"unsupported mode in Step 16 summary: {row['mode']}")


def validate_mode_rows(rows):
    modes = {row["mode"] for row in rows}
    if modes != {"none", "penalty", "moving_boundary"}:
        raise RuntimeError(f"unexpected Step 16 mode matrix rows: {sorted(modes)}")
    for row in rows:
        validate_mode_summary(row)


def print_summary(prefix, row):
    print(
        f"{prefix} case={row['case']}, mode={row['mode']}, n_grid={row['n_grid']}, "
        f"n_particles={row['n_particles']}, completed_lbm_steps={row['completed_lbm_steps']}, "
        f"total_mpm_substeps={row['total_mpm_substeps']}, rho_min={float(row['rho_min_global']):.9e}, "
        f"rho_max={float(row['rho_max_global']):.9e}, lbm_max_v={float(row['lbm_max_v_global']):.9e}, "
        f"mpm_min_J={float(row['mpm_min_J_global']):.9e}, "
        f"mpm_max_speed={float(row['mpm_max_speed_global']):.9e}, "
        f"bb_link_count_min={row['bb_link_count_min']}, cell_force_max_norm={float(row['cell_force_max_norm']):.9e}, "
        f"hydro_force_max_norm={float(row['hydro_force_max_norm']):.9e}, "
        f"elapsed_seconds={float(row['elapsed_seconds']):.3f}, stable={row['stable']}"
    )


def elapsed_label(t0):
    return f"{time.time() - t0:.2f}s"
