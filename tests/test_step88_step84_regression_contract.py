import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step88_step84_regression_guard_passes():
    payload = read_json("outputs/step88_step84_regression_guard/step84_regression_guard.json")
    summary = payload["summary"]

    assert summary["step88_step84_regression_guard_pass"] is True
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["step84_activation_feature_count"] == 2
    assert summary["step84_runtime_geometry_enabled_count"] == 1
    assert summary["step84_wall_velocity_enabled_count"] == 1
    assert summary["step84_combined_runtime_geometry_wall_velocity_enabled_count"] == 1
    assert summary["step84_squid_proxy_enabled_count"] == 0
    assert summary["step84_particle_npy_count"] == 0
    assert summary["step84_vtr_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
