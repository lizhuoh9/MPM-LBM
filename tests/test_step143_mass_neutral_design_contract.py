import csv
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
STEP141_PHASE = "planeflux_density_feedback_isolation48"
STEP141_ROLE = "density_feedback_isolation_diagnostic_48"
STEP142_SUMMARY = ROOT / "outputs" / "step142_mass_neutral_plane_flux_design" / "step142_design_readiness_report.json"
STEP142_GOAL = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "142" / "goal.md"
STEP143_PHASE = "planeflux_mass_neutral_design48"
STEP143_ROLE = "mass_neutral_design_diagnostic_48"
STEP143_OUTPUT_ROOT = ROOT / "outputs" / "step143_mass_neutral_design_diagnostic"
STEP143_PHASE_ROOT = STEP143_OUTPUT_ROOT / "mass_neutral_design48"
STEP143_GOAL = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "143" / "goal.md"
STEP143_REPORT = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "143" / "report.md"

MASS_NEUTRAL_FIELDS = [
    "open_boundary_mass_neutral_flux_control_enabled",
    "open_boundary_mass_neutral_flux_control_mode",
    "open_boundary_mass_neutral_mass_error_gain",
    "open_boundary_mass_neutral_mass_error_cap",
    "open_boundary_mass_neutral_correction_blend",
    "open_boundary_mass_neutral_reference_mass_mode",
]

MASS_NEUTRAL_TELEMETRY_FIELDS = [
    "mass_neutral_runtime_behavior_active",
    "mass_neutral_mass_current",
    "mass_neutral_mass_initial_reference",
    "mass_neutral_mass_error",
    "mass_neutral_rho_feedback",
    "mass_neutral_rho_feedback_abs",
    "mass_neutral_feedback_saturation_count_step",
    "mass_neutral_feedback_saturation_count_run",
    "mass_neutral_feedback_update_count_step",
    "mass_neutral_feedback_update_count_run",
    "mass_neutral_feedback_saturation_fraction_run",
    "mass_neutral_activation_hash",
]


def test_step142_goal_drift_is_reconciled_before_step143_runtime_activation():
    text = STEP142_GOAL.read_text(encoding="utf-8")

    assert "runtime_initial" not in text
    assert "step142_design_readiness_report.json" in text
    assert "step142_design_readiness_report.md" in text
    assert "outputs/step142_mass_neutral_plane_flux_design/design_readiness_report.json" not in text
    assert "outputs/step142_mass_neutral_plane_flux_design/design_readiness_report.md" not in text


