import json
from pathlib import Path

from src.mpm_lbm.evidence.candidate_descriptor_schema_audit import build_step74_candidate_descriptor_schema_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step74_candidate_descriptor_schema_audit(ROOT)
    assert rows
    assert summary["candidate_descriptor_schema_audit_pass"] is True
    assert summary["valid_descriptor_pass_count"] == 1
    assert summary["invalid_descriptor_rejected_count"] == summary["invalid_descriptor_required_count"]
    assert summary["private_absolute_path_policy_enforced"] is True
    assert summary["external_path_rejected"] is True


def test_artifact_passes():
    payload = read_json("outputs/step74_candidate_descriptor_schema_audit/candidate_descriptor_schema.json")
    assert payload["rows"]
    assert payload["summary"]["candidate_descriptor_schema_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
