import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import (  # noqa: E402
    FSIDiagnostics3D,
    GridUnitMapper,
    LBMFluid3D,
    MPMToLBMProjector3D,
    MPMSolid3D,
    MovingBoundaryFSICoupler3D,
    UnifiedSimConfig,
)


def make_all_fluid_geo(path, n_grid):
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int8)
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def assert_finite(name, values):
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"{name} contains NaN or Inf")


def assert_mpm_stats_ok(stats):
    values = [*stats["min_x"], *stats["max_x"], stats["max_speed"], stats["min_J"], stats["max_J"]]
    assert_finite("MPM stats", values)
    if stats["min_J"] <= 0.0:
        raise RuntimeError(f"MPM min_J became non-positive: {stats}")
    if stats["max_speed"] >= 10.0:
        raise RuntimeError(f"MPM max_speed exceeded threshold: {stats}")


def force_max_norm(field):
    values = field.to_numpy()
    return float(np.max(np.linalg.norm(values, axis=3)))


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.02, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    threshold = 0.5
    reaction_scale = 1.0
    force_cap_norm = 1.0e-2
    mpm_reaction_substeps = 100

    out_dir = os.path.join(ROOT, "outputs", "step9_mb_two_way_reaction")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_all_fluid_32.dat")
    make_all_fluid_geo(geo_path, sim.n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(
            gravity=(0.0, 0.0, 0.0),
            box_min=(0.25, 0.35, 0.25),
            box_max=(0.55, 0.65, 0.55),
        ),
        n_particles=4096,
    )
    solid.init_box()
    solid.set_uniform_velocity(float(target_u_norm[0]), float(target_u_norm[1]), float(target_u_norm[2]))

    projector = MPMToLBMProjector3D(sim)
    mb_coupler = MovingBoundaryFSICoupler3D(
        sim,
        reaction_scale=reaction_scale,
        force_cap_norm=force_cap_norm,
        phi_min=1.0e-6,
    )

    projector.project(solid, lbm)
    lbm.update_dynamic_solid(threshold)
    lbm.reinitialize_new_fluid_cells()
    lbm.step_moving_bounceback()

    initial_solid_mean_vx_norm = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
    hydro_force_max = force_max_norm(lbm.hydro_force)
    bb_stats = lbm.get_moving_boundary_stats()

    print("Step 9 moving-boundary MPM reaction")
    print(f"n_grid={sim.n_grid}")
    print("n_particles=4096")
    print(f"mpm_reaction_substeps={mpm_reaction_substeps}")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"threshold={threshold:.9e}")
    print(f"reaction_scale={reaction_scale:.9e}")
    print(f"force_cap_norm={force_cap_norm:.9e}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")
    print(f"bb_link_count={bb_stats['bb_link_count']}")
    print(f"hydro_force_max_norm={hydro_force_max:.9e}")
    t0 = time.time()

    final_reaction_stats = None
    final_mpm_stats = None
    for step in range(1, mpm_reaction_substeps + 1):
        solid.clear_grid()
        solid.p2g()
        mb_coupler.clear_reaction_diagnostics()
        mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
        solid.grid_update()
        solid.g2p()

        if step % 20 == 0 or step == mpm_reaction_substeps:
            final_reaction_stats = mb_coupler.get_stats()
            final_mpm_stats = solid.get_stats()
            assert_mpm_stats_ok(final_mpm_stats)
            solid_mean_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
            print(
                f"reaction_substep={step:04d}, "
                f"active_reaction_particle_count={final_reaction_stats['active_reaction_particle_count']}, "
                f"net_grid_reaction_force_x={final_reaction_stats['net_grid_reaction_force'][0]:.9e}, "
                f"solid_mean_vx_norm={solid_mean_vx:.9e}, "
                f"mpm_min_J={final_mpm_stats['min_J']:.9e}, "
                f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    final_solid_mean_vx_norm = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
    final_reaction_stats = mb_coupler.get_stats()
    final_mpm_stats = solid.get_stats()
    assert_mpm_stats_ok(final_mpm_stats)
    assert_finite(
        "two-way MPM reaction diagnostics",
        [
            initial_solid_mean_vx_norm,
            final_solid_mean_vx_norm,
            final_reaction_stats["net_grid_reaction_force"][0],
            final_reaction_stats["active_reaction_particle_count"],
            final_mpm_stats["min_J"],
            final_mpm_stats["max_speed"],
        ],
    )

    if initial_solid_mean_vx_norm <= 0.0:
        raise RuntimeError("initial solid mean vx is not positive")
    if final_solid_mean_vx_norm >= initial_solid_mean_vx_norm:
        raise RuntimeError(
            "solid mean vx did not decrease: "
            f"{final_solid_mean_vx_norm} >= {initial_solid_mean_vx_norm}"
        )
    if final_reaction_stats["net_grid_reaction_force"][0] >= 0.0:
        raise RuntimeError(f"net grid reaction force x should be negative: {final_reaction_stats}")
    if final_reaction_stats["active_reaction_particle_count"] <= 0:
        raise RuntimeError("no active reaction particles")

    solid.export_particles(out_dir)
    np.savez(
        os.path.join(out_dir, "diagnostics.npz"),
        initial_solid_mean_vx_norm=initial_solid_mean_vx_norm,
        final_solid_mean_vx_norm=final_solid_mean_vx_norm,
        active_reaction_particle_count=final_reaction_stats["active_reaction_particle_count"],
        max_particle_reaction_norm=final_reaction_stats["max_particle_reaction_norm"],
        max_grid_reaction_norm=final_reaction_stats["max_grid_reaction_norm"],
        net_particle_reaction_force=np.asarray(final_reaction_stats["net_particle_reaction_force"]),
        net_grid_reaction_force=np.asarray(final_reaction_stats["net_grid_reaction_force"]),
        hydro_force_max_norm=hydro_force_max,
        bb_link_count=bb_stats["bb_link_count"],
        mpm_min_J=final_mpm_stats["min_J"],
        mpm_max_speed=final_mpm_stats["max_speed"],
    )

    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")
    print(f"final_solid_mean_vx_norm={final_solid_mean_vx_norm:.9e}")
    print(f"active_reaction_particle_count={final_reaction_stats['active_reaction_particle_count']}")
    print(f"max_particle_reaction_norm={final_reaction_stats['max_particle_reaction_norm']:.9e}")
    print(f"max_grid_reaction_norm={final_reaction_stats['max_grid_reaction_norm']:.9e}")
    print(f"net_particle_reaction_force_x={final_reaction_stats['net_particle_reaction_force'][0]:.9e}")
    print(f"net_grid_reaction_force_x={final_reaction_stats['net_grid_reaction_force'][0]:.9e}")
    print(f"mpm_min_J={final_mpm_stats['min_J']:.9e}")
    print(f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}")
    print("[OK] Step 9 moving-boundary MPM reaction finished")


if __name__ == "__main__":
    main()
