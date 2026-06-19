import os

import taichi as ti

from step24_common import ROOT, run_strict_config_paths, write_log


CONFIGS = [
    "configs/step24_strict_mesh_ellipsoid_48_moving_boundary.json",
    "configs/step24_strict_mesh_ellipsoid_48_link_area.json",
]


def main():
    os.chdir(ROOT)
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step24_strict_mesh_ellipsoid_48_long")
    rows = run_strict_config_paths(
        "mesh_ellipsoid",
        CONFIGS,
        out_dir,
        "mesh_ellipsoid_48_strict_long_results.csv",
        "mesh_ellipsoid_48_strict_long_results.npz",
    )
    marker = "[OK] Step 24 strict mesh_ellipsoid 48 long-run finished"
    write_log("logs/step24_strict_mesh_ellipsoid_48_long.log", [marker, f"row_count={len(rows)}"])
    print(marker)


if __name__ == "__main__":
    main()
