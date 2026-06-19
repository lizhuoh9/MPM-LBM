import csv
import json
import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import (  # noqa: E402
    FSIDiagnostics3D,
    FSIDriver3D,
    FSIDriverConfig,
    GeometryConfig,
    GeometrySampler3D,
    LBMFluid3D,
    MPMToLBMProjector3D,
    MPMSolid3D,
    UnifiedSimConfig,
)
from src.run_utils import assert_no_nan_inf_array, make_all_fluid_geo, save_csv_rows  # noqa: E402


STEP21_DRIVER_FIELDS = [
    "case",
    "geometry_type",
    "geometry_source",
    "mode",
    "reaction_transfer_mode",
    "n_grid",
    "n_particles",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "projected_mass",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "active_reaction_particle_count",
    "area_scale_final",
    "stable",
    "notes",
]


STEP21_PROJECTION_FIELDS = [
    "case",
    "geometry_type",
    "particle_count",
    "geometry_volume",
    "particle_mass_sum",
    "projected_mass",
    "relative_mass_error",
    "active_cell_count",
    "solid_phi_min",
    "solid_phi_max",
    "occupied_count_32",
    "occupied_fraction_32",
    "particle_bounds_min_x",
    "particle_bounds_min_y",
    "particle_bounds_min_z",
    "particle_bounds_max_x",
    "particle_bounds_max_y",
    "particle_bounds_max_z",
    "stable",
    "notes",
]


STEP21_SUMMARY_FIELDS = [
    "stable",
    "required_row_count",
    "driver_row_count",
    "projection_quality_row_count",
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "mpm_min_J_global",
    "mpm_max_speed_global",
    "max_relative_mass_error",
    "large_file_count",
    "notes",
]


def load_driver_config(relative_path):
    return FSIDriverConfig.from_json(os.path.join(ROOT, relative_path))


