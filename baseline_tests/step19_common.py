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


AREA_SCALE_MIN = 0.25
AREA_SCALE_MAX = 2.0


STEP19_SUMMARY_FIELDS = [
    "case",
    "transfer_mode",
    "reaction_transfer_mode",
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
    "max_grid_reaction_norm",
    "area_scale_initial",
    "area_scale_final",
    "area_scale_min",
    "area_scale_max",
    "area_scale_mean",
    "raw_area_scale_initial",
    "raw_area_scale_final",
    "raw_area_scale_min",
    "raw_area_scale_max",
    "area_proxy_total_initial",
    "area_proxy_total_final",
    "area_proxy_total_min",
    "area_proxy_total_max",
    "estimated_memory_mb",
    "stable",
    "well_behaved",
    "elapsed_seconds",
    "notes",
]


LINK_AREA_TIMESERIES_FIELDS = [
    "step",
    "total_mpm_substeps",
    "reaction_transfer_mode",
    "area_policy",
    "area_scale",
    "raw_area_scale",
    "area_proxy_total",
    "area_weighted_hydro_sum_x",
    "area_weighted_hydro_sum_y",
    "area_weighted_hydro_sum_z",
    "bb_link_count",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
    "net_grid_reaction_force_x",
    "net_grid_reaction_force_y",
    "net_grid_reaction_force_z",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
]


STEP19_AGGREGATE_FIELDS = [
    "summary_case",
    "artifact_path",
    "row_count",
    "stable",
    "area_scale_min",
    "area_scale_max",
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "mpm_min_J_global",
    "mpm_max_speed_global",
    "notes",
]


def load_driver_config(root, relative_path):
    return FSIDriverConfig.from_json(os.path.join(root, relative_path))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def config_with(config, **updates):
    return replace(config, **updates)


def write_step19_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    normalized = [{field: row.get(field, "") for field in fieldnames} for row in rows]
    save_csv_rows(normalized, csv_path, fieldnames=fieldnames)

    payload = {"columns": np.asarray(fieldnames)}
    for string_key in ("case", "transfer_mode", "reaction_transfer_mode", "mode", "geometry_type", "notes", "summary_case", "artifact_path", "area_policy"):
        if any(string_key in row for row in normalized):
            payload[string_key + "s"] = np.asarray([str(row.get(string_key, "")) for row in normalized])

    for field in fieldnames:
        values = [row.get(field, "") for row in normalized]
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue
    np.savez(npz_path, **payload)


