import os
import sys

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step20_common import (  # noqa: E402
    STEP20_DRIVER_FIELDS,
    make_driver_config,
    run_driver_case,
    write_rows_csv_npz,
)


CASES = [
    (
        "voxel_sphere",
        "none",
        "voxel",
        "configs/step20_voxel_sphere_geometry.json",
        "engineering",
    ),
    (
        "voxel_sphere",
        "penalty",
        "voxel",
        "configs/step20_voxel_sphere_geometry.json",
        "engineering",
    ),
    (
        "mesh_cube",
        "none",
        "mesh",
        "configs/step20_mesh_cube_geometry.json",
        "engineering",
    ),
    (
        "mesh_cube",
        "penalty",
        "mesh",
        "configs/step20_mesh_cube_geometry.json",
        "engineering",
    ),
    (
        "mesh_cube",
        "moving_boundary",
        "mesh",
        "configs/step20_mesh_cube_geometry.json",
        "engineering",
    ),
]


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step20_driver_imported_geometry_modes")
    os.makedirs(out_dir, exist_ok=True)

    rows = []
    for case, mode, geometry_type, geometry_config_path, reaction_transfer_mode in CASES:
        config = make_driver_config(case, mode, geometry_type, geometry_config_path, reaction_transfer_mode)
        row = run_driver_case(case, config, os.path.join(out_dir, f"{case}_{mode}_{reaction_transfer_mode}"))
        rows.append(row)
        print(
            f"case={case}, mode={mode}, reaction={reaction_transfer_mode}, "
            f"rho_min={row['rho_min']:.9e}, rho_max={row['rho_max']:.9e}, "
            f"lbm_max_v={row['lbm_max_v']:.9e}, mpm_min_J={row['mpm_min_J']:.9e}, "
            f"projected_mass={row['projected_mass']:.9e}, active_cell_count={row['active_cell_count']}, "
            f"cell_force_max_norm={row['cell_force_max_norm']:.9e}, "
            f"hydro_force_max_norm={row['hydro_force_max_norm']:.9e}"
        )

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "imported_geometry_mode_results.csv"),
        os.path.join(out_dir, "imported_geometry_mode_results.npz"),
        STEP20_DRIVER_FIELDS,
    )

    if not np.all([bool(row["stable"]) for row in rows]):
        raise RuntimeError("not all driver rows are stable")
    print("[OK] Step 20 driver imported geometry modes finished")


if __name__ == "__main__":
    main()