def load_geometry_config(relative_path):
    return GeometryConfig.from_json(os.path.join(ROOT, relative_path))


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def read_csv_rows(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    normalized = [{field: row.get(field, "") for field in fieldnames} for row in rows]
    save_csv_rows(normalized, csv_path, fieldnames=fieldnames)

    payload = {"columns": np.asarray(fieldnames)}
    for string_key in (
        "case",
        "geometry_type",
        "geometry_source",
        "mode",
        "reaction_transfer_mode",
        "stable",
        "notes",
    ):
        if any(string_key in row for row in normalized):
            payload[string_key + "s"] = np.asarray([str(row.get(string_key, "")) for row in normalized])

    for field in fieldnames:
        values = [row.get(field, "") for row in normalized]
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue

    np.savez(npz_path, **payload)


def run_driver_config_paths(case, config_paths, out_dir, csv_name, npz_name):
    rows = []
    for relative_path in config_paths:
        config = load_driver_config(relative_path)
        row = run_driver_case(case, config, os.path.join(out_dir, _case_output_name(config)))
        rows.append(row)
        print(
            f"case={case}, mode={row['mode']}, transfer={row['reaction_transfer_mode']}, "
            f"n_grid={row['n_grid']}, steps={row['completed_lbm_steps']}, "
            f"rho=[{row['rho_min']:.9e}, {row['rho_max']:.9e}], "
            f"lbm_max_v={row['lbm_max_v']:.9e}, projected_mass={row['projected_mass']:.9e}, "
            f"active_cell_count={row['active_cell_count']}, stable={row['stable']}"
        )

    write_rows_csv_npz(rows, os.path.join(out_dir, csv_name), os.path.join(out_dir, npz_name), STEP21_DRIVER_FIELDS)
    if not all(_as_bool(row["stable"]) for row in rows):
        raise RuntimeError(f"not all Step 21 driver rows are stable for {case}")
    return rows


def run_driver_case(case, config, out_dir):
    driver = FSIDriver3D(config, out_dir)
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for {case}/{config.coupling_mode}")

    row = summarize_driver_case(case, config, diagnostics, driver)
    assert_driver_row(row)
    return row


def summarize_driver_case(case, config, diagnostics, driver):
    area_scale_final = 1.0
    if driver.link_area_coupler is not None:
        area_scale_final = float(driver.link_area_coupler.get_stats()["area_scale"])

    return {
        "case": case,
        "geometry_type": config.geometry_type,
        "geometry_source": config.geometry_config_path or config.geometry_type,
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "completed_lbm_steps": max(int(row["step"]) for row in diagnostics),
        "total_mpm_substeps": max(int(row["total_mpm_substeps"]) for row in diagnostics),
        "rho_min": min(float(row["rho_min"]) for row in diagnostics),
        "rho_max": max(float(row["rho_max"]) for row in diagnostics),
        "lbm_max_v": max(float(row["lbm_max_v"]) for row in diagnostics),
        "mpm_min_J": min(float(row["mpm_min_J"]) for row in diagnostics),
        "mpm_max_speed": max(float(row["mpm_max_speed"]) for row in diagnostics),
        "projected_mass": max(float(row["projected_mass"]) for row in diagnostics),
        "active_cell_count": max(int(row["active_cell_count"]) for row in diagnostics),
        "cell_force_max_norm": max(float(row["cell_force_max_norm"]) for row in diagnostics),
        "hydro_force_max_norm": max(float(row["hydro_force_max_norm"]) for row in diagnostics),
        "bb_link_count": max(int(row["bb_link_count"]) for row in diagnostics),
        "active_reaction_particle_count": max(int(row["active_reaction_particle_count"]) for row in diagnostics),
        "area_scale_final": area_scale_final,
        "stable": True,
        "notes": "Step 21 imported geometry scale validation; no new FSI physics",
    }


def build_projection_harness(out_dir, n_particles, n_grid=48):
    os.makedirs(out_dir, exist_ok=True)
    sim = UnifiedSimConfig(n_grid=n_grid, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=5)
    geo_path = os.path.join(out_dir, f"geo_all_fluid_{n_grid}.dat")
    make_all_fluid_geo(geo_path, n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(gravity=(0.0, 0.0, 0.0), box_min=(0.25, 0.25, 0.25), box_max=(0.75, 0.75, 0.75)),
        n_particles=n_particles,
    )
    projector = MPMToLBMProjector3D(sim)
    return {"sim": sim, "lbm": lbm, "solid": solid, "projector": projector}


def run_projection_quality_cases(cases, out_dir, n_grid=48):
    os.makedirs(out_dir, exist_ok=True)
    harness = build_projection_harness(out_dir, n_particles=4096, n_grid=n_grid)
    rows = []
    for case, config_path in cases:
        config = load_geometry_config(config_path)
        row = run_projection_quality_case(case, config, out_dir, harness)
        rows.append(row)
        print(
            f"case={case}, geometry_type={row['geometry_type']}, "
            f"projected_mass={row['projected_mass']:.9e}, "
            f"relative_mass_error={row['relative_mass_error']:.9e}, "
            f"active_cell_count={row['active_cell_count']}, stable={row['stable']}"
        )

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "projection_quality.csv"),
        os.path.join(out_dir, "projection_quality.npz"),
        STEP21_PROJECTION_FIELDS,
    )
    if not all(_as_bool(row["stable"]) for row in rows):
        raise RuntimeError("not all Step 21 projection quality rows are stable")
    return rows


