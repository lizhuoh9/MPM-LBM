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


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32)
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.03, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)

    out_dir = os.path.join(ROOT, "outputs", "step6_penalty_force_field")
    os.makedirs(out_dir, exist_ok=True)
    geo_path = os.path.join(out_dir, "geo_force_32.dat")
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

    rho_initial = lbm.rho.to_numpy()
    J_initial = solid.Jp.to_numpy()

    projector.project(solid, lbm)
    coupler.clear_force_fields(lbm)
    coupler.build_penalty_force(lbm)
    stats = coupler.get_stats()

    cell_force = lbm.cell_force.to_numpy()
    hydro_force = lbm.hydro_force.to_numpy()
    rho_final = lbm.rho.to_numpy()
    J_final = solid.Jp.to_numpy()

    assert_finite("cell_force", cell_force)
    assert_finite("hydro_force", hydro_force)
    assert_finite("rho", rho_final)
    assert_finite("Jp", J_final)

    cell_force_max_norm = float(np.max(np.linalg.norm(cell_force, axis=3)))
    hydro_force_max_norm = float(np.max(np.linalg.norm(hydro_force, axis=3)))
    net_cell_force = np.sum(cell_force.reshape(-1, 3), axis=0, dtype=np.float64)
    net_hydro_force = np.sum(hydro_force.reshape(-1, 3), axis=0, dtype=np.float64)
    balance_error = float(np.linalg.norm(net_cell_force + net_hydro_force))
    rho_delta = float(np.max(np.abs(rho_final - rho_initial)))
    J_delta = float(np.max(np.abs(J_final - J_initial)))

    print("Step 6 penalty force field baseline")
    print(f"target_u_lbm={target_u_lbm}")
    print(f"target_u_norm={tuple(float(v) for v in target_u_norm)}")
    print(f"beta_lbm={stats['beta_lbm']:.9e}")
    print(f"phi_min={stats['phi_min']:.9e}")
    print(f"force_cap_lbm={stats['force_cap_lbm']:.9e}")
    print(f"reaction_scale={stats['reaction_scale']:.9e}")
    print(f"force_density_scale_lbm_to_norm={stats['force_density_scale_lbm_to_norm']:.9e}")
    print(f"active_force_cell_count={stats['active_force_cell_count']}")
    print(f"cell_force_max_norm={cell_force_max_norm:.9e}")
    print(f"hydro_force_max_norm={hydro_force_max_norm:.9e}")
    print(f"net_cell_force={net_cell_force.tolist()}")
    print(f"net_hydro_force={net_hydro_force.tolist()}")
    print(f"balance_error={balance_error:.9e}")
    print(f"rho_delta={rho_delta:.9e}")
    print(f"J_delta={J_delta:.9e}")
    print(f"elapsed={time.time() - t0:.2f}s")

    if stats["active_force_cell_count"] <= 0:
        raise RuntimeError("no active force cells")
    if cell_force_max_norm <= 0.0 or hydro_force_max_norm <= 0.0:
        raise RuntimeError("force fields stayed zero")
    if net_cell_force[0] <= 0.0:
        raise RuntimeError(f"net cell force x is not positive: {net_cell_force}")
    if net_hydro_force[0] >= 0.0:
        raise RuntimeError(f"net hydro force x is not negative: {net_hydro_force}")
    if balance_error >= 1.0e-10:
        raise RuntimeError(f"force balance error too high: {balance_error}")
    if abs(float(net_cell_force[1])) >= 1.0e-10 or abs(float(net_cell_force[2])) >= 1.0e-10:
        raise RuntimeError(f"unexpected lateral net cell force: {net_cell_force}")
    if rho_delta != 0.0:
        raise RuntimeError(f"rho changed without LBM advance: {rho_delta}")
    if J_delta != 0.0:
        raise RuntimeError(f"MPM J changed without MPM advance: {J_delta}")

    np.save(os.path.join(out_dir, "cell_force.npy"), cell_force)
    np.save(os.path.join(out_dir, "hydro_force.npy"), hydro_force)
    lbm.export_VTK(0, out_prefix=os.path.join(out_dir, "LBMForce"))

    print("[OK] Step 6 penalty force field baseline finished")


if __name__ == "__main__":
    main()
