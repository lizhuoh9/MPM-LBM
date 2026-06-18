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
    out_dir = os.path.join(ROOT, "outputs", "step13_squid_proxy_geometry")
    config = GeometryConfig.from_json(os.path.join(ROOT, "configs", "step13_squid_proxy_geometry.json"))

    sampler = GeometrySampler3D(config)
    voxel = sampler.voxelize(32)
    result = run_projection_case(config, out_dir, n_grid=32)
    cloud = result["cloud"]
    stats = result["stats"]
    stats["occupied_count"] = int(voxel["occupied_count"])
    stats["voxel_volume_estimate"] = float(voxel["geometry_volume_estimate"])
    stats["component_count"] = 5
    stats["scope_note"] = "procedural squid proxy geometry, not anatomical or validated squid geometry"

    save_geometry_arrays(out_dir, cloud, voxel=voxel)
    write_json(os.path.join(out_dir, "geometry_stats.json"), stats)

    required_components = [
        "mantle_particle_count",
        "head_particle_count",
        "left_fin_particle_count",
        "right_fin_particle_count",
        "arms_particle_count",
    ]
    missing_components = [name for name in required_components if int(stats.get(name, 0)) <= 0]
    if missing_components:
        raise RuntimeError(f"squid proxy missing occupied components: {missing_components}")
    if voxel["occupied_count"] <= 0:
        raise RuntimeError("squid proxy voxelization is empty")
    if stats["active_cell_count"] <= 0 or stats["projected_mass"] <= 0.0:
        raise RuntimeError("squid proxy projection did not activate LBM cells")
    if stats["cell_force_max_norm"] != 0.0 or stats["hydro_force_max_norm"] != 0.0:
        raise RuntimeError("squid proxy geometry baseline should not create forces")
    if not np.all(np.isfinite(cloud["x"])):
        raise RuntimeError("squid proxy particles contain NaN or Inf")

    print("Step 13 squid proxy geometry")
    print(f"particle_count={stats['particle_count']}")
    print(f"occupied_count={stats['occupied_count']}")
    print(f"component_count={stats['component_count']}")
    print(f"geometry_volume={stats['geometry_volume']:.9e}")
    print(f"active_cell_count={stats['active_cell_count']}")
    print(f"projected_mass={stats['projected_mass']:.9e}")
    print("[OK] Step 13 squid proxy geometry finished")


if __name__ == "__main__":
    main()
