import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step120_open_boundary_limiter_counters_are_direct_kernel_counters():
    from src.mpm_lbm.sim.lbm.config import LBMConfig
    from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _ensure_taichi

    _ensure_taichi()
    lbm = LBMFluid3D(
        LBMConfig(
            nx=5,
            ny=4,
            nz=4,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            open_boundary_limiter_enabled=True,
            open_boundary_rho_min=0.9,
            open_boundary_rho_max=1.1,
            open_boundary_u_max=0.01,
            open_boundary_noneq_cap=0.001,
            open_boundary_population_floor=0.09,
            bc_x_left=1,
            rho_bc_x_left=2.0,
        )
    )
    lbm.init_simulation()

    v = lbm.v.to_numpy()
    v[1, :, :, 0] = 1.0
    lbm.v.from_numpy(v.astype(np.float32))

    F = lbm.F.to_numpy()
    F[1, :, :, :] = 2.0
    lbm.F.from_numpy(F.astype(np.float32))

    lbm.clear_open_boundary_limiter_run_counters()
    lbm.Boundary_condition()
    stats = lbm.get_open_boundary_limiter_stats()

    expected_reconstructed = 5 * 4 * 4
    assert stats["reconstructed_population_count_step"] == expected_reconstructed
    assert stats["reconstructed_population_count_run"] == expected_reconstructed
    assert stats["rho_clip_count_step"] == expected_reconstructed
    assert stats["velocity_clip_count_step"] == expected_reconstructed
    assert stats["noneq_clip_count_step"] == expected_reconstructed
    assert stats["population_floor_count_step"] > 0
    assert stats["limiter_activation_denominator"] == expected_reconstructed
    assert stats["limiter_activation_count"] >= (
        stats["rho_clip_count_step"]
        + stats["velocity_clip_count_step"]
        + stats["noneq_clip_count_step"]
        + stats["population_floor_count_step"]
    )
