import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
CONVECTIVE_PLANE = "convective_plane_flux_controlled_damped_outlet"
STEP131_PLANE_FLUX_CONTROL = {REGULARIZED_PLANE, CONVECTIVE_PLANE}
STEP130_FLOW_REPAIR = {
    "regularized_flux_matched_pressure_outlet",
    "convective_flux_matched_damped_outlet",
}


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
        "open_boundary_flux_feedback_gain_u": 0.0025,
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


def test_step131_new_semantics_are_valid_config_values_and_dispatch_to_distinct_kernels():
    from src.mpm_lbm.sim.lbm.config import LBMConfig, VALID_LBM_OPEN_BOUNDARY_SEMANTICS

    assert STEP131_PLANE_FLUX_CONTROL.issubset(set(VALID_LBM_OPEN_BOUNDARY_SEMANTICS))
    cfg = LBMConfig(
        nx=8,
        ny=6,
        nz=6,
        open_boundary_semantics=REGULARIZED_PLANE,
        open_boundary_flux_feedback_gain_u=0.0025,
        open_boundary_flux_feedback_gain_rho=0.0,
        open_boundary_flux_filter_alpha=0.02,
        open_boundary_flux_correction_cap_u=0.002,
        open_boundary_convective_blend_weight=0.02,
    )
    assert cfg.open_boundary_semantics == REGULARIZED_PLANE

    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    assert "apply_regularized_plane_flux_controlled_pressure_outlet_x_open_boundaries" in source
    assert "apply_convective_plane_flux_controlled_damped_outlet_x_open_boundaries" in source
    assert "update_open_boundary_plane_flux_controller" in source
    assert "self.ob_flux_control_u_feedback" in source
    assert "self.vx_bcxl - target_u[0]" in source
    assert "_regularized_plane_flux_controlled_population" in source
    assert "_convective_plane_flux_controlled_damped_population" in source


def _controller_spec(**overrides):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec

    base = {
        "name": "tiny_step131_controller_contract",
        "nx": 8,
        "ny": 6,
        "nz": 6,
        "n_steps": 3,
        "output_interval": 1,
        "failure_check_interval": 1,
        "checkpoint_every": 0,
        "open_boundary_semantics": REGULARIZED_PLANE,
        "geometry_mode": "duct_only",
        "requested_nx": 8,
        "requested_n_steps": 3,
        "allow_large_real_run_without_flag": True,
        "row_role": "plane_flux_control_candidate_48",
        "open_boundary_flux_feedback_gain_u": 1.0,
        "open_boundary_flux_feedback_gain_rho": 0.0,
        "open_boundary_flux_filter_alpha": 1.0,
        "open_boundary_flux_correction_cap_u": 0.002,
        "open_boundary_convective_blend_weight": 0.02,
    }
    base.update(overrides)
    return Step120RunSpec(**base)


def _set_plane_velocities(lbm, *, inlet_ux: float, outlet_ux: float) -> None:
    rho = np.ones_like(lbm.rho.to_numpy(), dtype=np.float32)
    velocity = np.zeros_like(lbm.v.to_numpy(), dtype=np.float32)
    solid = np.zeros_like(lbm.solid.to_numpy(), dtype=np.int8)
    velocity[0, :, :, 0] = np.float32(inlet_ux)
    velocity[-1, :, :, 0] = np.float32(outlet_ux)
    lbm.rho.from_numpy(rho)
    lbm.v.from_numpy(velocity)
    lbm.solid.from_numpy(solid)


