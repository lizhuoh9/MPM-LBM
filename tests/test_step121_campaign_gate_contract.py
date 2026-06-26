import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _row(
    name,
    semantics,
    *,
    role,
    complete=True,
    validation=True,
    simulation=True,
    flux=0.04,
    mass=0.001,
    limiter=0.0,
    not_used=False,
):
    return {
        "name": name,
        "row_role": role,
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": 48,
        "requested_n_steps": 500,
        "steps_completed": 500 if complete else 0,
        "requested_window_completed": bool(complete),
        "step120_validation_claimed": bool(validation and complete),
        "simulation_backed_artifact": bool(simulation),
        "not_used_for_validation": bool(not_used),
        "finite_pass": bool(complete),
        "density_gate_pass": bool(complete),
        "mass_drift_gate_pass": abs(mass) < 0.005,
        "population_gate_pass": bool(complete),
        "mach_gate_pass": bool(complete),
        "first_failure_step": None if complete else 10,
        "first_failure_reason": None if complete else "rho_range",
        "flux_imbalance_rel_tail_mean": flux,
        "flux_imbalance_rel_tail_max": min(float(flux) * 1.5, 0.19),
        "flux_balance_reported": True,
        "inlet_flux_tail_mean": 0.031,
        "outlet_flux_tail_mean": 0.030,
        "outlet_flux_tail_cv": 0.02,
        "outlet_to_inlet_flux_ratio_tail_mean": 0.030 / 0.031,
        "midplane_to_inlet_flux_ratio_tail_mean": 1.0,
        "flow_development_gate_pass": flux < 0.1,
        "mass_total_delta_rel_final": mass,
        "limiter_activation_fraction": limiter,
        "limiter_activation_gate_pass": limiter <= 0.05,
        "runtime_s": 1.0,
        "open_boundary_limiter_enabled": semantics == "regularized_velocity_pressure_limited",
        "open_boundary_rho_min": 0.91,
        "open_boundary_rho_max": 1.09,
        "open_boundary_u_max": 0.08,
        "open_boundary_noneq_cap": 0.17,
        "open_boundary_population_floor": -2.0e-8,
        "inlet_u_lbm": 0.031,
        "outlet_rho": 0.997,
        "lbm_niu": 0.023,
        "lbm_viscosity_semantics": "legacy_external",
        "lbm_relaxation_semantics": "legacy_external_solver_parameter",
        "tau": 0.572,
        "config_hash": "candidate-config-hash",
        "solver_state_hash": "candidate-config-hash",
        "selected_source_row_name": "duct_only_48_regularized_limited_boundary_500step_real" if role in {"selected_96_duct", "selected_96_static"} else None,
        "selected_source_config_hash": "candidate-config-hash" if role in {"selected_96_duct", "selected_96_static"} else None,
        "selected_source_tau": 0.572 if role in {"selected_96_duct", "selected_96_static"} else None,
        "selected_source_lbm_relaxation_semantics": "legacy_external_solver_parameter" if role in {"selected_96_duct", "selected_96_static"} else None,
    }


def _references():
    return [
        _row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            role="reference_48",
            flux=0.08,
        ),
        _row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            role="reference_48",
            flux=0.20,
        ),
    ]


def test_step121_pending_candidates_are_partial_not_failed():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    selection = select_step121_best_boundary(_references())

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "awaiting_48_candidates"
    assert selection["final_classification"] == "boundary_repair_partial_continue_lbm"


def test_step121_failure_requires_both_real_candidates_to_have_run():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    one_failed_one_missing = select_step121_best_boundary(
        _references()
        + [
            _row(
                "duct_only_48_regularized_limited_boundary_500step_real",
                "regularized_velocity_pressure_limited",
                role="candidate_48",
                complete=True,
                validation=False,
                flux=0.50,
                mass=0.02,
            )
        ]
    )
    assert one_failed_one_missing["campaign_state"] == "awaiting_48_candidates"
    assert one_failed_one_missing["final_classification"] == "boundary_repair_partial_continue_lbm"

    both_failed = select_step121_best_boundary(
        _references()
        + [
            _row(
                "duct_only_48_regularized_limited_boundary_500step_real",
                "regularized_velocity_pressure_limited",
                role="candidate_48",
                complete=True,
                validation=False,
                flux=0.50,
                mass=0.02,
            ),
            _row(
                "duct_only_48_convective_outlet_boundary_500step_real",
                "convective_pressure_outlet_experimental",
                role="candidate_48",
                complete=True,
                validation=False,
                flux=0.45,
                mass=0.02,
            ),
        ]
    )
    assert both_failed["campaign_state"] == "48_candidates_failed"
    assert both_failed["final_classification"] == "boundary_repair_failed_revisit_lbm_solver"


