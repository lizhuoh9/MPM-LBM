import json
import os
import time
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
from src import FSIDiagnostics3D, FSIDriverConfig, LBMFluid3D, LinkAreaMomentumAccounting3D, UnifiedSimConfig
from src.run_utils import save_csv_rows


POLICIES = ("uniform", "inverse_length", "length")


DIRECTIONAL_SANITY_FIELDS = [
    "case",
    "bb_link_count",
    "sum_link_count_by_dir",
    "link_count_sum_error",
    "bb_net_fluid_impulse_x",
    "bb_net_solid_force_x",
    "directional_fluid_impulse_x",
    "directional_solid_force_x",
    "scalar_vs_directional_impulse_error_x",
    "scalar_vs_directional_solid_error_x",
    "hydro_vs_directional_solid_error_x",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "cell_force_max_norm",
    "hydro_force_max_norm",
]


AREA_POLICY_FIELDS = [
    "case",
    "policy",
    "total_link_count",
    "axis_link_count",
    "face_diagonal_link_count",
    "area_proxy_total",
    "bb_net_fluid_impulse_x",
    "bb_net_solid_force_x",
    "area_weighted_fluid_impulse_x",
    "area_weighted_solid_force_x",
    "area_weighted_balance_error_x",
    "scalar_vs_directional_impulse_error_x",
    "hydro_vs_directional_solid_error_x",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "cell_force_max_norm",
    "hydro_force_max_norm",
]


LINK_BUDGET_FIELDS = LONG_SUMMARY_FIELDS + [
    "policy",
    "total_link_count",
    "axis_link_count",
    "face_diagonal_link_count",
    "area_proxy_total",
    "bb_net_fluid_impulse_x",
    "bb_net_solid_force_x",
    "area_weighted_fluid_impulse_x",
    "area_weighted_solid_force_x",
    "area_weighted_balance_error_x",
    "scalar_vs_directional_impulse_error_x",
    "scalar_vs_directional_solid_error_x",
    "hydro_vs_directional_solid_error_x",
]


def config_with(config, **updates):
    return replace(config, **updates)


def make_y_wall_geo(path, n_grid):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int8)
    geo[:, 0, :] = 1
    geo[:, n_grid - 1, :] = 1
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def set_top_wall_velocity(lbm, ux):
    solid_vel = lbm.solid_vel.to_numpy()
    solid_vel[:, :, :, :] = 0.0
    solid_vel[:, lbm.ny - 1, :, 0] = ux
    lbm.solid_vel.from_numpy(solid_vel)


def force_max_norm(field):
    values = field.to_numpy()
    return float(np.max(np.linalg.norm(values, axis=3)))


def assert_finite_row(row, excluded=()):
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


def assert_lbm_stats_ok(stats):
    values = [stats["max_v"], stats["rho_min"], stats["rho_max"], stats["mass_total"]]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"LBM stats contain NaN or Inf: {stats}")
    if stats["rho_min"] <= 0.95 or stats["rho_max"] >= 1.05:
        raise RuntimeError(f"LBM rho left accepted range: {stats}")
    if stats["max_v"] >= 0.1:
        raise RuntimeError(f"LBM max_v exceeded threshold: {stats}")


