import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
STEP136_ROLE = "interior_reflection_diagnostic_48"


def _step136_row(name, semantics, *, solver_state_hash="step136-hash", **overrides):
    row = {
        "name": name,
        "row_role": STEP136_ROLE,
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
        "open_boundary_flux_feedback_gain_u": 0.50,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_flux_control_target_scale": 0.95,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 100,
        "open_boundary_inlet_ramp_profile": "linear",
        "step135_interior_reflection_candidate": False,
        "step136_ramped_throughput_calibration_candidate": True,
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
        _step136_row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            solver_state_hash="legacy-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
            step136_ramped_throughput_calibration_candidate=False,
        ),
        _step136_row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            solver_state_hash="regularized-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
            step136_ramped_throughput_calibration_candidate=False,
        ),
    ]


def _failed_step127_candidates():
    return [
        _step136_row(
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
            step136_ramped_throughput_calibration_candidate=False,
        ),
        _step136_row(
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
            step136_ramped_throughput_calibration_candidate=False,
        ),
    ]


def _step136_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": (
            "duct_only_48_regularized_plane_flux_controlled_gain0p50_cap0p005"
            "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
            "_ramp100_target0p95_out5_250step_ramp_tuned"
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
        "row_role": STEP136_ROLE,
        "open_boundary_flux_feedback_gain_u": 0.50,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 2,
        "open_boundary_flux_control_target_scale": 0.95,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "open_boundary_inlet_ramp_steps": 100,
        "open_boundary_inlet_ramp_profile": "linear",
        "niu": 0.10,
        "artifact_scope_note": (
            "Step136 bounded 48^3 ramped-inlet throughput calibration; "
            "diagnostic only and not selected96 or 500-step evidence"
        ),
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def test_step136_ramp_tuned_phase_is_distinct_bounded_diagnostic_surface():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_plane_flux_interior_diag_48_specs,
        step121_plane_flux_ramp_tuned_48_specs,
    )

    specs = step121_plane_flux_ramp_tuned_48_specs(output_interval=5)
    step135_names = {spec.name for spec in step121_plane_flux_interior_diag_48_specs(output_interval=5)}

    assert resolve_step121_phase_specs("planeflux_ramp_tuned48", output_interval=5) == specs
    assert len(specs) == 6
    assert all(spec.row_role == STEP136_ROLE for spec in specs)
    assert all(spec.open_boundary_semantics == REGULARIZED_PLANE for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all(spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.output_interval == 5 for spec in specs)
    assert all("Step136" in spec.artifact_scope_note for spec in specs)
    assert all(spec.name not in step135_names for spec in specs)
    assert all("target" in spec.name and "250step_ramp_tuned" in spec.name for spec in specs)
    assert {spec.open_boundary_inlet_ramp_steps for spec in specs} == {75, 100}
    assert {round(float(spec.open_boundary_flux_control_target_scale), 2) for spec in specs} == {0.90, 0.95, 1.00}
    assert {
        (round(float(spec.open_boundary_flux_feedback_gain_u), 2), round(float(spec.open_boundary_flux_correction_cap_u), 4))
        for spec in specs
    } == {(0.35, 0.005), (0.50, 0.005), (0.50, 0.0075)}


def test_step136_target_scale_defaults_config_and_solver_identity():
    from experiments.steps.step118_lbm_open_boundary_stability_repair import _make_lbm_config
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        _tau_feasibility_report,
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_plane_flux_interior_diag_48_specs,
        step121_plane_flux_ramp_tuned_48_specs,
    )
    from src.mpm_lbm.sim.lbm.config import LBMConfig

    default_spec = Step120RunSpec(
        name="default_target_scale",
        nx=4,
        ny=4,
        nz=4,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="equilibrium_all_population_reset",
        geometry_mode="duct_only",
    )
    assert default_spec.open_boundary_flux_control_target_scale == pytest.approx(1.0)
    assert LBMConfig(nx=4, ny=4, nz=4).open_boundary_flux_control_target_scale == pytest.approx(1.0)
    with pytest.raises(ValueError, match="open_boundary_flux_control_target_scale"):
        LBMConfig(nx=4, ny=4, nz=4, open_boundary_flux_control_target_scale=0.0)

    base = _step136_spec(open_boundary_flux_control_target_scale=1.0)
    scaled = _step136_spec(open_boundary_flux_control_target_scale=0.95)
    assert solver_state_hash_for_spec(base) != solver_state_hash_for_spec(scaled)
    assert run_manifest_hash_for_spec(base) != run_manifest_hash_for_spec(scaled)

    cfg = _make_lbm_config(scaled, _tau_feasibility_report(scaled))
    assert cfg.open_boundary_flux_control_target_scale == pytest.approx(0.95)

    step135_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_interior_diag_48_specs(output_interval=5)}
    step136_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_ramp_tuned_48_specs(output_interval=5)}
    assert len(step136_hashes) == 6
    assert step136_hashes.isdisjoint(step135_hashes)


