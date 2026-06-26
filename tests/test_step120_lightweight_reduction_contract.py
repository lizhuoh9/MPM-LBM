import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step120_lightweight_reduction_matches_full_numpy_stability_diagnostics():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        create_step120_lbm,
        summarize_step120_lightweight_stability,
    )
    from src.mpm_lbm.sim.diagnostics.lbm_stability_diagnostics import summarize_lbm_stability_diagnostics

    spec = Step120RunSpec(
        name="reduction_match",
        nx=5,
        ny=4,
        nz=4,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=1,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    lbm, _tau_report = create_step120_lbm(spec)
    full = summarize_lbm_stability_diagnostics(lbm, step=0)
    reduced = summarize_step120_lightweight_stability(lbm, step=0)

    assert reduced["diagnostic_mode"] == "lightweight_reduction"
    assert abs(reduced["rho_min"] - full["rho_min"]) < 1.0e-7
    assert abs(reduced["rho_max"] - full["rho_max"]) < 1.0e-7
    assert abs(reduced["max_v"] - full["max_v"]) < 1.0e-7
    assert abs(reduced["f_min"] - full["f_min"]) < 1.0e-7
    assert abs(reduced["F_max"] - full["F_max"]) < 1.0e-7
    assert reduced["negative_population_count"] == full["negative_population_count"]
    assert reduced["boundary_x_min_negative_population_count"] == full["boundary_x_min_negative_population_count"]
    assert reduced["boundary_x_max_negative_population_count"] == full["boundary_x_max_negative_population_count"]