def run_prescribed_wall_case(root, out_dir, n_steps, target_u_lbm_x):
    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    geo_path = os.path.join(out_dir, "geo_moving_wall_32.dat")
    make_y_wall_geo(geo_path, sim.n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()
    set_top_wall_velocity(lbm, target_u_lbm_x)

    for step in range(1, n_steps + 1):
        lbm.step_moving_bounceback()
        if step % max(1, n_steps // 5) == 0 or step == n_steps:
            assert_lbm_stats_ok(lbm.get_stats())

    return lbm


def directional_sanity_row(lbm, case):
    bb_stats = lbm.get_moving_boundary_stats()
    directional = lbm.get_moving_boundary_directional_stats()
    link_count = directional["link_count_by_dir"]
    fluid_by_dir = directional["fluid_impulse_by_dir"]
    solid_by_dir = directional["solid_force_by_dir"]
    directional_fluid = np.sum(fluid_by_dir, axis=0, dtype=np.float64)
    directional_solid = np.sum(solid_by_dir, axis=0, dtype=np.float64)
    scalar_fluid = np.asarray(bb_stats["bb_net_fluid_impulse"], dtype=np.float64)
    scalar_solid = np.asarray(bb_stats["bb_net_solid_force"], dtype=np.float64)
    hydro_sum = np.sum(lbm.hydro_force.to_numpy().reshape(-1, 3), axis=0, dtype=np.float64)
    lbm_stats = lbm.get_stats()
    row = {
        "case": case,
        "bb_link_count": int(bb_stats["bb_link_count"]),
        "sum_link_count_by_dir": int(np.sum(link_count)),
        "link_count_sum_error": int(abs(int(bb_stats["bb_link_count"]) - int(np.sum(link_count)))),
        "bb_net_fluid_impulse_x": float(scalar_fluid[0]),
        "bb_net_solid_force_x": float(scalar_solid[0]),
        "directional_fluid_impulse_x": float(directional_fluid[0]),
        "directional_solid_force_x": float(directional_solid[0]),
        "scalar_vs_directional_impulse_error_x": float(abs(scalar_fluid[0] - directional_fluid[0])),
        "scalar_vs_directional_solid_error_x": float(abs(scalar_solid[0] - directional_solid[0])),
        "hydro_vs_directional_solid_error_x": float(abs(hydro_sum[0] - directional_solid[0])),
        "rho_min": float(lbm_stats["rho_min"]),
        "rho_max": float(lbm_stats["rho_max"]),
        "lbm_max_v": float(lbm_stats["max_v"]),
        "cell_force_max_norm": force_max_norm(lbm.cell_force),
        "hydro_force_max_norm": force_max_norm(lbm.hydro_force),
    }
    validate_directional_sanity_row(row)
    return row


def validate_directional_sanity_row(row):
    assert_finite_row(row, excluded=("case",))
    if int(row["sum_link_count_by_dir"]) != int(row["bb_link_count"]):
        raise RuntimeError("directional link count does not match scalar bb_link_count")
    if float(row["link_count_sum_error"]) != 0.0:
        raise RuntimeError("directional link count sum error is nonzero")
    if float(row["scalar_vs_directional_impulse_error_x"]) >= 1.0e-4:
        raise RuntimeError("directional fluid impulse does not match scalar impulse")
    if float(row["scalar_vs_directional_solid_error_x"]) >= 1.0e-4:
        raise RuntimeError("directional solid force does not match scalar solid force")
    if float(row["bb_net_fluid_impulse_x"]) <= 0.0:
        raise RuntimeError("bb_net_fluid_impulse_x should be positive")
    if float(row["bb_net_solid_force_x"]) >= 0.0:
        raise RuntimeError("bb_net_solid_force_x should be negative")
    if float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("moving-boundary accounting should keep cell_force zero")
    if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
        raise RuntimeError("LBM rho left accepted range")
    if float(row["lbm_max_v"]) >= 0.1:
        raise RuntimeError("LBM max velocity exceeded threshold")


def area_policy_rows(lbm, case):
    lbm_stats = lbm.get_stats()
    rows = []
    for policy in POLICIES:
        summary = LinkAreaMomentumAccounting3D.summarize_link_accounting(lbm, policy=policy)
        row = {
            "case": case,
            "policy": policy,
            "rho_min": float(lbm_stats["rho_min"]),
            "rho_max": float(lbm_stats["rho_max"]),
            "lbm_max_v": float(lbm_stats["max_v"]),
            "cell_force_max_norm": force_max_norm(lbm.cell_force),
            "hydro_force_max_norm": force_max_norm(lbm.hydro_force),
        }
        row.update({field: summary[field] for field in AREA_POLICY_FIELDS if field in summary})
        rows.append(row)

    validate_area_policy_rows(rows)
    return rows


def validate_area_policy_rows(rows):
    if {row["policy"] for row in rows} != set(POLICIES):
        raise RuntimeError("area policy comparison is missing required policies")
    for row in rows:
        assert_finite_row(row, excluded=("case", "policy"))
        if int(row["total_link_count"]) <= 0:
            raise RuntimeError("area policy row has no links")
        if int(row["axis_link_count"]) <= 0 or int(row["face_diagonal_link_count"]) <= 0:
            raise RuntimeError("area policy row must include axis and face diagonal links")
        if float(row["area_proxy_total"]) <= 0.0:
            raise RuntimeError("area proxy total must be positive")
        if float(row["bb_net_fluid_impulse_x"]) <= 0.0:
            raise RuntimeError("fluid impulse x must be positive")
        if float(row["area_weighted_solid_force_x"]) >= 0.0:
            raise RuntimeError("weighted solid force x must be negative")
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("cell_force must remain zero")
        if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
            raise RuntimeError("LBM rho left accepted range")
        if float(row["lbm_max_v"]) >= 0.1:
            raise RuntimeError("LBM max velocity exceeded threshold")


def save_rows_npz(rows, path, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"columns": np.asarray(fieldnames)}
    if any("policy" in row for row in rows):
        payload["policies"] = np.asarray([row.get("policy", "") for row in rows])
    for field in fieldnames:
        values = [row.get(field, "") for row in rows]
        if field in {"case", "policy", "mode", "geometry_type", "notes"}:
            continue
        try:
            payload[field] = np.asarray([float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue
    np.savez(path, **payload)


def write_directional_sanity_outputs(lbm, row, csv_path, npz_path):
    save_csv_rows([row], csv_path, fieldnames=DIRECTIONAL_SANITY_FIELDS)
    LinkAreaMomentumAccounting3D.save_directional_npz(lbm, npz_path)


def write_area_policy_outputs(rows, csv_path, npz_path):
    save_csv_rows(rows, csv_path, fieldnames=AREA_POLICY_FIELDS)
    save_rows_npz(rows, npz_path, AREA_POLICY_FIELDS)


def write_link_budget_timeseries(driver_result, path, final_summary):
    rows = []
    for diag in driver_result["diagnostics"]:
        row = dict(diag)
        if int(row["step"]) == int(final_summary["completed_lbm_steps"]):
            for key in (
                "policy",
                "total_link_count",
                "axis_link_count",
                "face_diagonal_link_count",
                "area_proxy_total",
                "scalar_vs_directional_impulse_error_x",
                "hydro_vs_directional_solid_error_x",
            ):
                row[key] = final_summary[key]
        rows.append(row)
    fieldnames = list(rows[0].keys()) if rows else []
    for key in (
        "policy",
        "total_link_count",
        "axis_link_count",
        "face_diagonal_link_count",
        "area_proxy_total",
        "scalar_vs_directional_impulse_error_x",
        "hydro_vs_directional_solid_error_x",
    ):
        if key not in fieldnames:
            fieldnames.append(key)
    save_csv_rows(rows, path, fieldnames=fieldnames)


def link_budget_summary(driver_result, case, notes, policy="inverse_length"):
    base = summarize_driver_result(driver_result, case, notes=notes)
    link = LinkAreaMomentumAccounting3D.summarize_link_accounting(driver_result["driver"].lbm, policy=policy)
    summary = dict(base)
    for field in LINK_BUDGET_FIELDS:
        if field in link:
            summary[field] = link[field]
    validate_link_budget_summary(summary)
    return summary


def validate_link_budget_summary(summary):
    base_summary = {field: summary[field] for field in LONG_SUMMARY_FIELDS if field in summary}
    assert_long_run_stable(base_summary, require_moving_boundary=True)
    if int(summary["axis_link_count"]) <= 0:
        raise RuntimeError("link budget has no axis links")
    if int(summary["face_diagonal_link_count"]) <= 0:
        raise RuntimeError("link budget has no face diagonal links")
    if float(summary["area_proxy_total"]) <= 0.0:
        raise RuntimeError("link budget area proxy total must be positive")
    if float(summary["scalar_vs_directional_impulse_error_x"]) >= 1.0e-4:
        raise RuntimeError("link budget directional impulse error is too large")
    if not np.isfinite(float(summary["hydro_vs_directional_solid_error_x"])):
        raise RuntimeError("link budget hydro-vs-directional error is not finite")


def write_link_budget_outputs(driver_result, summary, out_dir):
    write_json(summary, os.path.join(out_dir, "link_budget_summary.json"))
    write_link_budget_timeseries(driver_result, os.path.join(out_dir, "link_budget_timeseries.csv"), summary)
    LinkAreaMomentumAccounting3D.save_directional_npz(
        driver_result["driver"].lbm,
        os.path.join(out_dir, "directional_stats_final.npz"),
    )


def run_link_budget_case(root, config_path, out_dir, case, notes, policy="inverse_length"):
    config = load_driver_config(root, config_path)
    result = run_driver_case(config, out_dir)
    summary = link_budget_summary(result, case=case, notes=notes, policy=policy)
    write_link_budget_outputs(result, summary, out_dir)
    return summary


def write_regression_outputs(rows, csv_path, npz_path):
    save_csv_rows(rows, csv_path, fieldnames=LONG_SUMMARY_FIELDS)
    write_summary_npz(rows, npz_path, fieldnames=LONG_SUMMARY_FIELDS)


def print_link_summary(prefix, summary):
    print(
        f"{prefix} case={summary['case']}, n_grid={summary['n_grid']}, "
        f"completed_lbm_steps={summary['completed_lbm_steps']}, "
        f"total_mpm_substeps={summary['total_mpm_substeps']}, "
        f"rho_min={float(summary['rho_min_global']):.9e}, "
        f"rho_max={float(summary['rho_max_global']):.9e}, "
        f"lbm_max_v={float(summary['lbm_max_v_global']):.9e}, "
        f"mpm_min_J={float(summary['mpm_min_J_global']):.9e}, "
        f"bb_link_count_min={summary['bb_link_count_min']}, "
        f"area_proxy_total={float(summary['area_proxy_total']):.9e}, "
        f"axis_link_count={summary['axis_link_count']}, "
        f"face_diagonal_link_count={summary['face_diagonal_link_count']}, "
        f"cell_force_max_norm={float(summary['cell_force_max_norm']):.9e}, "
        f"stable={summary['stable']}"
    )


def elapsed_label(t0):
    return f"{time.time() - t0:.2f}s"
