import os
from dataclasses import replace

import numpy as np

from baseline_tests.step16_common import (
    LONG_SUMMARY_FIELDS,
    assert_long_run_stable,
    load_driver_config,
    run_driver_case,
    summarize_driver_result,
    write_json,
    write_summary_npz,
)
from baseline_tests.step17_common import link_budget_summary
from src import FSIDriverConfig
from src.run_utils import save_csv_rows


POLICIES = ("uniform", "inverse_length", "length")
AREA_SCALE_MIN = 0.25
AREA_SCALE_MAX = 2.0


TRANSFER_RESULT_FIELDS = [
    "case",
    "transfer_mode",
    "policy",
    "stable",
    "global_rho_min",
    "global_rho_max",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "solid_slowdown",
    "projection_zone_ux_final",
    "area_scale_final",
    "raw_area_scale_final",
    "area_proxy_total",
    "bb_link_count",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
    "cell_force_max_norm",
]


SANITY_FIELDS = [
    "step",
    "area_policy",
    "raw_area_scale",
    "area_scale",
    "area_proxy_total",
    "bb_link_count",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
    "net_grid_reaction_force_x",
    "cell_force_max_norm",
    "stable",
]


POLICY_SWEEP_FIELDS = [
    "policy",
    "stable",
    "area_scale_final",
    "raw_area_scale_final",
    "area_proxy_total",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "solid_slowdown",
    "projection_zone_ux_final",
    "cell_force_max_norm",
    "bb_link_count",
    "active_reaction_particle_count",
]


COMPARISON_FIELDS = [
    "case",
    "transfer_mode",
    "policy",
    "stable",
    "global_rho_min",
    "global_rho_max",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "solid_slowdown",
    "projection_zone_ux_final",
    "area_scale_final",
    "bb_link_count",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
    "cell_force_max_norm",
]


def config_with(config, **updates):
    return replace(config, **updates)


def assert_finite_row(row, excluded=()):
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


def _bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().lower()
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    return float(value)


def save_rows_npz(rows, path, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"columns": np.asarray(fieldnames)}
    if any("policy" in row for row in rows):
        payload["policies"] = np.asarray([row.get("policy", "") for row in rows])
    if any("transfer_mode" in row for row in rows):
        payload["transfer_modes"] = np.asarray([row.get("transfer_mode", "") for row in rows])
    if any("case" in row for row in rows):
        payload["cases"] = np.asarray([row.get("case", "") for row in rows])
    for field in fieldnames:
        values = [row.get(field, "") for row in rows]
        if field in {"case", "transfer_mode", "policy", "area_policy"}:
            continue
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue
    np.savez(path, **payload)


def _coupler_stats(result):
    driver = result["driver"]
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
            }
        )
        return stats
    return {
        "area_policy": "",
        "area_scale": 1.0,
        "raw_area_scale": 1.0,
        "area_proxy_total": 0.0,
        "active_reaction_particle_count": 0,
        "max_grid_reaction_norm": 0.0,
        "net_grid_reaction_force": (0.0, 0.0, 0.0),
    }


def summarize_transfer_result(result, case, transfer_mode=None, policy=None):
    base = summarize_driver_result(result, case, notes="Step 18 transfer summary")
    assert_long_run_stable(base, require_moving_boundary=True)
    stats = _coupler_stats(result)
    transfer_mode = transfer_mode or result["config"].reaction_transfer_mode
    policy = policy or stats.get("area_policy", result["config"].link_area_policy)
    row = {
        "case": case,
        "transfer_mode": transfer_mode,
        "policy": policy,
        "stable": bool(base["stable"]),
        "global_rho_min": float(base["rho_min_global"]),
        "global_rho_max": float(base["rho_max_global"]),
        "rho_min": float(base["rho_min_global"]),
        "rho_max": float(base["rho_max_global"]),
        "lbm_max_v": float(base["lbm_max_v_global"]),
        "mpm_min_J": float(base["mpm_min_J_global"]),
        "mpm_max_speed": float(base["mpm_max_speed_global"]),
        "solid_slowdown": float(base["solid_vx_initial"]) - float(base["solid_vx_final"]),
        "projection_zone_ux_final": float(base["projection_zone_ux_final"]),
        "area_scale_final": float(stats.get("area_scale", 1.0)),
        "raw_area_scale_final": float(stats.get("raw_area_scale", 1.0)),
        "area_proxy_total": float(stats.get("area_proxy_total", 0.0)),
        "bb_link_count": int(base["bb_link_count_min"]),
        "active_reaction_particle_count": int(base["active_reaction_particle_count_min"]),
        "max_grid_reaction_norm": float(stats["max_grid_reaction_norm"]),
        "cell_force_max_norm": float(base["cell_force_max_norm"]),
    }
    validate_transfer_row(row, require_area_scale=transfer_mode == "link_area_experimental")
    return row


