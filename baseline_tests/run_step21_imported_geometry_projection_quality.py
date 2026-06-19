import os

import taichi as ti

from step21_common import ROOT, run_projection_quality_cases


CASES = [
    ("voxel_sphere", "configs/step20_voxel_sphere_geometry.json"),
    ("mesh_cube", "configs/step20_mesh_cube_geometry.json"),
    ("mesh_ellipsoid", "configs/step20_mesh_ellipsoid_geometry.json"),
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step21_imported_geometry_projection_quality")
    run_projection_quality_cases(CASES, out_dir, n_grid=48)
    print("[OK] Step 21 imported geometry projection quality finished")


if __name__ == "__main__":
    main()
