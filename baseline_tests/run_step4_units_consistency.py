import os
import sys

import numpy as np


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from src import GridUnitMapper, UnifiedSimConfig


def assert_close(name, actual, expected, tol=1.0e-12):
    err = float(np.max(np.abs(np.asarray(actual, dtype=np.float64) - np.asarray(expected, dtype=np.float64))))
    print(f"{name}: max_abs_error={err:.6e}")
    if err >= tol:
        raise RuntimeError(f"{name} exceeded tolerance {tol}: {err}")


def main():
    sim = UnifiedSimConfig(n_grid=32, mpm_dt=4.0e-4, mpm_substeps_per_lbm_step=10)
    mapper = GridUnitMapper.from_sim_config(sim)

    print("Step 4 units consistency baseline")
    print(f"n_grid={sim.n_grid}")
    print(f"dx_norm={sim.dx_norm:.8f}")
    print(f"mpm_dt={sim.mpm_dt:.8f}")
    print(f"mpm_substeps_per_lbm_step={sim.mpm_substeps_per_lbm_step}")
    print(f"lbm_dt_phys={sim.lbm_dt_phys:.8f}")

    x_norm = np.array(
        [
            [0.0, 0.25, 0.999999],
            [0.03125, 0.5, 0.75],
            [-0.1, 1.1, 0.125],
        ],
        dtype=np.float64,
    )
    x_lbm = mapper.norm_to_lbm_coord(x_norm)
    x_round = mapper.lbm_coord_to_norm(x_lbm)
    assert_close("position_coord_round_trip", x_round, x_norm)

    idx = mapper.norm_to_lbm_index(x_norm)
    centers = mapper.lbm_index_to_norm_center(idx)
    print(f"mapped_indices={idx.tolist()}")
    print(f"cell_centers={centers.tolist()}")
    if np.min(idx) < 0 or np.max(idx) >= sim.n_grid:
        raise RuntimeError(f"mapped index outside [0, {sim.n_grid - 1}]: {idx}")

    v_lbm = np.array([0.03, 0.0, -0.01], dtype=np.float64)
    v_norm = mapper.velocity_lbm_to_norm(v_lbm)
    v_lbm_round = mapper.velocity_norm_to_lbm(v_norm)
    assert_close("velocity_round_trip", v_lbm_round, v_lbm)

    a_norm = np.array([9.8, -1.5, 0.0], dtype=np.float64)
    a_lbm = mapper.acceleration_norm_to_lbm(a_norm)
    a_norm_round = mapper.acceleration_lbm_to_norm(a_lbm)
    assert_close("acceleration_round_trip", a_norm_round, a_norm)

    nu_lbm = 0.1
    nu_norm = mapper.viscosity_lbm_to_norm(nu_lbm)
    nu_lbm_round = mapper.viscosity_norm_to_lbm(nu_norm)
    assert_close("viscosity_round_trip", nu_lbm_round, nu_lbm)

    example_u_norm = float(mapper.velocity_lbm_to_norm(0.03))
    example_a_lbm = float(mapper.acceleration_norm_to_lbm(9.8))
    print(f"u_lbm=0.03 -> u_norm={example_u_norm:.6f}")
    print(f"a_norm=9.8 -> a_lbm={example_a_lbm:.7f}")
    print(f"niu_lbm=0.1 -> nu_norm={nu_norm:.8f}")

    if abs(example_u_norm - 0.234375) >= 1.0e-12:
        raise RuntimeError(f"unexpected velocity example: {example_u_norm}")
    if abs(example_a_lbm - 0.0050176) >= 1.0e-12:
        raise RuntimeError(f"unexpected acceleration example: {example_a_lbm}")

    print("[OK] Step 4 units consistency baseline finished")


if __name__ == "__main__":
    main()
