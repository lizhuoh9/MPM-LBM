import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step80_activation_guard_artifact_passes():
    payload = read_json("outputs/step80_activation_guard/activation_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step80_runtime_geometry_diagnostic_only_activation_guard_pass"] is True
    assert summary["step80_activation_guard_pass"] is True
    assert summary["pass_count"] == summary["row_count"]
    assert summary["activation_feature_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 0
    assert summary["planned_step80_activation_feature_count"] == 1


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
