import json
from pathlib import Path

from src.mpm_lbm.evidence.step74_full_activation_gate_coverage_audit import (
    build_step74_full_activation_gate_coverage_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step74_full_activation_gate_coverage_audit(ROOT)
    assert rows
    assert summary["full_activation_gate_coverage_audit_pass"] is True
    assert summary["required_gate_count"] == 10
    assert summary["closed_gate_count"] == 10
    assert summary["activation_allowed_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step74_full_activation_gate_coverage_audit/full_activation_gate_coverage.json")
    assert payload["rows"]
    assert payload["summary"]["full_activation_gate_coverage_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
