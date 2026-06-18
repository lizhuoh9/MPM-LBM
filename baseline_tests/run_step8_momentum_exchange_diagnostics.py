import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import FSIDiagnostics3D, LBMFluid3D, UnifiedSimConfig  # noqa: E402


def make_y_wall_geo(path, n_grid):
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int8)
    geo[:, 0, :] = 1
    geo[:, n_grid - 1, :] = 1
    np.savetxt(path, geo.reshape(-1, order="F"), fmt="%d")


def set_top_wall_velocity(lbm, ux):
    solid_vel = lbm.solid_vel.to_numpy()
    solid_vel[:, :, :, :] = 0.0
    solid_vel[:, lbm.ny - 1, :, 0] = ux
    lbm.solid_vel.from_numpy(solid_vel)


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


def force_max_norm(field):
    values = field.to_numpy()
    return float(np.max(np.linalg.norm(values, axis=3)))


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    target_u_lbm = (0.03, 0.0, 0.0)
    n_steps = 500
    out_dir = os.path.join(ROOT, "outputs", "step8_momentum_exchange")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_momentum_exchange_32.dat")
    make_y_wall_geo(geo_path, sim.n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()
    set_top_wall_velocity(lbm, target_u_lbm[0])

    records = []
    cumulative_fluid_impulse_x = 0.0
    cumulative_solid_force_x = 0.0

    print("Step 8 momentum-exchange diagnostics")
    print(f"n_grid={sim.n_grid}")
    print(f"n_steps={n_steps}")
    print(f"target_u_lbm={target_u_lbm}")
    t0 = time.time()

    for step in range(1, n_steps + 1):
        lbm.step_moving_bounceback()
        lbm_stats = lbm.get_stats()
        bb_stats = lbm.get_moving_boundary_stats()
        hydro_force_max = force_max_norm(lbm.hydro_force)
        cell_force_max = force_max_norm(lbm.cell_force)
        fluid_impulse = np.asarray(bb_stats["bb_net_fluid_impulse"], dtype=np.float64)
        solid_force = np.asarray(bb_stats["bb_net_solid_force"], dtype=np.float64)
        force_balance_error = float(np.linalg.norm(fluid_impulse + solid_force))

        assert_lbm_stats_ok(lbm_stats)
        assert_finite(
            "momentum exchange record",
            [
                bb_stats["bb_link_count"],
                bb_stats["bb_max_correction"],
                fluid_impulse[0],
                solid_force[0],
                force_balance_error,
                hydro_force_max,
                cell_force_max,
                lbm_stats["rho_min"],
                lbm_stats["rho_max"],
                lbm_stats["max_v"],
            ],
        )

        cumulative_fluid_impulse_x += float(fluid_impulse[0])
        cumulative_solid_force_x += float(solid_force[0])
        records.append(
            (
                step,
                bb_stats["bb_link_count"],
                bb_stats["bb_max_correction"],
                fluid_impulse[0],
                solid_force[0],
                force_balance_error,
                hydro_force_max,
                cell_force_max,
                lbm_stats["rho_min"],
                lbm_stats["rho_max"],
                lbm_stats["max_v"],
                cumulative_fluid_impulse_x,
                cumulative_solid_force_x,
            )
        )

        if step % 100 == 0 or step == n_steps:
            print(
                f"step={step:04d}, "
                f"bb_link_count={bb_stats['bb_link_count']}, "
                f"bb_max_correction={bb_stats['bb_max_correction']:.9e}, "
                f"bb_net_fluid_impulse_x={fluid_impulse[0]:.9e}, "
                f"bb_net_solid_force_x={solid_force[0]:.9e}, "
                f"force_balance_error={force_balance_error:.9e}, "
                f"rho_min={lbm_stats['rho_min']:.9e}, "
                f"rho_max={lbm_stats['rho_max']:.9e}, "
                f"lbm_max_v={lbm_stats['max_v']:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    records_np = np.asarray(records, dtype=np.float64)
    final_lbm_stats = lbm.get_stats()
    final_bb_stats = lbm.get_moving_boundary_stats()
    max_force_balance_error = float(np.max(records_np[:, 5]))
    mean_force_balance_error = float(np.mean(records_np[:, 5]))
    max_hydro_force_norm = float(np.max(records_np[:, 6]))
    max_cell_force_norm = float(np.max(records_np[:, 7]))

    if final_bb_stats["bb_link_count"] <= 0:
        raise RuntimeError("moving wall encountered no bounce-back links")
    if final_bb_stats["bb_max_correction"] <= 0.0:
        raise RuntimeError("moving wall correction did not become positive")
    if final_bb_stats["bb_net_fluid_impulse"][0] <= 0.0:
        raise RuntimeError(f"bb_net_fluid_impulse_x should be positive: {final_bb_stats}")
    if final_bb_stats["bb_net_solid_force"][0] >= 0.0:
        raise RuntimeError(f"bb_net_solid_force_x should be negative: {final_bb_stats}")
    if max_force_balance_error >= 1.0e-6:
        raise RuntimeError(f"max force balance error too high: {max_force_balance_error}")
    if max_hydro_force_norm <= 0.0:
        raise RuntimeError("hydro_force diagnostic should be nonzero")
    if max_cell_force_norm != 0.0:
        raise RuntimeError(f"cell_force should remain zero, got {max_cell_force_norm}")

    np.savez(
        os.path.join(out_dir, "momentum_exchange_timeseries.npz"),
        columns=np.asarray(
            [
                "step",
                "bb_link_count",
                "bb_max_correction",
                "bb_net_fluid_impulse_x",
                "bb_net_solid_force_x",
                "force_balance_error",
                "hydro_force_max_norm",
                "cell_force_max_norm",
                "rho_min",
                "rho_max",
                "lbm_max_v",
                "cumulative_fluid_impulse_x",
                "cumulative_solid_force_x",
            ]
        ),
        records=records_np,
        max_force_balance_error=max_force_balance_error,
        mean_force_balance_error=mean_force_balance_error,
        cumulative_fluid_impulse_x=cumulative_fluid_impulse_x,
        cumulative_solid_force_x=cumulative_solid_force_x,
        max_hydro_force_norm=max_hydro_force_norm,
        max_cell_force_norm=max_cell_force_norm,
    )
    lbm.export_VTK(n_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print(f"bb_link_count={final_bb_stats['bb_link_count']}")
    print(f"bb_max_correction={final_bb_stats['bb_max_correction']:.9e}")
    print(f"bb_net_fluid_impulse_x={final_bb_stats['bb_net_fluid_impulse'][0]:.9e}")
    print(f"bb_net_solid_force_x={final_bb_stats['bb_net_solid_force'][0]:.9e}")
    print(f"max_force_balance_error={max_force_balance_error:.9e}")
    print(f"mean_force_balance_error={mean_force_balance_error:.9e}")
    print(f"cumulative_fluid_impulse_x={cumulative_fluid_impulse_x:.9e}")
    print(f"cumulative_solid_force_x={cumulative_solid_force_x:.9e}")
    print(f"hydro_force_max_norm={max_hydro_force_norm:.9e}")
    print(f"cell_force_max_norm={max_cell_force_norm:.9e}")
    print(f"rho_min={final_lbm_stats['rho_min']:.9e}")
    print(f"rho_max={final_lbm_stats['rho_max']:.9e}")
    print(f"lbm_max_v={final_lbm_stats['max_v']:.9e}")
    print("[OK] Step 8 momentum-exchange diagnostics finished")


if __name__ == "__main__":
    main()
