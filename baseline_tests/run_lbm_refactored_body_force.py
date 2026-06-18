import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import LBMConfig, LBMFluid3D


def make_force_geo(path, nx, ny, nz):
    geo = np.zeros((nx, ny, nz), dtype=np.int32)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def compute_force_stats(lbm):
    stats = lbm.get_stats()
    vel = lbm.v.to_numpy()
    solid = lbm.solid.to_numpy()
    fluid = solid == 0
    ux = vel[..., 0]
    uy = vel[..., 1]
    uz = vel[..., 2]
    stats.update(
        {
            "mean_ux": float(np.mean(ux[fluid])),
            "max_abs_uy": float(np.max(np.abs(uy[fluid]))),
            "max_abs_uz": float(np.max(np.abs(uz[fluid]))),
        }
    )
    return stats


def assert_force_ok(stats, label):
    values = [
        stats["max_v"],
        stats["rho_min"],
        stats["rho_max"],
        stats["force_norm_max"],
        stats["mean_ux"],
        stats["max_abs_uy"],
        stats["max_abs_uz"],
    ]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{label} stats contain NaN or Inf: {stats}")
    if stats["rho_min"] <= 0.95 or stats["rho_max"] >= 1.05:
        raise RuntimeError(f"{label} rho left accepted range: {stats}")
    if stats["max_v"] >= 0.1:
        raise RuntimeError(f"{label} max_v exceeded hard limit: {stats}")


def main():
    ti.init(arch=ti.gpu, kernel_profiler=False, print_ir=False)

    nx, ny, nz = 32, 32, 32
    n_steps = 1000
    force_x = 1.0e-6
    out_dir = os.path.join(ROOT, "outputs", "lbm_refactored_force")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_force_32.dat")
    make_force_geo(geo_path, nx, ny, nz)

    lbm = LBMFluid3D(LBMConfig(nx=nx, ny=ny, nz=nz, niu=0.1))
    lbm.init_geo(geo_path)
    lbm.clear_coupling_fields()
    lbm.init_simulation()
    lbm.set_uniform_cell_force(force_x, 0.0, 0.0)

    initial_stats = compute_force_stats(lbm)
    if initial_stats["max_v"] != 0.0:
        raise RuntimeError(f"body-force initial velocity is not zero: {initial_stats}")

    t0 = time.time()
    max_v_values = []

    for it in range(n_steps + 1):
        lbm.step()

        if it % 200 == 0:
            stats = compute_force_stats(lbm)
            max_v_values.append(stats["max_v"])
            print(
                f"iter={it:04d}, max_v={stats['max_v']:.6e}, "
                f"rho_min={stats['rho_min']:.6e}, rho_max={stats['rho_max']:.6e}, "
                f"mean_ux={stats['mean_ux']:.6e}, "
                f"max_abs_uy={stats['max_abs_uy']:.6e}, max_abs_uz={stats['max_abs_uz']:.6e}, "
                f"force_norm_max={stats['force_norm_max']:.6e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )
            assert_force_ok(stats, "body-force")

    lbm.build_dummy_hydro_force()
    out_prefix = os.path.join(out_dir, "LBMFluid")
    lbm.export_VTK(n_steps, out_prefix=out_prefix)
    vtk_path = f"{out_prefix}_{n_steps}.vtr"
    if not os.path.isfile(vtk_path):
        raise RuntimeError(f"Missing VTK output: {vtk_path}")

    final_stats = compute_force_stats(lbm)
    assert_force_ok(final_stats, "body-force final")
    if final_stats["max_v"] <= initial_stats["max_v"] + 1.0e-8:
        raise RuntimeError(f"cell_force did not increase max_v: initial={initial_stats}, final={final_stats}")
    if abs(final_stats["force_norm_max"] - force_x) > 1.0e-12:
        raise RuntimeError(f"cell_force norm mismatch: {final_stats}")
    if final_stats["mean_ux"] <= 0.0:
        raise RuntimeError(f"body-force mean ux did not become positive: {final_stats}")
    if final_stats["max_abs_uy"] > final_stats["mean_ux"] * 0.05 + 1.0e-10:
        raise RuntimeError(f"body-force generated too much transverse y velocity: {final_stats}")
    if final_stats["max_abs_uz"] > final_stats["mean_ux"] * 0.05 + 1.0e-10:
        raise RuntimeError(f"body-force generated too much transverse z velocity: {final_stats}")

    print(
        "[OK] Step 2 refactored body-force baseline finished. "
        f"initial_max_v={initial_stats['max_v']:.6e}, "
        f"max_v_min={min(max_v_values):.6e}, "
        f"max_v_max={max(max_v_values):.6e}, "
        f"final_max_v={final_stats['max_v']:.6e}, "
        f"rho_min={final_stats['rho_min']:.6e}, "
        f"rho_max={final_stats['rho_max']:.6e}, "
        f"mean_ux={final_stats['mean_ux']:.6e}, "
        f"force_norm_max={final_stats['force_norm_max']:.6e}, "
        f"vtk={vtk_path}"
    )


if __name__ == "__main__":
    main()
