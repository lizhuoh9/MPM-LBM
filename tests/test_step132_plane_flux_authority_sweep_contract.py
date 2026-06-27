import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
CONVECTIVE_PLANE = "convective_plane_flux_controlled_damped_outlet"
STEP131_PLANE_FLUX_CONTROL = {REGULARIZED_PLANE, CONVECTIVE_PLANE}


def _row(name, semantics, *, role="candidate_48", requested_n_steps=500, solver_state_hash="hash"):
    return {
        "name": name,
        "row_role": role,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": 48,
        "executed_nx": 48,
        "requested_n_steps": requested_n_steps,
        "steps_completed": requested_n_steps,
        "requested_window_completed": True,
        "step120_validation_claimed": True,
        "simulation_backed_artifact": True,
        "not_used_for_validation": False,
        "finite_pass": True,
        "density_gate_pass": True,
        "mass_drift_gate_pass": True,
        "population_gate_pass": True,
        "mach_gate_pass": True,
        "first_failure_step": None,
        "first_failure_reason": None,
        "stop_reason": None,
        "flux_balance_reported": True,
        "flux_imbalance_rel_tail_mean": 0.04,
        "flux_imbalance_rel_tail_max": 0.08,
        "inlet_flux_tail_mean": 42.0,
        "outlet_flux_tail_mean": 41.5,
        "outlet_to_inlet_flux_ratio_tail_mean": 0.988,
        "midplane_to_inlet_flux_ratio_tail_mean": 0.99,
        "outlet_flux_tail_cv": 0.02,
        "flow_development_gate_pass": True,
        "flow_development_rejection_reasons": [],
        "mass_total_delta_rel_final": 0.001,
        "candidate_mass_acceptance_observed_abs": 0.001,
        "candidate_mass_acceptance_gate_pass": True,
        "mach_proxy_observed_max": 0.08,
        "limiter_activation_fraction": 0.0,
        "limiter_activation_gate_pass": True,
        "runtime_s": 1.0,
        "open_boundary_limiter_enabled": False,
        "open_boundary_rho_min": 0.91,
        "open_boundary_rho_max": 1.09,
        "open_boundary_u_max": 0.08,
        "open_boundary_noneq_cap": 0.17,
        "open_boundary_population_floor": None,
        "open_boundary_flux_feedback_gain_u": 0.25,
        "open_boundary_flux_feedback_gain_rho": 0.0,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.002,
        "open_boundary_convective_blend_weight": 0.02,
        "controller_u_feedback_tail_mean": 0.001,
        "controller_saturation_fraction_tail": 0.0,
        "inlet_u_lbm": 0.031,
        "outlet_rho": 0.997,
        "lbm_niu": 0.023,
        "lbm_viscosity_semantics": "legacy_external",
        "lbm_relaxation_semantics": "legacy_external_solver_parameter",
        "tau": 0.572,
        "config_hash": solver_state_hash,
        "solver_state_hash": solver_state_hash,
    }


def _references():
    return [
        _row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            role="reference_48",
            solver_state_hash="legacy-reference-hash",
        ),
        _row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            role="reference_48",
            solver_state_hash="regularized-reference-hash",
        ),
    ]


def _failed_step127_candidates():
    failed_regularized = _row(
        "duct_only_48_regularized_limited_boundary_500step_real",
        "regularized_velocity_pressure_limited",
        solver_state_hash="limited-step127-hash",
    )
    failed_regularized.update(
        {
            "flux_imbalance_rel_tail_mean": 0.51165,
            "flux_imbalance_rel_tail_max": 0.866,
            "outlet_to_inlet_flux_ratio_tail_mean": 1.4127,
            "midplane_to_inlet_flux_ratio_tail_mean": 1.306,
            "outlet_flux_tail_cv": 0.452,
            "flow_development_gate_pass": False,
        }
    )
    failed_convective = _row(
        "duct_only_48_convective_outlet_boundary_500step_real",
        "convective_pressure_outlet_experimental",
        requested_n_steps=500,
        solver_state_hash="convective-step127-hash",
    )
    failed_convective.update(
        {
            "steps_completed": 200,
            "requested_window_completed": False,
            "step120_validation_claimed": False,
            "first_failure_step": 200,
            "first_failure_reason": "mass_drift",
            "stop_reason": "lightweight_failure:mass_drift",
            "mass_total_delta_rel_final": 0.046,
            "flow_development_gate_pass": False,
        }
    )
    return [failed_regularized, failed_convective]


