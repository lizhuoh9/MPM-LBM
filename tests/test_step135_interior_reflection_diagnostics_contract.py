import csv
import json
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
CONVECTIVE_PLANE = "convective_plane_flux_controlled_damped_outlet"
STEP135_ROLE = "interior_reflection_diagnostic_48"


def _step135_row(name, semantics, *, solver_state_hash="step135-hash", **overrides):
    row = {
        "name": name,
        "row_role": STEP135_ROLE,
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
        "open_boundary_rho_min": 0.91,
        "open_boundary_rho_max": 1.09,
        "open_boundary_u_max": 0.08,
        "open_boundary_noneq_cap": 0.17,
        "open_boundary_population_floor": None,
        "open_boundary_flux_feedback_gain_u": 0.25,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 0,
        "open_boundary_inlet_ramp_profile": "linear",
        "step135_interior_reflection_candidate": True,
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
        _step135_row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            solver_state_hash="legacy-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
        ),
        _step135_row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            solver_state_hash="regularized-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
        ),
    ]


def _failed_step127_candidates():
    return [
        _step135_row(
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
        ),
        _step135_row(
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
        ),
    ]


def _step135_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": (
            "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005"
            "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
            "_ramp0_niu0p10_out5_250step_interior_diag"
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
        "row_role": STEP135_ROLE,
        "open_boundary_flux_feedback_gain_u": 0.25,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 0,
        "open_boundary_inlet_ramp_profile": "linear",
        "niu": 0.10,
        "artifact_scope_note": (
            "Step135 bounded 48^3 interior reflection and bulk-dynamics diagnosis; "
            "diagnostic only and not a selected96 enabling row"
        ),
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def test_step135_interior_diag_phase_is_distinct_bounded_diagnostic_surface():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_plane_flux_interior_diag_48_specs,
        step121_plane_flux_stationarity_48_specs,
    )

    specs = step121_plane_flux_interior_diag_48_specs(output_interval=5)
    step134_names = {spec.name for spec in step121_plane_flux_stationarity_48_specs(output_interval=5)}

    assert resolve_step121_phase_specs("planeflux_interior_diag48", output_interval=5) == specs
    assert len(specs) == 6
    assert all(spec.row_role == STEP135_ROLE for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all(spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.output_interval == 5 for spec in specs)
    assert all("Step135" in spec.artifact_scope_note for spec in specs)
    assert all(spec.name not in step134_names for spec in specs)
    assert all("out5" in spec.name and "250step_interior_diag" in spec.name for spec in specs)
    assert {spec.open_boundary_semantics for spec in specs} == {REGULARIZED_PLANE, CONVECTIVE_PLANE}
    assert sum(spec.open_boundary_semantics == CONVECTIVE_PLANE for spec in specs) == 1
    assert {spec.open_boundary_inlet_ramp_steps for spec in specs} == {0, 50, 100}
    assert {round(float(spec.niu), 2) for spec in specs} >= {0.08, 0.10, 0.12}
    assert all(spec.open_boundary_flux_control_measure_plane_offset in {1, 2} for spec in specs)
    assert all(spec.open_boundary_outlet_flux_drop_guard_enabled is True for spec in specs)
    assert all(spec.open_boundary_outlet_flux_drop_guard_min_ratio == pytest.approx(0.70) for spec in specs)


def test_step135_solver_hash_manifest_and_identity_include_ramp_and_niu():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        run_manifest_hash_for_spec,
        step121_plane_flux_interior_diag_48_specs,
        step121_plane_flux_stationarity_48_specs,
    )

    base = _step135_spec()
    ramp_changed = _step135_spec(open_boundary_inlet_ramp_steps=50)
    niu_changed = _step135_spec(niu=0.08)

    base_hash = solver_state_hash_for_spec(base)
    assert solver_state_hash_for_spec(ramp_changed) != base_hash
    assert solver_state_hash_for_spec(niu_changed) != base_hash
    assert run_manifest_hash_for_spec(ramp_changed) != run_manifest_hash_for_spec(base)

    step134_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_stationarity_48_specs(output_interval=5)}
    step135_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_interior_diag_48_specs(output_interval=5)}
    assert len(step135_hashes) == 6
    assert step135_hashes.isdisjoint(step134_hashes)


def test_step135_manifest_rejects_stale_step134_stationarity_rows(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_plane_flux_interior_diag_48_specs,
        step121_plane_flux_stationarity_48_specs,
        write_step121_campaign_manifest,
    )

    out = tmp_path / "campaign"
    specs = step121_plane_flux_interior_diag_48_specs(output_interval=5)
    write_step121_campaign_manifest(out, specs, phase="planeflux_interior_diag48")
    spec = specs[0]
    stale_source = next(
        item
        for item in step121_plane_flux_stationarity_48_specs(output_interval=5)
        if item.open_boundary_semantics == spec.open_boundary_semantics
    )
    stale = _step135_row(
        spec.name,
        spec.open_boundary_semantics,
        solver_state_hash=solver_state_hash_for_spec(stale_source),
        row_role=STEP135_ROLE,
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "solver_state_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]
    assert solver_state_hash_for_spec(spec) != stale["solver_state_hash"]


def test_step135_rows_do_not_enable_selected96_even_if_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    diagnostic = _step135_row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005"
        "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
        "_ramp0_niu0p10_out5_250step_interior_diag",
        REGULARIZED_PLANE,
    )

    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [diagnostic])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False
    assert all(item["semantics"] != REGULARIZED_PLANE for item in selection["candidate_summaries"])


