import csv
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGULARIZED_PLANE = "regularized_plane_flux_controlled_pressure_outlet"
STEP146_READINESS = (
    ROOT
    / "outputs"
    / "step146_coupled_saturation_stationarity_design"
    / "step146_design_readiness_report.json"
)
STEP147_PHASE = "planeflux_saturation_stationarity48"
STEP147_ROLE = "saturation_stationarity_diagnostic_48"
STEP147_OUTPUT_ROOT = ROOT / "outputs" / "step147_saturation_stationarity_diagnostic"
STEP147_PHASE_ROOT = STEP147_OUTPUT_ROOT / "saturation_stationarity48"
STEP147_GOAL = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "147" / "goal.md"
STEP147_REPORT = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "147" / "report.md"

STEP147_ROWS = [
    (
        "baseline_high_repeat",
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010"
        "_mnhigh_mgain0p50_mcap0p001_blend1p00_slew0p50_out5_250step_satstat",
        0.50,
        0.0010,
        1.00,
        0.50,
    ),
    (
        "relief_low_slew025",
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010"
        "_mnrelieflow_mgain0p35_mcap0p001_blend0p50_slew0p25_out5_250step_satstat",
        0.35,
        0.0010,
        0.50,
        0.25,
    ),
    (
        "relief_mid_slew025",
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010"
        "_mnreliefmid_mgain0p50_mcap0p001_blend0p50_slew0p25_out5_250step_satstat",
        0.50,
        0.0010,
        0.50,
        0.25,
    ),
    (
        "relief_cap_test_slew025",
        "duct_only_48_regularized_plane_flux_controlled_gain0p75_cap0p0075_rho0p0010"
        "_mncaptest_mgain0p50_mcap0p0015_blend0p50_slew0p25_out5_250step_satstat",
        0.50,
        0.0015,
        0.50,
        0.25,
    ),
]


STEP146_PROVENANCE_FIELDS = [
    "source_step146_readiness_hash",
    "source_step146_readiness_path",
    "source_step146_status",
    "source_step146_recommended_design",
    "source_step146_recommended_phase",
    "source_step146_recommended_row_role",
    "source_step145_decision_case",
    "source_step144_decision_case",
]


def test_step147_phase_resolves_exact_four_bounded_diagnostic_rows():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        CANDIDATE_SEMANTICS,
        REPAIRED_CANDIDATE_SEMANTICS,
        SELECTED_CHAIN_ROLES,
        resolve_step121_phase_specs,
        step121_saturation_stationarity_48_specs,
    )

    specs = step121_saturation_stationarity_48_specs(output_interval=5)

    assert resolve_step121_phase_specs(STEP147_PHASE, output_interval=5) == specs
    assert len(specs) == 4
    assert [spec.name for spec in specs] == [row[1] for row in STEP147_ROWS]
    assert all(spec.row_role == STEP147_ROLE for spec in specs)
    assert STEP147_ROLE not in SELECTED_CHAIN_ROLES
    assert REGULARIZED_PLANE not in CANDIDATE_SEMANTICS
    assert REGULARIZED_PLANE not in REPAIRED_CANDIDATE_SEMANTICS

    assert all((spec.nx, spec.ny, spec.nz) == (48, 48, 48) for spec in specs)
    assert all(spec.requested_nx == 48 for spec in specs)
    assert all(spec.n_steps == 250 and spec.requested_n_steps == 250 for spec in specs)
    assert all(spec.output_interval == 5 for spec in specs)
    assert all(spec.geometry_mode == "duct_only" for spec in specs)
    assert all(spec.open_boundary_semantics == REGULARIZED_PLANE for spec in specs)
    assert all(spec.allow_large_real_run_without_flag is True for spec in specs)
    assert all(spec.not_used_for_validation is True for spec in specs)
    assert all("Step147" in spec.artifact_scope_note for spec in specs)
    assert all("selected96" in spec.artifact_scope_note for spec in specs)
    assert all("500-step" in spec.artifact_scope_note for spec in specs)

    common = {
        (
            round(float(spec.open_boundary_flux_feedback_gain_u), 8),
            round(float(spec.open_boundary_flux_correction_cap_u), 8),
            round(float(spec.open_boundary_flux_feedback_gain_rho), 8),
            round(float(spec.open_boundary_flux_filter_alpha), 8),
            round(float(spec.open_boundary_flux_feedback_delta_cap_u), 8),
            int(spec.open_boundary_flux_control_measure_plane_offset),
            round(float(spec.open_boundary_flux_control_target_scale), 8),
            int(spec.open_boundary_inlet_ramp_steps),
            bool(spec.open_boundary_outlet_flux_drop_guard_enabled),
            round(float(spec.open_boundary_outlet_flux_drop_guard_min_ratio), 8),
            round(float(spec.niu), 8),
        )
        for spec in specs
    }
    assert common == {(0.75, 0.0075, 0.001, 0.02, 0.0005, 2, 0.8, 85, True, 0.7, 0.1)}

    for spec, row in zip(specs, STEP147_ROWS):
        label, _name, gain_mass, cap_mass, blend, slew = row
        assert spec.mass_neutral_label == label
        assert spec.open_boundary_mass_neutral_flux_control_enabled is True
        assert spec.open_boundary_mass_neutral_flux_control_mode == "global_mass_error_density_offset"
        assert round(float(spec.open_boundary_mass_neutral_mass_error_gain), 8) == gain_mass
        assert round(float(spec.open_boundary_mass_neutral_mass_error_cap), 8) == cap_mass
        assert round(float(spec.open_boundary_mass_neutral_correction_blend), 8) == blend
        assert spec.open_boundary_mass_neutral_reference_mass_mode == "initial"
        assert round(float(spec.open_boundary_flux_feedback_slew_alpha), 8) == slew


