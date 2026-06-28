import csv
import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
STEP141_PHASE = "planeflux_density_feedback_isolation48"
STEP141_ROLE = "density_feedback_isolation_diagnostic_48"
STEP140_SUMMARY = ROOT / "outputs" / "step140_long_window_drift_forensics" / "step140_failure_mechanism_summary.json"
STEP141_OUTPUT_ROOT = ROOT / "outputs" / "step141_density_feedback_isolation"
STEP139_RUNTIME_CODE_COMMIT = "4e43162a641085e56a4ba72c8bc013e58cb08cc3"


def test_step141_phase_resolves_exact_density_feedback_isolation_rows():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
        SELECTED_CHAIN_ROLES,
        resolve_step121_phase_specs,
        step121_density_feedback_isolation_48_specs,
    )

    specs = step121_density_feedback_isolation_48_specs(output_interval=5)
    assert resolve_step121_phase_specs(STEP141_PHASE, output_interval=5) == specs
    assert len(specs) == 4
    assert all(spec.row_role == STEP141_ROLE for spec in specs)
    assert all(spec.open_boundary_semantics == REGULARIZED_PLANE for spec in specs)
    assert REGULARIZED_PLANE not in CANDIDATE_SEMANTICS
    assert REGULARIZED_PLANE not in REPAIRED_CANDIDATE_SEMANTICS
    assert STEP141_ROLE not in SELECTED_CHAIN_ROLES

    assert all((spec.nx, spec.ny, spec.nz) == (48, 48, 48) for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all(spec.n_steps == 250 and spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.output_interval == 5 for spec in specs)
    assert all(spec.geometry_mode == "duct_only" for spec in specs)
    assert all(spec.allow_large_real_run_without_flag is True for spec in specs)
    assert all("Step141" in spec.artifact_scope_note for spec in specs)
    assert all("selected96" in spec.artifact_scope_note for spec in specs)
    assert all("500-step" in spec.artifact_scope_note for spec in specs)

    varying = {
        (
            round(float(spec.open_boundary_flux_feedback_gain_u), 8),
            round(float(spec.open_boundary_flux_correction_cap_u), 8),
            round(float(spec.open_boundary_flux_filter_alpha), 8),
            round(float(spec.open_boundary_flux_feedback_delta_cap_u), 8),
            round(float(spec.open_boundary_flux_feedback_slew_alpha), 8),
            int(spec.open_boundary_flux_control_measure_plane_offset),
            round(float(spec.open_boundary_flux_control_target_scale), 8),
            int(spec.open_boundary_inlet_ramp_steps),
            round(float(spec.open_boundary_outlet_flux_drop_guard_min_ratio), 8),
            round(float(spec.niu), 8),
        )
        for spec in specs
    }
    assert varying == {(0.75, 0.0075, 0.02, 0.0005, 0.5, 2, 0.8, 85, 0.7, 0.1)}
    assert sorted(round(float(spec.open_boundary_flux_feedback_gain_rho), 8) for spec in specs) == [
        0.0,
        0.00025,
        0.0005,
        0.001,
    ]
    assert {spec.name for spec in specs} == {
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0000_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso",
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p00025_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso",
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0005_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso",
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_out5_250step_density_iso",
    }


def test_step141_provenance_links_step140_summary_and_step139_source_row(tmp_path):
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_density_feedback_isolation_48_specs,
        write_step121_campaign_manifest,
    )

    specs = step121_density_feedback_isolation_48_specs(output_interval=5)
    summary = _read_json(STEP140_SUMMARY)
    expected_hash = _sha256(STEP140_SUMMARY)

    for spec in specs:
        assert spec.source_step == 140
        assert spec.source_step139_row_name.endswith("_ramp85_target0p80_500step_final")
        assert spec.source_step139_solver_state_hash
        assert spec.source_step139_run_manifest_hash
        assert spec.source_step139_code_commit == STEP139_RUNTIME_CODE_COMMIT
        assert spec.source_step140_summary_hash == expected_hash
        assert spec.source_step140_summary_path == "outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json"
        assert spec.source_step140_dominant_failure_mechanism == summary["dominant_failure_mechanism"]
        assert spec.source_step140_mass_drift_mechanism == summary["mechanism_summary"]["mass_drift_mechanism"]
        assert "post-250 mass excursion" in spec.artifact_scope_note

    manifest = write_step121_campaign_manifest(tmp_path, specs, phase=STEP141_PHASE)
    expected = manifest["expected_rows"][specs[0].name]
    assert manifest["phase_history"][-1] == STEP141_PHASE
    assert expected["row_role"] == STEP141_ROLE
    assert expected["source_step"] == 140
    assert expected["source_step139_row_name"] == specs[0].source_step139_row_name
    assert expected["source_step140_summary_hash"] == expected_hash
    assert expected["source_step140_dominant_failure_mechanism"] == summary["dominant_failure_mechanism"]


