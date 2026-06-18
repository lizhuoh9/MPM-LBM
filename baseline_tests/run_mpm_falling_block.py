import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import MPMConfig, MPMSolid3D


def assert_stats_finite(stats, label):
    values = [
        *stats["min_x"],
        *stats["max_x"],
        stats["max_speed"],
        stats["min_J"],
        stats["max_J"],
        stats["total_mass"],
    ]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{label} stats contain NaN or Inf: {stats}")


def assert_outputs_exist(out_dir):
    for name in ("particles_x.npy", "particles_v.npy", "particles_F.npy", "particles_J.npy"):
        path = os.path.join(out_dir, name)
        if not os.path.isfile(path):
            raise RuntimeError(f"Missing particle output: {path}")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32)

    steps = 100
    out_dir = os.path.join(ROOT, "outputs", "mpm_falling_block")
    os.makedirs(out_dir, exist_ok=True)

    config = MPMConfig(
        n_grid=32,
        dx=1.0 / 32.0,
        dt=4.0e-4,
        gravity=(0.0, -9.8, 0.0),
        young_modulus=400.0,
        poisson_ratio=0.2,
        box_min=(0.25, 0.35, 0.25),
        box_max=(0.55, 0.65, 0.55),
        output_interval=10,
    )
    solid = MPMSolid3D(config, n_particles=4096)
    solid.init_box()

    initial_stats = solid.get_stats()
    t0 = time.time()

    for step in range(steps + 1):
        if step > 0:
            solid.substep()

        if step % config.output_interval == 0:
            stats = solid.get_stats()
            print(
                f"step={step:04d}, min_y={stats['min_y']:.6f}, max_y={stats['max_y']:.6f}, "
                f"max_speed={stats['max_speed']:.6e}, min_J={stats['min_J']:.6f}, "
                f"max_J={stats['max_J']:.6f}, total_mass={stats['total_mass']:.6e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )
            assert_stats_finite(stats, "falling block")
            if stats["min_J"] <= 0.0:
                raise RuntimeError(f"falling block J became non-positive: {stats}")

    final_stats = solid.get_stats()
    assert_stats_finite(final_stats, "falling block final")
    if final_stats["min_y"] >= initial_stats["min_y"]:
        raise RuntimeError(f"falling block did not move downward: initial={initial_stats}, final={final_stats}")
    if final_stats["max_speed"] <= initial_stats["max_speed"] + 1.0e-8:
        raise RuntimeError(f"falling block speed did not increase: initial={initial_stats}, final={final_stats}")
    if final_stats["min_J"] <= 0.0:
        raise RuntimeError(f"falling block J became non-positive: {final_stats}")
    if final_stats["max_speed"] >= 10.0:
        raise RuntimeError(f"falling block max_speed exceeded hard limit: {final_stats}")

    solid.export_particles(out_dir)
    assert_outputs_exist(out_dir)

    print(
        "[OK] Step 3 MPM falling block baseline finished. "
        f"initial_min_y={initial_stats['min_y']:.6f}, final_min_y={final_stats['min_y']:.6f}, "
        f"initial_max_speed={initial_stats['max_speed']:.6e}, "
        f"final_max_speed={final_stats['max_speed']:.6e}, "
        f"min_J={final_stats['min_J']:.6f}, max_J={final_stats['max_J']:.6f}, "
        f"total_mass={final_stats['total_mass']:.6e}, out_dir={out_dir}"
    )


if __name__ == "__main__":
    main()
