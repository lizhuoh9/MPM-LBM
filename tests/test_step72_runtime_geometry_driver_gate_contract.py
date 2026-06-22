import json
from pathlib import Path

from src.mpm_lbm.evidence.runtime_geometry_driver_gate_audit import build_step72_runtime_geometry_driver_gate_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step72_runtime_geometry_driver_gate_audit(ROOT)
    assert rows
    assert summary["runtime_geometry_driver_gate_audit_pass"] is True
    assert summary["default_gate_closed"] is True
    assert summary["invalid_combination_rejected_count"] == summary["invalid_combination_count"]
    assert summary["safe_output_defaults_preserved"] is True
    assert summary["driver_run"] is False


def test_artifact_passes():
    payload = read_json("outputs/step72_runtime_geometry_driver_gate_audit/runtime_geometry_driver_gate.json")
    assert payload["rows"]
    assert payload["summary"]["runtime_geometry_driver_gate_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
