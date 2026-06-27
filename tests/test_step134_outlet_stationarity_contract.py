import csv
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
CONVECTIVE_PLANE = "convective_plane_flux_controlled_damped_outlet"
STEP134_SEMANTICS = {REGULARIZED_PLANE, CONVECTIVE_PLANE}


def _step134_row(name, semantics, *, solver_state_hash="step134-hash", **overrides):
    row = {
        "name": name,
        "row_role": "plane_flux_control_candidate_48",
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
        "open_boundary_flux_control_measure_plane_offset": 1,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "controller_u_feedback_tail_mean": 0.001,
        "controller_u_feedback_tail_std": 0.0001,
        "controller_saturation_fraction_tail": 0.0,
        "density_feedback_tail_abs_max": 0.00002,
        "outlet_flux_drop_guard_activation_fraction_tail": 0.0,
        "inlet_u_lbm": 0.031,
        "outlet_rho": 0.997,
        "lbm_niu": 0.023,
        "lbm_viscosity_semantics": "legacy_external",
        "lbm_relaxation_semantics": "legacy_external_solver_parameter",
        "tau": 0.572,
        "config_hash": solver_state_hash,
        "solver_state_hash": solver_state_hash,
    }
    row.update(overrides)
    return row


def _references():
    return [
        _step134_row(
            "duct_only_48_legacy_boundary_500step_reference_real",
            "equilibrium_all_population_reset",
            solver_state_hash="legacy-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
        ),
        _step134_row(
            "duct_only_48_regularized_boundary_500step_reference_real",
            "regularized_velocity_pressure",
            solver_state_hash="regularized-reference-hash",
            row_role="reference_48",
            requested_n_steps=500,
            steps_completed=500,
        ),
    ]


def _failed_step127_candidates():
    failed_regularized = _step134_row(
        "duct_only_48_regularized_limited_boundary_500step_real",
        "regularized_velocity_pressure_limited",
        solver_state_hash="limited-step127-hash",
        row_role="candidate_48",
        requested_n_steps=500,
        steps_completed=500,
        flux_imbalance_rel_tail_mean=0.51165,
        flux_imbalance_rel_tail_max=0.866,
        outlet_to_inlet_flux_ratio_tail_mean=1.4127,
        midplane_to_inlet_flux_ratio_tail_mean=1.306,
        outlet_flux_tail_cv=0.452,
        flow_development_gate_pass=False,
    )
    failed_convective = _step134_row(
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
        mass_total_delta_rel_final=0.046,
        flow_development_gate_pass=False,
    )
    return [failed_regularized, failed_convective]


