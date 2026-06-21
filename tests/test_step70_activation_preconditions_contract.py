import json
from pathlib import Path

from src.mpm_lbm.evidence.activation_preconditions_audit import build_step70_activation_preconditions_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step70_activation_preconditions_audit(ROOT)
    assert rows
    assert summary["activation_preconditions_audit_pass"] is True
    assert summary["activation_allowed_count"] == 0
    assert summary["pending_gate_count"] >= 5


def test_artifact_passes():
    payload = read_json("outputs/step70_activation_preconditions_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["activation_preconditions_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
