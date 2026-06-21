import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_GOAL.md",
    "STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_REPORT.md",
    "docs/54_repository_evidence_integrity_repair.md",
    "docs/REPOSITORY_EVIDENCE_INDEX.md",
    "docs/REPOSITORY_EVIDENCE_INTEGRITY_ERRATA.md",
    "configs/step54_repository_evidence_integrity_repair.json",
    "configs/step54_lbm_relaxation_semantics_policy.json",
    "configs/step54_evidence_classification_policy.json",
    "src/lbm_relaxation_semantics.py",
    "src/proxy_diagnostic_truthfulness.py",
    "src/state_guard_truthfulness.py",
    "src/repository_evidence_index.py",
    "src/repository_test_strength_audit.py",
    "src/repository_evidence_integrity_claim_guard.py",
    "src/repository_evidence_integrity_artifact_manifest.py",
    "src/repository_evidence_integrity_regression_guard.py",
    "baseline_tests/step54_common.py",
    "baseline_tests/run_step54_lbm_relaxation_semantics_audit.py",
    "baseline_tests/run_step54_proxy_diagnostic_truthfulness_audit.py",
    "baseline_tests/run_step54_state_guard_truthfulness_audit.py",
    "baseline_tests/run_step54_test_strength_audit.py",
    "baseline_tests/run_step54_repository_evidence_index.py",
    "baseline_tests/run_step54_claim_guard.py",
    "baseline_tests/run_step54_step53_regression_guard.py",
    "baseline_tests/run_step54_artifact_manifest.py",
    "tests/test_step54_lbm_relaxation_semantics_contract.py",
    "tests/test_step54_repository_evidence_integrity_repair_contract.py",
]

OUTPUT_FILES = [
    "outputs/step54_lbm_relaxation_semantics_audit/lbm_relaxation_semantics.csv",
    "outputs/step54_lbm_relaxation_semantics_audit/lbm_relaxation_semantics_summary.csv",
    "outputs/step54_lbm_relaxation_semantics_audit/lbm_relaxation_semantics.json",
    "outputs/step54_proxy_diagnostic_truthfulness_audit/proxy_diagnostic_truthfulness.csv",
    "outputs/step54_proxy_diagnostic_truthfulness_audit/proxy_diagnostic_truthfulness_summary.csv",
    "outputs/step54_proxy_diagnostic_truthfulness_audit/proxy_diagnostic_truthfulness.json",
    "outputs/step54_state_guard_truthfulness_audit/state_guard_truthfulness.csv",
    "outputs/step54_state_guard_truthfulness_audit/state_guard_truthfulness_summary.csv",
    "outputs/step54_state_guard_truthfulness_audit/state_guard_truthfulness.json",
    "outputs/step54_test_strength_audit/test_strength_audit.csv",
    "outputs/step54_test_strength_audit/test_strength_audit_summary.csv",
    "outputs/step54_test_strength_audit/test_strength_audit.json",
    "outputs/step54_repository_evidence_index/repository_evidence_index.csv",
    "outputs/step54_repository_evidence_index/repository_evidence_index_summary.csv",
    "outputs/step54_repository_evidence_index/repository_evidence_index.json",
    "outputs/step54_claim_guard/claim_guard.csv",
    "outputs/step54_claim_guard/claim_guard_summary.csv",
    "outputs/step54_claim_guard/claim_guard.json",
    "outputs/step54_step53_regression_guard/step53_regression_guard.csv",
    "outputs/step54_step53_regression_guard/step53_regression_guard_summary.csv",
    "outputs/step54_step53_regression_guard/step53_regression_guard.json",
    "outputs/step54_artifact_manifest/artifact_manifest.csv",
    "outputs/step54_artifact_manifest/artifact_summary.csv",
    "outputs/step54_artifact_manifest/artifact_summary.json",
]