def test_step147_provenance_locks_to_step146_design_readiness():
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        step121_saturation_stationarity_48_specs,
    )

    readiness = _read_json(STEP146_READINESS)
    specs = step121_saturation_stationarity_48_specs(output_interval=5)

    assert readiness["status"] == "design_ready"
    assert readiness["recommended_step147_phase"] == STEP147_PHASE
    assert readiness["recommended_step147_row_role"] == STEP147_ROLE

    for spec in specs:
        assert spec.source_step == 146
        assert spec.source_step146_readiness_hash == _sha256(STEP146_READINESS)
        assert spec.source_step146_readiness_path == (
            "outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json"
        )
        assert spec.source_step146_status == "design_ready"
        assert spec.source_step146_recommended_design == (
            "saturation_aware_mass_neutral_relief_with_stationarity_damping"
        )
        assert spec.source_step146_recommended_phase == STEP147_PHASE
        assert spec.source_step146_recommended_row_role == STEP147_ROLE
        assert spec.source_step145_decision_case == "mixed_saturation_stationarity_failure"
        assert spec.source_step144_decision_case == "mass_neutral_flow_stationarity_long_window_failure"


def test_step147_manifest_records_and_rejects_step146_provenance_and_activation_hash_mismatch(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        mass_neutral_activation_hash_for_spec,
        run_manifest_hash_for_spec,
        solver_state_hash_for_spec,
    )
    from experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction import (
        collect_step121_rows,
        step121_saturation_stationarity_48_specs,
        write_step121_campaign_manifest,
    )

    specs = step121_saturation_stationarity_48_specs(output_interval=5)
    spec = specs[1]
    manifest = write_step121_campaign_manifest(tmp_path, specs, phase=STEP147_PHASE)
    expected = manifest["expected_rows"][spec.name]

    assert manifest["phase_history"][-1] == STEP147_PHASE
    assert expected["source_step146_readiness_hash"] == spec.source_step146_readiness_hash
    assert expected["source_step146_recommended_phase"] == STEP147_PHASE
    assert expected["mass_neutral_label"] == spec.mass_neutral_label
    assert expected["mass_neutral_activation_hash"] == mass_neutral_activation_hash_for_spec(spec)

    stale = _good_step147_row(name=spec.name)
    stale.update(expected)
    stale["solver_state_hash"] = solver_state_hash_for_spec(spec)
    stale["run_manifest_hash"] = run_manifest_hash_for_spec(spec)
    stale["source_step146_readiness_hash"] = "wrong-step146-readiness-hash"
    _write_json(tmp_path / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(tmp_path, return_ignored=True)

    assert collected["rows"] == []
    assert "source_step146_readiness_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]

    stale.update(expected)
    stale["solver_state_hash"] = solver_state_hash_for_spec(spec)
    stale["run_manifest_hash"] = run_manifest_hash_for_spec(spec)
    stale["mass_neutral_activation_hash"] = "wrong-activation-hash"
    _write_json(tmp_path / spec.name / "finite_stability_report.json", {"summary_row": stale})

    collected = collect_step121_rows(tmp_path, return_ignored=True)

    assert collected["rows"] == []
    assert "mass_neutral_activation_hash_mismatch" in collected["ignored_rows"][0]["ignored_reasons"]


def test_step147_summary_metadata_boundary_and_flow_diagnostics_expose_source_scope(tmp_path):
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
        step121_saturation_stationarity_48_specs,
    )

    spec = step121_saturation_stationarity_48_specs(output_interval=5)[1]
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
        assert payload["step147_saturation_stationarity_candidate"] is True
        assert payload["mass_neutral_label"] == "relief_low_slew025"
        assert payload["source_step146_readiness_hash"] == _sha256(STEP146_READINESS)
        assert payload["source_step146_status"] == "design_ready"
        assert payload["selected96_claim_allowed"] is False
        assert payload["validation_claim_allowed"] is False

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
    assert record["step147_saturation_stationarity_candidate"] is True
    for field in ["mass_neutral_label", *STEP146_PROVENANCE_FIELDS]:
        assert field in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS
        assert field in record

    _write_flow_development_diagnostics(tmp_path, [record])

    rows = list(csv.DictReader((tmp_path / "flow_development_diagnostics.csv").open("r", encoding="utf-8", newline="")))
    assert rows[-1]["step147_saturation_stationarity_candidate"] == "True"
    diagnostic_summary = _read_json(tmp_path / "flow_development_diagnostics_summary.json")
    assert diagnostic_summary["step"] == 147
    assert diagnostic_summary["final"]["source_step146_readiness_hash"] == _sha256(STEP146_READINESS)
    assert diagnostic_summary["selected96_claim_allowed"] is False


