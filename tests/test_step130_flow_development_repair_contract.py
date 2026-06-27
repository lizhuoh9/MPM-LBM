import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_FLOW_REPAIR = "regularized_flux_matched_pressure_outlet"
CONVECTIVE_FLOW_REPAIR = "convective_flux_matched_damped_outlet"
STEP130_FLOW_REPAIR = {REGULARIZED_FLOW_REPAIR, CONVECTIVE_FLOW_REPAIR}
STEP129_REPAIR = {
    "regularized_mass_balanced_pressure_outlet",
    "convective_mass_balanced_pressure_outlet",
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
        "open_boundary_flux_feedback_gain_u": 0.01,
        "open_boundary_flux_feedback_gain_rho": 0.005,
        "open_boundary_flux_filter_alpha": 0.05,
        "open_boundary_flux_correction_cap_u": 0.005,
        "open_boundary_convective_blend_weight": 0.05,
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


def test_step130_new_semantics_are_valid_config_values_and_dispatched():
    from src.mpm_lbm.sim.lbm.config import LBMConfig, VALID_LBM_OPEN_BOUNDARY_SEMANTICS

    assert STEP130_FLOW_REPAIR.issubset(set(VALID_LBM_OPEN_BOUNDARY_SEMANTICS))
    cfg = LBMConfig(
        nx=4,
        ny=3,
        nz=3,
        open_boundary_semantics=REGULARIZED_FLOW_REPAIR,
        open_boundary_flux_feedback_gain_u=0.01,
        open_boundary_flux_feedback_gain_rho=0.005,
        open_boundary_flux_filter_alpha=0.05,
        open_boundary_flux_correction_cap_u=0.005,
        open_boundary_convective_blend_weight=0.05,
    )
    assert cfg.open_boundary_semantics == REGULARIZED_FLOW_REPAIR
    assert cfg.open_boundary_flux_correction_cap_u == 0.005

    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    assert "apply_regularized_flux_matched_pressure_outlet_x_open_boundaries" in source
    assert "apply_convective_flux_matched_damped_outlet_x_open_boundaries" in source
    assert REGULARIZED_FLOW_REPAIR in source
    assert CONVECTIVE_FLOW_REPAIR in source


def test_step130_flowrepair_phase_is_separate_from_repair48_and_candidates48():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        CANDIDATE_SEMANTICS,
        FLOW_REPAIR_CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        resolve_step121_phase_specs,
        step121_candidate_48_specs,
        step121_flow_repair_48_specs,
        step121_repair_48_specs,
    )

    assert set(FLOW_REPAIR_CANDIDATE_SEMANTICS) == STEP130_FLOW_REPAIR
    assert set(REPAIRED_CANDIDATE_SEMANTICS) == STEP129_REPAIR
    assert STEP130_FLOW_REPAIR.isdisjoint(set(CANDIDATE_SEMANTICS))

    old_specs = step121_candidate_48_specs(output_interval=25)
    repair_specs = step121_repair_48_specs(output_interval=25)
    flow_specs = step121_flow_repair_48_specs(output_interval=25)

    assert {spec.open_boundary_semantics for spec in old_specs}.isdisjoint(STEP130_FLOW_REPAIR)
    assert {spec.open_boundary_semantics for spec in repair_specs} == STEP129_REPAIR
    assert {spec.open_boundary_semantics for spec in flow_specs} == STEP130_FLOW_REPAIR
    assert all(spec.row_role == "flow_repair_candidate_48" for spec in flow_specs)
    assert all(spec.requested_n_steps == 250 for spec in flow_specs)
    assert {spec.open_boundary_semantics for spec in resolve_step121_phase_specs("flowrepair48")} == STEP130_FLOW_REPAIR


def test_step130_solver_state_hash_includes_flow_repair_gain_and_cap_parameters():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        Step120RunSpec,
        solver_state_hash_for_spec,
    )

    base = {
        "name": "hash_row",
        "nx": 5,
        "ny": 4,
        "nz": 4,
        "n_steps": 3,
        "output_interval": 1,
        "failure_check_interval": 1,
        "geometry_mode": "duct_only",
        "requested_nx": 5,
        "requested_n_steps": 3,
        "allow_large_real_run_without_flag": True,
        "row_role": "flow_repair_candidate_48",
        "open_boundary_semantics": REGULARIZED_FLOW_REPAIR,
    }
    low_gain = Step120RunSpec(**base, open_boundary_flux_feedback_gain_u=0.005, open_boundary_flux_correction_cap_u=0.002)
    high_gain = Step120RunSpec(**base, open_boundary_flux_feedback_gain_u=0.02, open_boundary_flux_correction_cap_u=0.01)
    step129 = Step120RunSpec(
        **{**base, "open_boundary_semantics": "regularized_mass_balanced_pressure_outlet", "row_role": "repair_candidate_48"}
    )

    assert solver_state_hash_for_spec(low_gain) != solver_state_hash_for_spec(high_gain)
    assert solver_state_hash_for_spec(low_gain) != solver_state_hash_for_spec(step129)


def test_step130_triage_rows_do_not_enable_selected96_even_if_flow_metrics_are_good():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    flow_triage = _row(
        "duct_only_48_regularized_flux_matched_pressure_outlet_250step_triage",
        REGULARIZED_FLOW_REPAIR,
        role="flow_repair_candidate_48",
        requested_n_steps=250,
        solver_state_hash="step130-triage-hash",
    )
    selection = select_step121_best_boundary(_references() + _failed_step127_candidates() + [flow_triage])

    assert selection["best_boundary_selected"] is False
    assert selection["campaign_state"] == "48_candidates_failed"
    assert selection["validation_claim_allowed"] is False
    assert all(item["semantics"] not in STEP130_FLOW_REPAIR for item in selection["candidate_summaries"])


def test_step130_manifest_rejects_stale_step129_repaired_rows_for_flowrepair_phase(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import solver_state_hash_for_spec
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_flow_repair_48_specs,
        write_step121_campaign_manifest,
    )

    out = tmp_path / "campaign"
    specs = step121_flow_repair_48_specs(output_interval=25)
    write_step121_campaign_manifest(out, specs, phase="flowrepair48")
    spec = specs[0]
    stale = _row(
        spec.name,
        "regularized_mass_balanced_pressure_outlet",
        role="repair_candidate_48",
        requested_n_steps=250,
        solver_state_hash="step129-stale-hash",
    )
    _write_json(out / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(out, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "lbm_open_boundary_semantics_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]
    assert solver_state_hash_for_spec(spec) != stale["solver_state_hash"]
