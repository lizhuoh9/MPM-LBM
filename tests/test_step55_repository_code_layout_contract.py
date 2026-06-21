import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "STEP55_REPOSITORY_CODE_LAYOUT_SEPARATION_IMPORT_BOUNDARY_GOAL.md",
    "STEP55_REPOSITORY_CODE_LAYOUT_SEPARATION_IMPORT_BOUNDARY_REPORT.md",
    "docs/55_repository_code_layout_separation_import_boundary.md",
    "docs/REPOSITORY_CODE_LAYOUT_POLICY.md",
    "configs/step55_code_layout_policy.json",
    "configs/step55_import_boundary_policy.json",
    "configs/step55_compatibility_shim_policy.json",
    "configs/step55_test_strength_enum_policy.json",
    "src/mpm_lbm/__init__.py",
    "src/mpm_lbm/sim/__init__.py",
    "src/mpm_lbm/diagnostics/__init__.py",
    "src/mpm_lbm/evidence/__init__.py",
    "src/mpm_lbm/evidence/code_layout_audit.py",
    "src/mpm_lbm/evidence/import_boundary_audit.py",
    "src/mpm_lbm/evidence/compatibility_shim_audit.py",
    "experiments/__init__.py",
    "experiments/steps/__init__.py",
    "baseline_tests/step55_common.py",
    "baseline_tests/run_step55_code_layout_audit.py",
    "baseline_tests/run_step55_import_boundary_audit.py",
    "baseline_tests/run_step55_compatibility_shim_audit.py",
    "baseline_tests/run_step55_test_strength_enum_audit.py",
    "baseline_tests/run_step55_step54_regression_guard.py",
    "baseline_tests/run_step55_artifact_manifest.py",
]

OUTPUT_FILES = [
    "outputs/step55_code_layout_audit/code_layout_audit.csv",
    "outputs/step55_code_layout_audit/code_layout_audit_summary.csv",
    "outputs/step55_code_layout_audit/code_layout_audit.json",
    "outputs/step55_import_boundary_audit/import_boundary_audit.csv",
    "outputs/step55_import_boundary_audit/import_boundary_audit_summary.csv",
    "outputs/step55_import_boundary_audit/import_boundary_audit.json",
    "outputs/step55_compatibility_shim_audit/compatibility_shim_audit.csv",
    "outputs/step55_compatibility_shim_audit/compatibility_shim_audit_summary.csv",
    "outputs/step55_compatibility_shim_audit/compatibility_shim_audit.json",
    "outputs/step55_test_strength_enum_audit/test_strength_enum_audit.csv",
    "outputs/step55_test_strength_enum_audit/test_strength_enum_audit_summary.csv",
    "outputs/step55_test_strength_enum_audit/test_strength_enum_audit.json",
    "outputs/step55_step54_regression_guard/step54_regression_guard.csv",
    "outputs/step55_step54_regression_guard/step54_regression_guard_summary.csv",
    "outputs/step55_step54_regression_guard/step54_regression_guard.json",
    "outputs/step55_artifact_manifest/artifact_manifest.csv",
    "outputs/step55_artifact_manifest/artifact_summary.csv",
    "outputs/step55_artifact_manifest/artifact_summary.json",
]

LOG_MARKERS = {
    "logs/step55_code_layout_audit.log": "[OK] Step 55 code layout audit finished",
    "logs/step55_import_boundary_audit.log": "[OK] Step 55 import boundary audit finished",
    "logs/step55_compatibility_shim_audit.log": "[OK] Step 55 compatibility shim audit finished",
    "logs/step55_test_strength_enum_audit.log": "[OK] Step 55 test strength enum audit finished",
    "logs/step55_step54_regression_guard.log": "[OK] Step 55 Step 54 regression guard finished",
    "logs/step55_artifact_manifest.log": "[OK] Step 55 artifact manifest finished",
}


def test_step55_required_files_outputs_and_logs_exist():
    missing = [path for path in REQUIRED_FILES + OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step55_code_layout_audit_passes():
    payload = read_json("outputs/step55_code_layout_audit/code_layout_audit.json")
    summary = payload["summary"]
    assert summary["code_layout_audit_pass"] is True
    assert summary["canonical_sim_package_exists"] is True
    assert summary["canonical_diagnostics_package_exists"] is True
    assert summary["canonical_evidence_package_exists"] is True
    assert summary["experiments_steps_package_exists"] is True
    assert int(summary["canonical_required_path_count"]) == int(summary["canonical_required_path_pass_count"])
    assert int(summary["unclassified_root_src_file_count"]) == 0
    assert int(summary["step55_new_root_evidence_file_count"]) == 0
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False


def test_step55_docs_and_readme_state_boundaries():
    report = read_text("STEP55_REPOSITORY_CODE_LAYOUT_SEPARATION_IMPORT_BOUNDARY_REPORT.md")
    docs = read_text("docs/55_repository_code_layout_separation_import_boundary.md")
    policy = read_text("docs/REPOSITORY_CODE_LAYOUT_POLICY.md")
    readme = read_text("README.md")
    joined = "\n".join([report, docs, policy, readme])
    for phrase in [
        "Step 55 does not change solver behavior.",
        "Step 55 does not add a 48^3 link-area run.",
        "Step 55 does not migrate LBM tau or viscosity formulas.",
        "Step 55 does not validate jet propulsion.",
        "Root `src/*.py` remains a compatibility and approved legacy surface",
    ]:
        assert phrase in joined


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
