import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step84_step80_regression_guard_passes():
    payload = read_json("outputs/step84_step80_regression_guard/step80_regression_guard.json")
    summary = payload["summary"]
    assert summary["step84_step80_regression_guard_pass"] is True
    assert summary["step80_activation_feature_count"] == 1
    assert summary["step80_runtime_geometry_enabled_count"] == 1
    assert summary["step80_wall_velocity_enabled_count"] == 0
    assert summary["step80_combined_runtime_geometry_wall_velocity_enabled_count"] == 0
    assert summary["step80_vtr_count"] == 0
    assert summary["step80_particle_npy_count"] == 0
    assert summary["step80_artifact_budget_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
