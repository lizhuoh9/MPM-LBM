import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step20_common import assert_particle_cloud, load_geometry_config, write_json  # noqa: E402
from src import GeometrySampler3D  # noqa: E402


CASES = [
    ("mesh_cube", "configs/step20_mesh_cube_geometry.json", "cube_particles_x.npy"),
    ("mesh_ellipsoid", "configs/step20_mesh_ellipsoid_geometry.json", "ellipsoid_particles_x.npy"),
]


def main():
    out_dir = os.path.join(ROOT, "outputs", "step20_mesh_import_sanity")
    os.makedirs(out_dir, exist_ok=True)
    stats_by_case = {}

    for case, config_path, particles_file in CASES:
        config = load_geometry_config(config_path)
        sampler = GeometrySampler3D(config)
        cloud = sampler.sample_particles()
        voxel = sampler.voxelize(32)
        assert_particle_cloud(cloud, 4096)

        stats = dict(cloud["sampling_stats"])
        stats["geometry_volume"] = float(cloud["geometry_volume"])
        stats["voxel_occupied_count"] = int(voxel["occupied_count"])
        stats["particle_min"] = [float(v) for v in np.min(cloud["x"], axis=0)]
        stats["particle_max"] = [float(v) for v in np.max(cloud["x"], axis=0)]

        if int(stats["vertices_count"]) <= 0 or int(stats["faces_count"]) <= 0:
            raise RuntimeError(f"{case} mesh did not load vertices/faces")
        if int(stats["voxel_occupied_count"]) <= 0:
            raise RuntimeError(f"{case} voxelization is empty")
        if float(stats["geometry_volume"]) <= 0.0:
            raise RuntimeError(f"{case} geometry volume must be positive")

        np.save(os.path.join(out_dir, particles_file), cloud["x"])
        stats_by_case[case] = stats
        print(
            f"case={case}, vertices={stats['vertices_count']}, faces={stats['faces_count']}, "
            f"particle_count={stats['particle_count']}, occupied={stats['voxel_occupied_count']}, "
            f"geometry_volume={stats['geometry_volume']:.9e}"
        )

    write_json(os.path.join(out_dir, "mesh_import_stats.json"), stats_by_case)
    print("[OK] Step 20 mesh import sanity finished")


if __name__ == "__main__":
    main()
