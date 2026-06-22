import json
from pathlib import Path

from src.mpm_lbm.evidence.candidate_manifest_policy_audit import build_step74_candidate_manifest_policy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step74_candidate_manifest_policy_audit(ROOT)
    assert rows
    assert summary["candidate_manifest_policy_audit_pass"] is True
    assert summary["absolute_path_redaction_pass"] is True
    assert summary["large_file_policy_enforced"] is True
    assert summary["unavailable_source_policy_enforced"] is True
    assert summary["duplicate_candidate_id_rejected"] is True
    assert summary["real_geometry_candidate_edit_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step74_candidate_manifest_policy_audit/candidate_manifest_policy.json")
    assert payload["rows"]
    assert payload["summary"]["candidate_manifest_policy_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
