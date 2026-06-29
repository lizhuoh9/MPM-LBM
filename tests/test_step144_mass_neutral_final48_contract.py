import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
STEP143_DECISION = ROOT / "outputs" / "step143_mass_neutral_design_diagnostic" / "step143_decision_summary.json"
STEP143_COMPARISON = ROOT / "outputs" / "step143_mass_neutral_design_diagnostic" / "step143_mass_neutral_comparison.json"
STEP144_PHASE = "planeflux_mass_neutral_final48"
STEP144_ROLE = "mass_neutral_final_evidence_candidate_48"
STEP144_OUTPUT_ROOT = ROOT / "outputs" / "step144_mass_neutral_final48"
STEP144_PHASE_ROOT = STEP144_OUTPUT_ROOT / "mass_neutral_final48"
STEP144_GOAL = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "144" / "goal.md"
STEP144_REPORT = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "144" / "report.md"
STEP144_ROW_NAME = (
    "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010"
    "_mnhigh_mgain0p50_mcap0p001_blend1p00_out10_500step_mass_neutral_final"
)


def test_step144_phase_resolves_exact_single_final48_probe():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
        SELECTED_CHAIN_ROLES,
        resolve_step121_phase_specs,
        step121_mass_neutral_final_48_specs,
    )

    specs = step121_mass_neutral_final_48_specs(output_interval=10)

    assert resolve_step121_phase_specs(STEP144_PHASE, output_interval=10) == specs
    assert len(specs) == 1

    spec = specs[0]
    assert spec.name == STEP144_ROW_NAME
    assert spec.row_role == STEP144_ROLE
    assert STEP144_ROLE not in SELECTED_CHAIN_ROLES
    assert REGULARIZED_PLANE not in CANDIDATE_SEMANTICS
    assert REGULARIZED_PLANE not in REPAIRED_CANDIDATE_SEMANTICS

    assert (spec.nx, spec.ny, spec.nz) == (48, 48, 48)
    assert spec.requested_nx == 48
    assert spec.n_steps == 500
    assert spec.requested_n_steps == 500
    assert spec.output_interval == 10
    assert spec.geometry_mode == "duct_only"
    assert spec.open_boundary_semantics == REGULARIZED_PLANE
    assert spec.allow_large_real_run_without_flag is True
    assert spec.not_used_for_validation is True
    assert "Step144" in spec.artifact_scope_note
    assert "selected96" in spec.artifact_scope_note

    assert round(float(spec.open_boundary_inlet_ramp_steps), 8) == 85
    assert round(float(spec.open_boundary_flux_control_target_scale), 8) == 0.80
    assert round(float(spec.open_boundary_flux_feedback_gain_u), 8) == 0.75
    assert round(float(spec.open_boundary_flux_correction_cap_u), 8) == 0.0075
    assert round(float(spec.open_boundary_flux_feedback_gain_rho), 8) == 0.001
    assert round(float(spec.open_boundary_flux_filter_alpha), 8) == 0.02
    assert round(float(spec.open_boundary_flux_feedback_delta_cap_u), 8) == 0.0005
    assert round(float(spec.open_boundary_flux_feedback_slew_alpha), 8) == 0.50
    assert int(spec.open_boundary_flux_control_measure_plane_offset) == 2
    assert spec.open_boundary_outlet_flux_drop_guard_enabled is True
    assert round(float(spec.open_boundary_outlet_flux_drop_guard_min_ratio), 8) == 0.70
    assert round(float(spec.niu), 8) == 0.10

    assert spec.open_boundary_mass_neutral_flux_control_enabled is True
    assert spec.open_boundary_mass_neutral_flux_control_mode == "global_mass_error_density_offset"
    assert round(float(spec.open_boundary_mass_neutral_mass_error_gain), 8) == 0.50
    assert round(float(spec.open_boundary_mass_neutral_mass_error_cap), 8) == 0.00100
    assert round(float(spec.open_boundary_mass_neutral_correction_blend), 8) == 1.0
    assert spec.open_boundary_mass_neutral_reference_mass_mode == "initial"


