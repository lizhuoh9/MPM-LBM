import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LBM_DIR = os.path.join(ROOT, "external", "taichi_LBM3D", "Single_phase")
sys.path.insert(0, LBM_DIR)


def make_smoke_geo(path, nx, ny, nz):
    """Create a small all-fluid geometry file for the LBM smoke baseline."""
    geo = np.zeros((nx, ny, nz), dtype=np.int32)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def main():
    ti.init(arch=ti.gpu, kernel_profiler=False, print_ir=False)

    import LBM_3D_SinglePhase_Solver as lbm

    nx, ny, nz = 32, 32, 32
    n_steps = 500
    out_dir = os.path.join(ROOT, "outputs", "lbm_smoke")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_smoke_32.dat")
    make_smoke_geo(geo_path, nx, ny, nz)

    lb3d = lbm.LB3D_Solver_Single_Phase(
        nx=nx,
        ny=ny,
        nz=nz,
        sparse_storage=False,
    )
    lb3d.set_viscosity(0.16667)
    lb3d.init_geo(geo_path)
    lb3d.set_bc_vel_x1([0.0, 0.0, 0.03])
    lb3d.init_simulation()

    t0 = time.time()
    max_v_values = []

    for it in range(n_steps + 1):
        lb3d.step()

        if it % 100 == 0:
            max_v = float(lb3d.get_max_v())
            max_v_values.append(max_v)
            print(f"iter={it:04d}, max_v={max_v:.6e}, elapsed={time.time() - t0:.2f}s")

            if not np.isfinite(max_v):
                raise RuntimeError("LBM max_v is NaN or Inf")

        if it == n_steps:
            old_cwd = os.getcwd()
            try:
                os.chdir(out_dir)
                lb3d.export_VTK(it)
            finally:
                os.chdir(old_cwd)

    rho_np = lb3d.rho.to_numpy()
    vel_np = lb3d.v.to_numpy()
    if not np.all(np.isfinite(rho_np)):
        raise RuntimeError("LBM rho contains NaN or Inf")
    if not np.all(np.isfinite(vel_np)):
        raise RuntimeError("LBM velocity contains NaN or Inf")

    print(
        "[OK] LBM all-fluid smoke baseline finished. "
        f"max_v_min={min(max_v_values):.6e}, "
        f"max_v_max={max(max_v_values):.6e}, "
        f"rho_min={float(np.min(rho_np)):.6e}, "
        f"rho_max={float(np.max(rho_np)):.6e}"
    )


if __name__ == "__main__":
    main()