def test_step135_x_profile_sampling_is_bounded_and_schema_stable():
    from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import (
        sampled_x_profile_flux_map,
        sampled_x_profile_indices,
        summarize_lbm_boundary_diagnostics,
    )

    assert sampled_x_profile_indices(48) == [0, 6, 12, 18, 24, 30, 36, 42, 45, 46, 47]
    assert sampled_x_profile_indices(5) == [0, 1, 2, 3, 4]

    rho = np.ones((5, 4, 4), dtype=float)
    v = np.zeros((5, 4, 4, 3), dtype=float)
    solid = np.zeros((5, 4, 4), dtype=np.int8)
    for x in range(5):
        v[x, :, :, 0] = 0.01 * (x + 1)

    snapshot = {"rho": rho, "v": v, "solid": solid}
    flux_map = sampled_x_profile_flux_map(snapshot)
    summary = summarize_lbm_boundary_diagnostics(snapshot, step=10)

    assert list(flux_map) == ["0", "1", "2", "3", "4"]
    assert set(summary["x_profile_flux_samples"]) == set(flux_map)
    assert set(summary["x_profile_ux_mean_samples"]) == set(flux_map)
    assert set(summary["x_profile_rho_mean_samples"]) == set(flux_map)
    assert len(summary["sampled_x_profile_flux"].split(";")) == 5


def test_step135_flow_diagnostics_add_x_profile_tail_and_collapse_summary(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = _step135_spec()
    x_profiles = [
        {"36": 40.0, "42": 38.0, "46": 37.0, "47": 36.0},
        {"36": 39.0, "42": 37.0, "46": 36.0, "47": 35.0},
        {"36": 38.0, "42": 36.0, "46": 35.0, "47": 10.0},
    ]
    diagnostics = []
    for step, outlet_flux, profile in zip([200, 225, 250], [36.0, 35.0, 10.0], x_profiles):
        diagnostics.append(
            _flow_development_diagnostic_record(
                {
                    "step": step,
                    "inlet_flux": 42.0,
                    "outlet_flux": outlet_flux,
                    "midplane_flux": 39.0,
                    "mass_total_delta_rel": 0.014,
                    "outlet_plane_rho_mean": 1.0,
                    "outlet_plane_rho_std": 0.002,
                    "outlet_plane_ux_min": -0.02,
                    "outlet_plane_negative_ux_fraction": 0.10,
                    "near_outlet_flux_xminus1": profile["46"],
                    "near_outlet_flux_xminus2": profile["42"],
                    "near_outlet_flux_xminus3": profile["36"],
                    "near_outlet_to_outlet_flux_ratio": profile["46"] / outlet_flux,
                    "x_profile_flux_samples": profile,
                    "x_profile_ux_mean_samples": {key: value / 1000.0 for key, value in profile.items()},
                    "x_profile_rho_mean_samples": {key: 1.0 for key in profile},
                    "sampled_x_profile_flux": ";".join(f"{key}:{value}" for key, value in profile.items()),
                },
                spec,
                {
                    "flow_correction_cap_u": 0.005,
                    "controller_target_outlet_flux": 42.0,
                    "controller_measured_outlet_flux": profile["46"],
                    "controller_raw_flux_error": 42.0 - profile["46"],
                    "controller_filtered_flux_error": 0.25,
                    "controller_u_feedback": -0.0005,
                    "controller_density_feedback": -0.00001,
                    "controller_delta_cap_u": 0.0005,
                    "controller_slew_alpha": 0.5,
                    "controller_saturation_fraction_run": 0.0,
                    "controller_drop_guard_active_step": 0,
                    "controller_drop_guard_activation_count_run": 0,
                    "controller_measure_plane_offset": 2,
                },
            )
        )
    _write_flow_development_diagnostics(tmp_path, diagnostics)

    required = {
        "step135_interior_reflection_candidate",
        "open_boundary_inlet_ramp_steps",
        "open_boundary_inlet_ramp_profile",
        "x_profile_flux_samples",
        "x_profile_ux_mean_samples",
        "x_profile_rho_mean_samples",
    }
    assert required.issubset(set(FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS))

    with (tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[-1]["step135_interior_reflection_candidate"] == "True"
    assert rows[-1]["selected96_claim_allowed"] == "False"
    assert rows[-1]["open_boundary_inlet_ramp_steps"] == "0"

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 135
    assert summary["x_profile_flux_tail_values_by_x"]["47"] == pytest.approx([36.0, 35.0, 10.0])
    assert summary["x_profile_flux_tail_cv_by_x"]["47"] > summary["x_profile_flux_tail_cv_by_x"]["46"]
    assert summary["x_profile_flux_last_to_mean_ratio_by_x"]["47"] == pytest.approx(10.0 / ((36.0 + 35.0 + 10.0) / 3.0))
    assert summary["collapse_first_x"] == 47
    assert summary["collapse_first_step"] == 250
    assert summary["x_profile_flux_phase_lag_proxy"]["collapse_station_count"] == 1
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_claim_allowed"] is False