def run_projection_quality_case(case, geometry_config, out_dir, harness):
    sampler = GeometrySampler3D(geometry_config)
    cloud = sampler.sample_particles()
    assert_particle_cloud(cloud, geometry_config.n_particles)

    lbm = harness["lbm"]
    solid = harness["solid"]
    projector = harness["projector"]
    solid.init_from_numpy(cloud["x"], cloud["vol0"], cloud["mass"])
    projector.project(solid, lbm)

    projection_stats = projector.get_stats()
    force_stats = FSIDiagnostics3D.force_stats(lbm)
    solid_phi = lbm.solid_phi.to_numpy()
    particles = solid.x.to_numpy()
    voxelized_32 = sampler.voxelize(32)

    assert_no_nan_inf_array("solid_phi", solid_phi)
    assert_no_nan_inf_array("particles_x", particles)
    if float(np.min(solid_phi)) < 0.0 or float(np.max(solid_phi)) > 1.0:
        raise RuntimeError("solid_phi must stay in [0, 1]")
    if float(force_stats["max_cell_force_norm"]) != 0.0:
        raise RuntimeError("projection-quality baseline should not create cell_force")
    if float(force_stats["max_hydro_force_norm"]) != 0.0:
        raise RuntimeError("projection-quality baseline should not create hydro_force")

    particle_mass_sum = float(np.sum(np.asarray(cloud["mass"], dtype=np.float64)))
    projected_mass = float(projection_stats["projected_mass"])
    relative_mass_error = abs(projected_mass - particle_mass_sum) / max(particle_mass_sum, 1.0e-12)
    bounds_min = np.min(particles, axis=0)
    bounds_max = np.max(particles, axis=0)

    case_dir = os.path.join(out_dir, case)
    os.makedirs(case_dir, exist_ok=True)
    np.save(os.path.join(case_dir, "solid_phi.npy"), solid_phi)
    np.save(os.path.join(case_dir, "particles_x.npy"), particles)

    row = {
        "case": case,
        "geometry_type": geometry_config.geometry_type,
        "particle_count": int(geometry_config.n_particles),
        "geometry_volume": float(cloud["geometry_volume"]),
        "particle_mass_sum": particle_mass_sum,
        "projected_mass": projected_mass,
        "relative_mass_error": float(relative_mass_error),
        "active_cell_count": int(projection_stats["active_cell_count"]),
        "solid_phi_min": float(np.min(solid_phi)),
        "solid_phi_max": float(np.max(solid_phi)),
        "occupied_count_32": int(voxelized_32["occupied_count"]),
        "occupied_fraction_32": float(voxelized_32["occupied_count"]) / float(32**3),
        "particle_bounds_min_x": float(bounds_min[0]),
        "particle_bounds_min_y": float(bounds_min[1]),
        "particle_bounds_min_z": float(bounds_min[2]),
        "particle_bounds_max_x": float(bounds_max[0]),
        "particle_bounds_max_y": float(bounds_max[1]),
        "particle_bounds_max_z": float(bounds_max[2]),
        "stable": True,
        "notes": "projection quality only; no FSI force path",
    }
    assert_projection_quality_row(row)
    return row


def assert_particle_cloud(cloud, expected_count):
    x = np.asarray(cloud["x"])
    vol0 = np.asarray(cloud["vol0"])
    mass = np.asarray(cloud["mass"])

    if x.shape != (expected_count, 3):
        raise RuntimeError(f"unexpected particle shape: {x.shape}")
    assert_no_nan_inf_array("particles_x", x)
    assert_no_nan_inf_array("particle_vol0", vol0)
    assert_no_nan_inf_array("particle_mass", mass)
    if float(np.min(x)) < 0.0 or float(np.max(x)) > 1.0:
        raise RuntimeError("particle positions escaped [0, 1]^3")
    if not np.all(vol0 > 0.0):
        raise RuntimeError("particle vol0 must be positive")
    if not np.all(mass > 0.0):
        raise RuntimeError("particle mass must be positive")


