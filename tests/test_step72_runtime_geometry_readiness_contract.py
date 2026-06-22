import json
from pathlib import Path

from src.mpm_lbm.evidence.runtime_geometry_readiness_audit import build_step72_runtime_geometry_readiness_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step72_runtime_geometry_readiness_audit(ROOT)
    assert rows
    assert summary["runtime_geometry_readiness_audit_pass"] is True
    assert summary["required_audit_pass_count"] == summary["required_audit_count"]
    assert summary["closed_gate_pass_count"] == summary["required_closed_gate_count"]
    assert summary["activation_allowed_after_step72"] is False


def test_artifact_passes():
    payload = read_json("outputs/step72_runtime_geometry_readiness_audit/runtime_geometry_readiness.json")
    assert payload["rows"]
    assert payload["summary"]["runtime_geometry_readiness_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