def _step134_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": (
            "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005"
            "_rho0p001_alpha0p02_du0p0005_slew0p50_offset1_guard_on_min0p70_250step_triage"
        ),
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
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_flux_filter_alpha": 0.02,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_flux_feedback_delta_cap_u": 0.0005,
        "open_boundary_flux_feedback_slew_alpha": 0.5,
        "open_boundary_convective_blend_weight": 0.02,
        "open_boundary_flux_control_measure_plane_offset": 1,
        "open_boundary_outlet_flux_drop_guard_enabled": True,
        "open_boundary_outlet_flux_drop_guard_min_ratio": 0.70,
        "artifact_scope_note": (
            "Step134 bounded 48^3 outlet tail-collapse diagnosis and near-outlet control-plane repair; "
            "not a selected96 enabling row"
        ),
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def test_step134_stationarity_phase_is_distinct_48_triage_surface():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_plane_flux_mass_damped_48_specs,
        step121_plane_flux_stationarity_48_specs,
    )

    specs = step121_plane_flux_stationarity_48_specs(output_interval=25)
    step133_names = {spec.name for spec in step121_plane_flux_mass_damped_48_specs(output_interval=25)}

    assert resolve_step121_phase_specs("planeflux_stationarity48", output_interval=25) == specs
    assert len(specs) == 6
    assert {spec.open_boundary_semantics for spec in specs} == STEP134_SEMANTICS
    assert all(spec.row_role == "plane_flux_control_candidate_48" for spec in specs)
    assert all(spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all("Step134" in spec.artifact_scope_note for spec in specs)
    assert all(spec.name not in step133_names for spec in specs)
    assert all("offset" in spec.name and "guard" in spec.name and "min" in spec.name for spec in specs)
    assert {spec.open_boundary_flux_control_measure_plane_offset for spec in specs} == {1, 2}
    assert {spec.open_boundary_outlet_flux_drop_guard_enabled for spec in specs} == {False, True}
    assert {spec.open_boundary_outlet_flux_drop_guard_min_ratio for spec in specs} == {0.50, 0.60, 0.70}
    assert sum(spec.open_boundary_semantics == CONVECTIVE_PLANE for spec in specs) == 1


def test_step134_solver_hash_includes_outlet_stationarity_params():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_plane_flux_mass_damped_48_specs,
        step121_plane_flux_stationarity_48_specs,
    )

    base = _step134_spec()
    offset_changed = _step134_spec(open_boundary_flux_control_measure_plane_offset=2)
    guard_changed = _step134_spec(open_boundary_outlet_flux_drop_guard_enabled=False)
    min_ratio_changed = _step134_spec(open_boundary_outlet_flux_drop_guard_min_ratio=0.50)

    base_hash = solver_state_hash_for_spec(base)
    assert solver_state_hash_for_spec(offset_changed) != base_hash
    assert solver_state_hash_for_spec(guard_changed) != base_hash
    assert solver_state_hash_for_spec(min_ratio_changed) != base_hash

    step133_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_mass_damped_48_specs(output_interval=25)}
    step134_hashes = {solver_state_hash_for_spec(spec) for spec in step121_plane_flux_stationarity_48_specs(output_interval=25)}
    assert len(step134_hashes) == 6
    assert step134_hashes.isdisjoint(step133_hashes)


def test_step134_manifest_rejects_stale_step133_rows_for_stationarity_phase(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_plane_flux_mass_damped_48_specs,
        step121_plane_flux_stationarity_48_specs,
        write_step121_campaign_manifest,
    )

    out = tmp_path / "campaign"
    specs = step121_plane_flux_stationarity_48_specs(output_interval=25)
    write_step121_campaign_manifest(out, specs, phase="planeflux_stationarity48")
    spec = specs[0]
    stale_source = next(
        item
        for item in step121_plane_flux_mass_damped_48_specs(output_interval=25)
        if item.open_boundary_semantics == spec.open_boundary_semantics
    )
    stale = _step134_row(
        spec.name,
        spec.open_boundary_semantics,
        solver_state_hash=solver_state_hash_for_spec(stale_source),
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "solver_state_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]
    assert solver_state_hash_for_spec(spec) != stale["solver_state_hash"]


def test_step134_rows_do_not_enable_selected96_even_if_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    stationarity_triage = _step134_row(
        "duct_only_48_regularized_plane_flux_controlled_gain0p25_cap0p005"
        "_rho0p001_alpha0p02_du0p0005_slew0p50_offset1_guard_on_min0p70_250step_triage",
        REGULARIZED_PLANE,
    )
    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [stationarity_triage])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False
    assert all(item["semantics"] not in STEP134_SEMANTICS for item in selection["candidate_summaries"])