LOG_MARKERS = {
    "logs/step54_lbm_relaxation_semantics_audit.log": "[OK] Step 54 LBM relaxation semantics audit finished",
    "logs/step54_proxy_diagnostic_truthfulness_audit.log": "[OK] Step 54 proxy diagnostic truthfulness audit finished",
    "logs/step54_state_guard_truthfulness_audit.log": "[OK] Step 54 state guard truthfulness audit finished",
    "logs/step54_test_strength_audit.log": "[OK] Step 54 test strength audit finished",
    "logs/step54_repository_evidence_index.log": "[OK] Step 54 repository evidence index finished",
    "logs/step54_claim_guard.log": "[OK] Step 54 claim guard finished",
    "logs/step54_step53_regression_guard.log": "[OK] Step 54 Step 53 regression guard finished",
    "logs/step54_artifact_manifest.log": "[OK] Step 54 artifact manifest finished",
}

PROXY_METADATA = {
    "record_kind": "proxy_diagnostic_record",
    "solver_time_integration_run": False,
    "completed_lbm_steps_source": "config_declared_proxy_steps",
    "total_mpm_substeps_source": "config_declared_proxy_substeps",
    "rho_velocity_source": "proxy_formula",
    "hydro_force_source": "proxy_formula",
    "nan_inf_source": "finite_input_proxy_assumption",
}

STATE_METHOD_FIELDS = [
    "default_driver_state_mutation_count_method",
    "default_lbm_state_mutation_count_method",
    "default_mpm_state_mutation_count_method",
    "default_projection_state_mutation_count_method",
    "persistent_projected_state_count_method",
    "persistent_displaced_geometry_count_method",
    "persistent_lbm_solid_vel_count_method",
]

REQUIRED_SCOPE_PHRASES = [
    "Step 54 does not add a 48^3 `link_area_experimental` run.",
    "Step 54 does not migrate LBM viscosity formulas.",
    "Step 54 does not validate jet propulsion.",
    "Step 54 does not implement squid swimming.",
    "Step 54 does not prove grid convergence.",
    "A passing full pytest run means contract/artifact/proxy/solver-smoke tests passed according to the test strength audit classification.",
]


