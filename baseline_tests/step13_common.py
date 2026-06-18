import json
import os

import numpy as np

from src import GeometryConfig, GeometrySampler3D, LBMFluid3D, MPMToLBMProjector3D, MPMSolid3D, UnifiedSimConfig
from src.run_utils import assert_no_nan_inf_array, make_all_fluid_geo


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def save_geometry_arrays(out_dir, cloud, voxel=None):
    os.makedirs(out_dir, exist_ok=True)
    np.save(os.path.join(out_dir, "particles_x.npy"), cloud["x"])
    np.save(os.path.join(out_dir, "particles_vol0.npy"), cloud["vol0"])
    np.save(os.path.join(out_dir, "particles_mass.npy"), cloud["mass"])
    if voxel is not None:
        np.save(os.path.join(out_dir, "geometry_occupancy.npy"), voxel["occupancy"])


def run_projection_case(geometry_config: GeometryConfig, out_dir: str, n_grid: int = 32):
    os.makedirs(out_dir, exist_ok=True)
    sampler = GeometrySampler3D(geometry_config)
    cloud = sampler.sample_particles()

    sim = UnifiedSimConfig(n_grid=n_grid, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    geo_path = os.path.join(out_dir, f"geo_all_fluid_{n_grid}.dat")
    make_all_fluid_geo(geo_path, n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(gravity=(0.0, 0.0, 0.0), box_min=geometry_config.box_min, box_max=geometry_config.box_max),
        n_particles=geometry_config.n_particles,
    )
    solid.init_from_numpy(cloud["x"], cloud["vol0"], cloud["mass"])

    projector = MPMToLBMProjector3D(sim)
    projector.project(solid, lbm)

    solid_stats = solid.get_stats()
    projection_stats = projector.get_stats()
    solid_phi = lbm.solid_phi.to_numpy()
    solid_vel = lbm.solid_vel.to_numpy()
    cell_force = lbm.cell_force.to_numpy()
    hydro_force = lbm.hydro_force.to_numpy()

    assert_no_nan_inf_array("particles_x", cloud["x"])
    assert_no_nan_inf_array("particles_vol0", cloud["vol0"])
    assert_no_nan_inf_array("particles_mass", cloud["mass"])
    assert_no_nan_inf_array("solid_phi", solid_phi)
    assert_no_nan_inf_array("solid_vel", solid_vel)
    assert_no_nan_inf_array("cell_force", cell_force)
    assert_no_nan_inf_array("hydro_force", hydro_force)

    np.save(os.path.join(out_dir, "solid_phi.npy"), solid_phi)

    stats = {
        "geometry_type": geometry_config.geometry_type,
        "particle_count": int(geometry_config.n_particles),
        "geometry_volume": float(cloud["geometry_volume"]),
        "total_mass": float(np.sum(cloud["mass"])),
        "particle_min": [float(v) for v in np.min(cloud["x"], axis=0)],
        "particle_max": [float(v) for v in np.max(cloud["x"], axis=0)],
        "mpm_min_J": float(solid_stats["min_J"]),
        "mpm_max_J": float(solid_stats["max_J"]),
        "mpm_max_speed": float(solid_stats["max_speed"]),
        "projected_mass": float(projection_stats["projected_mass"]),
        "projected_volume_raw": float(projection_stats["projected_volume_raw"]),
        "projected_volume_clamped": float(projection_stats["projected_volume_clamped"]),
        "active_cell_count": int(projection_stats["active_cell_count"]),
        "max_phi_raw": float(projection_stats["max_phi_raw"]),
        "solid_phi_min": float(np.min(solid_phi)),
        "solid_phi_max": float(np.max(solid_phi)),
        "cell_force_max_norm": float(np.max(np.linalg.norm(cell_force.reshape(-1, 3), axis=1))),
        "hydro_force_max_norm": float(np.max(np.linalg.norm(hydro_force.reshape(-1, 3), axis=1))),
    }
    stats.update(cloud["sampling_stats"])

    return {
        "sampler": sampler,
        "cloud": cloud,
        "solid": solid,
        "lbm": lbm,
        "projector": projector,
        "stats": stats,
    }
