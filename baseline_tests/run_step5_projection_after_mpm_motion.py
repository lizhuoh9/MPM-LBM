import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import GridUnitMapper, LBMFluid3D, MPMToLBMProjector3D, MPMSolid3D, UnifiedSimConfig


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


def save_frame(lbm, out_dir, frame):
    np.save(os.path.join(out_dir, f"solid_phi_{frame}.npy"), lbm.solid_phi.to_numpy())
    np.save(os.path.join(out_dir, f"solid_mass_{frame}.npy"), lbm.solid_mass.to_numpy())
    np.save(os.path.join(out_dir, f"solid_vel_{frame}.npy"), lbm.solid_vel.to_numpy())
    lbm.export_VTK(frame, out_prefix=os.path.join(out_dir, "LBMProjection"))


def projection_snapshot(projector, solid, lbm):
    projector.project(solid, lbm)
    stats = projector.get_stats()
    x_np = solid.x.to_numpy()
    solid_phi = lbm.solid_phi.to_numpy()
    solid_mass = lbm.solid_mass.to_numpy()
    solid_vel = lbm.solid_vel.to_numpy()
    assert_finite("particles_x", x_np)
    assert_finite("solid_phi", solid_phi)
    assert_finite("solid_mass", solid_mass)
    assert_finite("solid_vel", solid_vel)
    return {
        "stats": stats,
        "center_x": float(np.mean(x_np[:, 0])),
        "index_min": np.min(np.floor(x_np * projector.inv_dx_norm).astype(np.int32), axis=0),
        "index_max": np.max(np.floor(x_np * projector.inv_dx_norm).astype(np.int32), axis=0),
    }


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.02, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    mpm_substeps = 50

    out_dir = os.path.join(ROOT, "outputs", "step5_projection_motion")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_motion_32.dat")
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
    solid.set_uniform_velocity(float(target_u_norm[0]), float(target_u_norm[1]), float(target_u_norm[2]))

    projector = MPMToLBMProjector3D(sim)
    initial = projection_snapshot(projector, solid, lbm)
    save_frame(lbm, out_dir, 0)

    for _ in range(mpm_substeps):
        solid.substep()

    final = projection_snapshot(projector, solid, lbm)
    save_frame(lbm, out_dir, 1)

    total_particle_mass = float(np.sum(solid.mass.to_numpy()))
    initial_mass_error = abs(initial["stats"]["projected_mass"] - total_particle_mass) / max(
        total_particle_mass, 1.0e-12
    )
    final_mass_error = abs(final["stats"]["projected_mass"] - total_particle_mass) / max(
        total_particle_mass, 1.0e-12
    )

    print("Step 5 projection after MPM motion baseline")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"mpm_substeps={mpm_substeps}")
    print(f"center_x_initial={initial['center_x']:.9e}")
    print(f"center_x_final={final['center_x']:.9e}")
    print(f"index_min_initial={initial['index_min'].tolist()}")
    print(f"index_max_initial={initial['index_max'].tolist()}")
    print(f"index_min_final={final['index_min'].tolist()}")
    print(f"index_max_final={final['index_max'].tolist()}")
    print(f"active_cell_count_initial={initial['stats']['active_cell_count']}")
    print(f"active_cell_count_final={final['stats']['active_cell_count']}")
    print(f"relative_mass_error_initial={initial_mass_error:.9e}")
    print(f"relative_mass_error_final={final_mass_error:.9e}")
    print(f"elapsed={time.time() - t0:.2f}s")

    if final["center_x"] <= initial["center_x"]:
        raise RuntimeError("particle center_x did not increase")
    if initial["stats"]["active_cell_count"] <= 0 or final["stats"]["active_cell_count"] <= 0:
        raise RuntimeError("projection created no active cells")
    if initial_mass_error >= 1.0e-5 or final_mass_error >= 1.0e-5:
        raise RuntimeError(f"projected mass error too high: {initial_mass_error}, {final_mass_error}")

    assert_force_fields_zero(lbm)
    print("[OK] Step 5 projection after MPM motion baseline finished")


if __name__ == "__main__":
    main()