def test_step143_phase_resolves_exact_four_bounded_diagnostic_rows():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
        SELECTED_CHAIN_ROLES,
        resolve_step121_phase_specs,
        step121_mass_neutral_design_48_specs,
    )

    specs = step121_mass_neutral_design_48_specs(output_interval=5)

    assert resolve_step121_phase_specs(STEP143_PHASE, output_interval=5) == specs
    assert len(specs) == 4
    assert all(spec.row_role == STEP143_ROLE for spec in specs)
    assert STEP143_ROLE not in SELECTED_CHAIN_ROLES
    assert REGULARIZED_PLANE not in CANDIDATE_SEMANTICS
    assert REGULARIZED_PLANE not in REPAIRED_CANDIDATE_SEMANTICS

    assert all((spec.nx, spec.ny, spec.nz) == (48, 48, 48) for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all(spec.n_steps == 250 and spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.output_interval == 5 for spec in specs)
    assert all(spec.geometry_mode == "duct_only" for spec in specs)
    assert all(spec.allow_large_real_run_without_flag is True for spec in specs)
    assert all(spec.open_boundary_semantics == REGULARIZED_PLANE for spec in specs)
    assert all("Step143" in spec.artifact_scope_note for spec in specs)
    assert all("selected96" in spec.artifact_scope_note for spec in specs)
    assert all("500-step" in spec.artifact_scope_note for spec in specs)

    common = {
        (
            round(float(spec.open_boundary_flux_feedback_gain_u), 8),
            round(float(spec.open_boundary_flux_correction_cap_u), 8),
            round(float(spec.open_boundary_flux_feedback_gain_rho), 8),
            round(float(spec.open_boundary_flux_filter_alpha), 8),
            round(float(spec.open_boundary_flux_feedback_delta_cap_u), 8),
            round(float(spec.open_boundary_flux_feedback_slew_alpha), 8),
            int(spec.open_boundary_flux_control_measure_plane_offset),
            round(float(spec.open_boundary_flux_control_target_scale), 8),
            int(spec.open_boundary_inlet_ramp_steps),
            bool(spec.open_boundary_outlet_flux_drop_guard_enabled),
            round(float(spec.open_boundary_outlet_flux_drop_guard_min_ratio), 8),
            round(float(spec.niu), 8),
        )
        for spec in specs
    }
    assert common == {(0.75, 0.0075, 0.001, 0.02, 0.0005, 0.5, 2, 0.8, 85, True, 0.7, 0.1)}

    disabled = specs[0]
    enabled = specs[1:]
    assert disabled.open_boundary_mass_neutral_flux_control_enabled is False
    assert disabled.open_boundary_mass_neutral_flux_control_mode == "disabled"
    assert disabled.open_boundary_mass_neutral_mass_error_gain == 0.0
    assert disabled.open_boundary_mass_neutral_mass_error_cap == 0.0
    assert disabled.open_boundary_mass_neutral_correction_blend == 0.0

    assert all(spec.open_boundary_mass_neutral_flux_control_enabled is True for spec in enabled)
    assert all(spec.open_boundary_mass_neutral_flux_control_mode == "global_mass_error_density_offset" for spec in enabled)
    assert [round(spec.open_boundary_mass_neutral_mass_error_gain, 8) for spec in enabled] == [0.10, 0.25, 0.50]
    assert [round(spec.open_boundary_mass_neutral_mass_error_cap, 8) for spec in enabled] == [0.00025, 0.00050, 0.00100]
    assert all(spec.open_boundary_mass_neutral_correction_blend == 1.0 for spec in enabled)
    assert all(spec.open_boundary_mass_neutral_reference_mass_mode == "initial" for spec in specs)


def test_step143_enabled_rows_only_vary_mass_neutral_activation_identity():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        MASS_NEUTRAL_ACTIVATION_FIELDS,
        mass_neutral_activation_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_mass_neutral_design_48_specs,
    )

    specs = step121_mass_neutral_design_48_specs(output_interval=5)
    enabled = specs[1:]
    baseline = _spec_identity_without(enabled[0], MASS_NEUTRAL_FIELDS + ["name", "artifact_scope_note"])

    assert MASS_NEUTRAL_ACTIVATION_FIELDS == tuple(MASS_NEUTRAL_FIELDS)
    assert all(_spec_identity_without(spec, MASS_NEUTRAL_FIELDS + ["name", "artifact_scope_note"]) == baseline for spec in enabled)
    assert len({mass_neutral_activation_hash_for_spec(spec) for spec in specs}) == 4
    assert all(len(mass_neutral_activation_hash_for_spec(spec)) == 64 for spec in specs)


