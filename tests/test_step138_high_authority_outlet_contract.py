import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
STEP138_ROLE = "interior_reflection_diagnostic_48"


def _step138_row(name, semantics, *, solver_state_hash="step138-hash", **overrides):
    row = {
        "name": name,
        "row_role": STEP138_ROLE,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": semantics,
        "requested_nx": 48,
        "executed_nx": 48,
        "requested_n_steps": 250,
        "steps_completed": 250,
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
        "flux_imbalance_rel_tail_mean": 0.06,
        "flux_imbalance_rel_tail_max": 0.12,
        "inlet_flux_tail_mean": 42.0,
        "outlet_flux_tail_mean": 40.0,
        "outlet_to_inlet_flux_ratio_tail_mean": 0.952,
        "midplane_to_inlet_flux_ratio_tail_mean": 0.98,
        "outlet_flux_tail_cv": 0.08,
        "outlet_flux_tail_slope": -0.05,
        "outlet_flux_tail_drop_ratio": 0.90,
        "outlet_flux_tail_last_to_mean_ratio": 0.95,
        "near_outlet_to_outlet_flux_ratio_tail_mean": 1.03,
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
        "open_boundary_rho_min": 0.25,
        "open_boundary_rho_max": 1.80,
        "open_boundary_u_max": 0.18,
        "open_boundary_noneq_cap": 0.08,
        "open_boundary_population_floor": 1.0e-9,
        "open_boundary_mass_correction_enabled": True,
        "mass_balance_correction_count": 0,
        "mass_balance_correction_abs_sum": 0.0,
        "unknown_population_delta_abs_sum": 0.0,
        "open_boundary_flux_feedback_gain_u": 0.75,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.0075,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.50,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_flux_control_target_scale": 0.85,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 85,
        "open_boundary_inlet_ramp_profile": "linear",
        "step135_interior_reflection_candidate": False,
        "step136_ramped_throughput_calibration_candidate": False,
        "step137_ramp_target_refinement_candidate": False,
        "step138_high_authority_outlet_candidate": True,
        "selected96_claim_allowed": False,
        "validation_claim_allowed": False,
        "inlet_u_lbm": 0.031,
        "outlet_rho": 0.997,
        "lbm_niu": 0.10,
        "lbm_viscosity_semantics": "legacy_external",
        "lbm_relaxation_semantics": "legacy_external_solver_parameter",
        "tau": 0.8,
        "config_hash": solver_state_hash,
        "solver_state_hash": solver_state_hash,
    }
    row.update(overrides)
    return row


def _references():
    return [
        _step138_row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            solver_state_hash="legacy-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
            step138_high_authority_outlet_candidate=False,
        ),
        _step138_row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            solver_state_hash="regularized-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
            step138_high_authority_outlet_candidate=False,
        ),
    ]


def _failed_step127_candidates():
    return [
        _step138_row(
            "duct_only_48_regularized_limited_boundary_500step_real",
            "regularized_velocity_pressure_limited",
            solver_state_hash="limited-step127-hash",
            row_role="candidate_48",
            requested_n_steps=500,
            steps_completed=500,
            flow_development_gate_pass=False,
            flux_imbalance_rel_tail_mean=0.51165,
            flux_imbalance_rel_tail_max=0.866,
            outlet_to_inlet_flux_ratio_tail_mean=1.4127,
            midplane_to_inlet_flux_ratio_tail_mean=1.306,
            outlet_flux_tail_cv=0.452,
            step138_high_authority_outlet_candidate=False,
        ),
        _step138_row(
            "duct_only_48_convective_outlet_boundary_500step_real",
            "convective_pressure_outlet_experimental",
            solver_state_hash="convective-step127-hash",
            row_role="candidate_48",
            requested_n_steps=500,
            steps_completed=200,
            requested_window_completed=False,
            step120_validation_claimed=False,
            first_failure_step=200,
            first_failure_reason="mass_drift",
            stop_reason="lightweight_failure:mass_drift",
            flow_development_gate_pass=False,
            step138_high_authority_outlet_candidate=False,
        ),
    ]


