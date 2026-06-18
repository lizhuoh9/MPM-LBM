import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import LBMFluid3D, UnifiedSimConfig  # noqa: E402


def make_y_wall_geo(path, n_grid):
    geo = np.zeros((n_grid, n_grid, n_grid), dtype=np.int8)
    geo[:, 0, :] = 1
    geo[:, n_grid - 1, :] = 1
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


def cell_force_max_norm(lbm):
    force = lbm.cell_force.to_numpy()
    return float(np.max(np.linalg.norm(force, axis=3)))


def make_lbm(sim, geo_path):
    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()
    return lbm


def run_solver(label, sim, geo_path, n_steps, out_dir, use_moving_bounceback):
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    lbm = make_lbm(sim, geo_path)
    t0 = time.time()
    print(f"running_{label}=true")

    for step in range(1, n_steps + 1):
        if use_moving_bounceback:
            lbm.step_moving_bounceback()
        else:
            lbm.step()

        if step % 25 == 0 or step == n_steps:
            stats = lbm.get_stats()
            assert_lbm_stats_ok(stats)
            print(
                f"{label}_step={step:04d}, "
                f"rho_min={stats['rho_min']:.9e}, "
                f"rho_max={stats['rho_max']:.9e}, "
                f"lbm_max_v={stats['max_v']:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    stats = lbm.get_stats()
    bb_stats = lbm.get_moving_boundary_stats() if use_moving_bounceback else None
    force_max = cell_force_max_norm(lbm)
    velocity = lbm.v.to_numpy()
    rho = lbm.rho.to_numpy()
    out_prefix = "LBMMovingZero" if use_moving_bounceback else "LBMStatic"
    lbm.export_VTK(n_steps, out_prefix=os.path.join(out_dir, out_prefix))
    return velocity, rho, stats, bb_stats, force_max


def main():
    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    n_steps = 100
    out_dir = os.path.join(ROOT, "outputs", "step8_static_bounceback_regression")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_y_walls_32.dat")
    make_y_wall_geo(geo_path, sim.n_grid)

    print("Step 8 static bounce-back regression")
    print(f"n_grid={sim.n_grid}")
    print(f"n_steps={n_steps}")

    static_velocity, static_rho, static_stats, _, static_force_max = run_solver(
        "static", sim, geo_path, n_steps, out_dir, use_moving_bounceback=False
    )
    ti.reset()
    moving_velocity, moving_rho, moving_stats, bb_stats, force_max = run_solver(
        "moving_zero", sim, geo_path, n_steps, out_dir, use_moving_bounceback=True
    )

    velocity_difference = moving_velocity - static_velocity
    rho_difference = moving_rho - static_rho
    max_abs_velocity_difference = float(np.max(np.abs(velocity_difference)))
    max_abs_rho_difference = float(np.max(np.abs(rho_difference)))

    assert_finite(
        "static regression differences",
        [max_abs_velocity_difference, max_abs_rho_difference, force_max],
    )
    if bb_stats["bb_link_count"] <= 0:
        raise RuntimeError("moving bounce-back encountered no solid links")
    if abs(bb_stats["bb_max_correction"]) > 1.0e-12:
        raise RuntimeError(f"zero wall velocity correction is nonzero: {bb_stats}")
    if max_abs_velocity_difference >= 1.0e-6:
        raise RuntimeError(f"velocity regression difference too large: {max_abs_velocity_difference}")
    if max_abs_rho_difference >= 1.0e-6:
        raise RuntimeError(f"rho regression difference too large: {max_abs_rho_difference}")
    if static_force_max != 0.0:
        raise RuntimeError(f"static cell_force should remain zero, got {static_force_max}")
    if force_max != 0.0:
        raise RuntimeError(f"moving cell_force should remain zero, got {force_max}")

    np.save(os.path.join(out_dir, "velocity_difference.npy"), velocity_difference)
    np.save(os.path.join(out_dir, "rho_difference.npy"), rho_difference)

    print(f"bb_link_count={bb_stats['bb_link_count']}")
    print(f"bb_max_correction={bb_stats['bb_max_correction']:.9e}")
    print(f"bb_net_fluid_impulse_x={bb_stats['bb_net_fluid_impulse'][0]:.9e}")
    print(f"bb_net_solid_force_x={bb_stats['bb_net_solid_force'][0]:.9e}")
    print(f"max_abs_velocity_difference={max_abs_velocity_difference:.9e}")
    print(f"max_abs_rho_difference={max_abs_rho_difference:.9e}")
    print(f"static_rho_min={static_stats['rho_min']:.9e}")
    print(f"static_rho_max={static_stats['rho_max']:.9e}")
    print(f"rho_min={moving_stats['rho_min']:.9e}")
    print(f"rho_max={moving_stats['rho_max']:.9e}")
    print(f"lbm_max_v={moving_stats['max_v']:.9e}")
    print(f"cell_force_max_norm={force_max:.9e}")
    print("[OK] Step 8 static bounce-back regression finished")


if __name__ == "__main__":
    main()
