import json
import os
import time
from dataclasses import replace

import numpy as np

from src import (
    FSIDriver3D,
    FSIDriverConfig,
    FSIDiagnostics3D,
    MomentumAccounting3D,
    classify_calibration_row,
    choose_recommended_row,
)
from src.run_utils import save_csv_rows, save_json_config


ACCOUNTING_FIELDS = [
    "step",
    "bb_link_count",
    "bb_net_fluid_impulse_x",
    "bb_net_solid_force_x",
    "hydro_force_sum_x",
    "cell_force_sum_x",
    "net_particle_reaction_force_x",
    "net_grid_reaction_force_x",
    "applied_particle_reaction_force_x",
    "applied_grid_reaction_force_x",
    "solid_momentum_x",
    "solid_momentum_delta_x",
    "fluid_mean_ux",
    "projection_zone_ux",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "hydro_field_vs_bb_error_x",
    "grid_vs_particle_reaction_error_x",
    "solid_momentum_response_ratio_x",
    "force_sign_consistent",
]


CALIBRATION_FIELDS = [
    "reaction_scale",
    "force_cap_norm",
    "geometry_type",
    "stable",
    "well_behaved",
    "over_damped",
    "sign_reversed",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "initial_solid_vx",
    "final_solid_vx",
    "solid_slowdown",
    "projection_zone_ux_final",
    "hydro_force_max_norm",
    "net_grid_reaction_force_x",
    "solid_momentum_delta_x",
    "cell_force_max_norm",
    "bb_link_count",
    "accounting_error_x",
    "classification_reason",
    "score",
]


COMPARISON_FIELDS = [
    "label",
    "target_u_lbm_x",
    "reaction_scale",
    "force_cap_norm",
    "stable",
    "well_behaved",
    "sign_reversed",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "solid_slowdown",
    "projection_zone_ux_final",
    "hydro_force_max_norm",
    "accounting_error_x",
    "recommendation",
]


def load_driver_config(root, relative_path):
    return FSIDriverConfig.from_json(os.path.join(root, relative_path))


def config_with(config, **updates):
    return replace(config, **updates)


def _bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if str(value).strip().lower() in {"true", "false"}:
        return 1.0 if str(value).strip().lower() == "true" else 0.0
    return float(value)


def save_rows_npz(rows, path, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"columns": np.asarray(fieldnames)}
    for field in fieldnames:
        values = [row.get(field, "") for row in rows]
        if field == "label":
            payload["labels"] = np.asarray(values)
            continue
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue
    np.savez(path, **payload)


def assert_rows_finite(rows, excluded=()):
    for row in rows:
        numeric = []
        for key, value in row.items():
            if key in excluded or value == "":
                continue
            if isinstance(value, bool):
                continue
            if str(value).strip().lower() in {"true", "false"}:
                continue
            try:
                numeric.append(float(value))
            except (TypeError, ValueError):
                continue
        if not np.all(np.isfinite(numeric)):
            raise RuntimeError(f"row contains NaN or Inf: {row}")


def stable_thresholds_ok(row):
    return (
        float(row["rho_min"]) > 0.95
        and float(row["rho_max"]) < 1.05
        and float(row["lbm_max_v"]) < 0.1
        and float(row["mpm_min_J"]) > 0.0
        and float(row["mpm_max_speed"]) < 10.0
    )