def test_step147_audit_decision_cases_and_missing_inputs(tmp_path):
    from experiments.steps.step116_regularized_lbm_duct_flow_baseline import _write_json
    from experiments.steps.step147_saturation_stationarity_audit import run_step147_saturation_stationarity_audit

    missing = run_step147_saturation_stationarity_audit(
        phase_root=tmp_path / "missing_phase",
        step146_readiness=tmp_path / "missing_readiness.json",
        output_dir=tmp_path / "missing_out",
        force=True,
    )
    assert missing["status"] == "missing_input"
    assert missing["decision_case"] == "missing_input"
    assert missing["step148_500step_probe_proposal_allowed"] is False
    assert missing["selected96_execution_allowed"] is False

    supported_phase = tmp_path / "supported_phase"
    _write_json(
        supported_phase / "baseline" / "finite_stability_report.json",
        {"summary_row": _good_step147_row(name="baseline", label="baseline_high_repeat")},
    )
    _write_json(
        supported_phase / "relief_good" / "finite_stability_report.json",
        {
            "summary_row": _good_step147_row(
                name="relief_good",
                label="relief_low_slew025",
                mass=0.003,
                outlet_cv=0.04,
                flux_mean=0.04,
                saturation=0.30,
            )
        },
    )
    supported = run_step147_saturation_stationarity_audit(
        phase_root=supported_phase,
        step146_readiness=STEP146_READINESS,
        output_dir=tmp_path / "supported_out",
        force=True,
    )
    assert supported["status"] == "decision_ready"
    assert supported["decision_case"] == "saturation_stationarity_relief_supports_step148_500step_probe"
    assert supported["step148_500step_probe_proposal_allowed"] is True
    assert supported["selected96_execution_allowed"] is False
    assert supported["validation_claim_allowed"] is False

    mass_only_phase = tmp_path / "mass_only_phase"
    _write_json(
        mass_only_phase / "baseline" / "finite_stability_report.json",
        {"summary_row": _good_step147_row(name="baseline", label="baseline_high_repeat")},
    )
    _write_json(
        mass_only_phase / "mass_only" / "finite_stability_report.json",
        {
            "summary_row": _good_step147_row(
                name="mass_only",
                label="relief_mid_slew025",
                mass=0.003,
                outlet_cv=0.13,
                flux_mean=0.12,
                saturation=0.82,
                flow_development_gate_pass=False,
            )
        },
    )
    mass_only = run_step147_saturation_stationarity_audit(
        phase_root=mass_only_phase,
        step146_readiness=STEP146_READINESS,
        output_dir=tmp_path / "mass_only_out",
        force=True,
    )
    assert mass_only["decision_case"] == "mass_relief_without_stationarity"
    assert mass_only["step148_500step_probe_proposal_allowed"] is False

    stationarity_only_phase = tmp_path / "stationarity_only_phase"
    _write_json(
        stationarity_only_phase / "baseline" / "finite_stability_report.json",
        {"summary_row": _good_step147_row(name="baseline", label="baseline_high_repeat")},
    )
    _write_json(
        stationarity_only_phase / "stationarity_only" / "finite_stability_report.json",
        {
            "summary_row": _good_step147_row(
                name="stationarity_only",
                label="relief_cap_test_slew025",
                mass=0.009,
                outlet_cv=0.04,
                flux_mean=0.04,
                saturation=0.30,
            )
        },
    )
    stationarity_only = run_step147_saturation_stationarity_audit(
        phase_root=stationarity_only_phase,
        step146_readiness=STEP146_READINESS,
        output_dir=tmp_path / "stationarity_only_out",
        force=True,
    )
    assert stationarity_only["decision_case"] == "stationarity_relief_without_mass"
    assert (tmp_path / "supported_out" / "step147_saturation_stationarity_comparison.json").is_file()
    assert (tmp_path / "supported_out" / "step147_saturation_stationarity_comparison.csv").is_file()
    assert (tmp_path / "supported_out" / "step147_decision_summary.json").is_file()


