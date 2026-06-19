import os

import taichi as ti

from step21_common import ROOT, run_driver_config_paths


CONFIGS = [
    "configs/step21_mesh_cube_48_none.json",
    "configs/step21_mesh_cube_48_penalty.json",
    "configs/step21_mesh_cube_48_moving_boundary.json",
    "configs/step21_mesh_cube_48_link_area.json",
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step21_mesh_cube_48_modes")
    run_driver_config_paths("mesh_cube", CONFIGS, out_dir, "mesh_cube_48_results.csv", "mesh_cube_48_results.npz")
    print("[OK] Step 21 mesh_cube 48 modes finished")


if __name__ == "__main__":
    main()