def write_step19_summary_json(summary, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")


def run_driver_with_link_area_timeseries(config, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    total_start = time.perf_counter()
    driver = FSIDriver3D(config, out_dir)
    driver.initialize()

    driver.collect_diagnostics(0)
    link_area_rows = [collect_link_area_row(driver, 0)]

    for _ in range(config.n_lbm_steps):
        driver.step_once()
        should_record = (
            driver.current_lbm_step % config.output_interval == 0
            or driver.current_lbm_step == config.n_lbm_steps
        )
        if should_record:
            driver.collect_diagnostics(driver.current_lbm_step)
            link_area_rows.append(collect_link_area_row(driver, driver.current_lbm_step))

    driver.export_outputs(driver.current_lbm_step)
    driver.save_timeseries()
    driver.timing["total_time"] = time.perf_counter() - total_start

    write_step19_rows_csv_npz(
        link_area_rows,
        os.path.join(out_dir, "link_area_timeseries.csv"),
        os.path.join(out_dir, "link_area_timeseries.npz"),
        LINK_AREA_TIMESERIES_FIELDS,
    )

    return {
        "config": config,
        "driver": driver,
        "diagnostics": driver.diagnostics_rows,
        "link_area_rows": link_area_rows,
        "timing": driver.performance_row(),
        "out_dir": out_dir,
    }


def collect_link_area_row(driver, step):
    diagnostic = driver.diagnostics_rows[-1]
    stats = _reaction_stats(driver)
    net_grid = stats.get("net_grid_reaction_force", (0.0, 0.0, 0.0))
    weighted = stats.get("area_weighted_hydro_sum", (0.0, 0.0, 0.0))
    return {
        "step": int(step),
        "total_mpm_substeps": int(driver.total_mpm_substeps),
        "reaction_transfer_mode": driver.config.reaction_transfer_mode,
        "area_policy": stats.get("area_policy", "engineering"),
        "area_scale": float(stats.get("area_scale", 1.0)),
        "raw_area_scale": float(stats.get("raw_area_scale", 1.0)),
        "area_proxy_total": float(stats.get("area_proxy_total", 0.0)),
        "area_weighted_hydro_sum_x": float(weighted[0]),
        "area_weighted_hydro_sum_y": float(weighted[1]),
        "area_weighted_hydro_sum_z": float(weighted[2]),
        "bb_link_count": int(diagnostic["bb_link_count"]),
        "active_reaction_particle_count": int(stats.get("active_reaction_particle_count", 0)),
        "max_grid_reaction_norm": float(stats.get("max_grid_reaction_norm", 0.0)),
        "net_grid_reaction_force_x": float(net_grid[0]),
        "net_grid_reaction_force_y": float(net_grid[1]),
        "net_grid_reaction_force_z": float(net_grid[2]),
        "cell_force_max_norm": float(diagnostic["cell_force_max_norm"]),
        "hydro_force_max_norm": float(diagnostic["hydro_force_max_norm"]),
        "rho_min": float(diagnostic["rho_min"]),
        "rho_max": float(diagnostic["rho_max"]),
        "lbm_max_v": float(diagnostic["lbm_max_v"]),
        "mpm_min_J": float(diagnostic["mpm_min_J"]),
        "mpm_max_speed": float(diagnostic["mpm_max_speed"]),
    }


def summarize_link_area_timeseries(rows):
    if not rows:
        raise RuntimeError("empty link_area_timeseries")
    _assert_rows_finite(rows, excluded=("reaction_transfer_mode", "area_policy"))

    area_scale = [float(row["area_scale"]) for row in rows]
    raw_area_scale = [float(row["raw_area_scale"]) for row in rows]
    area_proxy = [float(row["area_proxy_total"]) for row in rows]
    max_grid = [float(row["max_grid_reaction_norm"]) for row in rows]
    return {
        "area_scale_initial": area_scale[0],
        "area_scale_final": area_scale[-1],
        "area_scale_min": min(area_scale),
        "area_scale_max": max(area_scale),
        "area_scale_mean": float(np.mean(area_scale)),
        "raw_area_scale_initial": raw_area_scale[0],
        "raw_area_scale_final": raw_area_scale[-1],
        "raw_area_scale_min": min(raw_area_scale),
        "raw_area_scale_max": max(raw_area_scale),
        "area_proxy_total_initial": area_proxy[0],
        "area_proxy_total_final": area_proxy[-1],
        "area_proxy_total_min": min(area_proxy),
        "area_proxy_total_max": max(area_proxy),
        "max_grid_reaction_norm": max(max_grid),
    }


def summarize_step19_case(result, case, transfer_mode=None, notes=""):
    config = result["config"]
    diagnostics = result["diagnostics"]
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for {case}")

    event_rows = [row for row in diagnostics if int(row["step"]) > 0] or diagnostics
    rho_min = min(float(row["rho_min"]) for row in diagnostics)
    rho_max = max(float(row["rho_max"]) for row in diagnostics)
    link_summary = summarize_link_area_timeseries(result["link_area_rows"])
    memory = estimate_total_memory_bytes(config.n_grid, config.n_particles)

    row = {
        "case": case,
        "transfer_mode": transfer_mode or config.reaction_transfer_mode,
        "reaction_transfer_mode": transfer_mode or config.reaction_transfer_mode,
        "mode": config.coupling_mode,
        "geometry_type": config.geometry_type,
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "completed_lbm_steps": max(int(row["step"]) for row in diagnostics),
        "total_mpm_substeps": max(int(row["total_mpm_substeps"]) for row in diagnostics),
        "rho_min_global": rho_min,
        "rho_max_global": rho_max,
        "rho_span_global": rho_max - rho_min,
        "lbm_max_v_global": max(float(row["lbm_max_v"]) for row in diagnostics),
        "mpm_min_J_global": min(float(row["mpm_min_J"]) for row in diagnostics),
        "mpm_max_speed_global": max(float(row["mpm_max_speed"]) for row in diagnostics),
        "solid_vx_initial": float(diagnostics[0]["solid_mean_vx_norm"]),
        "solid_vx_final": float(diagnostics[-1]["solid_mean_vx_norm"]),
        "projection_zone_ux_initial": float(diagnostics[0]["projection_zone_fluid_mean_ux"]),
        "projection_zone_ux_final": float(diagnostics[-1]["projection_zone_fluid_mean_ux"]),
        "bb_link_count_min": min(int(row["bb_link_count"]) for row in event_rows),
        "bb_link_count_max": max(int(row["bb_link_count"]) for row in event_rows),
        "active_reaction_particle_count_min": min(int(row["active_reaction_particle_count"]) for row in event_rows),
        "active_reaction_particle_count_max": max(int(row["active_reaction_particle_count"]) for row in event_rows),
        "cell_force_max_norm": max(float(row["cell_force_max_norm"]) for row in diagnostics),
        "hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in diagnostics),
        "estimated_memory_mb": float(memory["total_estimated_mb"]),
        "elapsed_seconds": float(diagnostics[-1]["elapsed_seconds"]),
        "notes": notes,
    }
    row["solid_vx_drift"] = row["solid_vx_final"] - row["solid_vx_initial"]
    row.update(link_summary)

    stable = _is_stable(row)
    row["stable"] = bool(stable)
    row["well_behaved"] = bool(
        stable
        and float(row["rho_min_global"]) > 0.98
        and float(row["rho_max_global"]) < 1.02
        and float(row["mpm_min_J_global"]) > 0.90
    )
    return {field: row.get(field, "") for field in STEP19_SUMMARY_FIELDS}


def assert_step19_stable(summary, require_link_area=False):
    _assert_row_finite(
        summary,
        excluded=("case", "transfer_mode", "reaction_transfer_mode", "mode", "geometry_type", "stable", "well_behaved", "notes"),
    )
    if not bool(summary["stable"]):
        raise RuntimeError(f"summary is not stable: {summary}")
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
    if float(summary["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("moving_boundary rows must keep cell_force_max_norm at zero")
    if int(summary["bb_link_count_min"]) <= 0:
        raise RuntimeError("moving_boundary row must have bounce-back links")
    if int(summary["active_reaction_particle_count_min"]) <= 0:
        raise RuntimeError("moving_boundary row must have active reaction particles")
    if float(summary["hydro_force_max_norm"]) <= 0.0:
        raise RuntimeError("moving_boundary row should have nonzero hydro_force diagnostics")
    if require_link_area:
        if summary["reaction_transfer_mode"] != "link_area_experimental":
            raise RuntimeError("expected link_area_experimental transfer")
        if not (AREA_SCALE_MIN <= float(summary["area_scale_min"]) <= float(summary["area_scale_max"]) <= AREA_SCALE_MAX):
            raise RuntimeError("area_scale is outside accepted bounds")


def print_step19_summary(prefix, row):
    print(
        f"{prefix} case={row['case']}, transfer={row['reaction_transfer_mode']}, "
        f"n_grid={row['n_grid']}, completed_lbm_steps={row['completed_lbm_steps']}, "
        f"total_mpm_substeps={row['total_mpm_substeps']}, "
        f"rho_min={float(row['rho_min_global']):.9e}, rho_max={float(row['rho_max_global']):.9e}, "
        f"lbm_max_v={float(row['lbm_max_v_global']):.9e}, mpm_min_J={float(row['mpm_min_J_global']):.9e}, "
        f"area_scale_final={float(row['area_scale_final']):.9e}, "
        f"area_scale_min={float(row['area_scale_min']):.9e}, "
        f"area_scale_max={float(row['area_scale_max']):.9e}, "
        f"cell_force_max_norm={float(row['cell_force_max_norm']):.9e}, stable={row['stable']}"
    )


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def aggregate_rows(summary_case, artifact_path, rows, notes=""):
    if not rows:
        raise RuntimeError(f"no rows found for {summary_case}")
    stable = all(_as_bool(row["stable"]) for row in rows)
    row = {
        "summary_case": summary_case,
        "artifact_path": artifact_path,
        "row_count": len(rows),
        "stable": bool(stable),
        "area_scale_min": min(float(row["area_scale_min"]) for row in rows),
        "area_scale_max": max(float(row["area_scale_max"]) for row in rows),
        "rho_min_global": min(float(row["rho_min_global"]) for row in rows),
        "rho_max_global": max(float(row["rho_max_global"]) for row in rows),
        "lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows),
        "mpm_min_J_global": min(float(row["mpm_min_J_global"]) for row in rows),
        "mpm_max_speed_global": max(float(row["mpm_max_speed_global"]) for row in rows),
        "notes": notes,
    }
    _assert_row_finite(row, excluded=("summary_case", "artifact_path", "stable", "notes"))
    return row


def _reaction_stats(driver):
    if driver.link_area_coupler is not None:
        return driver.link_area_coupler.get_stats()
    if driver.mb_coupler is not None:
        stats = driver.mb_coupler.get_stats()
        stats.update(
            {
                "area_policy": "engineering",
                "area_scale": 1.0,
                "raw_area_scale": 1.0,
                "area_proxy_total": 0.0,
                "area_weighted_hydro_sum": (0.0, 0.0, 0.0),
            }
        )
        return stats
    return {
        "area_policy": "",
        "area_scale": 1.0,
        "raw_area_scale": 1.0,
        "area_proxy_total": 0.0,
        "area_weighted_hydro_sum": (0.0, 0.0, 0.0),
        "active_reaction_particle_count": 0,
        "max_grid_reaction_norm": 0.0,
        "net_grid_reaction_force": (0.0, 0.0, 0.0),
    }


def _is_stable(row):
    stable = (
        float(row["rho_min_global"]) > 0.95
        and float(row["rho_max_global"]) < 1.05
        and float(row["lbm_max_v_global"]) < 0.1
        and float(row["mpm_min_J_global"]) > 0.0
        and float(row["mpm_max_speed_global"]) < 10.0
        and float(row["cell_force_max_norm"]) == 0.0
        and float(row["hydro_force_max_norm"]) > 0.0
        and int(row["bb_link_count_min"]) > 0
        and int(row["active_reaction_particle_count_min"]) > 0
        and _all_finite(row)
    )
    if row["reaction_transfer_mode"] == "link_area_experimental":
        stable = stable and AREA_SCALE_MIN <= float(row["area_scale_min"]) <= float(row["area_scale_max"]) <= AREA_SCALE_MAX
    return bool(stable)


def _bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().lower()
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    return float(value)


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _all_finite(row):
    return bool(np.all(np.isfinite(_finite_values(row))))


def _finite_values(row):
    excluded = {"case", "transfer_mode", "reaction_transfer_mode", "mode", "geometry_type", "stable", "well_behaved", "notes"}
    values = []
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        values.append(float(value))
    return values


def _assert_row_finite(row, excluded=()):
    values = []
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        values.append(float(value))
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"row contains NaN or Inf: {row}")


def _assert_rows_finite(rows, excluded=()):
    for row in rows:
        _assert_row_finite(row, excluded=excluded)
