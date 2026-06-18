import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import FSIDriver3D, FSIDriverConfig  # noqa: E402


def assert_final_stats_ok(final_row):
    values = [
        final_row["projection_zone_fluid_mean_ux"],
        final_row["solid_mean_vx_norm"],
        final_row["cell_force_max_norm"],
        final_row["hydro_force_max_norm"],
        final_row["bb_link_count"],
        final_row["active_reaction_particle_count"],
        final_row["rho_min"],
        final_row["rho_max"],
        final_row["lbm_max_v"],
        final_row["mpm_min_J"],
        final_row["mpm_max_speed"],
    ]
    if not np.all(np.isfinite(values)):
        raise RuntimeError("moving-boundary driver diagnostics contain NaN or Inf")
    if final_row["projection_zone_fluid_mean_ux"] <= 0.0:
        raise RuntimeError("moving-boundary driver projection zone ux did not increase")
    if final_row["cell_force_max_norm"] != 0.0:
        raise RuntimeError("moving-boundary driver cell_force should remain zero")
    if final_row["hydro_force_max_norm"] <= 0.0:
        raise RuntimeError("moving-boundary driver hydro_force stayed zero")
    if final_row["bb_link_count"] <= 0:
        raise RuntimeError("moving-boundary driver produced no bounce-back links")
    if final_row["active_reaction_particle_count"] <= 0:
        raise RuntimeError("moving-boundary driver produced no active reaction particles")
    if final_row["rho_min"] <= 0.95 or final_row["rho_max"] >= 1.05:
        raise RuntimeError(f"moving-boundary driver rho outside accepted range: {final_row}")
    if final_row["lbm_max_v"] >= 0.1:
        raise RuntimeError(f"moving-boundary driver lbm max_v exceeded threshold: {final_row}")
    if final_row["mpm_min_J"] <= 0.0:
        raise RuntimeError(f"moving-boundary driver mpm min_J became non-positive: {final_row}")
    if final_row["mpm_max_speed"] >= 10.0:
        raise RuntimeError(f"moving-boundary driver mpm max_speed exceeded threshold: {final_row}")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    config = FSIDriverConfig.from_json(os.path.join(ROOT, "configs", "step10_moving_boundary_default.json"))
    out_dir = os.path.join(ROOT, "outputs", "step10_driver_moving_boundary")

    print("Step 10 driver moving-boundary mode")
    print(f"coupling_mode={config.coupling_mode}")
    print(f"n_grid={config.n_grid}")
    print(f"n_particles={config.n_particles}")
    print(f"n_lbm_steps={config.n_lbm_steps}")
    print(f"mpm_substeps_per_lbm_step={config.mpm_substeps_per_lbm_step}")
    print(f"target_u_lbm={config.target_u_lbm}")
    print(f"mb_reaction_scale={config.mb_reaction_scale:.9e}")
    print(f"mb_force_cap_norm={config.mb_force_cap_norm:.9e}")
    t0 = time.time()

    driver = FSIDriver3D(config, out_dir)
    rows = driver.run()
    initial_row = rows[0]
    final_row = rows[-1]
    assert_final_stats_ok(final_row)
    if final_row["total_mpm_substeps"] != config.n_lbm_steps * config.mpm_substeps_per_lbm_step:
        raise RuntimeError("moving-boundary driver total_mpm_substeps mismatch")
    if final_row["solid_mean_vx_norm"] >= initial_row["solid_mean_vx_norm"]:
        raise RuntimeError("moving-boundary driver solid mean vx did not decrease")

    print(f"completed_lbm_steps={driver.current_lbm_step}")
    print(f"total_mpm_substeps={driver.total_mpm_substeps}")
    print(f"projection_zone_fluid_mean_ux_final={final_row['projection_zone_fluid_mean_ux']:.9e}")
    print(f"solid_mean_vx_initial={initial_row['solid_mean_vx_norm']:.9e}")
    print(f"solid_mean_vx_final={final_row['solid_mean_vx_norm']:.9e}")
    print(f"bb_link_count={final_row['bb_link_count']}")
    print(f"active_reaction_particle_count={final_row['active_reaction_particle_count']}")
    print(f"cell_force_max_norm={final_row['cell_force_max_norm']:.9e}")
    print(f"hydro_force_max_norm={final_row['hydro_force_max_norm']:.9e}")
    print(f"rho_min={final_row['rho_min']:.9e}")
    print(f"rho_max={final_row['rho_max']:.9e}")
    print(f"lbm_max_v={final_row['lbm_max_v']:.9e}")
    print(f"mpm_min_J={final_row['mpm_min_J']:.9e}")
    print(f"mpm_max_speed={final_row['mpm_max_speed']:.9e}")
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 10 driver moving-boundary mode finished")


if __name__ == "__main__":
    main()
