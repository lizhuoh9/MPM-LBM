import json
from pathlib import Path

from src.mpm_lbm.evidence.runtime_geometry_state_guard_audit import build_step72_runtime_geometry_state_guard_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step72_runtime_geometry_state_guard_audit(ROOT)
    assert rows
    assert summary["runtime_geometry_state_guard_audit_pass"] is True
    assert summary["config_mutation_flag_enabled_count"] == 0
    assert summary["driver_run"] is False


def test_artifact_passes():
    payload = read_json("outputs/step72_runtime_geometry_state_guard_audit/runtime_geometry_state_guard.json")
    assert payload["rows"]
    assert payload["summary"]["runtime_geometry_state_guard_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
