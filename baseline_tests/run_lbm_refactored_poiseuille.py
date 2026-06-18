import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import LBMConfig, LBMFluid3D


def make_channel_geo(path, nx, ny, nz):
    geo = np.zeros((nx, ny, nz), dtype=np.int32)
    geo[:, 0, :] = 1
    geo[:, -1, :] = 1
    geo[:, :, 0] = 1
    geo[:, :, -1] = 1
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def compute_channel_stats(lbm):
    rho = lbm.rho.to_numpy()
    vel = lbm.v.to_numpy()
    solid = lbm.solid.to_numpy()

    if not np.all(np.isfinite(rho)):
        raise RuntimeError("Poiseuille rho contains NaN or Inf")
    if not np.all(np.isfinite(vel)):
        raise RuntimeError("Poiseuille velocity contains NaN or Inf")

    fluid = solid == 0
    ux = vel[..., 0]
    uy = vel[..., 1]
    uz = vel[..., 2]

    nx, ny, nz = rho.shape
    center_ux = float(np.mean(ux[:, ny // 2, nz // 2]))
    near_wall_samples = [
        ux[:, 1, 1:-1],
        ux[:, ny - 2, 1:-1],
        ux[:, 1:-1, 1],
        ux[:, 1:-1, nz - 2],
    ]
    near_wall_ux = float(np.mean([np.mean(sample) for sample in near_wall_samples]))

    stats = lbm.get_stats()
    stats.update(
        {
            "mean_ux": float(np.mean(ux[fluid])),
            "center_ux": center_ux,
            "near_wall_ux": near_wall_ux,
            "max_abs_uy": float(np.max(np.abs(uy[fluid]))),
            "max_abs_uz": float(np.max(np.abs(uz[fluid]))),
        }
    )
    return stats


def assert_channel_ok(stats, label):
    values = [
        stats["max_v"],
        stats["rho_min"],
        stats["rho_max"],
        stats["mean_ux"],
        stats["center_ux"],
        stats["near_wall_ux"],
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
    rho_in = 1.0001
    rho_out = 1.0
    out_dir = os.path.join(ROOT, "outputs", "lbm_refactored_poiseuille")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_poiseuille_32.dat")
    make_channel_geo(geo_path, nx, ny, nz)

    config = LBMConfig(
        nx=nx,
        ny=ny,
        nz=nz,
        niu=0.1,
        bc_x_left=1,
        bc_x_right=1,
        rho_bc_x_left=rho_in,
        rho_bc_x_right=rho_out,
    )
    lbm = LBMFluid3D(config)
    lbm.init_geo(geo_path)
    lbm.clear_coupling_fields()
    lbm.init_simulation()

    t0 = time.time()
    max_v_values = []

    for it in range(n_steps + 1):
        lbm.step()

        if it % 200 == 0:
            stats = compute_channel_stats(lbm)
            max_v_values.append(stats["max_v"])
            print(
                f"iter={it:04d}, max_v={stats['max_v']:.6e}, "
                f"rho_min={stats['rho_min']:.6e}, rho_max={stats['rho_max']:.6e}, "
                f"mean_ux={stats['mean_ux']:.6e}, center_ux={stats['center_ux']:.6e}, "
                f"near_wall_ux={stats['near_wall_ux']:.6e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )
            assert_channel_ok(stats, "Poiseuille")

    out_prefix = os.path.join(out_dir, "LBMFluid")
    lbm.export_VTK(n_steps, out_prefix=out_prefix)
    vtk_path = f"{out_prefix}_{n_steps}.vtr"
    if not os.path.isfile(vtk_path):
        raise RuntimeError(f"Missing VTK output: {vtk_path}")

    final_stats = compute_channel_stats(lbm)
    assert_channel_ok(final_stats, "Poiseuille final")
    if final_stats["max_v"] >= 0.05:
        raise RuntimeError(f"Poiseuille max_v exceeded preferred limit: {final_stats}")
    if final_stats["mean_ux"] <= 0.0:
        raise RuntimeError(f"Poiseuille mean ux did not become positive: {final_stats}")
    if final_stats["center_ux"] <= final_stats["near_wall_ux"]:
        raise RuntimeError(f"Poiseuille profile lacks centerline acceleration: {final_stats}")

    print(
        "[OK] Step 2 refactored Poiseuille baseline finished. "
        f"max_v_min={min(max_v_values):.6e}, "
        f"max_v_max={max(max_v_values):.6e}, "
        f"final_max_v={final_stats['max_v']:.6e}, "
        f"rho_min={final_stats['rho_min']:.6e}, "
        f"rho_max={final_stats['rho_max']:.6e}, "
        f"mean_ux={final_stats['mean_ux']:.6e}, "
        f"center_ux={final_stats['center_ux']:.6e}, "
        f"near_wall_ux={final_stats['near_wall_ux']:.6e}, "
        f"force_norm_max={final_stats['force_norm_max']:.6e}, "
        f"vtk={vtk_path}"
    )


if __name__ == "__main__":
    main()
