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


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32)
    threshold = 0.5
    out_dir = os.path.join(ROOT, "outputs", "step5_dynamic_solid_mask")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_mask_32.dat")
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
    projection_stats = projector.get_stats()

    lbm.update_dynamic_solid(threshold)
    solid_on = lbm.solid.to_numpy()
    reinit_after_on = lbm.reinit_flag.to_numpy()
    solid_on_count = int(np.count_nonzero(solid_on))
    reinit_after_on_count = int(np.count_nonzero(reinit_after_on))
    np.save(os.path.join(out_dir, "solid_on.npy"), solid_on)
    lbm.export_VTK("mask_on", out_prefix=os.path.join(out_dir, "LBMProjection"))

    projector.clear_projection(lbm)
    lbm.update_dynamic_solid(threshold)
    reinit_before_clear = lbm.reinit_flag.to_numpy()
    reinit_count = int(np.count_nonzero(reinit_before_clear))
    lbm.reinitialize_new_fluid_cells()
    solid_off = lbm.solid.to_numpy()
    np.save(os.path.join(out_dir, "solid_off.npy"), solid_off)
    lbm.export_VTK("mask_off", out_prefix=os.path.join(out_dir, "LBMProjection"))

    solid_off_count = int(np.count_nonzero(solid_off))
    rho_np = lbm.rho.to_numpy()
    vel_np = lbm.v.to_numpy()
    assert_finite("rho", rho_np)
    assert_finite("velocity", vel_np)

    print("Step 5 dynamic solid mask dry run")
    print(f"threshold={threshold:.6f}")
    print(f"active_cell_count={projection_stats['active_cell_count']}")
    print(f"solid_on_count={solid_on_count}")
    print(f"solid_off_count={solid_off_count}")
    print(f"reinit_after_on_count={reinit_after_on_count}")
    print(f"reinit_count={reinit_count}")
    print(f"rho_min={float(np.min(rho_np)):.9e}")
    print(f"rho_max={float(np.max(rho_np)):.9e}")
    print(f"velocity_max={float(np.max(np.linalg.norm(vel_np, axis=3))):.9e}")
    print(f"elapsed={time.time() - t0:.2f}s")

    if solid_on_count <= 0:
        raise RuntimeError("dynamic mask did not turn on any cells")
    if solid_off_count != 0:
        raise RuntimeError(f"dynamic mask did not clear to all-fluid: {solid_off_count}")
    if reinit_count <= 0:
        raise RuntimeError("dynamic mask clear did not mark reinitialized cells")

    assert_force_fields_zero(lbm)
    print("[OK] Step 5 dynamic solid mask dry run finished")


if __name__ == "__main__":
    main()