def test_step143_disabled_row_matches_step141_baseline_except_step143_identity():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_density_feedback_isolation_48_specs,
        step121_mass_neutral_design_48_specs,
    )

    step141 = next(
        spec
        for spec in step121_density_feedback_isolation_48_specs(output_interval=5)
        if abs(float(spec.open_boundary_flux_feedback_gain_rho) - 0.001) < 1.0e-12
    )
    disabled = step121_mass_neutral_design_48_specs(output_interval=5)[0]

    shared_fields = [
        "open_boundary_semantics",
        "geometry_mode",
        "nx",
        "ny",
        "nz",
        "n_steps",
        "requested_nx",
        "requested_n_steps",
        "output_interval",
        "open_boundary_inlet_ramp_steps",
        "open_boundary_flux_control_target_scale",
        "open_boundary_flux_feedback_gain_u",
        "open_boundary_flux_correction_cap_u",
        "open_boundary_flux_feedback_gain_rho",
        "open_boundary_flux_filter_alpha",
        "open_boundary_flux_feedback_delta_cap_u",
        "open_boundary_flux_feedback_slew_alpha",
        "open_boundary_flux_control_measure_plane_offset",
        "open_boundary_outlet_flux_drop_guard_enabled",
        "open_boundary_outlet_flux_drop_guard_min_ratio",
        "niu",
    ]
    for field in shared_fields:
        assert getattr(disabled, field) == getattr(step141, field)

    assert disabled.name != step141.name
    assert disabled.row_role == STEP143_ROLE
    assert step141.row_role == STEP141_ROLE
    assert disabled.source_step == 142
    assert disabled.source_step142_readiness_hash == _sha256(STEP142_SUMMARY)


