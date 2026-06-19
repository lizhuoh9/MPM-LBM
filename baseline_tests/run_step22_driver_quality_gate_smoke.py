import os

import taichi as ti

from step22_common import (
    DRIVER_QUALITY_FIELDS,
    ROOT,
    load_driver_config,
    run_driver_quality_case,
    write_rows_csv_npz,
)


CASES = [
    ("voxel_sphere", "configs/step22_driver_quality_gate_voxel_penalty.json", "voxel_sphere_penalty"),
    ("mesh_cube", "configs/step22_driver_quality_gate_mesh_moving_boundary.json", "mesh_cube_moving_boundary"),
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step22_driver_quality_gate_smoke")
    rows = []
    for case, config_path, case_dir_name in CASES:
        row = run_driver_quality_case(case, load_driver_config(config_path), os.path.join(out_dir, case_dir_name))
        rows.append(row)
        print(
            f"case={case}, mode={row['mode']}, quality_gate_pass={row['quality_gate_pass']}, "
            f"rho=[{row['rho_min']:.9e}, {row['rho_max']:.9e}], "
            f"lbm_max_v={row['lbm_max_v']:.9e}, projected_mass={row['projected_mass']:.9e}"
        )

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "quality_gate_driver_results.csv"),
        os.path.join(out_dir, "quality_gate_driver_results.npz"),
        DRIVER_QUALITY_FIELDS,
    )
    print("[OK] Step 22 driver quality gate smoke finished")


if __name__ == "__main__":
    main()