def test_step141_rows_cannot_enable_selected96_even_if_metrics_pass():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import select_step121_best_boundary

    row = _good_step141_row()
    selection = select_step121_best_boundary([row])

    assert selection["best_boundary_selected"] is False
    assert selection["validation_claim_allowed"] is False
    assert row["selected96_claim_allowed"] is False
    assert row["validation_claim_allowed"] is False


def test_step141_manifest_rejects_stale_source_hashes(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_density_feedback_isolation_48_specs,
        write_step121_campaign_manifest,
    )

    specs = step121_density_feedback_isolation_48_specs(output_interval=5)
    manifest = write_step121_campaign_manifest(tmp_path, specs, phase=STEP141_PHASE)
    spec = specs[0]
    expected = manifest["expected_rows"][spec.name]

    stale = _good_step141_row(
        name=spec.name,
        lbm_open_boundary_semantics=spec.open_boundary_semantics,
        solver_state_hash=solver_state_hash_for_spec(spec),
        run_manifest_hash=run_manifest_hash_for_spec(spec),
        source_step139_solver_state_hash=expected["source_step139_solver_state_hash"],
        source_step139_run_manifest_hash=expected["source_step139_run_manifest_hash"],
        source_step140_summary_hash="wrong-step140-summary-hash",
    )
    _write_json(tmp_path / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(tmp_path, return_ignored=True)

    assert collected["rows"] == []
    assert collected["ignored_rows"][0]["name"] == spec.name
    assert "source_step140_summary_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]


def test_step141_flow_diagnostics_include_provenance_and_claim_flags(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_density_feedback_isolation_48_specs,
    )

    spec = step121_density_feedback_isolation_48_specs(output_interval=5)[0]
    record = _flow_development_diagnostic_record(
        {
            "step": 250,
            "inlet_flux": 42.0,
            "outlet_flux": 40.0,
            "midplane_flux": 41.0,
            "mass_total_delta_rel": 0.001,
            "sampled_x_profile_flux": json.dumps({"24": 41.0, "36": 40.5, "47": 40.0}, sort_keys=True),
        },
        spec,
        {
            "controller_target_outlet_flux": 33.6,
            "controller_measured_outlet_flux": 40.0,
            "controller_raw_flux_error": -6.4,
            "controller_filtered_flux_error": -3.2,
            "controller_u_feedback": -0.002,
            "controller_density_feedback": -0.0001,
            "controller_saturation_count_run": 0,
            "controller_saturation_fraction_run": 0.0,
            "controller_drop_guard_activation_count_run": 0,
        },
    )

    for field in [
        "step141_density_feedback_isolation_candidate",
        "source_step139_row_name",
        "source_step139_solver_state_hash",
        "source_step139_run_manifest_hash",
        "source_step139_code_commit",
        "source_step140_summary_hash",
        "source_step140_summary_path",
        "source_step140_dominant_failure_mechanism",
        "source_step140_mass_drift_mechanism",
    ]:
        assert field in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
        assert field in record

    assert record["step141_density_feedback_isolation_candidate"] is True
    assert record["source_step"] == 140
    assert record["source_step140_summary_hash"] == _sha256(STEP140_SUMMARY)
    assert record["selected96_claim_allowed"] is False
    assert record["validation_claim_allowed"] is False

    _write_flow_development_diagnostics(tmp_path, [record])

    rows = list(csv.DictReader((tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="")))
    assert rows[-1]["step141_density_feedback_isolation_candidate"] == "True"
    assert rows[-1]["selected96_claim_allowed"] == "False"
    summary = _read_json(tmp_path / "flow_development_diagnostics_summary.json")
    assert summary["step"] == 141
    assert summary["final"]["step141_density_feedback_isolation_candidate"] is True
    assert summary["selected96_claim_allowed"] is False


def test_step141_audit_sorts_rows_and_keeps_claims_blocked(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step141_density_feedback_isolation_audit import run_step141_density_feedback_audit

    phase_root = tmp_path / "phase"
    _write_json(phase_root / "rho_off" / "finite_stability_report.json", {"summary_row": _good_step141_row(name="rho_off", rho=0.0, mass=0.002, outlet_cv=0.08, flux_mean=0.07)})
    _write_json(phase_root / "rho_half" / "finite_stability_report.json", {"summary_row": _good_step141_row(name="rho_half", rho=0.0005, mass=0.004, outlet_cv=0.09, flux_mean=0.08)})
    _write_json(phase_root / "rho_base" / "finite_stability_report.json", {"summary_row": _good_step141_row(name="rho_base", rho=0.001, mass=0.008, outlet_cv=0.12, flux_mean=0.11)})

    summary = run_step141_density_feedback_audit(phase_root, STEP140_SUMMARY, tmp_path / "audit", force=True)

    assert summary["status"] == "decision_ready"
    assert summary["step"] == 141
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["step142_single_500step_final_evidence_proposal_allowed"] is True
    assert summary["best_row_name"] == "rho_off"
    assert summary["decision_case"] == "density_feedback_contributes_to_mass_stationarity_drift"

    comparison = _read_json(tmp_path / "audit" / "step141_density_feedback_comparison.json")
    assert [row["name"] for row in comparison["rows"]] == ["rho_off", "rho_half", "rho_base"]
    assert (tmp_path / "audit" / "step141_density_feedback_comparison.csv").is_file()
    assert (tmp_path / "audit" / "step141_decision_summary.json").is_file()


def test_step141_audit_missing_inputs_does_not_synthesize_decision(tmp_path):
    from experiments.steps.step141_density_feedback_isolation_audit import run_step141_density_feedback_audit

    summary = run_step141_density_feedback_audit(tmp_path / "missing_phase", STEP140_SUMMARY, tmp_path / "audit", force=True)

    assert summary["status"] == "missing_input"
    assert summary["missing_input"] is True
    assert summary["best_row_name"] is None
    assert summary["step142_single_500step_final_evidence_proposal_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False


def test_committed_step141_outputs_exist_after_real_phase_and_audit():
    decision_path = STEP141_OUTPUT_ROOT / "step141_decision_summary.json"
    comparison_path = STEP141_OUTPUT_ROOT / "step141_density_feedback_comparison.json"
    csv_path = STEP141_OUTPUT_ROOT / "step141_density_feedback_comparison.csv"

    assert decision_path.is_file()
    assert comparison_path.is_file()
    assert csv_path.is_file()

    decision = _read_json(decision_path)
    comparison = _read_json(comparison_path)

    assert decision["step"] == 141
    assert decision["selected96_execution_allowed"] is False
    assert decision["validation_claim_allowed"] is False
    assert decision["row_count"] == 4
    assert len(comparison["rows"]) == 4
    assert {row["row_role"] for row in comparison["rows"]} == {STEP141_ROLE}


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _good_step141_row(**overrides):
    row = {
        "name": "step141-good-row",
        "row_role": STEP141_ROLE,
        "geometry_mode": "duct_only",
        "lbm_open_boundary_semantics": REGULARIZED_PLANE,
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
        "inlet_flux_tail_mean": 42.0,
        "outlet_flux_tail_mean": 40.0,
        "outlet_to_inlet_flux_ratio_tail_mean": 0.952,
        "midplane_to_inlet_flux_ratio_tail_mean": 0.98,
        "flux_imbalance_rel_tail_mean": 0.07,
        "flux_imbalance_rel_tail_max": 0.12,
        "outlet_flux_tail_cv": 0.08,
        "flow_development_gate_pass": True,
        "candidate_mass_acceptance_observed_abs": 0.002,
        "candidate_mass_acceptance_gate_pass": True,
        "collapse_first_x": None,
        "collapse_first_step": None,
        "controller_authority_ratio_tail_mean": 0.4,
        "controller_saturation_fraction_tail": 0.0,
        "controller_density_feedback_tail_mean": -0.0001,
        "outlet_flux_drop_guard_activation_fraction_tail": 0.0,
        "selected96_claim_allowed": False,
        "validation_claim_allowed": False,
        "open_boundary_flux_feedback_gain_rho": 0.0,
        "source_step": 140,
        "source_step139_row_name": "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p001_alpha0p02_du0p0005_slew0p50_offset2_guard_on_min0p70_ramp85_target0p80_500step_final",
        "source_step139_solver_state_hash": "step139-solver-hash",
        "source_step139_run_manifest_hash": "step139-run-hash",
        "source_step139_code_commit": STEP139_RUNTIME_CODE_COMMIT,
        "source_step140_summary_hash": _sha256(STEP140_SUMMARY),
        "source_step140_summary_path": "outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json",
        "source_step140_dominant_failure_mechanism": "mass_accumulation_with_outlet_stationarity_drift",
        "source_step140_mass_drift_mechanism": "tail_mass_acceptance_failure",
        "solver_state_hash": "step141-solver-hash",
        "run_manifest_hash": "step141-run-hash",
    }
    if "rho" in overrides:
        row["open_boundary_flux_feedback_gain_rho"] = overrides.pop("rho")
    if "mass" in overrides:
        row["candidate_mass_acceptance_observed_abs"] = overrides.pop("mass")
    if "outlet_cv" in overrides:
        row["outlet_flux_tail_cv"] = overrides.pop("outlet_cv")
    if "flux_mean" in overrides:
        row["flux_imbalance_rel_tail_mean"] = overrides.pop("flux_mean")
    row.update(overrides)
    return row
