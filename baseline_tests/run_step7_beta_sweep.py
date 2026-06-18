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
    PenaltyFSICoupler3D,
    UnifiedSimConfig,
)


CSV_FIELDS = [
    "beta_lbm",
    "stable",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "initial_fluid_mean_ux",
    "final_fluid_mean_ux",
    "initial_solid_mean_vx_norm",
    "final_solid_mean_vx_norm",
    "solid_slowdown_norm",
    "max_cell_force_norm",
    "max_hydro_force_norm",
    "active_force_cell_count",
    "failure_reason",
]


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


def run_case(sim, beta_lbm, out_dir):
    mapper = GridUnitMapper.from_sim_config(sim)
    target_u_lbm = (0.02, 0.0, 0.0)
    target_u_norm = mapper.velocity_lbm_to_norm(target_u_lbm)
    n_lbm_steps = 50
    geo_path = os.path.join(out_dir, f"geo_beta_{beta_lbm:.0e}.dat")
    make_all_fluid_geo(geo_path, sim.n_grid)

    row = {
        "beta_lbm": beta_lbm,
        "stable": False,
        "rho_min": np.nan,
        "rho_max": np.nan,
        "lbm_max_v": np.nan,
        "mpm_min_J": np.nan,
        "mpm_max_speed": np.nan,
        "initial_fluid_mean_ux": np.nan,
        "final_fluid_mean_ux": np.nan,
        "initial_solid_mean_vx_norm": np.nan,
        "final_solid_mean_vx_norm": np.nan,
        "solid_slowdown_norm": np.nan,
        "max_cell_force_norm": np.nan,
        "max_hydro_force_norm": np.nan,
        "active_force_cell_count": 0,
        "failure_reason": "",
    }

    try:
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
        coupler = PenaltyFSICoupler3D(sim, beta_lbm=beta_lbm, force_cap_lbm=1.0e-4)

        projector.project(solid, lbm)
        row["initial_fluid_mean_ux"] = float(FSIDiagnostics3D.lbm_fluid_stats(lbm)["fluid_mean_velocity"][0])
        row["initial_solid_mean_vx_norm"] = float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0])

        for _ in range(n_lbm_steps):
            projector.project(solid, lbm)
            coupler.build_penalty_force(lbm)
            lbm.step()

            for _ in range(sim.mpm_substeps_per_lbm_step):
                solid.clear_grid()
                solid.p2g()
                coupler.add_lbm_reaction_to_mpm_grid(solid, lbm)
                solid.grid_update()
                solid.g2p()

        projector.project(solid, lbm)
        coupler.build_penalty_force(lbm)
        lbm_stats = lbm.get_stats()
        mpm_stats = solid.get_stats()
        force_stats = FSIDiagnostics3D.force_stats(lbm)
        assert_lbm_stats_ok(lbm_stats)
        assert_mpm_stats_ok(mpm_stats)

        row.update(
            {
                "rho_min": lbm_stats["rho_min"],
                "rho_max": lbm_stats["rho_max"],
                "lbm_max_v": lbm_stats["max_v"],
                "mpm_min_J": mpm_stats["min_J"],
                "mpm_max_speed": mpm_stats["max_speed"],
                "final_fluid_mean_ux": float(FSIDiagnostics3D.lbm_fluid_stats(lbm)["fluid_mean_velocity"][0]),
                "final_solid_mean_vx_norm": float(FSIDiagnostics3D.solid_mean_velocity_norm(solid)[0]),
                "max_cell_force_norm": force_stats["max_cell_force_norm"],
                "max_hydro_force_norm": force_stats["max_hydro_force_norm"],
                "active_force_cell_count": force_stats["active_force_cell_count"],
            }
        )
        row["solid_slowdown_norm"] = row["initial_solid_mean_vx_norm"] - row["final_solid_mean_vx_norm"]

        if row["final_fluid_mean_ux"] <= row["initial_fluid_mean_ux"]:
            raise RuntimeError("fluid response did not increase")
        if row["final_solid_mean_vx_norm"] >= row["initial_solid_mean_vx_norm"]:
            raise RuntimeError("solid slowdown did not occur")
        if row["active_force_cell_count"] <= 0:
            raise RuntimeError("no active force cells")

        row["stable"] = True
    except Exception as exc:
        row["failure_reason"] = str(exc)

    return row


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ti.init(arch=ti.gpu, default_fp=ti.f32, kernel_profiler=False, print_ir=False)

    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    beta_values = [3.0e-4, 1.0e-3, 3.0e-3]
    out_dir = os.path.join(ROOT, "outputs", "step7_beta_sweep")
    os.makedirs(out_dir, exist_ok=True)

    t0 = time.time()
    rows = []
    print("Step 7 beta sweep")
    print(f"n_grid={sim.n_grid}")
    print(f"n_lbm_steps=50")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")

    for beta_lbm in beta_values:
        row = run_case(sim, beta_lbm, out_dir)
        rows.append(row)
        print(
            f"beta_lbm={beta_lbm:.9e}, stable={row['stable']}, "
            f"rho_min={row['rho_min']:.9e}, rho_max={row['rho_max']:.9e}, "
            f"lbm_max_v={row['lbm_max_v']:.9e}, mpm_min_J={row['mpm_min_J']:.9e}, "
            f"mpm_max_speed={row['mpm_max_speed']:.9e}, "
            f"final_fluid_mean_ux={row['final_fluid_mean_ux']:.9e}, "
            f"final_solid_mean_vx_norm={row['final_solid_mean_vx_norm']:.9e}, "
            f"solid_slowdown_norm={row['solid_slowdown_norm']:.9e}, "
            f"elapsed={time.time() - t0:.2f}s, failure_reason={row['failure_reason']}"
        )

    stable_rows = [row for row in rows if row["stable"]]
    stable_betas = {row["beta_lbm"] for row in stable_rows}
    if 3.0e-4 not in stable_betas or 1.0e-3 not in stable_betas:
        raise RuntimeError(f"required stable beta rows missing: {stable_betas}")
    if 3.0e-3 not in stable_betas:
        raise RuntimeError("beta 3.0e-3 did not remain stable in this baseline")

    fluid_response = [
        row["final_fluid_mean_ux"] - row["initial_fluid_mean_ux"]
        for row in stable_rows
    ]
    solid_slowdown = [row["solid_slowdown_norm"] for row in stable_rows]
    if np.any(np.diff(fluid_response) < -1.0e-7):
        raise RuntimeError(f"fluid response is not non-decreasing: {fluid_response}")
    if np.any(np.diff(solid_slowdown) < -1.0e-7):
        raise RuntimeError(f"solid slowdown is not non-decreasing: {solid_slowdown}")

    csv_path = os.path.join(out_dir, "beta_sweep_results.csv")
    write_csv(csv_path, rows)
    np.savez(
        os.path.join(out_dir, "beta_sweep_results.npz"),
        beta_lbm=np.asarray([row["beta_lbm"] for row in rows], dtype=np.float64),
        stable=np.asarray([row["stable"] for row in rows], dtype=bool),
        rho_min=np.asarray([row["rho_min"] for row in rows], dtype=np.float64),
        rho_max=np.asarray([row["rho_max"] for row in rows], dtype=np.float64),
        lbm_max_v=np.asarray([row["lbm_max_v"] for row in rows], dtype=np.float64),
        mpm_min_J=np.asarray([row["mpm_min_J"] for row in rows], dtype=np.float64),
        mpm_max_speed=np.asarray([row["mpm_max_speed"] for row in rows], dtype=np.float64),
        final_fluid_mean_ux=np.asarray([row["final_fluid_mean_ux"] for row in rows], dtype=np.float64),
        final_solid_mean_vx_norm=np.asarray(
            [row["final_solid_mean_vx_norm"] for row in rows], dtype=np.float64
        ),
        solid_slowdown_norm=np.asarray([row["solid_slowdown_norm"] for row in rows], dtype=np.float64),
    )

    print(f"stable_beta_count={len(stable_rows)}")
    print(f"fluid_response={fluid_response}")
    print(f"solid_slowdown={solid_slowdown}")
    print(f"csv={csv_path}")
    print("[OK] Step 7 beta sweep finished")


if __name__ == "__main__":
    main()