def _step138_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": (
            "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075"
            "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
            "_ramp85_target0p85_out5_250step_high_authority"
        ),
        "nx": 48,
        "ny": 48,
        "nz": 48,
        "n_steps": 250,
        "output_interval": 5,
        "failure_check_interval": 5,
        "checkpoint_every": 50,
        "open_boundary_semantics": REGULARIZED_PLANE,
        "geometry_mode": "duct_only",
        "requested_nx": 48,
        "requested_n_steps": 250,
        "allow_large_real_run_without_flag": True,
        "row_role": STEP138_ROLE,
        "open_boundary_flux_feedback_gain_u": 0.75,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.0075,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_flux_control_target_scale": 0.85,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 85,
        "open_boundary_inlet_ramp_profile": "linear",
        "niu": 0.10,
        "artifact_scope_note": (
            "Step138 bounded 48^3 high-authority outlet diagnostic; "
            "diagnostic only and not selected96 or 500-step evidence"
        ),
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def test_step138_high_authority_phase_is_distinct_bounded_diagnostic_surface():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_plane_flux_high_authority_48_specs,
        step121_plane_flux_high_authority_tiny_smoke_specs,
        step121_plane_flux_ramp_refined_48_specs,
    )

    specs = step121_plane_flux_high_authority_48_specs(output_interval=5)
    step137_names = {spec.name for spec in step121_plane_flux_ramp_refined_48_specs(output_interval=5)}

    assert resolve_step121_phase_specs("planeflux_high_authority48", output_interval=5) == specs
    assert len(specs) == 6
    assert all(spec.row_role == STEP138_ROLE for spec in specs)
    assert all(spec.open_boundary_semantics == REGULARIZED_PLANE for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all(spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.output_interval == 5 for spec in specs)
    assert all("Step138" in spec.artifact_scope_note for spec in specs)
    assert all("selected96" in spec.artifact_scope_note and "500-step" in spec.artifact_scope_note for spec in specs)
    assert all(spec.name not in step137_names for spec in specs)
    assert all("target" in spec.name and "250step_high_authority" in spec.name for spec in specs)
    assert {
        (
            int(spec.open_boundary_inlet_ramp_steps),
            round(float(spec.open_boundary_flux_control_target_scale), 2),
            round(float(spec.open_boundary_flux_feedback_gain_u), 2),
            round(float(spec.open_boundary_flux_correction_cap_u), 4),
        )
        for spec in specs
    } == {
        (85, 0.85, 0.75, 0.0050),
        (85, 0.85, 0.75, 0.0075),
        (85, 0.85, 1.00, 0.0075),
        (85, 0.85, 1.00, 0.0100),
        (85, 0.80, 0.75, 0.0075),
        (90, 0.80, 0.75, 0.0075),
    }
    assert {round(float(spec.niu), 2) for spec in specs} == {0.10}

    tiny = step121_plane_flux_high_authority_tiny_smoke_specs()
    assert len(tiny) == 1
    assert tiny[0].name == "tiny_step138_high_authority_outlet_smoke"
    assert (tiny[0].nx, tiny[0].ny, tiny[0].nz, tiny[0].n_steps) == (8, 6, 6, 20)
    assert int(tiny[0].open_boundary_inlet_ramp_steps) == 10
    assert tiny[0].open_boundary_flux_control_target_scale == pytest.approx(0.85)
    assert tiny[0].open_boundary_flux_feedback_gain_u == pytest.approx(0.75)
    assert tiny[0].open_boundary_flux_correction_cap_u == pytest.approx(0.0075)
    assert tiny[0].row_role == "tiny_smoke"
    assert tiny[0].not_used_for_validation is True


def test_step138_manifest_identity_and_stale_step137_rows_are_rejected(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
        collect_step121_rows,
        step121_plane_flux_high_authority_48_specs,
        step121_plane_flux_ramp_refined_48_specs,
        write_step121_campaign_manifest,
    )

    base = _step138_spec(open_boundary_flux_feedback_gain_u=0.75, open_boundary_flux_correction_cap_u=0.0050)
    higher_gain = _step138_spec(open_boundary_flux_feedback_gain_u=1.00, open_boundary_flux_correction_cap_u=0.0050)
    higher_cap = _step138_spec(open_boundary_flux_feedback_gain_u=0.75, open_boundary_flux_correction_cap_u=0.0075)
    assert solver_state_hash_for_spec(base) != solver_state_hash_for_spec(higher_gain)
    assert solver_state_hash_for_spec(base) != solver_state_hash_for_spec(higher_cap)
    assert run_manifest_hash_for_spec(base) != run_manifest_hash_for_spec(higher_cap)
    assert REGULARIZED_PLANE not in CANDIDATE_SEMANTICS
    assert REGULARIZED_PLANE not in REPAIRED_CANDIDATE_SEMANTICS

    out = tmp_path / "campaign"
    specs = step121_plane_flux_high_authority_48_specs(output_interval=5)
    manifest = write_step121_campaign_manifest(out, specs, phase="planeflux_high_authority48")
    spec = next(
        item
        for item in specs
        if int(item.open_boundary_inlet_ramp_steps) == 85
        and math_isclose(item.open_boundary_flux_control_target_scale, 0.85)
        and math_isclose(item.open_boundary_flux_feedback_gain_u, 0.75)
        and math_isclose(item.open_boundary_flux_correction_cap_u, 0.0075)
    )
    expected = manifest["expected_rows"][spec.name]

    assert "planeflux_high_authority48" in manifest["phase_history"]
    assert expected["row_role"] == STEP138_ROLE
    assert expected["open_boundary_inlet_ramp_steps"] == 85
    assert expected["open_boundary_flux_control_target_scale"] == pytest.approx(0.85)
    assert expected["open_boundary_flux_feedback_gain_u"] == pytest.approx(0.75)
    assert expected["open_boundary_flux_correction_cap_u"] == pytest.approx(0.0075)

    step137_hashes = {solver_state_hash_for_spec(item) for item in step121_plane_flux_ramp_refined_48_specs(output_interval=5)}
    step138_hashes = {solver_state_hash_for_spec(item) for item in specs}
    assert len(step138_hashes) == 6
    assert step138_hashes.isdisjoint(step137_hashes)

    stale_source = next(
        item
        for item in step121_plane_flux_ramp_refined_48_specs(output_interval=5)
        if int(item.open_boundary_inlet_ramp_steps) == 85
        and math_isclose(item.open_boundary_flux_control_target_scale, 0.85)
    )
    stale = _step138_row(
        spec.name,
        spec.open_boundary_semantics,
        solver_state_hash=solver_state_hash_for_spec(stale_source),
        open_boundary_flux_feedback_gain_u=0.50,
        open_boundary_flux_correction_cap_u=0.005,
        step137_ramp_target_refinement_candidate=True,
        step138_high_authority_outlet_candidate=False,
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "solver_state_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]


def test_step138_rows_do_not_enable_selected96_even_if_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    diagnostic = _step138_row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075"
        "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
        "_ramp85_target0p85_out5_250step_high_authority",
        REGULARIZED_PLANE,
    )

    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [diagnostic])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False


