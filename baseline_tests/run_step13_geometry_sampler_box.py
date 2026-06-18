import os
import sys

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step13_common import run_projection_case, save_geometry_arrays, write_json  # noqa: E402
from src import GeometryConfig  # noqa: E402


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step13_geometry_box")
    config = GeometryConfig.from_json(os.path.join(ROOT, "configs", "step13_box_geometry.json"))

    result = run_projection_case(config, out_dir, n_grid=32)
    cloud = result["cloud"]
    stats = result["stats"]
    save_geometry_arrays(out_dir, cloud)
    write_json(os.path.join(out_dir, "geometry_stats.json"), stats)

    x = cloud["x"]
    if x.shape != (4096, 3):
        raise RuntimeError(f"unexpected particle shape: {x.shape}")
    if not np.all(np.isfinite(x)):
        raise RuntimeError("box particles contain NaN or Inf")
    if np.min(x) < 0.0 or np.max(x) > 1.0:
        raise RuntimeError("box particles escaped normalized domain")
    if np.any(np.min(x, axis=0) < np.asarray(config.box_min) - 1.0e-6):
        raise RuntimeError("box particle minimum is outside box_min")
    if np.any(np.max(x, axis=0) > np.asarray(config.box_max) + 1.0e-6):
        raise RuntimeError("box particle maximum is outside box_max")
    if stats["active_cell_count"] <= 0 or stats["projected_mass"] <= 0.0:
        raise RuntimeError("box projection did not activate LBM cells")
    if abs(stats["mpm_min_J"] - 1.0) > 1.0e-6:
        raise RuntimeError("box MPM deformation state was not reset")

    print("Step 13 box geometry sampler")
    print(f"particle_count={stats['particle_count']}")
    print(f"geometry_volume={stats['geometry_volume']:.9e}")
    print(f"total_mass={stats['total_mass']:.9e}")
    print(f"active_cell_count={stats['active_cell_count']}")
    print(f"projected_mass={stats['projected_mass']:.9e}")
    print("[OK] Step 13 box geometry sampler finished")


if __name__ == "__main__":
    main()
