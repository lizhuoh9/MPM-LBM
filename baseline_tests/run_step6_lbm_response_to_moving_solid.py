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


def assert_lbm_stats_ok(stats):
    values = [stats["max_v"], stats["rho_min"], stats["rho_max"], stats["mass_total"]]
    if not np.all(np.isfinite(values)):
        raise RuntimeError(f"LBM stats contain NaN or Inf: {stats}")
    if stats["rho_min"] <= 0.95 or stats["rho_max"] >= 1.05:
        raise RuntimeError(f"LBM rho left accepted range: {stats}")
    if stats["max_v"] >= 0.1:
        raise RuntimeError(f"LBM max_v exceeded threshold: {stats}")


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.03, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    n_lbm_steps = 100

    out_dir = os.path.join(ROOT, "outputs", "step6_lbm_response")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_lbm_response_32.dat")
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
    coupler = PenaltyFSICoupler3D(sim, beta_lbm=3.0e-3, force_cap_lbm=1.0e-4)

    projector.project(solid, lbm)
    initial_fluid_mean_ux = mean_active_ux(lbm)
    final_lbm_stats = None

    print("Step 6 LBM response baseline")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"n_lbm_steps={n_lbm_steps}")
    print(f"initial_fluid_mean_ux={initial_fluid_mean_ux:.9e}")

    for step in range(1, n_lbm_steps + 1):
        projector.project(solid, lbm)
        coupler.build_penalty_force(lbm)
        lbm.step()

        if step % 20 == 0 or step == n_lbm_steps:
            final_lbm_stats = lbm.get_stats()
            assert_lbm_stats_ok(final_lbm_stats)
            stats = coupler.get_stats()
            print(
                f"lbm_step={step:04d}, active_force_cell_count={stats['active_force_cell_count']}, "
                f"cell_force_max_norm={stats['max_cell_force_norm']:.9e}, "
                f"hydro_force_max_norm={stats['max_hydro_force_norm']:.9e}, "
                f"rho_min={final_lbm_stats['rho_min']:.9e}, rho_max={final_lbm_stats['rho_max']:.9e}, "
                f"lbm_max_v={final_lbm_stats['max_v']:.9e}, elapsed={time.time() - t0:.2f}s"
            )

    projector.project(solid, lbm)
    final_fluid_mean_ux = mean_active_ux(lbm)
    stats = coupler.get_stats()
    cell_force = lbm.cell_force.to_numpy()
    hydro_force = lbm.hydro_force.to_numpy()
    assert_finite("cell_force", cell_force)
    assert_finite("hydro_force", hydro_force)
    assert_lbm_stats_ok(final_lbm_stats)

    print(f"initial_fluid_mean_ux={initial_fluid_mean_ux:.9e}")
    print(f"final_fluid_mean_ux={final_fluid_mean_ux:.9e}")
    print(f"active_force_cell_count={stats['active_force_cell_count']}")
    print(f"cell_force_max_norm={stats['max_cell_force_norm']:.9e}")
    print(f"hydro_force_max_norm={stats['max_hydro_force_norm']:.9e}")
    print(f"net_cell_force={stats['net_cell_force']}")
    print(f"net_hydro_force={stats['net_hydro_force']}")

    if final_fluid_mean_ux <= initial_fluid_mean_ux:
        raise RuntimeError(
            f"fluid mean ux did not increase: {initial_fluid_mean_ux} -> {final_fluid_mean_ux}"
        )
    if final_fluid_mean_ux <= 0.0:
        raise RuntimeError(f"fluid mean ux is not positive: {final_fluid_mean_ux}")
    if stats["active_force_cell_count"] <= 0:
        raise RuntimeError("no active force cells")
    if stats["max_cell_force_norm"] <= 0.0 or stats["max_hydro_force_norm"] <= 0.0:
        raise RuntimeError("force fields stayed zero")

    np.save(os.path.join(out_dir, "cell_force.npy"), cell_force)
    np.save(os.path.join(out_dir, "hydro_force.npy"), hydro_force)
    lbm.export_VTK(n_lbm_steps, out_prefix=os.path.join(out_dir, "LBMFluid"))

    print("[OK] Step 6 LBM response baseline finished")


if __name__ == "__main__":
    main()