def run_accounted_moving_boundary_case(config, out_dir, accounting_csv=None, accounting_npz=None):
    if config.coupling_mode != "moving_boundary":
        raise ValueError("Step 15 accounting cases require coupling_mode='moving_boundary'")

    os.makedirs(out_dir, exist_ok=True)
    driver = FSIDriver3D(config, out_dir)
    t0 = time.perf_counter()
    driver.initialize()

    initial_solid_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(driver.solid)[0])
    initial_momentum = MomentumAccounting3D.solid_particle_momentum(driver.solid)
    cumulative_grid_impulse = np.zeros(3, dtype=np.float64)
    rows = []

    for step in range(1, config.n_lbm_steps + 1):
        driver._project()

        coupling_t0 = time.perf_counter()
        driver.lbm.update_dynamic_solid(config.dynamic_solid_threshold)
        driver.lbm.reinitialize_new_fluid_cells()
        driver.timing["coupling_time"] += time.perf_counter() - coupling_t0

        lbm_t0 = time.perf_counter()
        driver.lbm.step_moving_bounceback()
        driver.timing["lbm_step_time"] += time.perf_counter() - lbm_t0

        previous_momentum = MomentumAccounting3D.solid_particle_momentum(driver.solid)
        substep_grid_force = np.zeros(3, dtype=np.float64)

        mpm_t0 = time.perf_counter()
        for _ in range(config.mpm_substeps_per_lbm_step):
            driver.solid.clear_grid()
            driver.solid.p2g()
            driver.mb_coupler.clear_reaction_diagnostics()
            driver.mb_coupler.add_moving_boundary_reaction_to_mpm_grid(driver.solid, driver.lbm)
            mb_stats = driver.mb_coupler.get_stats()
            substep_grid_force += np.asarray(mb_stats["net_grid_reaction_force"], dtype=np.float64)
            driver.solid.grid_update()
            driver.solid.g2p()
            driver.total_mpm_substeps += 1
        driver.timing["mpm_substep_time"] += time.perf_counter() - mpm_t0

        cumulative_grid_impulse += substep_grid_force * float(config.mpm_dt)
        row = MomentumAccounting3D.moving_boundary_accounting_row(
            step=step,
            lbm=driver.lbm,
            solid=driver.solid,
            mb_coupler=driver.mb_coupler,
            previous_solid_momentum=previous_momentum,
            cumulative_grid_reaction_impulse=cumulative_grid_impulse,
            target_u_lbm_x=float(config.target_u_lbm[0]),
        )
        rows.append(row)
        driver.current_lbm_step = step

    final_solid_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(driver.solid)[0])
    final_momentum = MomentumAccounting3D.solid_particle_momentum(driver.solid)
    total_time = time.perf_counter() - t0
    driver.timing["total_time"] = total_time

    assert_rows_finite(rows, excluded=("force_sign_consistent",))
    if accounting_csv is not None:
        save_csv_rows(rows, accounting_csv, fieldnames=ACCOUNTING_FIELDS)
    if accounting_npz is not None:
        save_rows_npz(rows, accounting_npz, ACCOUNTING_FIELDS)

    return {
        "config": config,
        "driver": driver,
        "rows": rows,
        "initial_solid_vx": initial_solid_vx,
        "final_solid_vx": final_solid_vx,
        "initial_momentum": initial_momentum,
        "final_momentum": final_momentum,
        "total_solid_momentum_delta": final_momentum - initial_momentum,
        "total_time_sec": total_time,
    }


def summarize_case_result(result, geometry_type=None):
    rows = result["rows"]
    config = result["config"]
    final = rows[-1]
    initial_solid_vx = float(result["initial_solid_vx"])
    final_solid_vx = float(result["final_solid_vx"])
    accounting_error_x = max(
        float(row["hydro_field_vs_bb_error_x"]) + float(row["grid_vs_particle_reaction_error_x"])
        for row in rows
    )
    raw = {
        "reaction_scale": float(config.mb_reaction_scale),
        "force_cap_norm": float(config.mb_force_cap_norm),
        "geometry_type": geometry_type or config.geometry_type,
        "rho_min": float(final["rho_min"]),
        "rho_max": float(final["rho_max"]),
        "lbm_max_v": float(final["lbm_max_v"]),
        "mpm_min_J": float(final["mpm_min_J"]),
        "mpm_max_speed": float(final["mpm_max_speed"]),
        "initial_solid_vx": initial_solid_vx,
        "final_solid_vx": final_solid_vx,
        "solid_slowdown": max(initial_solid_vx - final_solid_vx, 0.0),
        "projection_zone_ux_final": float(final["projection_zone_ux"]),
        "hydro_force_max_norm": float(final["hydro_force_max_norm"]),
        "net_grid_reaction_force_x": float(final["net_grid_reaction_force_x"]),
        "solid_momentum_delta_x": float(result["total_solid_momentum_delta"][0]),
        "cell_force_max_norm": float(final["cell_force_max_norm"]),
        "bb_link_count": int(final["bb_link_count"]),
        "accounting_error_x": float(accounting_error_x),
    }
    return classify_calibration_row(raw)