def test_step143_manifest_records_and_rejects_activation_hash_mismatch(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        mass_neutral_activation_hash_for_spec,
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_mass_neutral_design_48_specs,
        write_step121_campaign_manifest,
    )

    specs = step121_mass_neutral_design_48_specs(output_interval=5)
    manifest = write_step121_campaign_manifest(tmp_path, specs, phase=STEP143_PHASE)
    spec = specs[1]
    expected = manifest["expected_rows"][spec.name]

    assert manifest["phase_history"][-1] == STEP143_PHASE
    for field in MASS_NEUTRAL_FIELDS:
        assert expected[field] == getattr(spec, field)
    assert expected["mass_neutral_activation_hash"] == mass_neutral_activation_hash_for_spec(spec)

    stale = _good_step143_row(name=spec.name)
    stale.update(expected)
    stale["solver_state_hash"] = solver_state_hash_for_spec(spec)
    stale["run_manifest_hash"] = run_manifest_hash_for_spec(spec)
    stale["mass_neutral_activation_hash"] = "wrong-activation-hash"
    _write_json(tmp_path / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(tmp_path, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "mass_neutral_activation_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]


def test_step143_summary_metadata_boundary_and_flow_diagnostics_expose_runtime_telemetry(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _boundary_report,
        _flow_development_diagnostic_record,
        _metadata,
        _summary_row,
        _tau_feasibility_report,
        _write_flow_development_diagnostics,
        mass_neutral_activation_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_mass_neutral_design_48_specs,
    )

    spec = step121_mass_neutral_design_48_specs(output_interval=5)[1]
    activation_hash = mass_neutral_activation_hash_for_spec(spec)
    limiter_stats = _mass_neutral_stats(activation_hash)
    tau_report = _tau_feasibility_report(spec)

    summary = _summary_row(
        spec,
        steps_completed=250,
        requested_window_completed=True,
        finite_pass=True,
        density_gate_pass=True,
        mass_drift_gate_pass=True,
        population_gate_pass=True,
        mach_gate_pass=True,
        first_failure_step=None,
        first_failure_reason=None,
        flux_imbalance_rel_final=0.02,
        flux_imbalance_rel_tail_mean=0.02,
        flux_imbalance_rel_tail_max=0.04,
        inlet_flux_tail_mean=42.0,
        outlet_flux_tail_mean=41.0,
        outlet_flux_tail_cv=0.05,
        outlet_to_inlet_flux_ratio_tail_mean=0.976,
        midplane_to_inlet_flux_ratio_tail_mean=0.990,
        flow_development_gate_pass=True,
        mass_total_delta_rel_final=0.001,
        mach_proxy_observed_max=0.05,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=False,
        stop_reason=None,
        row_source="unit_test",
        step120_validation_claimed=False,
        runtime_s=0.0,
        limiter_summary=limiter_stats,
        simulation_backed_artifact=True,
        flux_balance_reported=True,
        checkpoint_available=False,
        hard_stop_fields={},
        candidate_mass_fields={"candidate_mass_acceptance_observed_abs": 0.001},
    )
    metadata = _metadata(spec, tau_report, skipped=False, runtime_s=0.0, stop_reason=None, restored_checkpoint=None)
    boundary = _boundary_report(spec)

    for payload in [summary, metadata, boundary]:
        assert payload["mass_neutral_activation_hash"] == activation_hash
        for field in MASS_NEUTRAL_FIELDS:
            assert payload[field] == getattr(spec, field)

    assert summary["mass_neutral_runtime_behavior_active"] is True
    assert summary["mass_neutral_mass_error"] == -0.0025
    assert summary["mass_neutral_rho_feedback"] == 0.00025
    assert metadata["source_step142_readiness_hash"] == _sha256(STEP142_SUMMARY)
    assert boundary["mass_neutral_runtime_behavior_active"] is True

    record = _flow_development_diagnostic_record(
        {
            "step": 250,
            "inlet_flux": 42.0,
            "outlet_flux": 41.0,
            "midplane_flux": 41.6,
            "mass_total_delta_rel": 0.001,
            "sampled_x_profile_flux": json.dumps({"24": 41.6, "36": 41.3, "47": 41.0}, sort_keys=True),
        },
        spec,
        limiter_stats,
    )
    for field in MASS_NEUTRAL_TELEMETRY_FIELDS:
        assert field in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
        assert field in record
    assert record["step143_mass_neutral_design_candidate"] is True
    assert record["selected96_claim_allowed"] is False
    assert record["validation_claim_allowed"] is False

    _write_flow_development_diagnostics(tmp_path, [record])

    rows = list(csv.DictReader((tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="")))
    assert rows[-1]["step143_mass_neutral_design_candidate"] == "True"
    diagnostic_summary = _read_json(tmp_path / "flow_development_diagnostics_summary.json")
    assert diagnostic_summary["step"] == 143
    assert diagnostic_summary["final"]["mass_neutral_activation_hash"] == activation_hash
    assert diagnostic_summary["mass_neutral_rho_feedback_tail_mean"] == 0.00025
    assert diagnostic_summary["mass_neutral_mass_error_tail_mean"] == -0.0025
    assert diagnostic_summary["selected96_claim_allowed"] is False


def test_step143_rows_cannot_enable_selected_boundary_even_if_mock_metrics_pass():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    row = _good_step143_row()
    selection = select_step121_best_boundary([row])

    assert selection["best_boundary_selected"] is False
    assert selection["validation_claim_allowed"] is False
    assert row["selected96_claim_allowed"] is False
    assert row["validation_claim_allowed"] is False


def test_step143_audit_blocks_or_allows_step144_only_from_mass_flow_cv_improvement(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step143_mass_neutral_design_audit import run_step143_mass_neutral_design_audit

    blocked_phase = tmp_path / "blocked_phase"
    _write_json(
        blocked_phase / "disabled" / "finite_stability_report.json",
        {"summary_row": _good_step143_row(name="disabled", enabled=False, mass=0.006, outlet_cv=0.08, flux_mean=0.06)},
    )
    _write_json(
        blocked_phase / "enabled_no_gain" / "finite_stability_report.json",
        {"summary_row": _good_step143_row(name="enabled_no_gain", enabled=True, gain=0.25, mass=0.007, outlet_cv=0.07, flux_mean=0.06)},
    )

    blocked = run_step143_mass_neutral_design_audit(blocked_phase, STEP142_SUMMARY, tmp_path / "blocked_audit", force=True)

    assert blocked["status"] == "decision_ready"
    assert blocked["decision_case"] == "mass_neutral_design_insufficient"
    assert blocked["step144_single_500step_probe_proposal_allowed"] is False
    assert blocked["selected96_execution_allowed"] is False
    assert blocked["validation_claim_allowed"] is False

    allowed_phase = tmp_path / "allowed_phase"
    _write_json(
        allowed_phase / "disabled" / "finite_stability_report.json",
        {"summary_row": _good_step143_row(name="disabled", enabled=False, mass=0.006, outlet_cv=0.09, flux_mean=0.07)},
    )
    _write_json(
        allowed_phase / "enabled_mid" / "finite_stability_report.json",
        {"summary_row": _good_step143_row(name="enabled_mid", enabled=True, gain=0.25, mass=0.002, outlet_cv=0.04, flux_mean=0.04)},
    )

    allowed = run_step143_mass_neutral_design_audit(allowed_phase, STEP142_SUMMARY, tmp_path / "allowed_audit", force=True)

    assert allowed["decision_case"] == "mass_neutral_design_supports_step144_single_500step_probe"
    assert allowed["step144_single_500step_probe_proposal_allowed"] is True
    assert allowed["step144_selected96_execution_allowed"] is False
    assert (tmp_path / "allowed_audit" / "step143_mass_neutral_comparison.json").is_file()
    assert (tmp_path / "allowed_audit" / "step143_mass_neutral_comparison.csv").is_file()
    assert (tmp_path / "allowed_audit" / "step143_decision_summary.json").is_file()


def test_committed_step143_outputs_and_docs_remain_bounded_after_real_phase_and_audit():
    decision_path = STEP143_OUTPUT_ROOT / "step143_decision_summary.json"
    comparison_path = STEP143_OUTPUT_ROOT / "step143_mass_neutral_comparison.json"
    csv_path = STEP143_OUTPUT_ROOT / "step143_mass_neutral_comparison.csv"

    assert STEP143_GOAL.is_file()
    assert STEP143_REPORT.is_file()
    assert decision_path.is_file()
    assert comparison_path.is_file()
    assert csv_path.is_file()

    decision = _read_json(decision_path)
    comparison = _read_json(comparison_path)
    report = STEP143_REPORT.read_text(encoding="utf-8")
    current_status = (ROOT / "docs" / "current" / "STATUS.md").read_text(encoding="utf-8")
    current_gates = (ROOT / "docs" / "current" / "VALIDATION_GATES.md").read_text(encoding="utf-8")

    assert decision["step"] == 143
    assert comparison["step"] == 143
    assert decision["row_count"] == 4
    assert comparison["row_count"] == 4
    assert {row["row_role"] for row in comparison["rows"]} == {STEP143_ROLE}
    assert all(row["requested_nx"] == 48 and row["requested_n_steps"] == 250 for row in comparison["rows"])

    for payload in [decision, comparison]:
        assert payload["selected96_execution_allowed"] is False
        assert payload["selected_static_execution_allowed"] is False
        assert payload["validation_claim_allowed"] is False
        assert payload["fluent_validation_claim_allowed"] is False
        assert payload["fsi_validation_claim_allowed"] is False
        assert payload["production_readiness_claim_allowed"] is False

    for text in [STEP143_GOAL.read_text(encoding="utf-8"), report, current_status, current_gates]:
        assert "Step143 did not run selected96" in text
        assert "Step143 did not run selected-static" in text
        assert "Step143 did not run 96^3" in text
        assert "Step143 did not run a 500-step row" in text
        assert "Step143 did not run Fluent" in text
        assert "Step143 did not run FSI" in text
        assert "Step143 does not make a validation claim" in text


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _spec_identity_without(spec, excluded):
    excluded = set(excluded)
    return {key: value for key, value in asdict(spec).items() if key not in excluded}


def _mass_neutral_stats(activation_hash: str):
    return {
        "mass_neutral_runtime_behavior_active": True,
        "mass_neutral_mass_current": 119.7,
        "mass_neutral_mass_initial_reference": 120.0,
        "mass_neutral_mass_error": -0.0025,
        "mass_neutral_rho_feedback": 0.00025,
        "mass_neutral_rho_feedback_abs": 0.00025,
        "mass_neutral_feedback_saturation_count_step": 1,
        "mass_neutral_feedback_saturation_count_run": 2,
        "mass_neutral_feedback_update_count_step": 1,
        "mass_neutral_feedback_update_count_run": 10,
        "mass_neutral_feedback_saturation_fraction_run": 0.2,
        "mass_neutral_activation_hash": activation_hash,
        "controller_target_outlet_flux": 33.6,
        "controller_measured_outlet_flux": 41.0,
        "controller_raw_flux_error": -7.4,
        "controller_filtered_flux_error": -3.2,
        "controller_u_feedback": -0.002,
        "controller_density_feedback": -0.0001,
        "controller_saturation_count_run": 0,
        "controller_saturation_fraction_run": 0.0,
        "controller_drop_guard_activation_count_run": 0,
    }


def _good_step143_row(**overrides):
    row = {
        "name": "step143-good-row",
        "row_role": STEP143_ROLE,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": REGULARIZED_PLANE,
        "requested_nx": 48,
        "executed_nx": 48,
        "requested_n_steps": 250,
        "steps_completed": 250,
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
        "candidate_mass_acceptance_observed_abs": 0.002,
        "candidate_mass_acceptance_gate_pass": True,
        "collapse_first_x": None,
        "collapse_first_step": None,
        "controller_authority_ratio_tail_mean": 0.4,
        "controller_saturation_fraction_tail": 0.0,
        "controller_density_feedback_tail_mean": -0.0001,
        "mass_neutral_rho_feedback_tail_mean": 0.00025,
        "mass_neutral_rho_feedback_abs_tail_mean": 0.00025,
        "mass_neutral_mass_error_tail_mean": -0.0025,
        "mass_neutral_feedback_saturation_fraction_tail": 0.0,
        "selected96_claim_allowed": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "validation_claim_allowed": False,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_mass_neutral_flux_control_enabled": True,
        "open_boundary_mass_neutral_flux_control_mode": "global_mass_error_density_offset",
        "open_boundary_mass_neutral_mass_error_gain": 0.25,
        "open_boundary_mass_neutral_mass_error_cap": 0.0005,
        "open_boundary_mass_neutral_correction_blend": 1.0,
        "open_boundary_mass_neutral_reference_mass_mode": "initial",
        "mass_neutral_activation_hash": "step143-activation-hash",
        "source_step": 142,
        "source_step142_readiness_hash": _sha256(STEP142_SUMMARY),
        "source_step142_readiness_path": "outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json",
        "source_step142_status": "design_ready",
        "source_step142_recommended_design": "global_mass_error_density_offset",
        "solver_state_hash": "step143-solver-hash",
        "run_manifest_hash": "step143-run-hash",
    }
    if "enabled" in overrides:
        enabled = bool(overrides.pop("enabled"))
        row["open_boundary_mass_neutral_flux_control_enabled"] = enabled
        row["open_boundary_mass_neutral_flux_control_mode"] = "global_mass_error_density_offset" if enabled else "disabled"
        if not enabled:
            row["open_boundary_mass_neutral_mass_error_gain"] = 0.0
            row["open_boundary_mass_neutral_mass_error_cap"] = 0.0
            row["open_boundary_mass_neutral_correction_blend"] = 0.0
            row["mass_neutral_rho_feedback_tail_mean"] = 0.0
            row["mass_neutral_rho_feedback_abs_tail_mean"] = 0.0
            row["mass_neutral_mass_error_tail_mean"] = 0.0
    if "gain" in overrides:
        row["open_boundary_mass_neutral_mass_error_gain"] = overrides.pop("gain")
    if "mass" in overrides:
        row["candidate_mass_acceptance_observed_abs"] = overrides.pop("mass")
    if "outlet_cv" in overrides:
        row["outlet_flux_tail_cv"] = overrides.pop("outlet_cv")
    if "flux_mean" in overrides:
        row["flux_imbalance_rel_tail_mean"] = overrides.pop("flux_mean")
    row.update(overrides)
    return row
