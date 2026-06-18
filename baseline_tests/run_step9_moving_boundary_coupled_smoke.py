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


def assert_lbm_stats_ok(stats):
    values = [stats["max_v"], stats["rho_min"], stats["rho_max"], stats["mass_total"]]
    assert_finite("LBM stats", values)
    if stats["rho_min"] <= 0.95 or stats["rho_max"] >= 1.05:
        raise RuntimeError(f"LBM rho left accepted range: {stats}")
    if stats["max_v"] >= 0.1:
        raise RuntimeError(f"LBM max_v exceeded threshold: {stats}")


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
    n_lbm_steps = 20
    n_particles = 4096
    threshold = 0.5
    reaction_scale = 1.0
    force_cap_norm = 1.0e-4

    out_dir = os.path.join(ROOT, "outputs", "step9_mb_coupled_smoke")
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
        n_particles=n_particles,
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
    initial_projection_zone_fluid_mean_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])
    initial_solid_mean_vx_norm = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])

    print("Step 9 moving-boundary coupled smoke")
    print(f"n_grid={sim.n_grid}")
    print(f"n_particles={n_particles}")
    print(f"n_lbm_steps={n_lbm_steps}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"threshold={threshold:.9e}")
    print(f"reaction_scale={reaction_scale:.9e}")
    print(f"force_cap_norm={force_cap_norm:.9e}")
    print(f"initial_projection_zone_fluid_mean_ux={initial_projection_zone_fluid_mean_ux:.9e}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")
    t0 = time.time()

    total_mpm_substeps = 0
    records = []
    final_projection_zone_fluid_mean_ux = initial_projection_zone_fluid_mean_ux
    final_reaction_stats = None

    for lbm_step in range(1, n_lbm_steps + 1):
        projector.project(solid, lbm)
        lbm.update_dynamic_solid(threshold)
        lbm.reinitialize_new_fluid_cells()
        lbm.step_moving_bounceback()
        final_projection_zone_fluid_mean_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])

        for _ in range(sim.mpm_substeps_per_lbm_step):
            solid.clear_grid()
            solid.p2g()
            mb_coupler.clear_reaction_diagnostics()
            mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
            solid.grid_update()
            solid.g2p()
            total_mpm_substeps += 1

        final_lbm_stats = lbm.get_stats()
        final_mpm_stats = solid.get_stats()
        final_bb_stats = lbm.get_moving_boundary_stats()
        final_reaction_stats = mb_coupler.get_stats()
        force_stats = FSIDiagnostics3D.force_stats(lbm)
        hydro_force_max = force_max_norm(lbm.hydro_force)
        solid_mean_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])

        assert_mpm_stats_ok(final_mpm_stats)
        assert_finite(
            "moving-boundary coupled smoke diagnostics",
            [
                final_lbm_stats["max_v"],
                final_lbm_stats["rho_min"],
                final_lbm_stats["rho_max"],
                final_projection_zone_fluid_mean_ux,
                solid_mean_vx,
                final_bb_stats["bb_link_count"],
                hydro_force_max,
                final_reaction_stats["active_reaction_particle_count"],
                final_reaction_stats["net_grid_reaction_force"][0],
                force_stats["max_cell_force_norm"],
            ],
        )

        records.append(
            (
                lbm_step,
                total_mpm_substeps,
                final_projection_zone_fluid_mean_ux,
                solid_mean_vx,
                final_lbm_stats["rho_min"],
                final_lbm_stats["rho_max"],
                final_lbm_stats["max_v"],
                final_mpm_stats["min_J"],
                final_mpm_stats["max_speed"],
                final_bb_stats["bb_link_count"],
                hydro_force_max,
                final_reaction_stats["active_reaction_particle_count"],
                final_reaction_stats["net_grid_reaction_force"][0],
                force_stats["max_cell_force_norm"],
            )
        )

        if lbm_step % 5 == 0 or lbm_step == n_lbm_steps:
            print(
                f"lbm_step={lbm_step:04d}, total_mpm_substeps={total_mpm_substeps}, "
                f"projection_zone_fluid_mean_ux={final_projection_zone_fluid_mean_ux:.9e}, "
                f"solid_mean_vx_norm={solid_mean_vx:.9e}, "
                f"bb_link_count={final_bb_stats['bb_link_count']}, "
                f"hydro_force_max_norm={hydro_force_max:.9e}, "
                f"active_reaction_particle_count={final_reaction_stats['active_reaction_particle_count']}, "
                f"net_grid_reaction_force_x={final_reaction_stats['net_grid_reaction_force'][0]:.9e}, "
                f"cell_force_max_norm={force_stats['max_cell_force_norm']:.9e}, "
                f"rho_min={final_lbm_stats['rho_min']:.9e}, "
                f"rho_max={final_lbm_stats['rho_max']:.9e}, "
                f"lbm_max_v={final_lbm_stats['max_v']:.9e}, "
                f"mpm_min_J={final_mpm_stats['min_J']:.9e}, "
                f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    final_lbm_stats = lbm.get_stats()
    final_mpm_stats = solid.get_stats()
    final_bb_stats = lbm.get_moving_boundary_stats()
    final_solid_mean_vx_norm = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
    hydro_force_max = force_max_norm(lbm.hydro_force)
    force_stats = FSIDiagnostics3D.force_stats(lbm)

    assert_lbm_stats_ok(final_lbm_stats)
    assert_mpm_stats_ok(final_mpm_stats)

    expected_substeps = n_lbm_steps * sim.mpm_substeps_per_lbm_step
    if total_mpm_substeps != expected_substeps:
        raise RuntimeError(f"unexpected MPM substeps: {total_mpm_substeps} != {expected_substeps}")
    if final_bb_stats["bb_link_count"] <= 0:
        raise RuntimeError("moving-boundary coupled smoke produced no bounce-back links")
    if hydro_force_max <= 0.0:
        raise RuntimeError("moving-boundary coupled smoke produced zero hydro_force")
    if final_reaction_stats["active_reaction_particle_count"] <= 0:
        raise RuntimeError("moving-boundary coupled smoke produced no active reaction particles")
    if final_projection_zone_fluid_mean_ux <= initial_projection_zone_fluid_mean_ux:
        raise RuntimeError(
            "projection zone fluid ux did not increase: "
            f"{final_projection_zone_fluid_mean_ux} <= {initial_projection_zone_fluid_mean_ux}"
        )
    if final_solid_mean_vx_norm >= initial_solid_mean_vx_norm:
        raise RuntimeError(
            "solid mean vx did not decrease: "
            f"{final_solid_mean_vx_norm} >= {initial_solid_mean_vx_norm}"
        )
    if force_stats["max_cell_force_norm"] != 0.0:
        raise RuntimeError(f"cell_force should remain zero, got {force_stats['max_cell_force_norm']}")

    np.savez(
        os.path.join(out_dir, "diagnostics_timeseries.npz"),
        columns=np.asarray(
            [
                "lbm_step",
                "total_mpm_substeps",
                "projection_zone_fluid_mean_ux",
                "solid_mean_vx_norm",
                "rho_min",
                "rho_max",
                "lbm_max_v",
                "mpm_min_J",
                "mpm_max_speed",
                "bb_link_count",
                "hydro_force_max_norm",
                "active_reaction_particle_count",
                "net_grid_reaction_force_x",
                "cell_force_max_norm",
            ]
        ),
        records=np.asarray(records, dtype=np.float64),
        completed_lbm_steps=n_lbm_steps,
        total_mpm_substeps=total_mpm_substeps,
        initial_projection_zone_fluid_mean_ux=initial_projection_zone_fluid_mean_ux,
        final_projection_zone_fluid_mean_ux=final_projection_zone_fluid_mean_ux,
        initial_solid_mean_vx_norm=initial_solid_mean_vx_norm,
        final_solid_mean_vx_norm=final_solid_mean_vx_norm,
    )
    solid.export_particles(out_dir)
    lbm.export_VTK(n_lbm_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print(f"completed_lbm_steps={n_lbm_steps}")
    print(f"total_mpm_substeps={total_mpm_substeps}")
    print(f"bb_link_count={final_bb_stats['bb_link_count']}")
    print(f"hydro_force_max_norm={hydro_force_max:.9e}")
    print(f"active_reaction_particle_count={final_reaction_stats['active_reaction_particle_count']}")
    print(f"max_particle_reaction_norm={final_reaction_stats['max_particle_reaction_norm']:.9e}")
    print(f"max_grid_reaction_norm={final_reaction_stats['max_grid_reaction_norm']:.9e}")
    print(f"net_grid_reaction_force_x={final_reaction_stats['net_grid_reaction_force'][0]:.9e}")
    print(f"projection_zone_fluid_mean_ux_initial={initial_projection_zone_fluid_mean_ux:.9e}")
    print(f"projection_zone_fluid_mean_ux_final={final_projection_zone_fluid_mean_ux:.9e}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")
    print(f"final_solid_mean_vx_norm={final_solid_mean_vx_norm:.9e}")
    print(f"cell_force_max_norm={force_stats['max_cell_force_norm']:.9e}")
    print(f"rho_min={final_lbm_stats['rho_min']:.9e}")
    print(f"rho_max={final_lbm_stats['rho_max']:.9e}")
    print(f"lbm_max_v={final_lbm_stats['max_v']:.9e}")
    print(f"mpm_min_J={final_mpm_stats['min_J']:.9e}")
    print(f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}")
    print("[OK] Step 9 moving-boundary coupled smoke finished")


if __name__ == "__main__":
    main()
