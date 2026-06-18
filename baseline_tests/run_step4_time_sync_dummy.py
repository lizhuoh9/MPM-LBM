import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import LBMFluid3D, MPMSolid3D, UnifiedSimConfig


def make_all_fluid_geo(path, n_grid):
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int32)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def assert_finite_stats(lbm_stats, mpm_stats):
    values = [
        lbm_stats["max_v"],
        lbm_stats["rho_min"],
        lbm_stats["rho_max"],
        lbm_stats["mass_total"],
        lbm_stats["force_norm_max"],
        *mpm_stats["min_x"],
        *mpm_stats["max_x"],
        mpm_stats["max_speed"],
        mpm_stats["min_J"],
        mpm_stats["max_J"],
        mpm_stats["total_mass"],
    ]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"sync stats contain NaN or Inf: {lbm_stats}, {mpm_stats}")


def assert_outputs_exist(out_dir):
    required = [
        "LBMFluid_20.vtr",
        "particles_x.npy",
        "particles_v.npy",
        "particles_F.npy",
        "particles_J.npy",
    ]
    missing = [name for name in required if not os.path.isfile(os.path.join(out_dir, name))]
    if missing:
        raise RuntimeError(f"missing output files: {missing}")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    n_lbm_steps = 20
    output_interval = 5
    out_dir = os.path.join(ROOT, "outputs", "step4_time_sync_dummy")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_time_sync_32.dat")
    make_all_fluid_geo(geo_path, sim.n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config(force=(0.0, 0.0, 0.0)))
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(gravity=(0.0, 0.0, 0.0)),
        n_particles=4096,
    )
    solid.init_box()
    solid.set_uniform_velocity(0.0, 0.0, 0.0)

    print("Step 4 time sync dummy baseline")
    print(f"n_grid={sim.n_grid}")
    print(f"dx_norm={sim.dx_norm:.8f}")
    print(f"mpm_dt={sim.mpm_dt:.8f}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"lbm_dt_phys={sim.lbm_dt_phys:.8f}")

    t0 = time.time()
    total_mpm_substeps = 0
    final_lbm_stats = None
    final_mpm_stats = None

    for lbm_step in range(n_lbm_steps + 1):
        if lbm_step > 0:
            lbm.step()
            for _ in range(sim.mpm_substeps_per_lbm_step):
                solid.substep()
                total_mpm_substeps += 1

        if lbm_step % output_interval == 0:
            lbm_stats = lbm.get_stats()
            mpm_stats = solid.get_stats()
            assert_finite_stats(lbm_stats, mpm_stats)
            print(
                f"lbm_step={lbm_step:04d}, total_mpm_substeps={total_mpm_substeps}, "
                f"rho_min={lbm_stats['rho_min']:.6f}, rho_max={lbm_stats['rho_max']:.6f}, "
                f"lbm_max_v={lbm_stats['max_v']:.6e}, mpm_min_J={mpm_stats['min_J']:.6f}, "
                f"mpm_max_speed={mpm_stats['max_speed']:.6e}, elapsed={time.time() - t0:.2f}s"
            )
            final_lbm_stats = lbm_stats
            final_mpm_stats = mpm_stats

    expected_substeps = n_lbm_steps * sim.mpm_substeps_per_lbm_step
    if total_mpm_substeps != expected_substeps:
        raise RuntimeError(f"unexpected MPM substep count: {total_mpm_substeps} != {expected_substeps}")
    if final_lbm_stats["rho_min"] <= 0.95 or final_lbm_stats["rho_max"] >= 1.05:
        raise RuntimeError(f"LBM rho left accepted range: {final_lbm_stats}")
    if final_lbm_stats["max_v"] >= 0.1:
        raise RuntimeError(f"LBM max_v exceeded threshold: {final_lbm_stats}")
    if final_mpm_stats["min_J"] <= 0.0:
        raise RuntimeError(f"MPM min_J became non-positive: {final_mpm_stats}")
    if final_mpm_stats["max_speed"] >= 10.0:
        raise RuntimeError(f"MPM max_speed exceeded threshold: {final_mpm_stats}")

    lbm.export_VTK(n_lbm_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))
    solid.export_particles(out_dir)
    assert_outputs_exist(out_dir)

    print(
        "[OK] Step 4 time sync dummy baseline finished. "
        f"completed_lbm_steps={n_lbm_steps}, total_mpm_substeps={total_mpm_substeps}, "
        f"rho_min={final_lbm_stats['rho_min']:.6f}, rho_max={final_lbm_stats['rho_max']:.6f}, "
        f"lbm_max_v={final_lbm_stats['max_v']:.6e}, mpm_min_J={final_mpm_stats['min_J']:.6f}, "
        f"mpm_max_speed={final_mpm_stats['max_speed']:.6e}, out_dir={out_dir}"
    )


if __name__ == "__main__":
    main()
