import os

import taichi as ti

from step24_common import ROOT, run_mixed_strict_config_paths, write_log


CASE_CONFIGS = [
    ("voxel_sphere", "configs/step24_strict_voxel_sphere_64_moving_boundary.json"),
    ("mesh_cube", "configs/step24_strict_mesh_cube_64_moving_boundary.json"),
    ("mesh_cube", "configs/step24_strict_mesh_cube_64_link_area.json"),
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step24_strict_imported_geometry_64_feasibility")
    rows = run_mixed_strict_config_paths(
        CASE_CONFIGS,
        out_dir,
        "imported_geometry_64_strict_feasibility_results.csv",
        "imported_geometry_64_strict_feasibility_results.npz",
    )
    marker = "[OK] Step 24 strict imported geometry 64 feasibility finished"
    write_log("logs/step24_strict_imported_geometry_64_feasibility.log", [marker, f"row_count={len(rows)}"])
    print(marker)


if __name__ == "__main__":
    main()
