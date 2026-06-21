import json
from pathlib import Path

from src.mpm_lbm.evidence.output_artifact_policy_audit import build_step70_output_artifact_policy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step70_output_artifact_policy_audit(ROOT)
    assert rows
    assert summary["output_artifact_policy_audit_pass"] is True
    assert summary["vtr_default_allowed"] is False
    assert summary["particle_npy_default_allowed"] is False
    assert summary["protected_external_edit_allowed"] is False
    assert summary["protected_real_geometry_edit_allowed"] is False
    assert summary["report_consistency_required"] is True
    assert summary["artifact_manifest_required"] is True


def test_artifact_passes():
    payload = read_json("outputs/step70_output_artifact_policy_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["output_artifact_policy_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
