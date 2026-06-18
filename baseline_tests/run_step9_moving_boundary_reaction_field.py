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


def force_max_norm(field):
    values = field.to_numpy()
    return float(np.max(np.linalg.norm(values, axis=3)))


def make_lbm_and_solid(sim, out_dir):
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
    return lbm, solid


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.02, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    threshold = 0.5
    reaction_scale = 1.0
    force_cap_norm = 1.0e-2

    out_dir = os.path.join(ROOT, "outputs", "step9_mb_reaction_field")
    os.makedirs(out_dir, exist_ok=True)
    lbm, solid = make_lbm_and_solid(sim, out_dir)
    solid.set_uniform_velocity(float(target_u_norm[0]), float(target_u_norm[1]), float(target_u_norm[2]))

    projector = MPMToLBMProjector3D(sim)
    mb_coupler = MovingBoundaryFSICoupler3D(
        sim,
        reaction_scale=reaction_scale,
        force_cap_norm=force_cap_norm,
        phi_min=1.0e-6,
    )

    print("Step 9 moving-boundary reaction field")
    print(f"n_grid={sim.n_grid}")
    print("n_particles=4096")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"threshold={threshold:.9e}")
    print(f"reaction_scale={reaction_scale:.9e}")
    print(f"force_cap_norm={force_cap_norm:.9e}")
    t0 = time.time()

    projector.project(solid, lbm)
    lbm.update_dynamic_solid(threshold)
    lbm.reinitialize_new_fluid_cells()
    lbm.step_moving_bounceback()

    solid.clear_grid()
    solid.p2g()
    mb_coupler.clear_reaction_diagnostics()
    mb_coupler.add_moving_boundary_reaction_to_mpm_grid(solid, lbm)

    lbm_stats = lbm.get_stats()
    bb_stats = lbm.get_moving_boundary_stats()
    reaction_stats = mb_coupler.get_stats()
    force_stats = FSIDiagnostics3D.force_stats(lbm)
    hydro_force_max = force_max_norm(lbm.hydro_force)
    grid_f_ext = solid.grid_f_ext.to_numpy()
    grid_force_max = float(np.max(np.linalg.norm(grid_f_ext, axis=3)))

    assert_lbm_stats_ok(lbm_stats)
    assert_finite(
        "reaction field diagnostics",
        [
            bb_stats["bb_link_count"],
            hydro_force_max,
            reaction_stats["active_reaction_particle_count"],
            reaction_stats["max_particle_reaction_norm"],
            reaction_stats["max_grid_reaction_norm"],
            reaction_stats["net_particle_reaction_force"][0],
            reaction_stats["net_grid_reaction_force"][0],
            force_stats["max_cell_force_norm"],
            grid_force_max,
        ],
    )

    if bb_stats["bb_link_count"] <= 0:
        raise RuntimeError("moving-boundary step produced no bounce-back links")
    if hydro_force_max <= 0.0:
        raise RuntimeError("moving-boundary hydro_force is zero")
    if reaction_stats["active_reaction_particle_count"] <= 0:
        raise RuntimeError("reaction coupler found no active particles")
    if reaction_stats["max_particle_reaction_norm"] <= 0.0:
        raise RuntimeError("particle reaction norm is zero")
    if reaction_stats["max_grid_reaction_norm"] <= 0.0 or grid_force_max <= 0.0:
        raise RuntimeError("grid reaction norm is zero")
    if reaction_stats["net_particle_reaction_force"][0] >= 0.0:
        raise RuntimeError(f"net particle reaction force x should be negative: {reaction_stats}")
    if reaction_stats["net_grid_reaction_force"][0] >= 0.0:
        raise RuntimeError(f"net grid reaction force x should be negative: {reaction_stats}")
    if force_stats["max_cell_force_norm"] != 0.0:
        raise RuntimeError(f"cell_force should remain zero, got {force_stats['max_cell_force_norm']}")

    np.save(os.path.join(out_dir, "grid_f_ext.npy"), grid_f_ext)
    np.save(os.path.join(out_dir, "hydro_force.npy"), lbm.hydro_force.to_numpy())
    np.savez(
        os.path.join(out_dir, "diagnostics.npz"),
        bb_link_count=bb_stats["bb_link_count"],
        bb_max_correction=bb_stats["bb_max_correction"],
        hydro_force_max_norm=hydro_force_max,
        grid_force_max_norm=grid_force_max,
        active_reaction_particle_count=reaction_stats["active_reaction_particle_count"],
        max_particle_reaction_norm=reaction_stats["max_particle_reaction_norm"],
        max_grid_reaction_norm=reaction_stats["max_grid_reaction_norm"],
        net_particle_reaction_force=np.asarray(reaction_stats["net_particle_reaction_force"]),
        net_grid_reaction_force=np.asarray(reaction_stats["net_grid_reaction_force"]),
        cell_force_max_norm=force_stats["max_cell_force_norm"],
        rho_min=lbm_stats["rho_min"],
        rho_max=lbm_stats["rho_max"],
        lbm_max_v=lbm_stats["max_v"],
    )
    lbm.export_VTK(0, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print(f"bb_link_count={bb_stats['bb_link_count']}")
    print(f"bb_max_correction={bb_stats['bb_max_correction']:.9e}")
    print(f"hydro_force_max_norm={hydro_force_max:.9e}")
    print(f"active_reaction_particle_count={reaction_stats['active_reaction_particle_count']}")
    print(f"max_particle_reaction_norm={reaction_stats['max_particle_reaction_norm']:.9e}")
    print(f"max_grid_reaction_norm={reaction_stats['max_grid_reaction_norm']:.9e}")
    print(f"net_particle_reaction_force_x={reaction_stats['net_particle_reaction_force'][0]:.9e}")
    print(f"net_grid_reaction_force_x={reaction_stats['net_grid_reaction_force'][0]:.9e}")
    print(f"cell_force_max_norm={force_stats['max_cell_force_norm']:.9e}")
    print(f"rho_min={lbm_stats['rho_min']:.9e}")
    print(f"rho_max={lbm_stats['rho_max']:.9e}")
    print(f"lbm_max_v={lbm_stats['max_v']:.9e}")
    print(f"elapsed={time.time() - t0:.2f}s")
    print("[OK] Step 9 moving-boundary reaction field finished")


if __name__ == "__main__":
    main()
