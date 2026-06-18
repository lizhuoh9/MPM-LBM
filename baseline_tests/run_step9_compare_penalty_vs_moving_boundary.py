import csv
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


def force_max_norm(field):
    values = field.to_numpy()
    return float(np.max(np.linalg.norm(values, axis=3)))


def make_lbm_solid(sim, out_dir, geo_name, target_u_norm):
    geo_path = os.path.join(out_dir, geo_name)
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
    return lbm, solid


def run_penalty_mode(sim, out_dir, target_u_norm, n_lbm_steps):
    lbm, solid = make_lbm_solid(sim, out_dir, "geo_penalty_32.dat", target_u_norm)
    projector = MPMToLBMProjector3D(sim)
    coupler = PenaltyFSICoupler3D(sim, beta_lbm=1.0e-3, force_cap_lbm=1.0e-4)

    projector.project(solid, lbm)
    initial_fluid_mean_ux = float(FSIDiagnostics3D.lbm_fluid_stats(lbm)["fluid_mean_velocity"][0])
    initial_projection_zone_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])
    initial_solid_mean_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])

    total_mpm_substeps = 0
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

        if lbm_step % 5 == 0 or lbm_step == n_lbm_steps:
            lbm_stats = lbm.get_stats()
            mpm_stats = solid.get_stats()
            force_stats = FSIDiagnostics3D.force_stats(lbm)
            assert_lbm_stats_ok(lbm_stats)
            assert_mpm_stats_ok(mpm_stats)
            print(
                f"mode=penalty, lbm_step={lbm_step:04d}, "
                f"total_mpm_substeps={total_mpm_substeps}, "
                f"active_force_cell_count={force_stats['active_force_cell_count']}, "
                f"cell_force_max_norm={force_stats['max_cell_force_norm']:.9e}, "
                f"hydro_force_max_norm={force_stats['max_hydro_force_norm']:.9e}, "
                f"rho_min={lbm_stats['rho_min']:.9e}, rho_max={lbm_stats['rho_max']:.9e}, "
                f"mpm_min_J={mpm_stats['min_J']:.9e}"
            )

    projector.project(solid, lbm)
    coupler.build_penalty_force(lbm)
    lbm_stats = lbm.get_stats()
    mpm_stats = solid.get_stats()
    fluid_stats = FSIDiagnostics3D.lbm_fluid_stats(lbm)
    force_stats = FSIDiagnostics3D.force_stats(lbm)
    final_solid_mean_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
    final_projection_zone_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])

    assert_lbm_stats_ok(lbm_stats)
    assert_mpm_stats_ok(mpm_stats)

    result = {
        "mode": "penalty",
        "stable": True,
        "fluid_mean_ux_initial": initial_fluid_mean_ux,
        "fluid_mean_ux_final": float(fluid_stats["fluid_mean_velocity"][0]),
        "projection_zone_ux_initial": initial_projection_zone_ux,
        "projection_zone_ux_final": final_projection_zone_ux,
        "solid_mean_vx_initial": initial_solid_mean_vx,
        "solid_mean_vx_final": final_solid_mean_vx,
        "rho_min": lbm_stats["rho_min"],
        "rho_max": lbm_stats["rho_max"],
        "lbm_max_v": lbm_stats["max_v"],
        "mpm_min_J": mpm_stats["min_J"],
        "mpm_max_speed": mpm_stats["max_speed"],
        "active_force_or_bb_link_count": force_stats["active_force_cell_count"],
        "cell_force_max_norm": force_stats["max_cell_force_norm"],
        "hydro_force_max_norm": force_stats["max_hydro_force_norm"],
    }
    return result


