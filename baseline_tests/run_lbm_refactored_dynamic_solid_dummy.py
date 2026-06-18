import os
import sys

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import LBMConfig, LBMFluid3D


def make_dynamic_geo(path, nx, ny, nz):
    geo = np.zeros((nx, ny, nz), dtype=np.int32)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def assert_no_nan(lbm, label):
    rho = lbm.rho.to_numpy()
    vel = lbm.v.to_numpy()
    if not np.all(np.isfinite(rho)):
        raise RuntimeError(f"{label} rho contains NaN or Inf")
    if not np.all(np.isfinite(vel)):
        raise RuntimeError(f"{label} velocity contains NaN or Inf")


def main():
    ti.init(arch=ti.gpu, kernel_profiler=False, print_ir=False)

    nx, ny, nz = 32, 32, 32
    out_dir = os.path.join(ROOT, "outputs", "lbm_refactored_dynamic_solid")
    os.makedirs(out_dir, exist_ok=True)

    geo_path = os.path.join(out_dir, "geo_dynamic_solid_32.dat")
    make_dynamic_geo(geo_path, nx, ny, nz)

    lbm = LBMFluid3D(LBMConfig(nx=nx, ny=ny, nz=nz, niu=0.1))
    lbm.init_geo(geo_path)
    lbm.copy_solid_to_static()
    lbm.clear_coupling_fields()
    lbm.init_simulation()

    lbm.set_dummy_solid_phi_block(12, 20, 12, 20, 12, 20)
    lbm.update_dynamic_solid(0.5)
    assert_no_nan(lbm, "dynamic solid on")

    solid_on = lbm.solid.to_numpy()
    solid_phi_on = lbm.solid_phi.to_numpy()
    solid_on_count = int(np.sum(solid_on))
    phi_on_count = int(np.sum(solid_phi_on >= 0.5))
    if solid_on_count != 512 or phi_on_count != 512:
        raise RuntimeError(
            f"dynamic solid block count mismatch: solid_on_count={solid_on_count}, phi_on_count={phi_on_count}"
        )

    on_prefix = os.path.join(out_dir, "LBMFluid_dynamic_on")
    lbm.export_VTK(0, out_prefix=on_prefix)
    on_vtk = f"{on_prefix}_0.vtr"
    if not os.path.isfile(on_vtk):
        raise RuntimeError(f"Missing VTK output: {on_vtk}")

    lbm.clear_coupling_fields()
    lbm.update_dynamic_solid(0.5)
    reinit_count = int(np.sum(lbm.reinit_flag.to_numpy()))
    if reinit_count != 512:
        raise RuntimeError(f"expected 512 reinit cells after solid clears, got {reinit_count}")

    lbm.reinitialize_new_fluid_cells()
    assert_no_nan(lbm, "dynamic solid off")

    solid_off_count = int(np.sum(lbm.solid.to_numpy()))
    phi_off_count = int(np.sum(lbm.solid_phi.to_numpy() >= 0.5))
    final_reinit_count = int(np.sum(lbm.reinit_flag.to_numpy()))
    if solid_off_count != 0 or phi_off_count != 0 or final_reinit_count != 0:
        raise RuntimeError(
            "dynamic solid did not clear cleanly: "
            f"solid_off_count={solid_off_count}, phi_off_count={phi_off_count}, "
            f"final_reinit_count={final_reinit_count}"
        )

    off_prefix = os.path.join(out_dir, "LBMFluid_dynamic_off")
    lbm.export_VTK(1, out_prefix=off_prefix)
    off_vtk = f"{off_prefix}_1.vtr"
    if not os.path.isfile(off_vtk):
        raise RuntimeError(f"Missing VTK output: {off_vtk}")

    final_stats = lbm.get_stats()
    values = [final_stats["max_v"], final_stats["rho_min"], final_stats["rho_max"]]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"dynamic solid stats contain NaN or Inf: {final_stats}")
    if final_stats["rho_min"] <= 0.95 or final_stats["rho_max"] >= 1.05:
        raise RuntimeError(f"dynamic solid rho left accepted range: {final_stats}")

    print(
        "[OK] Step 2 dynamic-solid dummy baseline finished. "
        f"solid_on_count={solid_on_count}, "
        f"phi_on_count={phi_on_count}, "
        f"reinit_count={reinit_count}, "
        f"solid_off_count={solid_off_count}, "
        f"phi_off_count={phi_off_count}, "
        f"rho_min={final_stats['rho_min']:.6e}, "
        f"rho_max={final_stats['rho_max']:.6e}, "
        f"on_vtk={on_vtk}, off_vtk={off_vtk}"
    )


if __name__ == "__main__":
    main()