def test_committed_step147_outputs_and_docs_remain_bounded_after_real_phase_and_audit():
    decision_path = STEP147_OUTPUT_ROOT / "step147_decision_summary.json"
    comparison_path = STEP147_OUTPUT_ROOT / "step147_saturation_stationarity_comparison.json"
    csv_path = STEP147_OUTPUT_ROOT / "step147_saturation_stationarity_comparison.csv"

    assert STEP147_GOAL.is_file()
    assert STEP147_REPORT.is_file()
    assert decision_path.is_file()
    assert comparison_path.is_file()
    assert csv_path.is_file()

    decision = _read_json(decision_path)
    comparison = _read_json(comparison_path)
    current_status = (ROOT / "docs" / "current" / "STATUS.md").read_text(encoding="utf-8")
    current_gates = (ROOT / "docs" / "current" / "VALIDATION_GATES.md").read_text(encoding="utf-8")
    active_campaign = (ROOT / "docs" / "current" / "ACTIVE_CAMPAIGN.json").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    report = STEP147_REPORT.read_text(encoding="utf-8")

    assert decision["step"] == 147
    assert comparison["step"] == 147
    assert decision["source_step146_readiness_hash"] == _sha256(STEP146_READINESS)
    assert comparison["source_step146_readiness_hash"] == _sha256(STEP146_READINESS)
    assert decision["row_count"] == 4
    assert comparison["row_count"] == 4
    assert {row["row_role"] for row in comparison["rows"]} == {STEP147_ROLE}
    assert all(row["requested_nx"] == 48 and row["requested_n_steps"] == 250 for row in comparison["rows"])

    for payload in [decision, comparison]:
        assert payload["step148_500step_probe_proposal_allowed"] in {True, False}
        assert payload["selected96_execution_allowed"] is False
        assert payload["selected_static_execution_allowed"] is False
        assert payload["validation_claim_allowed"] is False
        assert payload["fluent_validation_claim_allowed"] is False
        assert payload["fsi_validation_claim_allowed"] is False
        assert payload["production_readiness_claim_allowed"] is False

    required_text = [
        "Step147 ran exactly four 48^3 / 250-step LBM-only rows",
        "Step147 did not run selected96",
        "Step147 did not run selected-static",
        "Step147 did not run 96^3",
        "Step147 did not run a 500-step row",
        "Step147 did not run Fluent",
        "Step147 did not run FSI",
        "Step147 does not make a validation claim",
        "origin/main = 54afab0c6b4bdae05fa08f50f274e8d2f557e1d9",
    ]
    for text in [STEP147_GOAL.read_text(encoding="utf-8"), report, current_status, current_gates, active_campaign, readme]:
        for needle in required_text:
            assert needle in text

    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8", newline="")))
    assert len(rows) == 4
    assert {row["mass_neutral_label"] for row in rows} == {row[0] for row in STEP147_ROWS}


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        "controller_saturation_count_run": 1,
        "controller_saturation_fraction_run": 0.1,
        "controller_drop_guard_activation_count_run": 0,
    }


