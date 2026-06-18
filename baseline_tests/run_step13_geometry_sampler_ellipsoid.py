import os
import sys

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step13_common import run_projection_case, save_geometry_arrays, write_json  # noqa: E402
from src import GeometryConfig, GeometrySampler3D  # noqa: E402


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)
    out_dir = os.path.join(ROOT, "outputs", "step13_geometry_ellipsoid")
    config = GeometryConfig.from_json(os.path.join(ROOT, "configs", "step13_ellipsoid_geometry.json"))

    sampler = GeometrySampler3D(config)
    voxel = sampler.voxelize(32)
    result = run_projection_case(config, out_dir, n_grid=32)
    cloud = result["cloud"]
    stats = result["stats"]
    stats["occupied_count"] = int(voxel["occupied_count"])
    stats["voxel_volume_estimate"] = float(voxel["geometry_volume_estimate"])

    save_geometry_arrays(out_dir, cloud, voxel=voxel)
    write_json(os.path.join(out_dir, "geometry_stats.json"), stats)

    center = np.asarray(config.center)
    radii = np.asarray(config.ellipsoid_radii)
    x = cloud["x"]
    if np.any(np.min(x, axis=0) < center - radii - 1.0e-6):
        raise RuntimeError("ellipsoid particles are below bounding box")
    if np.any(np.max(x, axis=0) > center + radii + 1.0e-6):
        raise RuntimeError("ellipsoid particles are above bounding box")
    if voxel["occupied_count"] <= 0:
        raise RuntimeError("ellipsoid voxelization is empty")
    if stats["active_cell_count"] <= 0 or stats["projected_mass"] <= 0.0:
        raise RuntimeError("ellipsoid projection did not activate LBM cells")
    if stats["solid_phi_min"] < -1.0e-6 or stats["solid_phi_max"] > 1.0 + 1.0e-6:
        raise RuntimeError("ellipsoid solid_phi outside [0, 1]")
    if stats["cell_force_max_norm"] != 0.0 or stats["hydro_force_max_norm"] != 0.0:
        raise RuntimeError("ellipsoid projection baseline should not create forces")

    print("Step 13 ellipsoid geometry sampler")
    print(f"particle_count={stats['particle_count']}")
    print(f"occupied_count={stats['occupied_count']}")
    print(f"geometry_volume={stats['geometry_volume']:.9e}")
    print(f"active_cell_count={stats['active_cell_count']}")
    print(f"projected_mass={stats['projected_mass']:.9e}")
    print("[OK] Step 13 ellipsoid geometry sampler finished")


if __name__ == "__main__":
    main()