def _step132_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p002_250step_triage",
        "nx": 48,
        "ny": 48,
        "nz": 48,
        "n_steps": 250,
        "output_interval": 25,
        "failure_check_interval": 5,
        "checkpoint_every": 50,
        "open_boundary_semantics": REGULARIZED_PLANE,
        "geometry_mode": "duct_only",
        "requested_nx": 48,
        "requested_n_steps": 250,
        "allow_large_real_run_without_flag": True,
        "row_role": "plane_flux_control_candidate_48",
        "open_boundary_flux_feedback_gain_u": 0.25,
        "open_boundary_flux_feedback_gain_rho": 0.0,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.002,
        "open_boundary_convective_blend_weight": 0.02,
        "artifact_scope_note": (
            "Step132 bounded 48^3 plane-flux controller authority sweep; not a selected96 enabling row"
        ),
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def test_step132_planeflux_sweep_phase_reuses_step131_semantics_with_bounded_authority_specs():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        PLANE_FLUX_CONTROL_CANDIDATE_SEMANTICS,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_plane_flux_sweep_48_specs,
    )
    from src.mpm_lbm.sim.lbm.config import VALID_LBM_OPEN_BOUNDARY_SEMANTICS

    specs = step121_plane_flux_sweep_48_specs(output_interval=25)

    assert set(PLANE_FLUX_CONTROL_CANDIDATE_SEMANTICS) == STEP131_PLANE_FLUX_CONTROL
    assert STEP131_PLANE_FLUX_CONTROL.issubset(set(VALID_LBM_OPEN_BOUNDARY_SEMANTICS))
    assert {spec.open_boundary_semantics for spec in specs} == STEP131_PLANE_FLUX_CONTROL
    assert [spec.open_boundary_flux_feedback_gain_rho for spec in specs] == [0.0] * len(specs)
    assert {spec.open_boundary_flux_filter_alpha for spec in specs} == {0.02}
    assert {spec.open_boundary_convective_blend_weight for spec in specs} == {0.02}
    assert all(spec.row_role == "plane_flux_control_candidate_48" for spec in specs)
    assert all(spec.requested_n_steps == 250 for spec in specs)
    assert all("Step132" in spec.artifact_scope_note for spec in specs)
    assert all("gain" in spec.name and "cap" in spec.name for spec in specs)
    observed_authority_specs = {
        (
            spec.open_boundary_semantics,
            spec.open_boundary_flux_feedback_gain_u,
            spec.open_boundary_flux_correction_cap_u,
        )
        for spec in specs
    }
    assert observed_authority_specs == {
        (REGULARIZED_PLANE, 0.05, 0.002),
        (REGULARIZED_PLANE, 0.10, 0.002),
        (REGULARIZED_PLANE, 0.25, 0.002),
        (REGULARIZED_PLANE, 0.25, 0.005),
        (CONVECTIVE_PLANE, 0.05, 0.002),
        (CONVECTIVE_PLANE, 0.10, 0.002),
    }
    assert resolve_step121_phase_specs("planeflux_sweep48", output_interval=25) == specs


def test_step132_sweep_specs_have_distinct_solver_hashes_from_step131_baseline():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_plane_flux_48_specs,
        step121_plane_flux_sweep_48_specs,
    )

    baseline_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_48_specs(output_interval=25)}
    sweep_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_sweep_48_specs(output_interval=25)}

    assert len(sweep_hashes) == 6
    assert sweep_hashes.isdisjoint(baseline_hashes)


