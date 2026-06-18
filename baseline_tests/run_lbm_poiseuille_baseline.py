import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LBM_DIR = os.path.join(ROOT, "external", "taichi_LBM3D", "Single_phase")
sys.path.insert(0, LBM_DIR)


def make_channel_geo(path, nx, ny, nz):
    """Create a pressure-driven x-channel with solid walls on y/z boundaries."""
    geo = np.zeros((nx, ny, nz), dtype=np.int32)
    geo[:, 0, :] = 1
    geo[:, -1, :] = 1
    geo[:, :, 0] = 1
    geo[:, :, -1] = 1
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def compute_channel_stats(lb3d):
    rho = lb3d.rho.to_numpy()
    vel = lb3d.v.to_numpy()
    solid = lb3d.solid.to_numpy()

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

    mean_ux = float(np.mean(ux[fluid]))
    max_abs_uy = float(np.max(np.abs(uy[fluid])))
    max_abs_uz = float(np.max(np.abs(uz[fluid])))

    return {
        "rho_min": float(np.min(rho[fluid])),
        "rho_max": float(np.max(rho[fluid])),
        "mean_ux": mean_ux,
        "center_ux": center_ux,
        "near_wall_ux": near_wall_ux,
        "max_abs_uy": max_abs_uy,
        "max_abs_uz": max_abs_uz,
    }


def main():
    ti.init(arch=ti.gpu, kernel_profiler=False, print_ir=False)

    import LBM_3D_SinglePhase_Solver as lbm

    nx, ny, nz = 32, 32, 32
    n_steps = 1000
    rho_in = 1.0001
    rho_out = 1.0
    out_dir = os.path.join(ROOT, "outputs", "lbm_poiseuille")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_poiseuille_32.dat")
    make_channel_geo(geo_path, nx, ny, nz)

    lb3d = lbm.LB3D_Solver_Single_Phase(
        nx=nx,
        ny=ny,
        nz=nz,
        sparse_storage=False,
    )
    lb3d.set_viscosity(0.1)
    lb3d.init_geo(geo_path)
    lb3d.set_bc_rho_x0(rho_in)
    lb3d.set_bc_rho_x1(rho_out)
    lb3d.init_simulation()

    t0 = time.time()
    max_v_values = []

    for it in range(n_steps + 1):
        lb3d.step()

        if it % 200 == 0:
            max_v = float(lb3d.get_max_v())
            max_v_values.append(max_v)
            stats = compute_channel_stats(lb3d)
            print(
                f"iter={it:04d}, max_v={max_v:.6e}, "
                f"rho_min={stats['rho_min']:.6e}, rho_max={stats['rho_max']:.6e}, "
                f"mean_ux={stats['mean_ux']:.6e}, center_ux={stats['center_ux']:.6e}, "
                f"near_wall_ux={stats['near_wall_ux']:.6e}, elapsed={time.time() - t0:.2f}s"
            )

            if not np.isfinite(max_v):
                raise RuntimeError("Poiseuille max_v is NaN or Inf")
            if stats["rho_min"] <= 0.95 or stats["rho_max"] >= 1.05:
                raise RuntimeError("Poiseuille rho left the accepted range")
            if max_v >= 0.05:
                raise RuntimeError("Poiseuille max_v exceeded 0.05")

        if it == n_steps:
            old_cwd = os.getcwd()
            try:
                os.chdir(out_dir)
                lb3d.export_VTK(it)
            finally:
                os.chdir(old_cwd)

    final_max_v = float(lb3d.get_max_v())
    final_stats = compute_channel_stats(lb3d)

    if final_stats["mean_ux"] <= 0.0:
        raise RuntimeError("Poiseuille mean ux did not become positive")
    if final_stats["center_ux"] <= final_stats["near_wall_ux"]:
        raise RuntimeError("Poiseuille channel profile did not show centerline speed above near-wall speed")
    print(
        "[OK] LBM Poiseuille baseline finished. "
        f"max_v_min={min(max_v_values):.6e}, "
        f"max_v_max={max(max_v_values):.6e}, "
        f"final_max_v={final_max_v:.6e}, "
        f"rho_min={final_stats['rho_min']:.6e}, "
        f"rho_max={final_stats['rho_max']:.6e}, "
        f"mean_ux={final_stats['mean_ux']:.6e}, "
        f"center_ux={final_stats['center_ux']:.6e}, "
        f"near_wall_ux={final_stats['near_wall_ux']:.6e}, "
        f"max_abs_uy={final_stats['max_abs_uy']:.6e}, "
        f"max_abs_uz={final_stats['max_abs_uz']:.6e}"
    )


if __name__ == "__main__":
    main()
