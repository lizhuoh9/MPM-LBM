import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step119_gate_report_blocks_quasi2d_when_required_real_rows_are_incomplete():
    from experiments.steps.step119_lbm_boundary_repair_real_run_validation import build_step119_gate_report

    rows = [
        {
            "name": "duct_only_48_regularized_limited_boundary_500step_real",
            "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
            "requested_window_completed": False,
            "step119_validation_claimed": False,
            "limiter_activation_fraction": 0.0,
            "first_failure_reason": "large_real_row_requires_explicit_allowance",
        }
    ]
    limiter_summary = {
        "max_limiter_activation_fraction": 0.0,
        "validation_blocked_by_limiter_activation": False,
    }

    gate = build_step119_gate_report(rows, limiter_summary)

    assert gate["step"] == 119
    assert gate["quasi2d_allowed"] is False
    assert gate["step120_quasi2d_allowed"] is False
    assert gate["validation_claim_allowed"] is False
    assert gate["fluent_validation_claim_allowed"] is False
    assert gate["full_fsi_validation_claim_allowed"] is False
    assert gate["final_classification"] == "boundary_repair_partial_continue_lbm"
    assert "duct_only_48_legacy_boundary_500step_reference_real" in gate["incomplete_required_rows"]


def test_step119_gate_report_marks_limiter_overuse_as_partial_not_success():
    from experiments.steps.step119_lbm_boundary_repair_real_run_validation import build_step119_gate_report

    rows = [
        {
            "name": "duct_only_48_legacy_boundary_500step_reference_real",
            "lbm_open_boundary_semantics": "equilibrium_all_population_reset",
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.0,
        },
        {
            "name": "duct_only_48_regularized_boundary_500step_reference_real",
            "lbm_open_boundary_semantics": "regularized_velocity_pressure",
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.0,
        },
        {
            "name": "duct_only_48_regularized_limited_boundary_500step_real",
            "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.4,
        },
        {
            "name": "duct_only_48_convective_outlet_boundary_500step_real",
            "lbm_open_boundary_semantics": "convective_pressure_outlet_experimental",
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.0,
        },
        {
            "name": "duct_only_96_regularized_limited_boundary_1000step_real",
            "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.4,
        },
        {
            "name": "duct_only_96_convective_outlet_boundary_1000step_real",
            "lbm_open_boundary_semantics": "convective_pressure_outlet_experimental",
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.0,
        },
        {
            "name": "static_two_flap_96_best_boundary_1000step_real",
            "lbm_open_boundary_semantics": "regularized_velocity_pressure_limited",
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.4,
        },
    ]
    limiter_summary = {
        "max_limiter_activation_fraction": 0.4,
        "validation_blocked_by_limiter_activation": True,
    }

    gate = build_step119_gate_report(rows, limiter_summary)

    assert gate["quasi2d_allowed"] is False
    assert gate["step120_quasi2d_allowed"] is False
    assert gate["limiter_activation_gate_pass"] is False
    assert gate["final_classification"] == "boundary_repair_partial_continue_lbm"


def test_step119_gate_report_only_allows_success_for_complete_real_rows_without_limiter_overuse():
    from experiments.steps.step119_lbm_boundary_repair_real_run_validation import (
        REQUIRED_VALIDATION_ROW_NAMES,
        build_step119_gate_report,
    )

    rows = [
        {
            "name": name,
            "requested_window_completed": True,
            "step119_validation_claimed": True,
            "limiter_activation_fraction": 0.0,
            "first_failure_reason": None,
        }
        for name in REQUIRED_VALIDATION_ROW_NAMES
    ]
    limiter_summary = {
        "max_limiter_activation_fraction": 0.0,
        "validation_blocked_by_limiter_activation": False,
    }

    gate = build_step119_gate_report(rows, limiter_summary)

    assert gate["quasi2d_allowed"] is True
    assert gate["step120_quasi2d_allowed"] is True
    assert gate["final_classification"] == "boundary_repair_success_go_to_quasi2d"