def validate_accounting_sanity(rows):
    for row in rows:
        if int(row["bb_link_count"]) <= 0:
            raise RuntimeError("bb_link_count must be positive")
        if float(row["cell_force_sum_x"]) != 0.0:
            raise RuntimeError("moving_boundary accounting must keep cell_force_sum_x at zero")
        if not bool(row["force_sign_consistent"]):
            raise RuntimeError("moving_boundary force sign is inconsistent with target_u_lbm_x")
        if not stable_thresholds_ok(row):
            raise RuntimeError(f"accounting row failed stability thresholds: {row}")

    first = rows[0]
    if float(first["bb_net_fluid_impulse_x"]) <= 0.0:
        raise RuntimeError("bb_net_fluid_impulse_x should be positive for +x moving-boundary target")
    if float(first["bb_net_solid_force_x"]) >= 0.0:
        raise RuntimeError("bb_net_solid_force_x should be negative for +x moving-boundary target")
    if float(first["hydro_force_sum_x"]) >= 0.0:
        raise RuntimeError("hydro_force_sum_x should be negative for +x moving-boundary target")
    if float(first["net_grid_reaction_force_x"]) >= 0.0:
        raise RuntimeError("net_grid_reaction_force_x should be negative for +x moving-boundary target")


def validate_calibration_rows(rows):
    assert_rows_finite(
        rows,
        excluded=("geometry_type", "stable", "well_behaved", "over_damped", "sign_reversed", "classification_reason"),
    )
    for row in rows:
        if bool(row["stable"]) and not stable_thresholds_ok(row):
            raise RuntimeError(f"stable row failed thresholds: {row}")


def write_calibration_outputs(rows, csv_path, npz_path, fieldnames=CALIBRATION_FIELDS):
    save_csv_rows(rows, csv_path, fieldnames=fieldnames)
    save_rows_npz(rows, npz_path, fieldnames)


def write_recommended_config(base_config, recommended_row, path):
    config = config_with(
        base_config,
        mb_reaction_scale=float(recommended_row["reaction_scale"]),
        mb_force_cap_norm=float(recommended_row["force_cap_norm"]),
        write_vtk=False,
        write_particles=False,
    )
    save_json_config(config, path)
    return config


def write_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def print_calibration_row(prefix, row):
    print(
        f"{prefix} reaction_scale={float(row['reaction_scale']):.6g}, "
        f"force_cap_norm={float(row['force_cap_norm']):.9g}, stable={row['stable']}, "
        f"well_behaved={row['well_behaved']}, sign_reversed={row['sign_reversed']}, "
        f"rho_min={float(row['rho_min']):.9e}, rho_max={float(row['rho_max']):.9e}, "
        f"lbm_max_v={float(row['lbm_max_v']):.9e}, mpm_min_J={float(row['mpm_min_J']):.9e}, "
        f"mpm_max_speed={float(row['mpm_max_speed']):.9e}, "
        f"solid_slowdown={float(row['solid_slowdown']):.9e}, score={float(row['score']):.6f}"
    )


def choose_and_mark_recommended(rows):
    recommended = choose_recommended_row(rows)
    marked = []
    for row in rows:
        row_out = dict(row)
        row_out["recommended"] = (
            abs(float(row_out["reaction_scale"]) - float(recommended["reaction_scale"])) < 1.0e-12
            and abs(float(row_out["force_cap_norm"]) - float(recommended["force_cap_norm"])) < 1.0e-12
        )
        marked.append(row_out)
    return recommended, marked


def elapsed_label(t0):
    return f"{time.time() - t0:.2f}s"