def test_step131_controller_fields_reset_and_feedback_sign_is_capped():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import create_step120_lbm

    spec = _controller_spec()
    lbm, _ = create_step120_lbm(spec)
    lbm.clear_open_boundary_limiter_run_counters()
    stats = lbm.get_open_boundary_limiter_stats()
    assert stats["controller_target_outlet_flux"] == 0.0
    assert stats["controller_measured_outlet_flux"] == 0.0
    assert stats["controller_u_feedback"] == 0.0
    assert stats["controller_saturation_count_run"] == 0

    _set_plane_velocities(lbm, inlet_ux=1.0, outlet_ux=0.0)
    lbm.update_open_boundary_plane_flux_controller()
    stats = lbm.get_open_boundary_limiter_stats()
    assert stats["controller_target_outlet_flux"] > stats["controller_measured_outlet_flux"]
    assert stats["controller_raw_flux_error"] > 0.0
    assert stats["controller_u_feedback"] == pytest.approx(spec.open_boundary_flux_correction_cap_u)
    assert stats["controller_saturation_count_run"] == 1

    lbm.clear_open_boundary_limiter_run_counters()
    _set_plane_velocities(lbm, inlet_ux=0.0, outlet_ux=1.0)
    lbm.update_open_boundary_plane_flux_controller()
    stats = lbm.get_open_boundary_limiter_stats()
    assert stats["controller_target_outlet_flux"] < stats["controller_measured_outlet_flux"]
    assert stats["controller_raw_flux_error"] < 0.0
    assert stats["controller_u_feedback"] == pytest.approx(-spec.open_boundary_flux_correction_cap_u)
    assert stats["controller_saturation_count_run"] == 1


def test_step131_planeflux_phase_is_separate_from_prior_48_phases_and_hashes_parameters():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        CANDIDATE_SEMANTICS,
        FLOW_REPAIR_CANDIDATE_SEMANTICS,
        PLANE_FLUX_CONTROL_CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_flow_repair_48_specs,
        step121_plane_flux_48_specs,
        step121_repair_48_specs,
    )

    assert set(PLANE_FLUX_CONTROL_CANDIDATE_SEMANTICS) == STEP131_PLANE_FLUX_CONTROL
    assert STEP131_PLANE_FLUX_CONTROL.isdisjoint(set(CANDIDATE_SEMANTICS))
    assert STEP131_PLANE_FLUX_CONTROL.isdisjoint(set(REPAIRED_CANDIDATE_SEMANTICS))
    assert STEP131_PLANE_FLUX_CONTROL.isdisjoint(set(FLOW_REPAIR_CANDIDATE_SEMANTICS))

    repair_specs = step121_repair_48_specs(output_interval=25)
    flow_specs = step121_flow_repair_48_specs(output_interval=25)
    plane_specs = step121_plane_flux_48_specs(output_interval=25)

    assert {spec.open_boundary_semantics for spec in repair_specs}.isdisjoint(STEP131_PLANE_FLUX_CONTROL)
    assert {spec.open_boundary_semantics for spec in flow_specs} == STEP130_FLOW_REPAIR
    assert {spec.open_boundary_semantics for spec in plane_specs} == STEP131_PLANE_FLUX_CONTROL
    assert all(spec.row_role == "plane_flux_control_candidate_48" for spec in plane_specs)
    assert all(spec.requested_n_steps == 250 for spec in plane_specs)
    assert {spec.open_boundary_semantics for spec in resolve_step121_phase_specs("planeflux48")} == STEP131_PLANE_FLUX_CONTROL

    low_alpha = _controller_spec(open_boundary_flux_filter_alpha=0.02, open_boundary_flux_correction_cap_u=0.002)
    high_alpha = _controller_spec(open_boundary_flux_filter_alpha=0.10, open_boundary_flux_correction_cap_u=0.002)
    high_cap = _controller_spec(open_boundary_flux_filter_alpha=0.02, open_boundary_flux_correction_cap_u=0.006)
    assert solver_state_hash_for_spec(low_alpha) != solver_state_hash_for_spec(high_alpha)
    assert solver_state_hash_for_spec(low_alpha) != solver_state_hash_for_spec(high_cap)


def test_step131_triage_rows_do_not_enable_selected96_even_if_flow_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    plane_triage = _row(
        "duct_only_48_regularized_plane_flux_controlled_pressure_outlet_250step_triage",
        REGULARIZED_PLANE,
        role="plane_flux_control_candidate_48",
        requested_n_steps=250,
        solver_state_hash="step131-triage-hash",
    )
    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [plane_triage])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False
    assert all(item["semantics"] not in STEP131_PLANE_FLUX_CONTROL for item in selection["candidate_summaries"])