def test_step121_selection_requires_simulation_backed_references():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    rows = [
        _row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            role="reference_48",
            simulation=False,
        ),
        _row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            role="candidate_48",
        ),
        _row(
            "duct_only_48_convective_outlet_boundary_500step_real",
            "convective_pressure_outlet_experimental",
            role="candidate_48",
        ),
    ]

    selection = select_step121_best_boundary(rows)

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "awaiting_48_references"
    assert selection["reference_comparison_ready"] is False


def test_step121_failed_candidates_remain_visible_even_when_not_used_for_validation():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    selection = select_step121_best_boundary(
        _references()
        + [
            _row(
                "duct_only_48_regularized_limited_boundary_500step_real",
                "regularized_velocity_pressure_limited",
                role="candidate_48",
                complete=True,
                validation=False,
                flux=0.50,
                mass=0.02,
                not_used=True,
            ),
            _row(
                "duct_only_48_convective_outlet_boundary_500step_real",
                "convective_pressure_outlet_experimental",
                role="candidate_48",
                complete=True,
                validation=False,
                flux=0.45,
                mass=0.02,
                not_used=True,
            ),
        ]
    )

    names = {row["name"] for row in selection["candidate_summaries"]}
    assert "duct_only_48_regularized_limited_boundary_500step_real" in names
    assert "duct_only_48_convective_outlet_boundary_500step_real" in names
    assert all(row["rejection_reasons"] for row in selection["candidate_summaries"])


def test_step121_selected_only_limiter_gate_ignores_unrelated_rows():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        build_step121_gate_report,
        select_step121_best_boundary,
    )

    selected_candidate = _row(
        "duct_only_48_regularized_limited_boundary_500step_real",
        "regularized_velocity_pressure_limited",
        role="candidate_48",
        limiter=0.0,
    )
    selection = select_step121_best_boundary(
        _references()
        + [
            selected_candidate,
            _row(
                "duct_only_48_convective_outlet_boundary_500step_real",
                "convective_pressure_outlet_experimental",
                role="candidate_48",
                complete=True,
                validation=False,
                flux=0.50,
                mass=0.02,
                limiter=0.99,
                not_used=True,
            ),
        ]
    )
    rows = _references() + [
        selected_candidate,
        {
            **_row(
                "duct_only_96_limited_1000step_real",
                "regularized_velocity_pressure_limited",
                role="selected_96_duct",
                limiter=0.0,
            ),
            "requested_nx": 96,
            "requested_n_steps": 1000,
            "steps_completed": 1000,
        },
        {
            **_row(
                "static_two_flap_96_limited_1000step_real",
                "regularized_velocity_pressure_limited",
                role="selected_96_static",
                limiter=0.0,
            ),
            "requested_nx": 96,
            "requested_n_steps": 1000,
            "steps_completed": 1000,
        },
        {
            **_row(
                "unrelated_tiny_with_high_limiter",
                "regularized_velocity_pressure_limited",
                role="tiny_smoke",
                limiter=0.99,
            ),
            "requested_nx": 5,
        },
    ]

    gate = build_step121_gate_report(rows, selection)

    assert gate["final_classification"] == "boundary_repair_success_go_to_quasi2d"
    assert gate["selected_chain_limiter_gate_pass"] is True
    assert gate["global_limiter_gate_not_used_for_final_classification"] is True


def test_step121_selected_96_phase_rejects_missing_selection_path(tmp_path):
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import resolve_step121_phase_specs

    try:
        resolve_step121_phase_specs("selected96", best_selection_path=None)
    except ValueError as exc:
        assert "best-selection" in str(exc)
    else:
        raise AssertionError("selected96 phase should require a best-selection artifact")

    selection_path = tmp_path / "best_boundary_selection.json"
    selection_path.write_text(
        json.dumps(
            {
                "best_boundary_selected": True,
                "selected_boundary_semantics": "convective_pressure_outlet_experimental",
                "selected_boundary_slug": "convective",
                "allow_legacy_provenance_defaults": True,
            }
        ),
        encoding="utf-8",
    )
    specs = resolve_step121_phase_specs("selected96", best_selection_path=selection_path)
    assert [spec.name for spec in specs] == ["duct_only_96_convective_1000step_real"]
