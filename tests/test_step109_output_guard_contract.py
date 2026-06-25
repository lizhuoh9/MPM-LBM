import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step109_output_guard_blocks_official_payloads_and_validation_claims():
    payload = read_json("outputs/step109_output_guard/output_guard_report.json")
    summary = payload["summary"]

    assert summary["output_guard_pass"] is True
    assert summary["official_case_file_count"] == 0
    assert summary["official_mesh_file_count"] == 0
    assert summary["official_journal_file_count"] == 0
    assert summary["official_case_data_h5_count"] == 0
    assert summary["official_png_committed_count"] == 0
    assert summary["private_fluent_csv_committed_count"] == 0
    assert summary["validation_claim_count"] == 0
    assert summary["direct_equivalence_claim_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0
    assert summary["step109_forbidden_file_count"] == 0
    assert summary["artifact_budget_pass"] is True


def test_step109_artifact_manifest_is_small_and_step_scoped():
    payload = read_json("outputs/step109_artifact_manifest/artifact_manifest.json")
    summary = payload["summary"]

    assert summary["artifact_manifest_pass"] is True
    assert summary["step109_file_count"] > 0
    assert summary["step109_total_size_mb"] < 40.0
    assert summary["step109_ansys_proprietary_file_count"] == 0
    assert summary["step109_official_image_count"] == 0
    assert summary["step109_driver_run_dir_count"] >= 5


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