def test_step136_manifest_records_target_scale_and_rejects_stale_step135_rows(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_plane_flux_interior_diag_48_specs,
        step121_plane_flux_ramp_tuned_48_specs,
        write_step121_campaign_manifest,
    )

    out = tmp_path / "campaign"
    specs = step121_plane_flux_ramp_tuned_48_specs(output_interval=5)
    manifest = write_step121_campaign_manifest(out, specs, phase="planeflux_ramp_tuned48")
    spec = specs[0]
    expected = manifest["expected_rows"][spec.name]

    assert expected["open_boundary_inlet_ramp_steps"] == 100
    assert expected["open_boundary_flux_feedback_gain_u"] == pytest.approx(0.35)
    assert expected["open_boundary_flux_correction_cap_u"] == pytest.approx(0.005)
    assert expected["open_boundary_flux_control_target_scale"] == pytest.approx(1.0)

    stale_source = next(
        item
        for item in step121_plane_flux_interior_diag_48_specs(output_interval=5)
        if item.open_boundary_semantics == spec.open_boundary_semantics
        and int(item.open_boundary_inlet_ramp_steps) == 100
    )
    stale = _step136_row(
        spec.name,
        spec.open_boundary_semantics,
        solver_state_hash=solver_state_hash_for_spec(stale_source),
        open_boundary_flux_control_target_scale=1.0,
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "solver_state_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]
    assert solver_state_hash_for_spec(spec) != stale["solver_state_hash"]


def test_step136_rows_do_not_enable_selected96_even_if_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    diagnostic = _step136_row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p50_cap0p005"
        "_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70"
        "_ramp100_target0p95_out5_250step_ramp_tuned",
        REGULARIZED_PLANE,
    )

    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [diagnostic])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False
    assert all(item["semantics"] != REGULARIZED_PLANE for item in selection["candidate_summaries"])


def test_step136_flow_diagnostics_record_target_scale_and_step_number(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = _step136_spec(open_boundary_flux_control_target_scale=0.90)
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
                    "mass_total_delta_rel": 0.008,
                    "outlet_plane_rho_mean": 1.0,
                    "outlet_plane_rho_std": 0.001,
                    "outlet_plane_ux_min": 0.01,
                    "outlet_plane_negative_ux_fraction": 0.0,
                    "near_outlet_flux_xminus1": profile["47"],
                    "near_outlet_flux_xminus2": profile["36"],
                    "near_outlet_flux_xminus3": profile["24"],
                    "near_outlet_to_outlet_flux_ratio": profile["36"] / profile["47"],
                    "x_profile_flux_samples": profile,
                    "x_profile_ux_mean_samples": {key: value / 1000.0 for key, value in profile.items()},
                    "x_profile_rho_mean_samples": {key: 1.0 for key in profile},
                    "sampled_x_profile_flux": ";".join(f"{key}:{value}" for key, value in profile.items()),
                },
                spec,
                {
                    "flow_correction_cap_u": 0.005,
                    "controller_target_outlet_flux": 90.0,
                    "controller_measured_outlet_flux": profile["47"],
                    "controller_raw_flux_error": 90.0 - profile["47"],
                    "controller_filtered_flux_error": 0.20,
                    "controller_u_feedback": -0.0005,
                    "controller_density_feedback": -0.00001,
                    "controller_delta_cap_u": 0.0005,
                    "controller_slew_alpha": 0.5,
                    "controller_saturation_fraction_run": 0.0,
                    "controller_drop_guard_active_step": 0,
                    "controller_drop_guard_activation_count_run": 0,
                    "controller_measure_plane_offset": 2,
                    "controller_target_scale": 0.90,
                },
            )
        )

    assert "open_boundary_flux_control_target_scale" in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
    assert "controller_target_scale" in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
    assert records[-1]["target_outlet_flux"] == pytest.approx(90.0)
    assert records[-1]["controller_target_scale"] == pytest.approx(0.90)
    assert records[-1]["step136_ramped_throughput_calibration_candidate"] is True
    assert records[-1]["step135_interior_reflection_candidate"] is False

    _write_flow_development_diagnostics(tmp_path, records)

    with (tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[-1]["open_boundary_flux_control_target_scale"] == "0.9"
    assert rows[-1]["controller_target_scale"] == "0.9"
    assert rows[-1]["selected96_claim_allowed"] == "False"

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 136
    assert summary["final"]["step136_ramped_throughput_calibration_candidate"] is True
    assert summary["collapse_first_x"] is None
    assert summary["selected96_claim_allowed"] is False


def test_step136_controller_target_scale_is_applied_in_core_controller():
    source = (ROOT / "src" / "mpm_lbm" / "sim" / "lbm" / "fluid.py").read_text(encoding="utf-8")

    assert "open_boundary_flux_control_target_scale * self.ob_target_outlet_flux" in source
    assert '"flow_control_target_scale"' in source
    assert '"controller_target_scale"' in source
