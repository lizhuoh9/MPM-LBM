import os

import taichi as ti

from step21_common import ROOT, run_driver_config_paths


CONFIGS = [
    ("voxel_sphere", "configs/step21_voxel_sphere_64_penalty.json"),
    ("voxel_sphere", "configs/step21_voxel_sphere_64_moving_boundary.json"),
    ("mesh_cube", "configs/step21_mesh_cube_64_penalty.json"),
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step21_imported_geometry_64_feasibility")
    rows = []
    for case, config_path in CONFIGS:
        rows.extend(run_driver_config_paths(case, [config_path], out_dir, "_tmp.csv", "_tmp.npz"))

    from step21_common import STEP21_DRIVER_FIELDS, write_rows_csv_npz

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "imported_geometry_64_results.csv"),
        os.path.join(out_dir, "imported_geometry_64_results.npz"),
        STEP21_DRIVER_FIELDS,
    )
    for name in ("_tmp.csv", "_tmp.npz"):
        path = os.path.join(out_dir, name)
        if os.path.exists(path):
            os.remove(path)
    print("[OK] Step 21 imported geometry 64 feasibility finished")


if __name__ == "__main__":
    main()
