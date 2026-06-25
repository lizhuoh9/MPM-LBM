import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step107_output_guard_blocks_official_payloads_and_validation_claims():
    payload = read_json("outputs/step107_output_guard/output_guard_report.json")
    summary = payload["summary"]
    paths = [row["path"] for row in payload["rows"]]

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
    assert summary["artifact_budget_pass"] is True
    assert all(not path.startswith("outputs/step107_artifact_manifest/") for path in paths)
    assert all(not path.startswith("outputs/step107_output_guard/") for path in paths)


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
