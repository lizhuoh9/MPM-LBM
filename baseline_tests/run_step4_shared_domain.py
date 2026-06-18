import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import GridUnitMapper, LBMFluid3D, MPMSolid3D, UnifiedSimConfig


def make_all_fluid_geo(path, n_grid):
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int32)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def assert_finite(name, values):
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{name} contains NaN or Inf")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32)
    mapper = GridUnitMapper.from_sim_config(sim)
    out_dir = os.path.join(ROOT, "outputs", "step4_shared_domain")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_shared_domain_32.dat")
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

    particles_x = solid.x.to_numpy()
    assert_finite("particles_x", particles_x)
    particle_lbm_indices = mapper.norm_to_lbm_index(particles_x)
    if np.min(particle_lbm_indices) < 0 or np.max(particle_lbm_indices) >= sim.n_grid:
        raise RuntimeError("particle mapped index outside LBM grid")

    np.save(os.path.join(out_dir, "particle_lbm_indices.npy"), particle_lbm_indices)
    np.save(os.path.join(out_dir, "particles_x.npy"), particles_x)

    print(f"lbm_shape=({lbm.nx}, {lbm.ny}, {lbm.nz})")
    print(f"mpm_grid={solid.n_grid}")
    print(f"dx_norm={sim.dx_norm:.8f}")
    print(f"lbm_dt_phys={sim.lbm_dt_phys:.8f}")
    print(f"particle_min={np.min(particles_x, axis=0).tolist()}")
    print(f"particle_max={np.max(particles_x, axis=0).tolist()}")
    print(f"index_min={np.min(particle_lbm_indices, axis=0).tolist()}")
    print(f"index_max={np.max(particle_lbm_indices, axis=0).tolist()}")
    print(f"elapsed={time.time() - t0:.2f}s")

    if (lbm.nx, lbm.ny, lbm.nz) != (sim.n_grid, sim.n_grid, sim.n_grid):
        raise RuntimeError("LBM grid shape does not match UnifiedSimConfig")
    if solid.n_grid != sim.n_grid:
        raise RuntimeError("MPM grid shape does not match UnifiedSimConfig")

    print("[OK] Step 4 shared domain baseline finished")


if __name__ == "__main__":
    main()