def test_step132_sweep_rows_do_not_enable_selected96_even_if_flow_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    authority_triage = _row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p002_250step_triage",
        REGULARIZED_PLANE,
        role="plane_flux_control_candidate_48",
        requested_n_steps=250,
        solver_state_hash="step132-authority-sweep-hash",
    )
    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [authority_triage])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False
    assert all(item["semantics"] not in STEP131_PLANE_FLUX_CONTROL for item in selection["candidate_summaries"])


def test_step132_manifest_rejects_stale_step131_rows_for_planeflux_sweep_phase(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_plane_flux_48_specs,
        step121_plane_flux_sweep_48_specs,
        write_step121_campaign_manifest,
    )

    out = tmp_path / "campaign"
    specs = step121_plane_flux_sweep_48_specs(output_interval=25)
    write_step121_campaign_manifest(out, specs, phase="planeflux_sweep48")
    spec = specs[0]
    stale_source = next(
        item
        for item in step121_plane_flux_48_specs(output_interval=25)
        if item.open_boundary_semantics == spec.open_boundary_semantics
    )
    stale = _row(
        spec.name,
        spec.open_boundary_semantics,
        role="plane_flux_control_candidate_48",
        requested_n_steps=250,
        solver_state_hash=solver_state_hash_for_spec(stale_source),
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "solver_state_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]
    assert solver_state_hash_for_spec(spec) != stale["solver_state_hash"]


def test_step132_flow_development_diagnostics_include_authority_ratio_and_tail_summary(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = _step132_spec()
    diagnostics = [
        _flow_development_diagnostic_record(
            {
                "step": 25,
                "inlet_flux": 42.0,
                "outlet_flux": 44.0,
                "midplane_flux": 43.0,
                "mass_total_delta_rel": 0.001,
            },
            spec,
            {
                "flow_correction_cap_u": 0.002,
                "controller_target_outlet_flux": 42.0,
                "controller_measured_outlet_flux": 44.0,
                "controller_raw_flux_error": -2.0,
                "controller_filtered_flux_error": -0.04,
                "controller_u_feedback": -0.0005,
                "controller_u_feedback_abs": 0.0005,
                "controller_saturation_count_step": 0,
                "controller_saturation_count_run": 0,
                "controller_saturation_fraction_run": 0.0,
            },
        ),
        _flow_development_diagnostic_record(
            {
                "step": 50,
                "inlet_flux": 42.0,
                "outlet_flux": 45.0,
                "midplane_flux": 43.0,
                "mass_total_delta_rel": 0.002,
            },
            spec,
            {
                "flow_correction_cap_u": 0.002,
                "controller_target_outlet_flux": 42.0,
                "controller_measured_outlet_flux": 45.0,
                "controller_raw_flux_error": -3.0,
                "controller_filtered_flux_error": -0.06,
                "controller_u_feedback": -0.0015,
                "controller_u_feedback_abs": 0.0015,
                "controller_saturation_count_step": 0,
                "controller_saturation_count_run": 0,
                "controller_saturation_fraction_run": 0.0,
            },
        ),
    ]
    _write_flow_development_diagnostics(tmp_path, diagnostics)

    assert "controller_authority_ratio" in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
    assert "step132_authority_sweep_candidate" in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
    assert diagnostics[-1]["controller_authority_ratio"] == pytest.approx(0.75)
    assert diagnostics[-1]["step132_authority_sweep_candidate"] is True

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 132
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_claim_allowed"] is False
    assert summary["final"]["controller_authority_ratio"] == pytest.approx(0.75)
    assert summary["controller_u_feedback_tail_abs_max"] == pytest.approx(0.0015)
    assert summary["controller_authority_ratio_tail_max"] == pytest.approx(0.75)
    assert 0.25 <= summary["controller_authority_ratio_tail_mean"] <= 0.75
