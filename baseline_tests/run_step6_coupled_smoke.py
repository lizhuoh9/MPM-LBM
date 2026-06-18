import os
import sys
import time

import numpy as np
import taichi as ti


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import (  # noqa: E402
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


def mean_active_ux(lbm, phi_min=1.0e-6):
    solid_phi = lbm.solid_phi.to_numpy()
    v = lbm.v.to_numpy()
    active = solid_phi > phi_min
    if not np.any(active):
        raise RuntimeError("no active projected cells")
    return float(np.average(v[..., 0][active], weights=solid_phi[active]))


def mean_solid_vx(solid):
    return float(np.mean(solid.v.to_numpy()[:, 0]))


def assert_lbm_stats_ok(stats):
    values = [stats["max_v"], stats["rho_min"], stats["rho_max"], stats["mass_total"]]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"LBM stats contain NaN or Inf: {stats}")
    if stats["rho_min"] <= 0.95 or stats["rho_max"] >= 1.05:
        raise RuntimeError(f"LBM rho left accepted range: {stats}")
    if stats["max_v"] >= 0.1:
        raise RuntimeError(f"LBM max_v exceeded threshold: {stats}")


def assert_mpm_stats_ok(stats):
    values = [*stats["min_x"], *stats["max_x"], stats["max_speed"], stats["min_J"], stats["max_J"]]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"MPM stats contain NaN or Inf: {stats}")
    if stats["min_J"] <= 0.0:
        raise RuntimeError(f"MPM min_J became non-positive: {stats}")
    if stats["max_speed"] >= 10.0:
        raise RuntimeError(f"MPM max_speed exceeded threshold: {stats}")


def assert_outputs_exist(out_dir):
    required = [
        "LBMFluid_20.vtr",
        "particles_x.npy",
        "particles_v.npy",
        "particles_F.npy",
        "particles_J.npy",
        "cell_force.npy",
        "hydro_force.npy",
    ]
    missing = [name for name in required if not os.path.isfile(os.path.join(out_dir, name))]
    if missing:
        raise RuntimeError(f"missing output files: {missing}")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.02, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    n_lbm_steps = 20

    out_dir = os.path.join(ROOT, "outputs", "step6_coupled_smoke")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_coupled_smoke_32.dat")
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
    initial_fluid_mean_ux = mean_active_ux(lbm)
    initial_solid_mean_vx_norm = mean_solid_vx(solid)

    print("Step 6 coupled smoke baseline")
    print(f"n_grid={sim.n_grid}")
    print(f"n_lbm_steps={n_lbm_steps}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"initial_fluid_mean_ux={initial_fluid_mean_ux:.9e}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")

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

        if lbm_step % 5 == 0 or lbm_step == n_lbm_steps:
            final_lbm_stats = lbm.get_stats()
            final_mpm_stats = solid.get_stats()
            assert_lbm_stats_ok(final_lbm_stats)
            assert_mpm_stats_ok(final_mpm_stats)
            stats = coupler.get_stats()
            print(
                f"lbm_step={lbm_step:04d}, total_mpm_substeps={total_mpm_substeps}, "
                f"active_force_cell_count={stats['active_force_cell_count']}, "
                f"cell_force_max_norm={stats['max_cell_force_norm']:.9e}, "
                f"hydro_force_max_norm={stats['max_hydro_force_norm']:.9e}, "
                f"rho_min={final_lbm_stats['rho_min']:.9e}, "
                f"rho_max={final_lbm_stats['rho_max']:.9e}, "
                f"lbm_max_v={final_lbm_stats['max_v']:.9e}, "
                f"mpm_min_J={final_mpm_stats['min_J']:.9e}, "
                f"mpm_max_speed={final_mpm_stats['max_speed']:.9e}, "
                f"elapsed={time.time() - t0:.2f}s"
            )

    projector.project(solid, lbm)
    coupler.build_penalty_force(lbm)
    final_fluid_mean_ux = mean_active_ux(lbm)
    final_solid_mean_vx_norm = mean_solid_vx(solid)
    final_lbm_stats = lbm.get_stats()
    final_mpm_stats = solid.get_stats()
    final_stats = coupler.get_stats()
    cell_force = lbm.cell_force.to_numpy()
    hydro_force = lbm.hydro_force.to_numpy()
    particles_x = solid.x.to_numpy()

    assert_lbm_stats_ok(final_lbm_stats)
    assert_mpm_stats_ok(final_mpm_stats)
    assert_finite("cell_force", cell_force)
    assert_finite("hydro_force", hydro_force)
    assert_finite("particles_x", particles_x)

    expected_substeps = n_lbm_steps * sim.mpm_substeps_per_lbm_step
    if total_mpm_substeps != expected_substeps:
        raise RuntimeError(f"unexpected MPM substeps: {total_mpm_substeps} != {expected_substeps}")
    if final_fluid_mean_ux <= initial_fluid_mean_ux:
        raise RuntimeError(
            f"fluid mean ux did not increase: {initial_fluid_mean_ux} -> {final_fluid_mean_ux}"
        )
    if final_solid_mean_vx_norm >= initial_solid_mean_vx_norm:
        raise RuntimeError(
            "solid mean vx did not decrease: "
            f"{initial_solid_mean_vx_norm} -> {final_solid_mean_vx_norm}"
        )
    if final_stats["max_cell_force_norm"] <= 0.0 or final_stats["max_hydro_force_norm"] <= 0.0:
        raise RuntimeError("force fields stayed zero")

    np.save(os.path.join(out_dir, "cell_force.npy"), cell_force)
    np.save(os.path.join(out_dir, "hydro_force.npy"), hydro_force)
    solid.export_particles(out_dir)
    lbm.export_VTK(n_lbm_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))
    assert_outputs_exist(out_dir)

    print(f"initial_fluid_mean_ux={initial_fluid_mean_ux:.9e}")
    print(f"final_fluid_mean_ux={final_fluid_mean_ux:.9e}")
    print(f"initial_solid_mean_vx_norm={initial_solid_mean_vx_norm:.9e}")
    print(f"final_solid_mean_vx_norm={final_solid_mean_vx_norm:.9e}")
    print(f"active_force_cell_count={final_stats['active_force_cell_count']}")
    print(f"cell_force_max_norm={final_stats['max_cell_force_norm']:.9e}")
    print(f"hydro_force_max_norm={final_stats['max_hydro_force_norm']:.9e}")
    print(f"net_cell_force={final_stats['net_cell_force']}")
    print(f"net_hydro_force={final_stats['net_hydro_force']}")
    print(f"max_reaction_grid_force_norm={final_stats['max_reaction_grid_force_norm']:.9e}")
    print(f"net_reaction_grid_force={final_stats['net_reaction_grid_force']}")
    print(f"completed_lbm_steps={n_lbm_steps}")
    print(f"total_mpm_substeps={total_mpm_substeps}")
    print(
        "[OK] Step 6 coupled smoke baseline finished. "
        f"completed_lbm_steps={n_lbm_steps}, total_mpm_substeps={total_mpm_substeps}, "
        f"rho_min={final_lbm_stats['rho_min']:.9e}, rho_max={final_lbm_stats['rho_max']:.9e}, "
        f"lbm_max_v={final_lbm_stats['max_v']:.9e}, "
        f"mpm_min_J={final_mpm_stats['min_J']:.9e}, "
        "mpm_max_speed="
        f"{final_mpm_stats['max_speed']:.9e}, out_dir=outputs/step6_coupled_smoke"
    )


if __name__ == "__main__":
    main()
