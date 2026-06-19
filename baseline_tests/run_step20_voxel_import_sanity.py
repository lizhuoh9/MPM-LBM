import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from baseline_tests.step20_common import assert_particle_cloud, load_geometry_config, write_json  # noqa: E402
from src import GeometrySampler3D, load_voxel_geometry  # noqa: E402


def main():
    out_dir = os.path.join(ROOT, "outputs", "step20_voxel_import_sanity")
    os.makedirs(out_dir, exist_ok=True)

    config = load_geometry_config("configs/step20_voxel_sphere_geometry.json")
    voxel_geometry = load_voxel_geometry(
        config.geometry_file,
        metadata_path=config.metadata_file,
        threshold=config.voxel_threshold,
    )
    sampler = GeometrySampler3D(config)
    cloud = sampler.sample_particles()
    voxel = sampler.voxelize(32)
    assert_particle_cloud(cloud, 4096)

    stats = dict(voxel_geometry.stats)
    stats.update(cloud["sampling_stats"])
    stats["geometry_volume"] = float(cloud["geometry_volume"])
    stats["voxelized_occupied_count"] = int(voxel["occupied_count"])

    if stats["shape"] != [32, 32, 32]:
        raise RuntimeError(f"unexpected voxel shape: {stats['shape']}")
    if int(stats["occupied_count"]) <= 0:
        raise RuntimeError("voxel fixture has no occupied cells")
    if float(stats["occupied_fraction"]) <= 0.0:
        raise RuntimeError("voxel occupied_fraction must be positive")

    np.save(os.path.join(out_dir, "particles_x.npy"), cloud["x"])
    np.save(os.path.join(out_dir, "particle_vol0.npy"), cloud["vol0"])
    np.save(os.path.join(out_dir, "particle_mass.npy"), cloud["mass"])
    np.save(os.path.join(out_dir, "geometry_occupancy.npy"), voxel["occupancy"])
    write_json(os.path.join(out_dir, "import_stats.json"), stats)

    print("Step 20 voxel import sanity")
    print(f"voxel_shape={stats['shape']}")
    print(f"occupied_count={stats['occupied_count']}")
    print(f"particle_count={stats['particle_count']}")
    print(f"geometry_volume={stats['geometry_volume']:.9e}")
    print("[OK] Step 20 voxel import sanity finished")


if __name__ == "__main__":
    main()