def validate_transfer_row(row, require_area_scale=True):
    assert_finite_row(row, excluded=("case", "transfer_mode", "policy", "stable"))
    if not bool(row["stable"]):
        raise RuntimeError(f"transfer row is unstable: {row}")
    if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
        raise RuntimeError(f"rho out of bounds: {row}")
    if float(row["lbm_max_v"]) >= 0.1:
        raise RuntimeError(f"lbm_max_v out of bounds: {row}")
    if float(row["mpm_min_J"]) <= 0.0:
        raise RuntimeError(f"mpm_min_J out of bounds: {row}")
    if float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("moving_boundary rows must keep cell_force_max_norm at zero")
    if int(row["bb_link_count"]) <= 0:
        raise RuntimeError("moving_boundary row must have bounce-back links")
    if int(row["active_reaction_particle_count"]) <= 0:
        raise RuntimeError("moving_boundary row must have active reaction particles")
    if require_area_scale and not (AREA_SCALE_MIN <= float(row["area_scale_final"]) <= AREA_SCALE_MAX):
        raise RuntimeError(f"area_scale is outside accepted bounds: {row}")


def run_transfer_case(root, config_path, out_dir, case):
    config = load_driver_config(root, config_path)
    result = run_driver_case(config, out_dir)
    row = summarize_transfer_result(result, case)
    return result, row


def write_single_transfer_outputs(row, out_dir, csv_name, npz_name):
    csv_path = os.path.join(out_dir, csv_name)
    npz_path = os.path.join(out_dir, npz_name)
    save_csv_rows([row], csv_path, fieldnames=TRANSFER_RESULT_FIELDS)
    save_rows_npz([row], npz_path, TRANSFER_RESULT_FIELDS)


def sanity_row(result):
    stats = _coupler_stats(result)
    final = result["driver"].final_diagnostics()
    net_grid = stats["net_grid_reaction_force"]
    row = {
        "step": int(final["step"]),
        "area_policy": stats["area_policy"],
        "raw_area_scale": float(stats["raw_area_scale"]),
        "area_scale": float(stats["area_scale"]),
        "area_proxy_total": float(stats["area_proxy_total"]),
        "bb_link_count": int(final["bb_link_count"]),
        "rho_min": float(final["rho_min"]),
        "rho_max": float(final["rho_max"]),
        "lbm_max_v": float(final["lbm_max_v"]),
        "mpm_min_J": float(final["mpm_min_J"]),
        "mpm_max_speed": float(final["mpm_max_speed"]),
        "active_reaction_particle_count": int(stats["active_reaction_particle_count"]),
        "max_grid_reaction_norm": float(stats["max_grid_reaction_norm"]),
        "net_grid_reaction_force_x": float(net_grid[0]),
        "cell_force_max_norm": float(final["cell_force_max_norm"]),
        "stable": True,
    }
    validate_sanity_row(row)
    return row


def validate_sanity_row(row):
    assert_finite_row(row, excluded=("area_policy", "stable"))
    if not (AREA_SCALE_MIN <= float(row["area_scale"]) <= AREA_SCALE_MAX):
        raise RuntimeError("area_scale is outside accepted bounds")
    if int(row["active_reaction_particle_count"]) <= 0:
        raise RuntimeError("sanity row has no active reaction particles")
    if float(row["max_grid_reaction_norm"]) <= 0.0:
        raise RuntimeError("sanity row has zero grid reaction")
    if float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("experimental transfer should not use lbm.cell_force")
    if int(row["bb_link_count"]) <= 0:
        raise RuntimeError("sanity row has no bounce-back links")
    if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
        raise RuntimeError("sanity row rho left accepted range")
    if float(row["lbm_max_v"]) >= 0.1:
        raise RuntimeError("sanity row lbm velocity exceeded threshold")
    if float(row["mpm_min_J"]) <= 0.0:
        raise RuntimeError("sanity row MPM J became non-positive")


def policy_sweep_row(result, policy):
    transfer = summarize_transfer_result(result, case=f"policy_{policy}", policy=policy)
    return {
        "policy": policy,
        "stable": transfer["stable"],
        "area_scale_final": transfer["area_scale_final"],
        "raw_area_scale_final": transfer["raw_area_scale_final"],
        "area_proxy_total": transfer["area_proxy_total"],
        "rho_min": transfer["rho_min"],
        "rho_max": transfer["rho_max"],
        "lbm_max_v": transfer["lbm_max_v"],
        "mpm_min_J": transfer["mpm_min_J"],
        "mpm_max_speed": transfer["mpm_max_speed"],
        "solid_slowdown": transfer["solid_slowdown"],
        "projection_zone_ux_final": transfer["projection_zone_ux_final"],
        "cell_force_max_norm": transfer["cell_force_max_norm"],
        "bb_link_count": transfer["bb_link_count"],
        "active_reaction_particle_count": transfer["active_reaction_particle_count"],
    }