def test_step54_required_files_outputs_and_logs_exist():
    missing = [path for path in REQUIRED_FILES + OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step54_config_keeps_scope_closed():
    config = read_json("configs/step54_repository_evidence_integrity_repair.json")
    assert config["audit_id"] == "step54_repository_evidence_integrity_repair"
    assert config["diagnostic_only"] is True
    assert config["post_processing_only"] is True
    for key in [
        "modify_solver_formulas",
        "modify_default_behavior",
        "allow_48_link_area_expansion",
        "allow_longer_cycle",
        "allow_64_grid",
        "allow_external_taichi_lbm3d_edit",
        "allow_real_geometry_candidates_edit",
        "real_jet_validation_claim",
        "jet_propulsion_validation_claim",
        "squid_swimming_claim",
        "grid_convergence_claim",
        "production_readiness_claim",
        "full_solver_validation_claim",
    ]:
        assert config[key] is False


def test_step54_proxy_metadata_is_in_step50_step51_step52_artifacts():
    artifacts = [
        "outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.json",
        "outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json",
        "outputs/step52_48_feasibility_matrix/feasibility_matrix.json",
    ]
    for path in artifacts:
        payload = read_json(path)
        for row in payload["rows"]:
            assert_proxy_metadata(row)
            assert row["solver_time_integration_run"] is False
            for step_record in row["step_records"]:
                assert_proxy_metadata(step_record)

    summary = read_json("outputs/step54_proxy_diagnostic_truthfulness_audit/proxy_diagnostic_truthfulness.json")["summary"]
    assert summary["proxy_truthfulness_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert summary["real_jet_validation_claim"] is False
    assert summary["full_solver_validation_claim"] is False


def test_step54_state_guard_fixed_zero_methods_are_disclosed():
    artifacts = [
        "outputs/step50_state_mutation_guard/state_mutation_guard.json",
        "outputs/step51_state_mutation_guard/state_mutation_guard.json",
        "outputs/step52_state_mutation_guard/state_mutation_guard.json",
    ]
    for path in artifacts:
        summary = read_json(path)["summary"]
        assert summary["fixed_zero_fields_disclosed"] is True
        assert summary["state_guard_kind"] == "hash_plus_artifact_scan_plus_not_applicable_proxy_fields"
        assert summary["hash_checks_method"] == "measured_config_hash_before_after"
        assert summary["forbidden_output_scan_method"] == "measured_artifact_scan"
        for field in STATE_METHOD_FIELDS:
            assert field in summary

    audit = read_json("outputs/step54_state_guard_truthfulness_audit/state_guard_truthfulness.json")["summary"]
    assert audit["state_guard_truthfulness_audit_pass"] is True
    assert int(audit["row_count"]) == int(audit["pass_count"])


def test_step54_repository_evidence_index_and_test_strength_pass():
    index = read_json("outputs/step54_repository_evidence_index/repository_evidence_index.json")
    summary = index["summary"]
    assert summary["repository_evidence_index_pass"] is True
    assert int(summary["step50_51_52_proxy_diagnostic_count"]) == 3
    assert int(summary["step53_post_processing_audit_count"]) == 1
    assert int(summary["step1_step2_solver_smoke_baseline_count"]) == 2
    rows_by_step = {int(row["step"]): row for row in index["rows"]}
    for step in (50, 51, 52):
        assert rows_by_step[step]["evidence_kind"] == "proxy_diagnostic"
        assert rows_by_step[step]["solver_time_integration_run"] is False
    assert rows_by_step[53]["evidence_kind"] == "post_processing_audit"

    strength = read_json("outputs/step54_test_strength_audit/test_strength_audit.json")["summary"]
    assert strength["test_strength_audit_pass"] is True
    assert strength["test_suite_result_interpretation"] == REQUIRED_SCOPE_PHRASES[-1]
    assert int(strength["audited_file_count"]) == int(strength["classified_file_count"])


def test_step54_claim_regression_and_artifact_guards_pass():
    claim = read_json("outputs/step54_claim_guard/claim_guard.json")["summary"]
    assert claim["claim_guard_pass"] is True
    assert int(claim["forbidden_claim_count"]) == 0

    regression = read_json("outputs/step54_step53_regression_guard/step53_regression_guard.json")["summary"]
    assert regression["step53_regression_pass"] is True
    assert int(regression["row_count"]) == int(regression["pass_count"]) == 8

    manifest = read_json("outputs/step54_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert float(manifest["step54_total_size_mb"]) < 5.0
    assert int(manifest["step54_vtr_count"]) == 0
    assert int(manifest["step54_particle_npy_count"]) == 0
    assert int(manifest["protected_external_taichi_lbm3d_step54_file_count"]) == 0
    assert int(manifest["protected_real_geometry_candidates_step54_file_count"]) == 0


def test_step54_docs_and_report_state_boundaries():
    docs = read_text("docs/54_repository_evidence_integrity_repair.md")
    report = read_text("STEP54_REPOSITORY_EVIDENCE_INTEGRITY_REPAIR_REPORT.md")
    errata = read_text("docs/REPOSITORY_EVIDENCE_INTEGRITY_ERRATA.md")
    evidence_index = read_text("docs/REPOSITORY_EVIDENCE_INDEX.md")
    joined = "\n".join([docs, report, errata, evidence_index])
    for phrase in REQUIRED_SCOPE_PHRASES:
        assert phrase in joined
    assert "Step 50, Step 51, and Step 52 are proxy diagnostics." in evidence_index
    assert "Step 53 is a post-processing audit" in evidence_index
    assert "standard-viscosity validation" in evidence_index


def assert_proxy_metadata(row):
    for key, value in PROXY_METADATA.items():
        assert row[key] == value


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
