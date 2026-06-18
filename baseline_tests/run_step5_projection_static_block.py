import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import LBMFluid3D, MPMToLBMProjector3D, MPMSolid3D, UnifiedSimConfig


def make_all_fluid_geo(path, n_grid):
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int8)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def assert_finite(name, values):
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{name} contains NaN or Inf")


def assert_force_fields_zero(lbm):
    cell_force = lbm.cell_force.to_numpy()
    hydro_force = lbm.hydro_force.to_numpy()
    cell_force_max = float(np.max(np.linalg.norm(cell_force, axis=3)))
    hydro_force_max = float(np.max(np.linalg.norm(hydro_force, axis=3)))
    print(f"cell_force_max_norm={cell_force_max:.6e}")
    print(f"hydro_force_max_norm={hydro_force_max:.6e}")
    if cell_force_max != 0.0:
        raise RuntimeError(f"cell_force changed: {cell_force_max}")
    if hydro_force_max != 0.0:
        raise RuntimeError(f"hydro_force changed: {hydro_force_max}")


def save_projection_arrays(lbm, solid, out_dir):
    np.save(os.path.join(out_dir, "solid_phi.npy"), lbm.solid_phi.to_numpy())
    np.save(os.path.join(out_dir, "solid_mass.npy"), lbm.solid_mass.to_numpy())
    np.save(os.path.join(out_dir, "solid_vel.npy"), lbm.solid_vel.to_numpy())
    np.save(os.path.join(out_dir, "particles_x.npy"), solid.x.to_numpy())


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32)
    out_dir = os.path.join(ROOT, "outputs", "step5_projection_static")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_static_32.dat")
    make_all_fluid_geo(geo_path, sim.n_grid)

    t0 = time.time()
    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(gravity=(0.0, 0.0, 0.0)),
        n_particles=4096,
    )
    solid.init_box()

    projector = MPMToLBMProjector3D(sim)
    projector.project(solid, lbm)
    stats = projector.get_stats()

    solid_phi = lbm.solid_phi.to_numpy()
    solid_mass = lbm.solid_mass.to_numpy()
    solid_vel = lbm.solid_vel.to_numpy()
    assert_finite("solid_phi", solid_phi)
    assert_finite("solid_mass", solid_mass)
    assert_finite("solid_vel", solid_vel)

    total_particle_mass = float(np.sum(solid.mass.to_numpy()))
    relative_mass_error = abs(stats["projected_mass"] - total_particle_mass) / max(
        total_particle_mass, 1.0e-12
    )
    active = solid_mass > 1.0e-12
    max_solid_speed_lbm = 0.0
    if np.any(active):
        max_solid_speed_lbm = float(np.max(np.linalg.norm(solid_vel[active], axis=1)))

    print("Step 5 static block projection baseline")
    print(f"projected_mass={stats['projected_mass']:.9e}")
    print(f"total_particle_mass={total_particle_mass:.9e}")
    print(f"relative_mass_error={relative_mass_error:.9e}")
    print(f"projected_volume_raw={stats['projected_volume_raw']:.9e}")
    print(f"projected_volume_clamped={stats['projected_volume_clamped']:.9e}")
    print(f"max_phi_raw={stats['max_phi_raw']:.9e}")
    print(f"active_cell_count={stats['active_cell_count']}")
    print(f"solid_phi_min={float(np.min(solid_phi)):.9e}")
    print(f"solid_phi_max={float(np.max(solid_phi)):.9e}")
    print(f"max_solid_speed_lbm={max_solid_speed_lbm:.9e}")
    print(f"elapsed={time.time() - t0:.2f}s")

    if relative_mass_error >= 1.0e-5:
        raise RuntimeError(f"projected mass error too high: {relative_mass_error}")
    if stats["active_cell_count"] <= 0:
        raise RuntimeError("projection created no active cells")
    if float(np.min(solid_phi)) < 0.0 or float(np.max(solid_phi)) > 1.0:
        raise RuntimeError("solid_phi outside [0, 1]")
    if max_solid_speed_lbm >= 1.0e-8:
        raise RuntimeError(f"static projected velocity is not zero: {max_solid_speed_lbm}")

    assert_force_fields_zero(lbm)
    save_projection_arrays(lbm, solid, out_dir)
    lbm.export_VTK(0, out_prefix=os.path.join(out_dir, "LBMProjection"))

    print("[OK] Step 5 static block projection baseline finished")


if __name__ == "__main__":
    main()