def test_step138_flow_diagnostics_record_step_number_and_bounded_profile(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = _step138_spec(open_boundary_flux_feedback_gain_u=0.75, open_boundary_flux_correction_cap_u=0.0075)
    records = []
    for step, profile in [
        (200, {"24": 41.0, "36": 40.0, "47": 39.0}),
        (225, {"24": 40.0, "36": 39.0, "47": 38.0}),
        (250, {"24": 39.0, "36": 38.0, "47": 37.0}),
    ]:
        records.append(
            _flow_development_diagnostic_record(
                {
                    "step": step,
                    "inlet_flux": 100.0,
                    "outlet_flux": profile["47"],
                    "midplane_flux": profile["36"],
                    "mass_total_delta_rel": 0.001,
                    "sampled_x_profile_flux": json.dumps(profile, sort_keys=True),
                },
                spec,
                {
                    "flow_correction_gain_effective_step": 0.75,
                    "flow_correction_cap_u": 0.0075,
                    "controller_target_outlet_flux": 85.0,
                    "controller_measured_outlet_flux": profile["47"],
                    "controller_raw_flux_error": 85.0 - profile["47"],
                    "controller_filtered_flux_error": 0.20,
                    "controller_u_feedback": -0.00075,
                    "controller_density_feedback": -0.00001,
                    "controller_delta_cap_u": 0.0005,
                    "controller_saturation_active_step": 1,
                    "controller_saturation_count_run": 1,
                    "controller_saturation_fraction_run": 0.1,
                    "controller_drop_guard_activation_count_run": 0,
                    "controller_measure_plane_offset": 2,
                    "controller_target_scale": 0.85,
                },
            )
        )

    assert "step138_high_authority_outlet_candidate" in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
    assert records[-1]["target_outlet_flux"] == pytest.approx(85.0)
    assert records[-1]["correction_gain_effective"] == pytest.approx(0.75)
    assert records[-1]["flow_correction_cap_u"] == pytest.approx(0.0075)
    assert records[-1]["controller_target_scale"] == pytest.approx(0.85)
    assert records[-1]["step138_high_authority_outlet_candidate"] is True
    assert records[-1]["step137_ramp_target_refinement_candidate"] is False

    _write_flow_development_diagnostics(tmp_path, records)

    with (tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[-1]["open_boundary_flux_control_target_scale"] == "0.85"
    assert rows[-1]["correction_gain_effective"] == "0.75"
    assert rows[-1]["flow_correction_cap_u"] == "0.0075"
    assert rows[-1]["step138_high_authority_outlet_candidate"] == "True"
    assert rows[-1]["selected96_claim_allowed"] == "False"
    assert len(rows[-1]["x_profile_flux_samples"]) < 80

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 138
    assert summary["final"]["step138_high_authority_outlet_candidate"] is True
    assert summary["collapse_first_x"] is None
    assert set(summary["x_profile_flux_tail_cv_by_x"]) == {"24", "36", "47"}
    assert summary["selected96_claim_allowed"] is False


def math_isclose(value, expected):
    return abs(float(value) - float(expected)) <= 1.0e-12
