import json
import os

import numpy as np

from src import (
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
from src.run_utils import assert_no_nan_inf_array, make_all_fluid_geo, save_csv_rows


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


STEP20_PROJECTION_FIELDS = [
    "case",
    "geometry_type",
    "particle_count",
    "projected_mass",
    "active_cell_count",
    "solid_phi_min",
    "solid_phi_max",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "stable",
    "notes",
]


STEP20_DRIVER_FIELDS = [
    "case",
    "geometry_type",
    "mode",
    "reaction_transfer_mode",
    "n_grid",
    "n_particles",
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
    "stable",
    "notes",
]


def load_geometry_config(relative_path):
    return GeometryConfig.from_json(os.path.join(ROOT, relative_path))


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    normalized = [{field: row.get(field, "") for field in fieldnames} for row in rows]
    save_csv_rows(normalized, csv_path, fieldnames=fieldnames)

    payload = {"columns": np.asarray(fieldnames)}
    for string_key in ("case", "geometry_type", "mode", "reaction_transfer_mode", "stable", "notes"):
        if any(string_key in row for row in normalized):
            payload[string_key + "s"] = np.asarray([str(row.get(string_key, "")) for row in normalized])

    for field in fieldnames:
        values = [row.get(field, "") for row in normalized]
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            continue

    np.savez(npz_path, **payload)


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


def run_projection_case(case, geometry_config, out_dir, n_grid=32):
    os.makedirs(out_dir, exist_ok=True)
    harness = build_projection_harness(out_dir, geometry_config.n_particles, n_grid=n_grid)
    return run_projection_case_with_harness(case, geometry_config, out_dir, harness)


def build_projection_harness(out_dir, n_particles, n_grid=32):
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


def run_projection_case_with_harness(case, geometry_config, out_dir, harness):
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

    assert_no_nan_inf_array("solid_phi", solid_phi)
    assert_no_nan_inf_array("particles_x", particles)
    if float(np.min(solid_phi)) < 0.0 or float(np.max(solid_phi)) > 1.0:
        raise RuntimeError("solid_phi must stay in [0, 1]")

    case_dir = os.path.join(out_dir, case)
    os.makedirs(case_dir, exist_ok=True)
    np.save(os.path.join(case_dir, "solid_phi.npy"), solid_phi)
    np.save(os.path.join(case_dir, "particles_x.npy"), particles)

    row = {
        "case": case,
        "geometry_type": geometry_config.geometry_type,
        "particle_count": int(geometry_config.n_particles),
        "projected_mass": float(projection_stats["projected_mass"]),
        "active_cell_count": int(projection_stats["active_cell_count"]),
        "solid_phi_min": float(np.min(solid_phi)),
        "solid_phi_max": float(np.max(solid_phi)),
        "cell_force_max_norm": float(force_stats["max_cell_force_norm"]),
        "hydro_force_max_norm": float(force_stats["max_hydro_force_norm"]),
        "stable": True,
        "notes": "imported geometry projection only; no FSI force path",
    }
    assert_projection_row(row)
    return row


def make_driver_config(case, mode, geometry_type, geometry_config_path, reaction_transfer_mode="engineering"):
    return FSIDriverConfig(
        coupling_mode=mode,
        geometry_type=geometry_type,
        geometry_config_path=geometry_config_path,
        reaction_transfer_mode=reaction_transfer_mode,
        n_grid=32,
        n_particles=4096,
        n_lbm_steps=5,
        mpm_substeps_per_lbm_step=5,
        target_u_lbm=(0.005, 0.0, 0.0),
        mb_force_cap_norm=1.0e-5,
        output_interval=5,
        write_vtk=False,
        write_particles=False,
    )


def run_driver_case(case, config, out_dir):
    driver = FSIDriver3D(config, out_dir)
    diagnostics = driver.run()
    if not diagnostics:
        raise RuntimeError(f"empty diagnostics for {case}/{config.coupling_mode}")

    row = summarize_driver_case(case, config, diagnostics)
    assert_driver_row(row)
    return row


def summarize_driver_case(case, config, diagnostics):
    return {
        "case": case,
        "geometry_type": config.geometry_type,
        "mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "n_grid": int(config.n_grid),
        "n_particles": int(config.n_particles),
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
        "stable": True,
        "notes": "32^3 Step 20 imported geometry driver smoke baseline",
    }


def assert_projection_row(row):
    _assert_row_finite(row, excluded=("case", "geometry_type", "stable", "notes"))
    if float(row["projected_mass"]) <= 0.0:
        raise RuntimeError("projected_mass must be positive")
    if int(row["active_cell_count"]) <= 0:
        raise RuntimeError("active_cell_count must be positive")
    if float(row["solid_phi_min"]) < 0.0 or float(row["solid_phi_max"]) > 1.0:
        raise RuntimeError("solid_phi must stay in [0, 1]")
    if float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("projection-only baseline should not create cell_force")
    if float(row["hydro_force_max_norm"]) != 0.0:
        raise RuntimeError("projection-only baseline should not create hydro_force")


def assert_driver_row(row):
    _assert_row_finite(row, excluded=("case", "geometry_type", "mode", "reaction_transfer_mode", "stable", "notes"))
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
    if row["mode"] == "moving_boundary" and float(row["cell_force_max_norm"]) != 0.0:
        raise RuntimeError("moving_boundary row must keep cell_force at zero")


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