def assert_driver_row(row):
    _assert_row_finite(
        row,
        excluded=("case", "geometry_type", "geometry_source", "mode", "reaction_transfer_mode", "stable", "notes"),
    )
    if not _as_bool(row["stable"]):
        raise RuntimeError(f"unstable driver row: {row}")
    if float(row["rho_min"]) <= 0.95 or float(row["rho_max"]) >= 1.05:
        raise RuntimeError(f"rho outside accepted range: {row}")
    if float(row["lbm_max_v"]) >= 0.1:
        raise RuntimeError(f"lbm_max_v exceeded accepted range: {row}")
    if float(row["mpm_min_J"]) <= 0.0:
        raise RuntimeError(f"mpm_min_J became non-positive: {row}")
    if float(row["mpm_max_speed"]) >= 10.0:
        raise RuntimeError(f"mpm_max_speed exceeded accepted range: {row}")
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError(f"projected_mass must be positive: {row}")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"active_cell_count must be positive: {row}")
    if row["mode"] == "none" and float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("none row must keep cell_force at zero")
    if row["mode"] == "penalty" and float(row["cell_force_max_norm"]) <= 0.0:
        raise RuntimeError("penalty row must produce finite positive cell_force")
    if row["mode"] == "moving_boundary":
        if float(row["cell_force_max_norm"]) != 0.0:
            raise RuntimeError("moving_boundary row must keep cell_force at zero")
        if int(row["bb_link_count"]) <= 0:
            raise RuntimeError("moving_boundary row must record bounce-back links")
        if float(row["hydro_force_max_norm"]) <= 0.0:
            raise RuntimeError("moving_boundary row must record hydro_force")
    if row["reaction_transfer_mode"] == "link_area_experimental" and not np.isfinite(float(row["area_scale_final"])):
        raise RuntimeError("link_area_experimental row must record finite area_scale_final")


def assert_projection_quality_row(row):
    _assert_row_finite(row, excluded=("case", "geometry_type", "stable", "notes"))
    if not _as_bool(row["stable"]):
        raise RuntimeError(f"unstable projection row: {row}")
    if int(row["particle_count"]) != 4096:
        raise RuntimeError(f"unexpected particle_count: {row}")
    if float(row["geometry_volume"]) <= 0.0:
        raise RuntimeError(f"geometry_volume must be positive: {row}")
    if float(row["particle_mass_sum"]) <= 0.0:
        raise RuntimeError(f"particle_mass_sum must be positive: {row}")
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError(f"projected_mass must be positive: {row}")
    if abs(float(row["relative_mass_error"])) >= 1.0e-4:
        raise RuntimeError(f"relative_mass_error too high: {row}")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError(f"active_cell_count must be positive: {row}")
    if float(row["solid_phi_min"]) < 0.0 or float(row["solid_phi_max"]) > 1.0:
        raise RuntimeError(f"solid_phi outside [0, 1]: {row}")
    for key in (
        "particle_bounds_min_x",
        "particle_bounds_min_y",
        "particle_bounds_min_z",
        "particle_bounds_max_x",
        "particle_bounds_max_y",
        "particle_bounds_max_z",
    ):
        if float(row[key]) < 0.0 or float(row[key]) > 1.0:
            raise RuntimeError(f"particle bounds outside [0, 1]: {row}")


def assert_summary_row(row):
    _assert_row_finite(row, excluded=("stable", "notes"))
    if not _as_bool(row["stable"]):
        raise RuntimeError(f"unstable summary row: {row}")
    if int(row["required_row_count"]) < 18:
        raise RuntimeError(f"required_row_count too low: {row}")
    if int(row["projection_quality_row_count"]) < 3:
        raise RuntimeError(f"projection_quality_row_count too low: {row}")
    if float(row["rho_min_global"]) <= 0.95 or float(row["rho_max_global"]) >= 1.05:
        raise RuntimeError(f"rho global outside accepted range: {row}")
    if float(row["lbm_max_v_global"]) >= 0.1:
        raise RuntimeError(f"lbm_max_v global exceeded accepted range: {row}")
    if float(row["mpm_min_J_global"]) <= 0.0:
        raise RuntimeError(f"mpm_min_J global became non-positive: {row}")
    if float(row["mpm_max_speed_global"]) >= 10.0:
        raise RuntimeError(f"mpm_max_speed global exceeded accepted range: {row}")
    if float(row["max_relative_mass_error"]) >= 1.0e-4:
        raise RuntimeError(f"max_relative_mass_error exceeded accepted range: {row}")


def _case_output_name(config):
    transfer = config.reaction_transfer_mode
    mode = config.coupling_mode
    return f"{config.n_grid}_{mode}_{transfer}"


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
