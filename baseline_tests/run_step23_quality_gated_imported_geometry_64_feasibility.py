import os

import taichi as ti

from step23_common import ROOT, run_mixed_quality_gated_config_paths


CASE_CONFIGS = [
    ("voxel_sphere", "configs/step23_quality_gated_voxel_sphere_64_penalty.json"),
    ("voxel_sphere", "configs/step23_quality_gated_voxel_sphere_64_moving_boundary.json"),
    ("mesh_cube", "configs/step23_quality_gated_mesh_cube_64_penalty.json"),
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step23_quality_gated_imported_geometry_64_feasibility")
    run_mixed_quality_gated_config_paths(
        CASE_CONFIGS,
        out_dir,
        "imported_geometry_64_quality_gated_results.csv",
        "imported_geometry_64_quality_gated_results.npz",
    )
    print("[OK] Step 23 quality-gated imported geometry 64 feasibility finished")


if __name__ == "__main__":
    main()