def test_step131_manifest_rejects_stale_step130_flowrepair_rows_for_planeflux_phase(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_plane_flux_48_specs,
        write_step121_campaign_manifest,
    )

    out = tmp_path / "campaign"
    specs = step121_plane_flux_48_specs(output_interval=25)
    write_step121_campaign_manifest(out, specs, phase="planeflux48")
    spec = specs[0]
    stale = _row(
        spec.name,
        "regularized_flux_matched_pressure_outlet",
        role="flow_repair_candidate_48",
        requested_n_steps=250,
        solver_state_hash="step130-stale-hash",
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "lbm_open_boundary_semantics_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]
    assert solver_state_hash_for_spec(spec) != stale["solver_state_hash"]


def test_step131_flow_development_diagnostics_include_controller_fields(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = _controller_spec()
    record = {
        "step": 5,
        "inlet_flux": 42.0,
        "outlet_flux": 44.0,
        "midplane_flux": 43.0,
        "mass_total_delta_rel": 0.001,
    }
    stats = {
        "controller_target_outlet_flux": 42.0,
        "controller_measured_outlet_flux": 44.0,
        "controller_raw_flux_error": -2.0,
        "controller_filtered_flux_error": -0.04,
        "controller_u_feedback": -0.0001,
        "controller_u_feedback_abs": 0.0001,
        "controller_saturation_count_step": 0,
        "controller_saturation_count_run": 0,
        "controller_saturation_fraction_run": 0.0,
    }
    diagnostic = _flow_development_diagnostic_record(record, spec, stats)
    _write_flow_development_diagnostics(tmp_path, [diagnostic])

    required = {
        "controller_target_outlet_flux",
        "controller_measured_outlet_flux",
        "controller_raw_flux_error",
        "controller_filtered_flux_error",
        "controller_u_feedback",
        "controller_u_feedback_abs",
        "controller_saturation_fraction_run",
    }
    assert required.issubset(set(FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS))

    with (tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["controller_u_feedback"] == "-0.0001"
    assert rows[0]["controller_raw_flux_error"] == "-2.0"

    summary = json.loads((tmp_path / "flow_development_diagnostics_summary.json").read_text(encoding="utf-8"))
    assert summary["step"] == 131
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_claim_allowed"] is False


def test_step131_tiny_real_controller_smoke_writes_bounded_controller_diagnostics(tmp_path):
    from experiments.steps import step120_lbm_boundary_repair_large_real_execution as step120

    spec = step120.Step120RunSpec(
        name="tiny_step131_plane_flux_controller_smoke",
        nx=8,
        ny=6,
        nz=6,
        n_steps=4,
        output_interval=1,
        failure_check_interval=1,
        checkpoint_every=0,
        open_boundary_semantics=CONVECTIVE_PLANE,
        geometry_mode="duct_only",
        requested_nx=8,
        requested_n_steps=4,
        allow_large_real_run_without_flag=True,
        row_role="plane_flux_control_candidate_48",
        open_boundary_flux_feedback_gain_u=0.0025,
        open_boundary_flux_feedback_gain_rho=0.0,
        open_boundary_flux_filter_alpha=0.02,
        open_boundary_flux_correction_cap_u=0.002,
        open_boundary_convective_blend_weight=0.02,
    )

    row = step120.run_step120_row(spec, tmp_path / spec.name, checkpoint_root=tmp_path / "checkpoints")
    csv_path = tmp_path / spec.name / "flow_development_diagnostics.csv"
    summary_path = tmp_path / spec.name / "flow_development_diagnostics_summary.json"

    assert row["simulation_backed_artifact"] is True
    assert csv_path.is_file()
    assert summary_path.is_file()
    assert csv_path.stat().st_size < 16384

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    feedback_values = [float(item["controller_u_feedback"]) for item in rows if item["controller_u_feedback"]]
    assert feedback_values
    assert all(math.isfinite(value) for value in feedback_values)
    assert max(abs(value) for value in feedback_values) <= spec.open_boundary_flux_correction_cap_u + 1.0e-9

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["validation_claim_allowed"] is False
    assert payload["selected96_claim_allowed"] is False
