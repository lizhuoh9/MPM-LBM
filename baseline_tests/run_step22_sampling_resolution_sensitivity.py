import json
import os

import taichi as ti

from step22_common import (
    RESOLUTION_SENSITIVITY_FIELDS,
    ROOT,
    build_projection_harness,
    load_geometry_config,
    replace_geometry_config,
    run_resolution_projection_case,
    write_rows_csv_npz,
)


SWEEP_CONFIGS = [
    "configs/step22_resolution_sweep_voxel_sphere.json",
    "configs/step22_resolution_sweep_mesh_ellipsoid.json",
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step22_sampling_resolution_sensitivity")
    rows = []
    harness = build_projection_harness(out_dir, n_particles=4096, n_grid=32)

    for sweep_path in SWEEP_CONFIGS:
        with open(os.path.join(ROOT, sweep_path), "r", encoding="utf-8") as f:
            sweep = json.load(f)
        base = load_geometry_config(sweep["geometry_config_path"])
        for index, hint in enumerate(sweep["particles_per_axis_hint"]):
            mesh_resolutions = sweep.get("mesh_voxel_resolution", [base.mesh_voxel_resolution])
            mesh_resolution = (
                mesh_resolutions[min(index, len(mesh_resolutions) - 1)]
                if base.geometry_type == "mesh"
                else base.mesh_voxel_resolution
            )
            config = replace_geometry_config(
                base,
                particles_per_axis_hint=int(hint),
                mesh_voxel_resolution=int(mesh_resolution),
            )
            row = run_resolution_projection_case(sweep["case"], config, harness)
            rows.append(row)
            print(
                f"case={row['case']}, hint={row['particles_per_axis_hint']}, "
                f"volume={row['geometry_volume']:.9e}, projected_mass={row['projected_mass']:.9e}, "
                f"active_cell_count={row['active_cell_count']}"
            )

    by_case = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(float(row["geometry_volume"]))
    for case, volumes in by_case.items():
        ratio = max(volumes) / min(volumes)
        if ratio >= 2.0:
            raise RuntimeError(f"{case} volume ratio too high: {ratio}")

    write_rows_csv_npz(
        rows,
        os.path.join(out_dir, "resolution_sensitivity.csv"),
        os.path.join(out_dir, "resolution_sensitivity.npz"),
        RESOLUTION_SENSITIVITY_FIELDS,
    )
    print("[OK] Step 22 sampling resolution sensitivity finished")


if __name__ == "__main__":
    main()
