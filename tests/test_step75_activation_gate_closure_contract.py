import json
from pathlib import Path

from src.mpm_lbm.evidence.activation_gate_closure_audit import build_step75_activation_gate_closure_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step75_activation_gate_closure_audit(ROOT)
    assert rows
    assert summary["activation_gate_closure_audit_pass"] is True
    assert summary["required_gate_count"] == 10
    assert summary["closed_gate_count"] == 10
    assert summary["activation_allowed_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step75_activation_gate_closure_audit/activation_gate_closure.json")
    assert payload["rows"]
    assert payload["summary"]["activation_gate_closure_audit_pass"] is True
    assert payload["summary"]["missing_gate_count"] == 0
    assert payload["summary"]["extra_gate_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
