import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _row(name, semantics, *, flux, mass, complete=True, validation=True, limiter=0.0):
    return {
        "name": name,
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": 48,
        "requested_window_completed": complete,
        "step120_validation_claimed": validation,
        "not_used_for_validation": False,
        "steps_completed": 500 if complete else 10,
        "finite_pass": complete,
        "density_gate_pass": complete,
        "mass_drift_gate_pass": abs(mass) < 0.005,
        "population_gate_pass": complete,
        "mach_gate_pass": complete,
        "first_failure_step": None if complete else 10,
        "flux_imbalance_rel_tail_mean": flux,
        "mass_total_delta_rel_final": mass,
        "limiter_activation_fraction": limiter,
        "runtime_s": 1.0,
    }


def _references():
    return [
        _row("legacy", "equilibrium_all_population_reset", flux=0.08, mass=0.001),
        _row("regularized", "regularized_velocity_pressure", flux=0.4, mass=0.002),
    ]


def test_step120_selects_limited_when_limited_passes_and_convective_fails():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import select_step120_best_boundary

    selection = select_step120_best_boundary(
        _references()
        + [
            _row("limited", "regularized_velocity_pressure_limited", flux=0.04, mass=0.001),
            _row("convective", "convective_pressure_outlet_experimental", flux=0.3, mass=0.02, complete=False, validation=False),
        ]
    )

    assert selection["best_boundary_selected"] is True
    assert selection["selected_row_name"] == "limited"
    assert selection["selected_boundary_semantics"] == "regularized_velocity_pressure_limited"


def test_step120_selects_convective_when_convective_passes_and_limited_fails():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import select_step120_best_boundary

    selection = select_step120_best_boundary(
        _references()
        + [
            _row("limited", "regularized_velocity_pressure_limited", flux=0.5, mass=0.02, complete=False, validation=False),
            _row("convective", "convective_pressure_outlet_experimental", flux=0.03, mass=0.001),
        ]
    )

    assert selection["best_boundary_selected"] is True
    assert selection["selected_row_name"] == "convective"
    assert selection["selected_boundary_semantics"] == "convective_pressure_outlet_experimental"


def test_step120_stops_at_48_when_both_candidates_fail():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import select_step120_best_boundary

    selection = select_step120_best_boundary(
        _references()
        + [
            _row("limited", "regularized_velocity_pressure_limited", flux=0.5, mass=0.02, complete=False, validation=False),
            _row("convective", "convective_pressure_outlet_experimental", flux=0.3, mass=0.02, complete=False, validation=False),
        ]
    )

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_should_stop_at_48"] is True
    assert selection["failure_classification"] == "boundary_repair_failed_revisit_lbm_solver"
