import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import (  # noqa: E402
    GridUnitMapper,
    LBMFluid3D,
    MPMToLBMProjector3D,
    MPMSolid3D,
    PenaltyFSICoupler3D,
    UnifiedSimConfig,
)


def make_all_fluid_geo(path, n_grid):
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int8)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def assert_finite(name, values):
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{name} contains NaN or Inf")


def mean_solid_vx(solid):
    return float(np.mean(solid.v.to_numpy()[:, 0]))


def assert_mpm_stats_ok(stats):
    values = [*stats["min_x"], *stats["max_x"], stats["max_speed"], stats["min_J"], stats["max_J"]]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"MPM stats contain NaN or Inf: {stats}")
    if stats["min_J"] <= 0.0:
        raise RuntimeError(f"MPM min_J became non-positive: {stats}")
    if stats["max_speed"] >= 10.0:
        raise RuntimeError(f"MPM max_speed exceeded threshold: {stats}")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.03, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    reaction_substeps = 50

    out_dir = os.path.join(ROOT, "outputs", "step6_two_way_reaction")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_reaction_32.dat")
    make_all_fluid_geo(geo_path, sim.n_grid)

    t0 = time.time()
    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(gravity=(0.0, 0.0, 0.0)),
        n_particles=4096,
    )
    solid.init_box()
    solid.set_uniform_velocity(float(target_u_norm[0]), float(target_u_norm[1]), float(target_u_norm[2]))

    projector = MPMToLBMProjector3D(sim)
    coupler = PenaltyFSICoupler3D(sim, beta_lbm=1.0e-3, force_cap_lbm=1.0e-4)

    initial_solid_mean_vx_norm = mean_solid_vx(solid)
    projector.project(solid, lbm)
    coupler.build_penalty_force(lbm)

    print("Step 6 MPM reaction baseline")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"reaction_substeps={reaction_substeps}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")

    last_stats = None
    for substep in range(1, reaction_substeps + 1):
        solid.clear_grid()
        solid.p2g()
        coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
        solid.grid_update()
        solid.g2p()

        if substep % 10 == 0 or substep == reaction_substeps:
            mpm_stats = solid.get_stats()
            assert_mpm_stats_ok(mpm_stats)
            last_stats = coupler.get_stats()
            print(
                f"reaction_substep={substep:04d}, "
                f"max_reaction_grid_force_norm={last_stats['max_reaction_grid_force_norm']:.9e}, "
                f"net_reaction_grid_force={last_stats['net_reaction_grid_force']}, "
                f"mpm_min_J={mpm_stats['min_J']:.9e}, "
                f"mpm_max_speed={mpm_stats['max_speed']:.9e}, elapsed={time.time() - t0:.2f}s"
            )

    final_solid_mean_vx_norm = mean_solid_vx(solid)
    final_mpm_stats = solid.get_stats()
    assert_mpm_stats_ok(final_mpm_stats)
    x_np = solid.x.to_numpy()
    v_np = solid.v.to_numpy()
    assert_finite("particles_x", x_np)
    assert_finite("particles_v", v_np)

    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")
    print(f"final_solid_mean_vx_norm={final_solid_mean_vx_norm:.9e}")
    print(f"max_reaction_grid_force_norm={last_stats['max_reaction_grid_force_norm']:.9e}")
    print(f"net_reaction_grid_force={last_stats['net_reaction_grid_force']}")
    print(f"mpm_min_J={final_mpm_stats['min_J']:.9e}")
    print(f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}")

    if initial_solid_mean_vx_norm <= 0.0:
        raise RuntimeError(f"initial solid mean vx is not positive: {initial_solid_mean_vx_norm}")
    if final_solid_mean_vx_norm >= initial_solid_mean_vx_norm:
        raise RuntimeError(
            "solid mean vx did not decrease: "
            f"{initial_solid_mean_vx_norm} -> {final_solid_mean_vx_norm}"
        )
    if last_stats["max_reaction_grid_force_norm"] <= 0.0:
        raise RuntimeError("reaction force stayed zero")
    if last_stats["net_reaction_grid_force"][0] >= 0.0:
        raise RuntimeError(f"net reaction x is not negative: {last_stats['net_reaction_grid_force']}")

    solid.export_particles(out_dir)

    print("[OK] Step 6 MPM reaction baseline finished")


if __name__ == "__main__":
    main()
