import os
import sys

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step20_common import (  # noqa: E402
    STEP20_PROJECTION_FIELDS,
    build_projection_harness,
    load_geometry_config,
    run_projection_case_with_harness,
    write_rows_csv_npz,
)


CASES = [
    ("voxel_sphere", "configs/step20_voxel_sphere_geometry.json"),
    ("mesh_cube", "configs/step20_mesh_cube_geometry.json"),
    ("mesh_ellipsoid", "configs/step20_mesh_ellipsoid_geometry.json"),
]


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step20_imported_geometry_projection")
    os.makedirs(out_dir, exist_ok=True)
    harness = build_projection_harness(out_dir, n_particles=4096, n_grid=32)

    rows = []
    for case, config_path in CASES:
        config = load_geometry_config(config_path)
        row = run_projection_case_with_harness(case, config, out_dir, harness)
        rows.append(row)
        print(
            f"case={case}, geometry_type={row['geometry_type']}, projected_mass={row['projected_mass']:.9e}, "
            f"active_cell_count={row['active_cell_count']}, solid_phi_max={row['solid_phi_max']:.9e}"
        )

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "projection_results.csv"),
        os.path.join(out_dir, "projection_results.npz"),
        STEP20_PROJECTION_FIELDS,
    )

    if not np.all([bool(row["stable"]) for row in rows]):
        raise RuntimeError("not all projection rows are stable")
    print("[OK] Step 20 imported geometry projection finished")


if __name__ == "__main__":
    main()
