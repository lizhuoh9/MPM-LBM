import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import LBMConfig, LBMFluid3D


def make_smoke_geo(path, nx, ny, nz):
    geo = np.zeros((nx, ny, nz), dtype=np.int32)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def assert_stats_ok(stats, label):
    values = [stats["max_v"], stats["rho_min"], stats["rho_max"], stats["mass_total"]]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{label} stats contain NaN or Inf: {stats}")
    if stats["rho_min"] <= 0.95 or stats["rho_max"] >= 1.05:
        raise RuntimeError(f"{label} rho left accepted range: {stats}")
    if stats["max_v"] >= 0.1:
        raise RuntimeError(f"{label} max_v exceeded hard limit: {stats}")


def main():
    ti.init(arch=ti.gpu, kernel_profiler=False, print_ir=False)

    nx, ny, nz = 32, 32, 32
    n_steps = 500
    out_dir = os.path.join(ROOT, "outputs", "lbm_refactored_smoke")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_smoke_32.dat")
    make_smoke_geo(geo_path, nx, ny, nz)

    config = LBMConfig(
        nx=nx,
        ny=ny,
        nz=nz,
        niu=0.16667,
        bc_x_right=2,
        vel_bc_x_right=(0.0, 0.0, 0.03),
    )
    lbm = LBMFluid3D(config)
    lbm.init_geo(geo_path)
    lbm.clear_coupling_fields()
    lbm.init_simulation()

    t0 = time.time()
    max_v_values = []

    for it in range(n_steps + 1):
        lbm.step()

        if it % 100 == 0:
            stats = lbm.get_stats()
            max_v_values.append(stats["max_v"])
            print(
                f"iter={it:04d}, max_v={stats['max_v']:.6e}, "
                f"rho_min={stats['rho_min']:.6e}, rho_max={stats['rho_max']:.6e}, "
                f"force_norm_max={stats['force_norm_max']:.6e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )
            assert_stats_ok(stats, "smoke")

    out_prefix = os.path.join(out_dir, "LBMFluid")
    lbm.export_VTK(n_steps, out_prefix=out_prefix)
    vtk_path = f"{out_prefix}_{n_steps}.vtr"
    if not os.path.isfile(vtk_path):
        raise RuntimeError(f"Missing VTK output: {vtk_path}")

    final_stats = lbm.get_stats()
    assert_stats_ok(final_stats, "smoke final")
    if final_stats["max_v"] >= 0.05:
        raise RuntimeError(f"smoke max_v exceeded preferred limit: {final_stats}")

    print(
        "[OK] Step 2 refactored smoke baseline finished. "
        f"max_v_min={min(max_v_values):.6e}, "
        f"max_v_max={max(max_v_values):.6e}, "
        f"rho_min={final_stats['rho_min']:.6e}, "
        f"rho_max={final_stats['rho_max']:.6e}, "
        f"mass_total={final_stats['mass_total']:.6e}, "
        f"force_norm_max={final_stats['force_norm_max']:.6e}, "
        f"vtk={vtk_path}"
    )


if __name__ == "__main__":
    main()
