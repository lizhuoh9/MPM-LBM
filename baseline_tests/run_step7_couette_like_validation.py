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
    PenaltyFSICoupler3D,
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


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.03, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    n_lbm_steps = 100

    out_dir = os.path.join(ROOT, "outputs", "step7_couette_like")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_couette_like_32.dat")
    make_all_fluid_geo(geo_path, sim.n_grid)

    t0 = time.time()
    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()

    solid = MPMSolid3D(
        sim.make_mpm_config(
            gravity=(0.0, 0.0, 0.0),
            box_min=(0.25, 0.55, 0.25),
            box_max=(0.55, 0.75, 0.55),
        ),
        n_particles=4096,
    )
    solid.init_box()
    solid.set_uniform_velocity(float(target_u_norm[0]), float(target_u_norm[1]), float(target_u_norm[2]))

    projector = MPMToLBMProjector3D(sim)
    coupler = PenaltyFSICoupler3D(sim, beta_lbm=1.0e-3, force_cap_lbm=1.0e-4)

    projector.project(solid, lbm)
    initial_projection_zone_fluid_mean = FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)
    initial_solid_mean_velocity = FSIDiagnostics3D.solid_mean_velocity_norm(solid)

    print("Step 7 Couette-like validation")
    print(f"n_grid={sim.n_grid}")
    print(f"n_lbm_steps={n_lbm_steps}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"initial_projection_zone_fluid_mean_ux={float(initial_projection_zone_fluid_mean[0]):.9e}")
    print(f"initial_solid_mean_vx_norm={float(initial_solid_mean_velocity[0]):.9e}")

    total_mpm_substeps = 0
    final_lbm_stats = None
    final_mpm_stats = None

    for lbm_step in range(1, n_lbm_steps + 1):
        projector.project(solid, lbm)
        coupler.build_penalty_force(lbm)
        lbm.step()

        for _ in range(sim.mpm_substeps_per_lbm_step):
            solid.clear_grid()
            solid.p2g()
            coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
            solid.grid_update()
            solid.g2p()
            total_mpm_substeps += 1

        if lbm_step % 20 == 0 or lbm_step == n_lbm_steps:
            final_lbm_stats = lbm.get_stats()
            final_mpm_stats = solid.get_stats()
            force_stats = FSIDiagnostics3D.force_stats(lbm)
            assert_lbm_stats_ok(final_lbm_stats)
            assert_mpm_stats_ok(final_mpm_stats)
            print(
                f"lbm_step={lbm_step:04d}, total_mpm_substeps={total_mpm_substeps}, "
                f"active_force_cell_count={force_stats['active_force_cell_count']}, "
                f"rho_min={final_lbm_stats['rho_min']:.9e}, "
                f"rho_max={final_lbm_stats['rho_max']:.9e}, "
                f"lbm_max_v={final_lbm_stats['max_v']:.9e}, "
                f"mpm_min_J={final_mpm_stats['min_J']:.9e}, "
                f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    projector.project(solid, lbm)
    coupler.build_penalty_force(lbm)
    final_projection_zone_fluid_mean = FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)
    far_field_fluid_mean = FSIDiagnostics3D.far_field_fluid_mean_velocity(lbm)
    final_lbm_stats = lbm.get_stats()
    final_mpm_stats = solid.get_stats()
    lbm_diagnostics = FSIDiagnostics3D.lbm_fluid_stats(lbm)
    final_solid_mean_velocity = FSIDiagnostics3D.solid_mean_velocity_norm(solid)
    force_stats = FSIDiagnostics3D.force_stats(lbm)
    ux_profile_y = FSIDiagnostics3D.lbm_velocity_profile_x_over_y(lbm)
    global_fluid_mean_ux = float(lbm_diagnostics["fluid_mean_velocity"][0])

    assert_lbm_stats_ok(final_lbm_stats)
    assert_mpm_stats_ok(final_mpm_stats)
    assert_finite("ux_profile_y", ux_profile_y)

    initial_projection_zone_fluid_mean_ux = float(initial_projection_zone_fluid_mean[0])
    final_projection_zone_fluid_mean_ux = float(final_projection_zone_fluid_mean[0])
    far_field_fluid_mean_ux = float(far_field_fluid_mean[0])
    initial_solid_mean_vx_norm = float(initial_solid_mean_velocity[0])
    final_solid_mean_vx_norm = float(final_solid_mean_velocity[0])

    print(f"initial_projection_zone_fluid_mean_ux={initial_projection_zone_fluid_mean_ux:.9e}")
    print(f"final_projection_zone_fluid_mean_ux={final_projection_zone_fluid_mean_ux:.9e}")
    print(f"far_field_fluid_mean_ux={far_field_fluid_mean_ux:.9e}")
    print(f"final_global_fluid_mean_ux={global_fluid_mean_ux:.9e}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")
    print(f"final_solid_mean_vx_norm={final_solid_mean_vx_norm:.9e}")
    print(f"active_force_cell_count={force_stats['active_force_cell_count']}")
    print(f"rho_min={final_lbm_stats['rho_min']:.9e}")
    print(f"rho_max={final_lbm_stats['rho_max']:.9e}")
    print(f"lbm_max_v={final_lbm_stats['max_v']:.9e}")
    print(f"mpm_min_J={final_mpm_stats['min_J']:.9e}")
    print(f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}")

    if final_projection_zone_fluid_mean_ux <= initial_projection_zone_fluid_mean_ux:
        raise RuntimeError("projection zone fluid ux did not increase")
    if final_projection_zone_fluid_mean_ux <= far_field_fluid_mean_ux:
        raise RuntimeError("projection zone fluid ux is not larger than far-field ux")
    if global_fluid_mean_ux <= 0.0:
        raise RuntimeError("global fluid mean ux is not positive")
    if final_solid_mean_vx_norm >= initial_solid_mean_vx_norm:
        raise RuntimeError("solid mean vx did not decrease")
    if force_stats["active_force_cell_count"] <= 0:
        raise RuntimeError("no active force cells")

    np.save(os.path.join(out_dir, "ux_profile_y.npy"), ux_profile_y)
    np.savez(
        os.path.join(out_dir, "diagnostics.npz"),
        initial_projection_zone_fluid_mean_ux=initial_projection_zone_fluid_mean_ux,
        final_projection_zone_fluid_mean_ux=final_projection_zone_fluid_mean_ux,
        far_field_fluid_mean_ux=far_field_fluid_mean_ux,
        final_global_fluid_mean_ux=global_fluid_mean_ux,
        initial_solid_mean_vx_norm=initial_solid_mean_vx_norm,
        final_solid_mean_vx_norm=final_solid_mean_vx_norm,
        ux_profile_y=ux_profile_y,
        rho_min=final_lbm_stats["rho_min"],
        rho_max=final_lbm_stats["rho_max"],
        lbm_max_v=final_lbm_stats["max_v"],
        mpm_min_J=final_mpm_stats["min_J"],
        mpm_max_speed=final_mpm_stats["max_speed"],
    )
    solid.export_particles(out_dir)
    lbm.export_VTK(n_lbm_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print("[OK] Step 7 Couette-like validation finished")


if __name__ == "__main__":
    main()
