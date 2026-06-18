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
    n_lbm_steps = 100
    n_particles = 4096
    threshold = 0.5

    out_dir = os.path.join(ROOT, "outputs", "step8_projected_mpm_boundary")
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
    projector.project(solid, lbm)
    initial_projection_zone_fluid_mean_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])

    print("Step 8 projected MPM moving boundary")
    print(f"n_grid={sim.n_grid}")
    print(f"n_particles={n_particles}")
    print(f"n_lbm_steps={n_lbm_steps}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"threshold={threshold:.9e}")
    print(f"initial_projection_zone_fluid_mean_ux={initial_projection_zone_fluid_mean_ux:.9e}")
    t0 = time.time()

    final_projection_zone_fluid_mean_ux = initial_projection_zone_fluid_mean_ux
    final_lbm_stats = None
    final_mpm_stats = None
    final_bb_stats = None
    total_mpm_substeps = 0

    for lbm_step in range(1, n_lbm_steps + 1):
        projector.project(solid, lbm)
        lbm.update_dynamic_solid(threshold)
        lbm.reinitialize_new_fluid_cells()
        lbm.step_moving_bounceback()
        final_projection_zone_fluid_mean_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])

        for _ in range(sim.mpm_substeps_per_lbm_step):
            solid.substep()
            total_mpm_substeps += 1

        if lbm_step % 20 == 0 or lbm_step == n_lbm_steps:
            final_lbm_stats = lbm.get_stats()
            final_mpm_stats = solid.get_stats()
            final_bb_stats = lbm.get_moving_boundary_stats()
            assert_lbm_stats_ok(final_lbm_stats)
            assert_mpm_stats_ok(final_mpm_stats)
            print(
                f"lbm_step={lbm_step:04d}, total_mpm_substeps={total_mpm_substeps}, "
                f"projection_zone_fluid_mean_ux={final_projection_zone_fluid_mean_ux:.9e}, "
                f"bb_link_count={final_bb_stats['bb_link_count']}, "
                f"bb_max_correction={final_bb_stats['bb_max_correction']:.9e}, "
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
    solid_np = lbm.solid.to_numpy()
    solid_phi_np = lbm.solid_phi.to_numpy()
    solid_on_count = int(np.count_nonzero(solid_np))
    cell_force_max = force_max_norm(lbm.cell_force)
    hydro_force_max = force_max_norm(lbm.hydro_force)
    force_balance_error = float(
        np.linalg.norm(
            np.asarray(final_bb_stats["bb_net_fluid_impulse"])
            + np.asarray(final_bb_stats["bb_net_solid_force"])
        )
    )

    assert_lbm_stats_ok(final_lbm_stats)
    assert_mpm_stats_ok(final_mpm_stats)
    assert_finite(
        "projected MPM moving boundary diagnostics",
        [
            solid_on_count,
            final_projection_zone_fluid_mean_ux,
            final_bb_stats["bb_max_correction"],
            final_bb_stats["bb_net_fluid_impulse"][0],
            final_bb_stats["bb_net_solid_force"][0],
            cell_force_max,
            hydro_force_max,
            force_balance_error,
        ],
    )

    if solid_on_count <= 0:
        raise RuntimeError("projected dynamic solid mask is empty")
    if final_bb_stats["bb_link_count"] <= 0:
        raise RuntimeError("projected moving boundary encountered no bounce-back links")
    if final_projection_zone_fluid_mean_ux <= initial_projection_zone_fluid_mean_ux:
        raise RuntimeError(
            "projection zone fluid ux did not increase: "
            f"{final_projection_zone_fluid_mean_ux} <= {initial_projection_zone_fluid_mean_ux}"
        )
    if final_bb_stats["bb_net_fluid_impulse"][0] <= 0.0:
        raise RuntimeError(f"bb_net_fluid_impulse_x should be positive: {final_bb_stats}")
    if final_bb_stats["bb_net_solid_force"][0] >= 0.0:
        raise RuntimeError(f"bb_net_solid_force_x should be negative: {final_bb_stats}")
    if cell_force_max != 0.0:
        raise RuntimeError(f"cell_force should remain zero, got {cell_force_max}")
    if hydro_force_max <= 0.0:
        raise RuntimeError("hydro_force diagnostic should be nonzero")
    if force_balance_error >= 1.0e-6:
        raise RuntimeError(f"force balance error too high: {force_balance_error}")

    np.save(os.path.join(out_dir, "solid.npy"), solid_np)
    np.save(os.path.join(out_dir, "solid_phi.npy"), solid_phi_np)
    solid.export_particles(out_dir)
    np.savez(
        os.path.join(out_dir, "diagnostics.npz"),
        initial_projection_zone_fluid_mean_ux=initial_projection_zone_fluid_mean_ux,
        final_projection_zone_fluid_mean_ux=final_projection_zone_fluid_mean_ux,
        solid_on_count=solid_on_count,
        bb_link_count=final_bb_stats["bb_link_count"],
        bb_max_correction=final_bb_stats["bb_max_correction"],
        bb_net_fluid_impulse=np.asarray(final_bb_stats["bb_net_fluid_impulse"]),
        bb_net_solid_force=np.asarray(final_bb_stats["bb_net_solid_force"]),
        force_balance_error=force_balance_error,
        hydro_force_max_norm=hydro_force_max,
        cell_force_max_norm=cell_force_max,
        rho_min=final_lbm_stats["rho_min"],
        rho_max=final_lbm_stats["rho_max"],
        lbm_max_v=final_lbm_stats["max_v"],
        mpm_min_J=final_mpm_stats["min_J"],
        mpm_max_speed=final_mpm_stats["max_speed"],
        total_mpm_substeps=total_mpm_substeps,
    )
    lbm.export_VTK(n_lbm_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print(f"solid_on_count={solid_on_count}")
    print(f"bb_link_count={final_bb_stats['bb_link_count']}")
    print(f"bb_max_correction={final_bb_stats['bb_max_correction']:.9e}")
    print(f"bb_net_fluid_impulse_x={final_bb_stats['bb_net_fluid_impulse'][0]:.9e}")
    print(f"bb_net_solid_force_x={final_bb_stats['bb_net_solid_force'][0]:.9e}")
    print(f"projection_zone_fluid_mean_ux_initial={initial_projection_zone_fluid_mean_ux:.9e}")
    print(f"projection_zone_fluid_mean_ux_final={final_projection_zone_fluid_mean_ux:.9e}")
    print(f"force_balance_error={force_balance_error:.9e}")
    print(f"hydro_force_max_norm={hydro_force_max:.9e}")
    print(f"cell_force_max_norm={cell_force_max:.9e}")
    print(f"rho_min={final_lbm_stats['rho_min']:.9e}")
    print(f"rho_max={final_lbm_stats['rho_max']:.9e}")
    print(f"lbm_max_v={final_lbm_stats['max_v']:.9e}")
    print(f"mpm_min_J={final_mpm_stats['min_J']:.9e}")
    print(f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}")
    print("[OK] Step 8 projected MPM moving boundary finished")


if __name__ == "__main__":
    main()