def validate_policy_rows(rows):
    if {row["policy"] for row in rows} != set(POLICIES):
        raise RuntimeError("policy sweep is missing required policies")
    for row in rows:
        assert_finite_row(row, excluded=("policy", "stable"))
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("policy row uses cell_force")
        if int(row["bb_link_count"]) <= 0:
            raise RuntimeError("policy row has no links")
        if row["stable"]:
            if not (AREA_SCALE_MIN <= float(row["area_scale_final"]) <= AREA_SCALE_MAX):
                raise RuntimeError("policy row area scale is outside accepted bounds")
            if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
                raise RuntimeError("policy row rho left accepted range")
            if float(row["lbm_max_v"]) >= 0.1:
                raise RuntimeError("policy row lbm velocity exceeded threshold")
            if float(row["mpm_min_J"]) <= 0.0:
                raise RuntimeError("policy row MPM J became non-positive")
    if not next(row for row in rows if row["policy"] == "inverse_length")["stable"]:
        raise RuntimeError("inverse_length policy must be stable")


def write_policy_outputs(rows, out_dir):
    validate_policy_rows(rows)
    save_csv_rows(rows, os.path.join(out_dir, "policy_sweep.csv"), fieldnames=POLICY_SWEEP_FIELDS)
    save_rows_npz(rows, os.path.join(out_dir, "policy_sweep.npz"), POLICY_SWEEP_FIELDS)


def write_comparison_outputs(rows, out_dir):
    expected = {
        ("box_48", "engineering"),
        ("box_48", "link_area_experimental"),
        ("squid_proxy_48", "engineering"),
        ("squid_proxy_48", "link_area_experimental"),
    }
    found = {(row["case"], row["transfer_mode"]) for row in rows}
    if not expected.issubset(found):
        raise RuntimeError(f"comparison rows missing cases: {expected - found}")
    for row in rows:
        validate_transfer_row(row, require_area_scale=row["transfer_mode"] == "link_area_experimental")
    save_csv_rows(rows, os.path.join(out_dir, "comparison.csv"), fieldnames=COMPARISON_FIELDS)
    save_rows_npz(rows, os.path.join(out_dir, "comparison.npz"), COMPARISON_FIELDS)


def write_regression_outputs(rows, out_dir):
    save_csv_rows(rows, os.path.join(out_dir, "regression_results.csv"), fieldnames=LONG_SUMMARY_FIELDS)
    write_summary_npz(rows, os.path.join(out_dir, "regression_results.npz"), fieldnames=LONG_SUMMARY_FIELDS)


def regression_rows(root, out_dir):
    default_mode = FSIDriverConfig(coupling_mode="moving_boundary").reaction_transfer_mode
    if default_mode != "engineering":
        raise RuntimeError("default reaction_transfer_mode must remain engineering")

    engineering_config = config_with(
        load_driver_config(root, "configs/step16_long_box_48_moving_boundary.json"),
        n_lbm_steps=10,
        output_interval=10,
        write_vtk=False,
        write_particles=False,
    )
    accounting_config = config_with(
        load_driver_config(root, "configs/step17_link_area_box_48.json"),
        n_lbm_steps=5,
        output_interval=5,
        write_vtk=False,
        write_particles=False,
    )
    cases = [
        ("engineering_box_48_regression", engineering_config, os.path.join(out_dir, "engineering_box_48_regression")),
        ("step17_accounting_regression", accounting_config, os.path.join(out_dir, "step17_accounting_regression")),
    ]
    rows = []
    for case, config, case_out_dir in cases:
        result = run_driver_case(config, case_out_dir)
        row = summarize_driver_result(result, case, notes="Step 18 existing mode regression")
        assert_long_run_stable(row, require_moving_boundary=True)
        if case == "step17_accounting_regression":
            link_summary = link_budget_summary(result, case, notes="Step 17 accounting regression")
            if float(link_summary["scalar_vs_directional_impulse_error_x"]) >= 1.0e-4:
                raise RuntimeError("Step 17 accounting regression failed directional consistency")
        rows.append(row)
    return rows


def write_json_summary(row, path):
    write_json(row, path)


def print_transfer_summary(prefix, row):
    print(
        f"{prefix} case={row['case']}, transfer_mode={row['transfer_mode']}, policy={row['policy']}, "
        f"rho_min={float(row['rho_min']):.9e}, rho_max={float(row['rho_max']):.9e}, "
        f"lbm_max_v={float(row['lbm_max_v']):.9e}, mpm_min_J={float(row['mpm_min_J']):.9e}, "
        f"area_scale={float(row['area_scale_final']):.9e}, bb_link_count={row['bb_link_count']}, "
        f"active_reaction_particle_count={row['active_reaction_particle_count']}, "
        f"cell_force_max_norm={float(row['cell_force_max_norm']):.9e}, stable={row['stable']}"
    )