def run_moving_boundary_mode(sim, out_dir, target_u_norm, n_lbm_steps):
    lbm, solid = make_lbm_solid(sim, out_dir, "geo_moving_boundary_32.dat", target_u_norm)
    projector = MPMToLBMProjector3D(sim)
    mb_coupler = MovingBoundaryFSICoupler3D(
        sim,
        reaction_scale=1.0,
        force_cap_norm=1.0e-4,
        phi_min=1.0e-6,
    )
    threshold = 0.5

    projector.project(solid, lbm)
    initial_fluid_mean_ux = float(FSIDiagnostics3D.lbm_fluid_stats(lbm)["fluid_mean_velocity"][0])
    initial_projection_zone_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])
    initial_solid_mean_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])

    total_mpm_substeps = 0
    final_reaction_stats = None
    for lbm_step in range(1, n_lbm_steps + 1):
        projector.project(solid, lbm)
        lbm.update_dynamic_solid(threshold)
        lbm.reinitialize_new_fluid_cells()
        lbm.step_moving_bounceback()

        for _ in range(sim.mpm_substeps_per_lbm_step):
            solid.clear_grid()
            solid.p2g()
            mb_coupler.clear_reaction_diagnostics()
            mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)
            solid.grid_update()
            solid.g2p()
            total_mpm_substeps += 1

        if lbm_step % 5 == 0 or lbm_step == n_lbm_steps:
            lbm_stats = lbm.get_stats()
            mpm_stats = solid.get_stats()
            bb_stats = lbm.get_moving_boundary_stats()
            force_stats = FSIDiagnostics3D.force_stats(lbm)
            final_reaction_stats = mb_coupler.get_stats()
            assert_mpm_stats_ok(mpm_stats)
            assert_finite(
                "moving-boundary comparison transient",
                [
                    lbm_stats["max_v"],
                    lbm_stats["rho_min"],
                    lbm_stats["rho_max"],
                    force_stats["max_cell_force_norm"],
                    force_stats["max_hydro_force_norm"],
                    final_reaction_stats["active_reaction_particle_count"],
                    final_reaction_stats["net_grid_reaction_force"][0],
                ],
            )
            print(
                f"mode=moving_boundary, lbm_step={lbm_step:04d}, "
                f"total_mpm_substeps={total_mpm_substeps}, "
                f"bb_link_count={bb_stats['bb_link_count']}, "
                f"active_reaction_particle_count={final_reaction_stats['active_reaction_particle_count']}, "
                f"net_grid_reaction_force_x={final_reaction_stats['net_grid_reaction_force'][0]:.9e}, "
                f"cell_force_max_norm={force_stats['max_cell_force_norm']:.9e}, "
                f"hydro_force_max_norm={force_stats['max_hydro_force_norm']:.9e}, "
                f"rho_min={lbm_stats['rho_min']:.9e}, rho_max={lbm_stats['rho_max']:.9e}, "
                f"mpm_min_J={mpm_stats['min_J']:.9e}"
            )

    lbm_stats = lbm.get_stats()
    mpm_stats = solid.get_stats()
    fluid_stats = FSIDiagnostics3D.lbm_fluid_stats(lbm)
    bb_stats = lbm.get_moving_boundary_stats()
    force_stats = FSIDiagnostics3D.force_stats(lbm)
    final_solid_mean_vx = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])
    final_projection_zone_ux = float(FSIDiagnostics3D.projection_zone_fluid_mean_velocity(lbm)[0])
    final_reaction_stats = mb_coupler.get_stats()

    assert_lbm_stats_ok(lbm_stats)
    assert_mpm_stats_ok(mpm_stats)

    result = {
        "mode": "moving_boundary",
        "stable": True,
        "fluid_mean_ux_initial": initial_fluid_mean_ux,
        "fluid_mean_ux_final": float(fluid_stats["fluid_mean_velocity"][0]),
        "projection_zone_ux_initial": initial_projection_zone_ux,
        "projection_zone_ux_final": final_projection_zone_ux,
        "solid_mean_vx_initial": initial_solid_mean_vx,
        "solid_mean_vx_final": final_solid_mean_vx,
        "rho_min": lbm_stats["rho_min"],
        "rho_max": lbm_stats["rho_max"],
        "lbm_max_v": lbm_stats["max_v"],
        "mpm_min_J": mpm_stats["min_J"],
        "mpm_max_speed": mpm_stats["max_speed"],
        "active_force_or_bb_link_count": bb_stats["bb_link_count"],
        "cell_force_max_norm": force_stats["max_cell_force_norm"],
        "hydro_force_max_norm": force_stats["max_hydro_force_norm"],
        "active_reaction_particle_count": final_reaction_stats["active_reaction_particle_count"],
        "net_grid_reaction_force_x": final_reaction_stats["net_grid_reaction_force"][0],
    }
    return result