def test_step144_provenance_matches_step143_best_artifacts():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        mass_neutral_activation_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_mass_neutral_final_48_specs,
    )

    decision = _read_json(STEP143_DECISION)
    comparison = _read_json(STEP143_COMPARISON)
    best = _step143_best_row(decision, comparison)
    spec = step121_mass_neutral_final_48_specs(output_interval=10)[0]

    assert spec.source_step == 143
    assert spec.source_step143_decision_hash == _sha256(STEP143_DECISION)
    assert spec.source_step143_comparison_hash == _sha256(STEP143_COMPARISON)
    assert spec.source_step143_best_row_name == decision["best_row_name"] == best["name"]
    assert spec.source_step143_best_row_solver_state_hash == best["solver_state_hash"]
    assert spec.source_step143_best_row_run_manifest_hash == best["run_manifest_hash"]
    assert spec.source_step143_best_row_mass_neutral_activation_hash == best["mass_neutral_activation_hash"]
    assert spec.source_step143_decision_case == "mass_neutral_design_supports_step144_single_500step_probe"
    assert mass_neutral_activation_hash_for_spec(spec) == best["mass_neutral_activation_hash"]


def test_step144_manifest_records_and_rejects_step143_provenance_mismatch(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        mass_neutral_activation_hash_for_spec,
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_mass_neutral_final_48_specs,
        write_step121_campaign_manifest,
    )

    spec = step121_mass_neutral_final_48_specs(output_interval=10)[0]
    manifest = write_step121_campaign_manifest(tmp_path, [spec], phase=STEP144_PHASE)
    expected = manifest["expected_rows"][spec.name]

    assert manifest["phase_history"][-1] == STEP144_PHASE
    assert expected["source_step143_decision_hash"] == spec.source_step143_decision_hash
    assert expected["source_step143_comparison_hash"] == spec.source_step143_comparison_hash
    assert expected["source_step143_best_row_name"] == spec.source_step143_best_row_name
    assert expected["source_step143_best_row_mass_neutral_activation_hash"] == (
        spec.source_step143_best_row_mass_neutral_activation_hash
    )
    assert expected["mass_neutral_activation_hash"] == mass_neutral_activation_hash_for_spec(spec)

    stale = _good_step144_row(name=spec.name)
    stale.update(expected)
    stale["solver_state_hash"] = solver_state_hash_for_spec(spec)
    stale["run_manifest_hash"] = run_manifest_hash_for_spec(spec)
    stale["source_step143_decision_hash"] = "wrong-step143-decision-hash"
    _write_json(tmp_path / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(tmp_path, return_ignored=True)

    assert collected["rows"] == []
    assert "source_step143_decision_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]

    stale.update(expected)
    stale["solver_state_hash"] = solver_state_hash_for_spec(spec)
    stale["run_manifest_hash"] = run_manifest_hash_for_spec(spec)
    stale["mass_neutral_activation_hash"] = "wrong-activation-hash"
    _write_json(tmp_path / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(tmp_path, return_ignored=True)

    assert collected["rows"] == []
    assert "mass_neutral_activation_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]


def test_step144_rows_cannot_enable_selected_boundary_even_if_mock_final_gates_pass():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    row = _good_step144_row()
    selection = select_step121_best_boundary([row])

    assert selection["best_boundary_selected"] is False
    assert selection["validation_claim_allowed"] is False
    assert row["selected96_claim_allowed"] is False
    assert row["validation_claim_allowed"] is False


def test_step144_audit_decisions_and_missing_inputs(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step144_mass_neutral_final48_audit import run_step144_mass_neutral_final48_audit

    missing = run_step144_mass_neutral_final48_audit(
        phase_root=tmp_path / "missing_phase",
        step143_decision=tmp_path / "missing_decision.json",
        step143_comparison=tmp_path / "missing_comparison.json",
        output_dir=tmp_path / "missing_out",
        force=True,
    )
    assert missing["status"] == "missing_input"
    assert missing["decision_case"] == "missing_input"
    assert missing["step145_selected_candidate_surface_review_proposal_allowed"] is False
    assert missing["selected96_execution_allowed"] is False

    pass_phase = tmp_path / "pass_phase"
    _write_json(pass_phase / STEP144_ROW_NAME / "finite_stability_report.json", {"summary_row": _good_step144_row()})
    passed = run_step144_mass_neutral_final48_audit(
        phase_root=pass_phase,
        step143_decision=STEP143_DECISION,
        step143_comparison=STEP143_COMPARISON,
        output_dir=tmp_path / "pass_out",
        force=True,
    )
    assert passed["status"] == "decision_ready"
    assert passed["decision_case"] == "mass_neutral_final48_probe_passed"
    assert passed["step145_selected_candidate_surface_review_proposal_allowed"] is True
    assert passed["selected96_execution_allowed"] is False
    assert passed["validation_claim_allowed"] is False

    mass_fail_phase = tmp_path / "mass_fail_phase"
    _write_json(
        mass_fail_phase / STEP144_ROW_NAME / "finite_stability_report.json",
        {"summary_row": _good_step144_row(candidate_mass_acceptance_observed_abs=0.007, candidate_mass_acceptance_gate_pass=False)},
    )
    mass_failed = run_step144_mass_neutral_final48_audit(
        phase_root=mass_fail_phase,
        step143_decision=STEP143_DECISION,
        step143_comparison=STEP143_COMPARISON,
        output_dir=tmp_path / "mass_fail_out",
        force=True,
    )
    assert mass_failed["decision_case"] == "mass_neutral_mass_long_window_failure"
    assert mass_failed["step145_selected_candidate_surface_review_proposal_allowed"] is False
    assert (tmp_path / "pass_out" / "step144_long_window_comparison.json").is_file()
    assert (tmp_path / "pass_out" / "step144_long_window_comparison.csv").is_file()
    assert (tmp_path / "pass_out" / "step144_decision_summary.json").is_file()


def test_committed_step144_outputs_and_docs_remain_bounded_after_real_phase_and_audit():
    decision_path = STEP144_OUTPUT_ROOT / "step144_decision_summary.json"
    comparison_path = STEP144_OUTPUT_ROOT / "step144_long_window_comparison.json"
    csv_path = STEP144_OUTPUT_ROOT / "step144_long_window_comparison.csv"

    assert STEP144_GOAL.is_file()
    assert STEP144_REPORT.is_file()
    assert decision_path.is_file()
    assert comparison_path.is_file()
    assert csv_path.is_file()

    decision = _read_json(decision_path)
    comparison = _read_json(comparison_path)
    current_status = (ROOT / "docs" / "current" / "STATUS.md").read_text(encoding="utf-8")
    current_gates = (ROOT / "docs" / "current" / "VALIDATION_GATES.md").read_text(encoding="utf-8")
    report = STEP144_REPORT.read_text(encoding="utf-8")

    assert decision["step"] == 144
    assert comparison["step"] == 144
    assert decision["row_count"] == 1
    assert comparison["row_count"] == 1
    assert decision["source_step143_decision_hash"] == _sha256(STEP143_DECISION)
    assert decision["source_step143_comparison_hash"] == _sha256(STEP143_COMPARISON)
    assert comparison["rows"][0]["row_role"] == STEP144_ROLE
    assert comparison["rows"][0]["requested_nx"] == 48
    assert comparison["rows"][0]["requested_n_steps"] == 500
    assert comparison["rows"][0]["steps_completed"] == 500

    for payload in [decision, comparison]:
        assert payload["selected96_execution_allowed"] is False
        assert payload["selected_static_execution_allowed"] is False
        assert payload["validation_claim_allowed"] is False
        assert payload["fluent_validation_claim_allowed"] is False
        assert payload["fsi_validation_claim_allowed"] is False
        assert payload["production_readiness_claim_allowed"] is False

    required_text = [
        "Step144 did not run selected96",
        "Step144 did not run selected-static",
        "Step144 did not run 96^3",
        "Step144 ran exactly one 48^3 / 500-step LBM-only row",
        "Step144 did not run Fluent",
        "Step144 did not run FSI",
        "Step144 does not make a validation claim",
        "Step144 keeps selected96 blocked",
    ]
    for text in [STEP144_GOAL.read_text(encoding="utf-8"), report, current_status, current_gates]:
        for needle in required_text:
            assert needle in text

    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8", newline="")))
    assert len(rows) == 1
    assert rows[0]["name"] == STEP144_ROW_NAME


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _step143_best_row(decision, comparison):
    for row in comparison["rows"]:
        if row["name"] == decision["best_row_name"]:
            return row
    raise AssertionError(f"missing Step143 best row: {decision['best_row_name']}")


def _good_step144_row(**overrides):
    decision = _read_json(STEP143_DECISION)
    comparison = _read_json(STEP143_COMPARISON)
    best = _step143_best_row(decision, comparison)
    row = {
        "name": STEP144_ROW_NAME,
        "row_role": STEP144_ROLE,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": REGULARIZED_PLANE,
        "requested_nx": 48,
        "executed_nx": 48,
        "requested_n_steps": 500,
        "steps_completed": 500,
        "requested_window_completed": True,
        "step120_validation_claimed": False,
        "simulation_backed_artifact": True,
        "not_used_for_validation": True,
        "finite_pass": True,
        "density_gate_pass": True,
        "mass_drift_gate_pass": True,
        "population_gate_pass": True,
        "mach_gate_pass": True,
        "first_failure_step": None,
        "first_failure_reason": None,
        "stop_reason": None,
        "flux_balance_reported": True,
        "inlet_flux_tail_mean": 42.0,
        "outlet_flux_tail_mean": 41.0,
        "outlet_to_inlet_flux_ratio_tail_mean": 0.976,
        "midplane_to_inlet_flux_ratio_tail_mean": 0.990,
        "flux_imbalance_rel_tail_mean": 0.04,
        "flux_imbalance_rel_tail_max": 0.08,
        "outlet_flux_tail_cv": 0.04,
        "flow_development_gate_pass": True,
        "candidate_mass_acceptance_observed_abs": 0.003,
        "candidate_mass_acceptance_gate_pass": True,
        "collapse_first_x": None,
        "collapse_first_step": None,
        "limiter_activation_fraction": 0.0,
        "controller_authority_ratio_tail_mean": 0.4,
        "controller_saturation_fraction_tail": 0.0,
        "drop_guard_activation_fraction_tail": 0.0,
        "controller_drop_guard_activation_fraction_tail": 0.0,
        "density_feedback_tail_mean": -0.0001,
        "mass_neutral_rho_feedback_tail_mean": -0.001,
        "mass_neutral_rho_feedback_abs_tail_mean": 0.001,
        "mass_neutral_mass_error_tail_mean": 0.0025,
        "mass_neutral_mass_error_final": 0.002,
        "mass_neutral_feedback_saturation_fraction_tail": 0.25,
        "selected96_claim_allowed": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_mass_neutral_flux_control_enabled": True,
        "open_boundary_mass_neutral_flux_control_mode": "global_mass_error_density_offset",
        "open_boundary_mass_neutral_mass_error_gain": 0.50,
        "open_boundary_mass_neutral_mass_error_cap": 0.00100,
        "open_boundary_mass_neutral_correction_blend": 1.0,
        "open_boundary_mass_neutral_reference_mass_mode": "initial",
        "mass_neutral_activation_hash": best["mass_neutral_activation_hash"],
        "source_step": 143,
        "source_step143_decision_hash": _sha256(STEP143_DECISION),
        "source_step143_comparison_hash": _sha256(STEP143_COMPARISON),
        "source_step143_best_row_name": best["name"],
        "source_step143_best_row_solver_state_hash": best["solver_state_hash"],
        "source_step143_best_row_run_manifest_hash": best["run_manifest_hash"],
        "source_step143_best_row_mass_neutral_activation_hash": best["mass_neutral_activation_hash"],
        "source_step143_decision_case": decision["decision_case"],
        "solver_state_hash": "step144-solver-hash",
        "run_manifest_hash": "step144-run-hash",
        "runtime_s": 12.0,
    }
    row.update(overrides)
    return row

