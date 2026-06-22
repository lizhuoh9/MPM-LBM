import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step84_activation_guard_passes():
    payload = read_json("outputs/step84_activation_guard/activation_guard.json")
    summary = payload["summary"]

    assert summary["step84_activation_guard_pass"] is True
    assert summary["activation_feature_count"] == 2
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 1
    assert summary["planned_step84_activation_feature_count"] == 2


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
