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

    out_dir = os.path.join(ROOT, "outputs", "step7_momentum_impulse")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_momentum_impulse_32.dat")
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

    projector.project(solid, lbm)
    initial_fluid_mean_ux = float(FSIDiagnostics3D.lbm_fluid_stats(lbm)["fluid_mean_velocity"][0])
    initial_solid_mean_vx_norm = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
    cumulative_cell_impulse_x = 0.0
    cumulative_hydro_impulse_x = 0.0

    records = []
    print("Step 7 momentum impulse diagnostics")
    print(f"n_grid={sim.n_grid}")
    print(f"n_lbm_steps={n_lbm_steps}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"initial_fluid_mean_ux={initial_fluid_mean_ux:.9e}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")

    for lbm_step in range(1, n_lbm_steps + 1):
        projector.project(solid, lbm)
        coupler.build_penalty_force(lbm)
        force_stats = FSIDiagnostics3D.force_stats(lbm)
        cumulative_cell_impulse_x += force_stats["net_cell_force"][0]
        cumulative_hydro_impulse_x += force_stats["net_hydro_force"][0]

        lbm.step()

        for _ in range(sim.mpm_substeps_per_lbm_step):
            solid.clear_grid()
            solid.p2g()
            coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
            solid.grid_update()
            solid.g2p()

        lbm_stats = lbm.get_stats()
        mpm_stats = solid.get_stats()
        assert_lbm_stats_ok(lbm_stats)
        assert_mpm_stats_ok(mpm_stats)

        fluid_mean_ux = float(FSIDiagnostics3D.lbm_fluid_stats(lbm)["fluid_mean_velocity"][0])
        projection_zone_fluid_mean_ux = float(
            FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0]
        )
        solid_mean_vx_norm = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
        records.append(
            (
                lbm_step,
                force_stats["net_cell_force"][0],
                force_stats["net_hydro_force"][0],
                force_stats["force_balance_error"],
                fluid_mean_ux,
                projection_zone_fluid_mean_ux,
                solid_mean_vx_norm,
                cumulative_cell_impulse_x,
                cumulative_hydro_impulse_x,
                lbm_stats["rho_min"],
                lbm_stats["rho_max"],
                lbm_stats["max_v"],
                mpm_stats["min_J"],
                mpm_stats["max_speed"],
            )
        )

        if lbm_step % 20 == 0 or lbm_step == n_lbm_steps:
            print(
                f"lbm_step={lbm_step:04d}, "
                f"net_cell_force_x={force_stats['net_cell_force'][0]:.9e}, "
                f"net_hydro_force_x={force_stats['net_hydro_force'][0]:.9e}, "
                f"force_balance_error={force_stats['force_balance_error']:.9e}, "
                f"fluid_mean_ux={fluid_mean_ux:.9e}, "
                f"solid_mean_vx_norm={solid_mean_vx_norm:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    records_np = np.asarray(records, dtype=np.float64)
    final_fluid_mean_ux = float(records_np[-1, 4])
    final_solid_mean_vx_norm = float(records_np[-1, 6])
    max_force_balance_error = float(np.max(records_np[:, 3]))
    mean_force_balance_error = float(np.mean(records_np[:, 3]))
    final_lbm_stats = lbm.get_stats()
    final_mpm_stats = solid.get_stats()

    print(f"max_force_balance_error={max_force_balance_error:.9e}")
    print(f"mean_force_balance_error={mean_force_balance_error:.9e}")
    print(f"cumulative_cell_impulse_x={cumulative_cell_impulse_x:.9e}")
    print(f"cumulative_hydro_impulse_x={cumulative_hydro_impulse_x:.9e}")
    print(f"final_fluid_mean_ux={final_fluid_mean_ux:.9e}")
    print(f"final_solid_mean_vx_norm={final_solid_mean_vx_norm:.9e}")
    print(f"rho_min={final_lbm_stats['rho_min']:.9e}")
    print(f"rho_max={final_lbm_stats['rho_max']:.9e}")
    print(f"lbm_max_v={final_lbm_stats['max_v']:.9e}")
    print(f"mpm_min_J={final_mpm_stats['min_J']:.9e}")
    print(f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}")

    if max_force_balance_error >= 1.0e-5:
        raise RuntimeError(f"max force balance error too high: {max_force_balance_error}")
    if mean_force_balance_error >= 1.0e-6:
        raise RuntimeError(f"mean force balance error too high: {mean_force_balance_error}")
    if cumulative_cell_impulse_x <= 0.0:
        raise RuntimeError("cumulative cell impulse x is not positive")
    if cumulative_hydro_impulse_x >= 0.0:
        raise RuntimeError("cumulative hydro impulse x is not negative")
    if final_fluid_mean_ux <= initial_fluid_mean_ux:
        raise RuntimeError("fluid mean ux did not increase")
    if final_solid_mean_vx_norm >= initial_solid_mean_vx_norm:
        raise RuntimeError("solid mean vx did not decrease")

    np.savez(
        os.path.join(out_dir, "diagnostics_timeseries.npz"),
        columns=np.asarray(
            [
                "step",
                "net_cell_force_x",
                "net_hydro_force_x",
                "force_balance_error",
                "fluid_mean_ux",
                "projection_zone_fluid_mean_ux",
                "solid_mean_vx_norm",
                "cumulative_cell_impulse_x",
                "cumulative_hydro_impulse_x",
                "rho_min",
                "rho_max",
                "lbm_max_v",
                "mpm_min_J",
                "mpm_max_speed",
            ]
        ),
        records=records_np,
        max_force_balance_error=max_force_balance_error,
        mean_force_balance_error=mean_force_balance_error,
        cumulative_cell_impulse_x=cumulative_cell_impulse_x,
        cumulative_hydro_impulse_x=cumulative_hydro_impulse_x,
    )
    lbm.export_VTK(n_lbm_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print("[OK] Step 7 momentum impulse diagnostics finished")


if __name__ == "__main__":
    main()
