import os

import taichi as ti

from step21_common import ROOT, run_driver_config_paths


CONFIGS = [
    "configs/step21_mesh_ellipsoid_48_none.json",
    "configs/step21_mesh_ellipsoid_48_penalty.json",
    "configs/step21_mesh_ellipsoid_48_moving_boundary.json",
    "configs/step21_mesh_ellipsoid_48_link_area.json",
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step21_mesh_ellipsoid_48_modes")
    run_driver_config_paths(
        "mesh_ellipsoid",
        CONFIGS,
        out_dir,
        "mesh_ellipsoid_48_results.csv",
        "mesh_ellipsoid_48_results.npz",
    )
    print("[OK] Step 21 mesh_ellipsoid 48 modes finished")


if __name__ == "__main__":
    main()