def validate_results(results):
    for result in results:
        values = [
            result["fluid_mean_ux_final"],
            result["projection_zone_ux_final"],
            result["solid_mean_vx_initial"],
            result["solid_mean_vx_final"],
            result["rho_min"],
            result["rho_max"],
            result["lbm_max_v"],
            result["mpm_min_J"],
            result["mpm_max_speed"],
            result["active_force_or_bb_link_count"],
            result["cell_force_max_norm"],
            result["hydro_force_max_norm"],
        ]
        assert_finite(f"{result['mode']} comparison result", values)
        if not result["stable"]:
            raise RuntimeError(f"{result['mode']} mode is not stable")
        if result["fluid_mean_ux_final"] <= result["fluid_mean_ux_initial"]:
            raise RuntimeError(f"{result['mode']} fluid ux did not increase")
        if result["projection_zone_ux_final"] <= result["projection_zone_ux_initial"]:
            raise RuntimeError(f"{result['mode']} projection-zone ux did not increase")
        if result["solid_mean_vx_final"] >= result["solid_mean_vx_initial"]:
            raise RuntimeError(f"{result['mode']} solid vx did not decrease")
        if result["rho_min"] <= 0.95 or result["rho_max"] >= 1.05:
            raise RuntimeError(f"{result['mode']} rho outside accepted range")
        if result["lbm_max_v"] >= 0.1:
            raise RuntimeError(f"{result['mode']} lbm max_v exceeded threshold")
        if result["mpm_min_J"] <= 0.0:
            raise RuntimeError(f"{result['mode']} mpm min_J became non-positive")
        if result["mpm_max_speed"] >= 10.0:
            raise RuntimeError(f"{result['mode']} mpm max_speed exceeded threshold")
        if result["hydro_force_max_norm"] <= 0.0:
            raise RuntimeError(f"{result['mode']} hydro_force stayed zero")
        if result["active_force_or_bb_link_count"] <= 0:
            raise RuntimeError(f"{result['mode']} active force/link count is zero")

    penalty = next(result for result in results if result["mode"] == "penalty")
    moving = next(result for result in results if result["mode"] == "moving_boundary")
    if penalty["cell_force_max_norm"] <= 0.0:
        raise RuntimeError("penalty mode should have nonzero cell_force")
    if moving["cell_force_max_norm"] != 0.0:
        raise RuntimeError(f"moving-boundary mode should keep cell_force zero: {moving['cell_force_max_norm']}")
    if moving["active_reaction_particle_count"] <= 0:
        raise RuntimeError("moving-boundary mode produced no active reaction particles")


def write_results(out_dir, results):
    columns = [
        "mode",
        "stable",
        "fluid_mean_ux_initial",
        "fluid_mean_ux_final",
        "projection_zone_ux_initial",
        "projection_zone_ux_final",
        "solid_mean_vx_initial",
        "solid_mean_vx_final",
        "rho_min",
        "rho_max",
        "lbm_max_v",
        "mpm_min_J",
        "mpm_max_speed",
        "active_force_or_bb_link_count",
        "cell_force_max_norm",
        "hydro_force_max_norm",
    ]
    csv_path = os.path.join(out_dir, "comparison_results.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for result in results:
            writer.writerow({key: result.get(key, "") for key in columns})

    np.savez(
        os.path.join(out_dir, "comparison_results.npz"),
        columns=np.asarray(columns),
        rows=np.asarray([[result.get(column, 0.0) for column in columns[2:]] for result in results], dtype=np.float64),
        modes=np.asarray([result["mode"] for result in results]),
    )


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.02, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    n_lbm_steps = 20

    out_dir = os.path.join(ROOT, "outputs", "step9_compare_modes")
    os.makedirs(out_dir, exist_ok=True)

    print("Step 9 penalty vs moving-boundary comparison")
    print(f"n_grid={sim.n_grid}")
    print("n_particles=4096")
    print(f"n_lbm_steps={n_lbm_steps}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    t0 = time.time()

    penalty_result = run_penalty_mode(sim, out_dir, target_u_norm, n_lbm_steps)
    moving_result = run_moving_boundary_mode(sim, out_dir, target_u_norm, n_lbm_steps)
    results = [penalty_result, moving_result]
    validate_results(results)
    write_results(out_dir, results)

    for result in results:
        print(
            f"mode={result['mode']}, stable={result['stable']}, "
            f"fluid_mean_ux_final={result['fluid_mean_ux_final']:.9e}, "
            f"projection_zone_ux_final={result['projection_zone_ux_final']:.9e}, "
            f"solid_mean_vx_initial={result['solid_mean_vx_initial']:.9e}, "
            f"solid_mean_vx_final={result['solid_mean_vx_final']:.9e}, "
            f"rho_min={result['rho_min']:.9e}, rho_max={result['rho_max']:.9e}, "
            f"lbm_max_v={result['lbm_max_v']:.9e}, "
            f"mpm_min_J={result['mpm_min_J']:.9e}, "
            f"mpm_max_speed={result['mpm_max_speed']:.9e}, "
            f"active_force_or_bb_link_count={int(result['active_force_or_bb_link_count'])}, "
            f"cell_force_max_norm={result['cell_force_max_norm']:.9e}, "
            f"hydro_force_max_norm={result['hydro_force_max_norm']:.9e}"
        )

    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 9 penalty vs moving-boundary comparison finished")


if __name__ == "__main__":
    main()
