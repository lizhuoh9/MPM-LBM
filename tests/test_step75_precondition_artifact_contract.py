import json
from pathlib import Path

from src.mpm_lbm.evidence.precondition_artifact_audit import build_step75_precondition_artifact_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step75_precondition_artifact_audit(ROOT)
    assert rows
    assert summary["precondition_artifact_audit_pass"] is True
    assert summary["required_artifact_count"] == 35
    assert summary["present_artifact_count"] == summary["required_artifact_count"]
    assert summary["green_artifact_count"] == summary["required_artifact_count"]
    assert summary["step71_pass"] is True
    assert summary["step72_pass"] is True
    assert summary["step73_pass"] is True
    assert summary["step74_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step75_precondition_artifact_audit/precondition_artifact.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["precondition_artifact_audit_pass"] is True
    assert summary["failed_artifact_count"] == 0
    assert summary["missing_artifact_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
