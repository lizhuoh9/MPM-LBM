import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _completed(name, semantics, nx=96):
    return {
        "name": name,
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": nx,
        "requested_window_completed": True,
        "step120_validation_claimed": True,
        "limiter_activation_gate_pass": True,
        "first_failure_step": None,
    }


def test_step120_gate_stays_closed_when_48_comparison_does_not_improve():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import build_step120_gate_report

    gate = build_step120_gate_report(
        rows=[],
        limiter_summary={"validation_blocked_by_limiter_activation": False},
        best_boundary_selection={"best_boundary_selected": False, "campaign_should_stop_at_48": True},
    )
    assert gate["quasi2d_allowed"] is False
    assert gate["final_classification"] == "boundary_repair_failed_revisit_lbm_solver"


def test_step120_gate_requires_selected_96_and_static_rows():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import build_step120_gate_report

    selection = {
        "best_boundary_selected": True,
        "selected_boundary_semantics": "regularized_velocity_pressure_limited",
        "selected_boundary_slug": "limited",
    }
    gate_missing_static = build_step120_gate_report(
        rows=[_completed("duct_only_96_limited_1000step_real", "regularized_velocity_pressure_limited")],
        limiter_summary={"validation_blocked_by_limiter_activation": False},
        best_boundary_selection=selection,
    )
    assert gate_missing_static["quasi2d_allowed"] is False
    assert "static_two_flap_96_limited_1000step_real" in gate_missing_static["missing_selected_rows"]

    gate_missing_96 = build_step120_gate_report(
        rows=[_completed("static_two_flap_96_limited_1000step_real", "regularized_velocity_pressure_limited")],
        limiter_summary={"validation_blocked_by_limiter_activation": False},
        best_boundary_selection=selection,
    )
    assert gate_missing_96["quasi2d_allowed"] is False
    assert "duct_only_96_limited_1000step_real" in gate_missing_96["missing_selected_rows"]


def test_step120_gate_does_not_require_failed_non_selected_candidate():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import build_step120_gate_report

    rows = [
        _completed("duct_only_96_limited_1000step_real", "regularized_velocity_pressure_limited"),
        _completed("static_two_flap_96_limited_1000step_real", "regularized_velocity_pressure_limited"),
        {
            "name": "duct_only_96_convective_1000step_real",
            "lbm_open_boundary_semantics": "convective_pressure_outlet_experimental",
            "requested_window_completed": False,
            "step120_validation_claimed": False,
        },
    ]
    gate = build_step120_gate_report(
        rows=rows,
        limiter_summary={"validation_blocked_by_limiter_activation": False},
        best_boundary_selection={
            "best_boundary_selected": True,
            "selected_boundary_semantics": "regularized_velocity_pressure_limited",
            "selected_boundary_slug": "limited",
        },
    )
    assert gate["quasi2d_allowed"] is True
    assert gate["final_classification"] == "boundary_repair_success_go_to_quasi2d"