def test_step134_outlet_tail_and_near_outlet_diagnostics_are_bounded(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = _step134_spec()
    diagnostics = [
        _flow_development_diagnostic_record(
            {
                "step": 200,
                "inlet_flux": 42.0,
                "outlet_flux": 58.49,
                "midplane_flux": 39.0,
                "mass_total_delta_rel": 0.014,
                "outlet_plane_rho_mean": 1.001,
                "outlet_plane_rho_std": 0.002,
                "outlet_plane_ux_min": -0.02,
                "outlet_plane_negative_ux_fraction": 0.10,
                "near_outlet_flux_xminus1": 60.0,
                "near_outlet_flux_xminus2": 61.0,
                "near_outlet_flux_xminus3": 62.0,
                "near_outlet_to_outlet_flux_ratio": 1.026,
            },
            spec,
            {
                "flow_correction_cap_u": 0.005,
                "controller_target_outlet_flux": 42.0,
                "controller_measured_outlet_flux": 60.0,
                "controller_raw_flux_error": -18.0,
                "controller_filtered_flux_error": -0.30,
                "controller_u_feedback": -0.0005,
                "controller_density_feedback": -0.00001,
                "controller_delta_cap_u": 0.0005,
                "controller_slew_alpha": 0.5,
                "controller_saturation_fraction_run": 0.0,
                "controller_drop_guard_active_step": 0,
                "controller_drop_guard_activation_count_run": 0,
                "controller_measure_plane_offset": 1,
            },
        ),
        _flow_development_diagnostic_record(
            {
                "step": 225,
                "inlet_flux": 42.0,
                "outlet_flux": 55.08,
                "midplane_flux": 38.5,
                "mass_total_delta_rel": 0.013,
                "outlet_plane_rho_mean": 0.999,
                "outlet_plane_rho_std": 0.003,
                "outlet_plane_ux_min": -0.015,
                "outlet_plane_negative_ux_fraction": 0.08,
                "near_outlet_flux_xminus1": 57.0,
                "near_outlet_flux_xminus2": 58.0,
                "near_outlet_flux_xminus3": 59.0,
                "near_outlet_to_outlet_flux_ratio": 1.035,
            },
            spec,
            {
                "flow_correction_cap_u": 0.005,
                "controller_target_outlet_flux": 42.0,
                "controller_measured_outlet_flux": 57.0,
                "controller_raw_flux_error": -15.0,
                "controller_filtered_flux_error": -0.28,
                "controller_u_feedback": -0.00025,
                "controller_density_feedback": -0.00002,
                "controller_delta_cap_u": 0.0005,
                "controller_slew_alpha": 0.5,
                "controller_saturation_fraction_run": 0.0,
                "controller_drop_guard_active_step": 0,
                "controller_drop_guard_activation_count_run": 0,
                "controller_measure_plane_offset": 1,
            },
        ),
        _flow_development_diagnostic_record(
            {
                "step": 250,
                "inlet_flux": 42.0,
                "outlet_flux": 14.31,
                "midplane_flux": 37.8,
                "mass_total_delta_rel": 0.012,
                "outlet_plane_rho_mean": 0.998,
                "outlet_plane_rho_std": 0.004,
                "outlet_plane_ux_min": -0.03,
                "outlet_plane_negative_ux_fraction": 0.20,
                "near_outlet_flux_xminus1": 52.0,
                "near_outlet_flux_xminus2": 54.0,
                "near_outlet_flux_xminus3": 55.0,
                "near_outlet_to_outlet_flux_ratio": 3.634,
            },
            spec,
            {
                "flow_correction_cap_u": 0.005,
                "controller_target_outlet_flux": 42.0,
                "controller_measured_outlet_flux": 52.0,
                "controller_raw_flux_error": -10.0,
                "controller_filtered_flux_error": -0.20,
                "controller_u_feedback": 0.0001,
                "controller_density_feedback": -0.00001,
                "controller_delta_cap_u": 0.0005,
                "controller_slew_alpha": 0.5,
                "controller_saturation_fraction_run": 0.0,
                "controller_drop_guard_active_step": 1,
                "controller_drop_guard_activation_count_run": 1,
                "controller_measure_plane_offset": 1,
            },
        ),
    ]
    _write_flow_development_diagnostics(tmp_path, diagnostics)

    required = {
        "step134_outlet_stationarity_candidate",
        "open_boundary_flux_control_measure_plane_offset",
        "open_boundary_outlet_flux_drop_guard_enabled",
        "open_boundary_outlet_flux_drop_guard_min_ratio",
        "near_outlet_flux_xminus1",
        "near_outlet_flux_xminus2",
        "near_outlet_flux_xminus3",
        "near_outlet_to_outlet_flux_ratio",
        "controller_measure_plane_offset",
        "controller_drop_guard_active_step",
        "controller_drop_guard_activation_count_run",
    }
    assert required.issubset(set(FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS))
    assert diagnostics[-1]["step134_outlet_stationarity_candidate"] is True

    with (tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["selected96_claim_allowed"] == "False"
    assert rows[-1]["near_outlet_flux_xminus1"] == "52.0"

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 134
    assert summary["tail_outlet_flux_values"] == pytest.approx([58.49, 55.08, 14.31])
    assert summary["outlet_flux_tail_drop_ratio"] == pytest.approx(14.31 / 58.49)
    assert summary["outlet_flux_tail_last_to_mean_ratio"] == pytest.approx(14.31 / ((58.49 + 55.08 + 14.31) / 3.0))
    assert summary["near_outlet_to_outlet_flux_ratio_tail_mean"] == pytest.approx((1.026 + 1.035 + 3.634) / 3.0)
    assert summary["controller_feedback_last_to_tail_mean"] == pytest.approx(0.0001 / ((-0.0005 - 0.00025 + 0.0001) / 3.0))
    assert summary["density_feedback_last_to_tail_mean"] == pytest.approx((-0.00001) / ((-0.00001 - 0.00002 - 0.00001) / 3.0))
    assert summary["outlet_rho_last"] == pytest.approx(0.998)
    assert summary["outlet_ux_min_last"] == pytest.approx(-0.03)
    assert summary["outlet_ux_negative_fraction_last"] == pytest.approx(0.20)
    assert summary["drop_guard_activation_count_tail"] == 1
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_claim_allowed"] is False


def test_step134_config_fields_validate_defaults_and_bounds():
    from src.mpm_lbm.sim.lbm.config import LBMConfig

    cfg = LBMConfig(nx=8, ny=6, nz=6, open_boundary_semantics=REGULARIZED_PLANE)
    assert cfg.open_boundary_flux_control_measure_plane_offset == 0
    assert cfg.open_boundary_outlet_flux_drop_guard_enabled is False
    assert cfg.open_boundary_outlet_flux_drop_guard_min_ratio == pytest.approx(0.60)

    cfg = LBMConfig(
        nx=8,
        ny=6,
        nz=6,
        open_boundary_semantics=REGULARIZED_PLANE,
        open_boundary_flux_control_measure_plane_offset=1,
        open_boundary_outlet_flux_drop_guard_enabled=True,
        open_boundary_outlet_flux_drop_guard_min_ratio=0.70,
    )
    assert cfg.open_boundary_flux_control_measure_plane_offset == 1
    assert cfg.open_boundary_outlet_flux_drop_guard_enabled is True
    assert cfg.open_boundary_outlet_flux_drop_guard_min_ratio == pytest.approx(0.70)

    with pytest.raises(ValueError, match="open_boundary_flux_control_measure_plane_offset"):
        LBMConfig(nx=8, ny=6, nz=6, open_boundary_flux_control_measure_plane_offset=-1)
    with pytest.raises(ValueError, match="open_boundary_flux_control_measure_plane_offset"):
        LBMConfig(nx=8, ny=6, nz=6, open_boundary_flux_control_measure_plane_offset=3)
    with pytest.raises(ValueError, match="open_boundary_outlet_flux_drop_guard_min_ratio"):
        LBMConfig(nx=8, ny=6, nz=6, open_boundary_outlet_flux_drop_guard_min_ratio=0.0)
    with pytest.raises(ValueError, match="open_boundary_outlet_flux_drop_guard_min_ratio"):
        LBMConfig(nx=8, ny=6, nz=6, open_boundary_outlet_flux_drop_guard_min_ratio=1.1)