def _good_step147_row(**overrides):
    readiness = _read_json(STEP146_READINESS)
    label = overrides.pop("label", "baseline_high_repeat")
    mass = overrides.pop("mass", 0.0073)
    outlet_cv = overrides.pop("outlet_cv", 0.115)
    flux_mean = overrides.pop("flux_mean", 0.102)
    saturation = overrides.pop("saturation", 0.94)
    flow_development_gate_pass = overrides.pop("flow_development_gate_pass", True)
    row = {
        "name": "step147-good-row",
        "mass_neutral_label": label,
        "row_role": STEP147_ROLE,
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
        "flux_imbalance_rel_tail_mean": flux_mean,
        "flux_imbalance_rel_tail_max": flux_mean * 1.5,
        "outlet_flux_tail_cv": outlet_cv,
        "flow_development_gate_pass": flow_development_gate_pass,
        "candidate_mass_acceptance_observed_abs": mass,
        "candidate_mass_acceptance_gate_pass": mass <= 0.005,
        "mass_total_delta_rel_final": mass,
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
        "mass_neutral_mass_error_tail_mean": mass,
        "mass_neutral_mass_error_final": mass,
        "mass_neutral_feedback_saturation_fraction_tail": saturation,
        "selected96_claim_allowed": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "open_boundary_flux_feedback_gain_rho": 0.001,
        "open_boundary_mass_neutral_flux_control_enabled": True,
        "open_boundary_mass_neutral_flux_control_mode": "global_mass_error_density_offset",
        "open_boundary_mass_neutral_mass_error_gain": 0.50,
        "open_boundary_mass_neutral_mass_error_cap": 0.00100,
        "open_boundary_mass_neutral_correction_blend": 1.0,
        "open_boundary_mass_neutral_reference_mass_mode": "initial",
        "mass_neutral_activation_hash": "step147-activation-hash",
        "source_step": 146,
        "source_step146_readiness_hash": _sha256(STEP146_READINESS),
        "source_step146_readiness_path": (
            "outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json"
        ),
        "source_step146_status": "design_ready",
        "source_step146_recommended_design": readiness["recommended_design"],
        "source_step146_recommended_phase": readiness["recommended_step147_phase"],
        "source_step146_recommended_row_role": readiness["recommended_step147_row_role"],
        "source_step145_decision_case": readiness["source_step145_decision_case"],
        "source_step144_decision_case": readiness["source_step144_decision_case"],
        "solver_state_hash": "step147-solver-hash",
        "run_manifest_hash": "step147-run-hash",
        "runtime_s": 12.0,
    }
    row.update(overrides)
    return row
