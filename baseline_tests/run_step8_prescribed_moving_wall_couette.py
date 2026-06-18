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
    n_steps = 1000
    out_dir = os.path.join(ROOT, "outputs", "step8_prescribed_moving_wall")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_moving_wall_32.dat")
    make_y_wall_geo(geo_path, sim.n_grid)

    lbm = LBMFluid3D(sim.make_lbm_config())
    lbm.init_geo(geo_path)
    lbm.init_simulation()
    set_top_wall_velocity(lbm, target_u_lbm[0])

    print("Step 8 prescribed moving wall Couette")
    print(f"n_grid={sim.n_grid}")
    print(f"n_steps={n_steps}")
    print(f"target_u_lbm={target_u_lbm}")
    t0 = time.time()

    for step in range(1, n_steps + 1):
        lbm.step_moving_bounceback()

        if step % 200 == 0 or step == n_steps:
            lbm_stats = lbm.get_stats()
            bb_stats = lbm.get_moving_boundary_stats()
            assert_lbm_stats_ok(lbm_stats)
            print(
                f"step={step:04d}, "
                f"rho_min={lbm_stats['rho_min']:.9e}, "
                f"rho_max={lbm_stats['rho_max']:.9e}, "
                f"lbm_max_v={lbm_stats['max_v']:.9e}, "
                f"bb_link_count={bb_stats['bb_link_count']}, "
                f"bb_max_correction={bb_stats['bb_max_correction']:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    ux_profile_y = FSIDiagnostics3D.lbm_velocity_profile_x_over_y(lbm)
    interior_profile = ux_profile_y[1:-1]
    profile_diffs = np.diff(interior_profile)
    mostly_increasing_fraction = float(np.mean(profile_diffs >= -1.0e-6))
    top_near_ux = float(ux_profile_y[-2])
    bottom_near_ux = float(ux_profile_y[1])
    global_mean_ux = float(FSIDiagnostics3D.lbm_fluid_stats(lbm)["fluid_mean_velocity"][0])
    lbm_stats = lbm.get_stats()
    bb_stats = lbm.get_moving_boundary_stats()
    cell_force_max = force_max_norm(lbm.cell_force)
    hydro_force_max = force_max_norm(lbm.hydro_force)
    force_balance_error = float(
        np.linalg.norm(np.asarray(bb_stats["bb_net_fluid_impulse"]) + np.asarray(bb_stats["bb_net_solid_force"]))
    )

    assert_lbm_stats_ok(lbm_stats)
    assert_finite(
        "moving wall diagnostics",
        [
            *ux_profile_y,
            top_near_ux,
            bottom_near_ux,
            global_mean_ux,
            bb_stats["bb_max_correction"],
            bb_stats["bb_net_fluid_impulse"][0],
            bb_stats["bb_net_solid_force"][0],
            cell_force_max,
            hydro_force_max,
            force_balance_error,
        ],
    )

    if top_near_ux <= bottom_near_ux:
        raise RuntimeError(f"top_near_ux <= bottom_near_ux: {top_near_ux} <= {bottom_near_ux}")
    if global_mean_ux <= 0.0:
        raise RuntimeError(f"global fluid ux is not positive: {global_mean_ux}")
    if mostly_increasing_fraction < 0.85:
        raise RuntimeError(f"ux_profile_y is not mostly increasing: {mostly_increasing_fraction}")
    if bb_stats["bb_link_count"] <= 0:
        raise RuntimeError("moving wall encountered no bounce-back links")
    if bb_stats["bb_max_correction"] <= 0.0:
        raise RuntimeError("moving wall correction did not become positive")
    if bb_stats["bb_net_fluid_impulse"][0] <= 0.0:
        raise RuntimeError(f"bb_net_fluid_impulse_x should be positive: {bb_stats}")
    if bb_stats["bb_net_solid_force"][0] >= 0.0:
        raise RuntimeError(f"bb_net_solid_force_x should be negative: {bb_stats}")
    if cell_force_max != 0.0:
        raise RuntimeError(f"cell_force should remain zero, got {cell_force_max}")
    if hydro_force_max <= 0.0:
        raise RuntimeError("hydro_force diagnostic should be nonzero")

    np.save(os.path.join(out_dir, "ux_profile_y.npy"), ux_profile_y)
    np.savez(
        os.path.join(out_dir, "diagnostics.npz"),
        top_near_ux=top_near_ux,
        bottom_near_ux=bottom_near_ux,
        global_mean_ux=global_mean_ux,
        mostly_increasing_fraction=mostly_increasing_fraction,
        bb_link_count=bb_stats["bb_link_count"],
        bb_max_correction=bb_stats["bb_max_correction"],
        bb_net_fluid_impulse=np.asarray(bb_stats["bb_net_fluid_impulse"]),
        bb_net_solid_force=np.asarray(bb_stats["bb_net_solid_force"]),
        force_balance_error=force_balance_error,
        hydro_force_max_norm=hydro_force_max,
        cell_force_max_norm=cell_force_max,
        rho_min=lbm_stats["rho_min"],
        rho_max=lbm_stats["rho_max"],
        lbm_max_v=lbm_stats["max_v"],
        ux_profile_y=ux_profile_y,
    )
    lbm.export_VTK(n_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print(f"top_near_ux={top_near_ux:.9e}")
    print(f"bottom_near_ux={bottom_near_ux:.9e}")
    print(f"global_mean_ux={global_mean_ux:.9e}")
    print(f"mostly_increasing_fraction={mostly_increasing_fraction:.9e}")
    print(f"bb_link_count={bb_stats['bb_link_count']}")
    print(f"bb_max_correction={bb_stats['bb_max_correction']:.9e}")
    print(f"bb_net_fluid_impulse_x={bb_stats['bb_net_fluid_impulse'][0]:.9e}")
    print(f"bb_net_solid_force_x={bb_stats['bb_net_solid_force'][0]:.9e}")
    print(f"force_balance_error={force_balance_error:.9e}")
    print(f"hydro_force_max_norm={hydro_force_max:.9e}")
    print(f"cell_force_max_norm={cell_force_max:.9e}")
    print(f"rho_min={lbm_stats['rho_min']:.9e}")
    print(f"rho_max={lbm_stats['rho_max']:.9e}")
    print(f"lbm_max_v={lbm_stats['max_v']:.9e}")
    print("[OK] Step 8 prescribed moving wall Couette finished")


if __name__ == "__main__":
    main()
