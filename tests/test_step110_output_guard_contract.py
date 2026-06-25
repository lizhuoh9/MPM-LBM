import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step110_output_guard_blocks_official_payloads_and_validation_claims():
    guard = read_json("outputs/step110_output_guard/output_guard_report.json")["summary"]
    manifest = read_json("outputs/step110_artifact_manifest/artifact_manifest.json")["summary"]

    assert guard["output_guard_pass"] is True
    assert guard["official_case_file_count"] == 0
    assert guard["official_mesh_file_count"] == 0
    assert guard["official_journal_file_count"] == 0
    assert guard["official_case_data_h5_count"] == 0
    assert guard["validation_claim_count"] == 0
    assert guard["direct_equivalence_claim_count"] == 0
    assert guard["protected_external_edit_count"] == 0
    assert guard["protected_real_geometry_candidate_edit_count"] == 0
    assert manifest["artifact_manifest_pass"] is True
    assert manifest["step110_ansys_proprietary_file_count"] == 0


def test_step110_docs_and_report_exist():
    assert (ROOT / "STEP110_FLUENT_PUBLIC_PLOT_ERROR_MINIMIZED_PREFLOW_MONITOR_CANDIDATE_GOAL.md").is_file()
    assert (ROOT / "STEP110_FLUENT_PUBLIC_PLOT_ERROR_MINIMIZED_PREFLOW_MONITOR_CANDIDATE_REPORT.md").is_file()
    assert (ROOT / "docs/110_fluent_public_plot_error_minimized_preflow_monitor_candidate.md").is_file()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Step 110 Fluent public-plot error-minimized proxy candidate" in readme


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)

