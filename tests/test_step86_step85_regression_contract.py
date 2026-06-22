import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step86_step85_regression_guard_passes():
    payload = read_json("outputs/step86_step85_regression_guard/step85_regression_guard.json")
    summary = payload["summary"]

    assert summary["step86_step85_regression_guard_pass"] is True
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["step85_squid_proxy_static_geometry_activation_plan_pass"] is True
    assert summary["step85_squid_proxy_static_geometry_activation_guard_pass"] is True
    assert summary["step85_step84_regression_guard_pass"] is True
    assert summary["step85_step31_reference_guard_pass"] is True
    assert summary["step85_activation_feature_count"] == 0
    assert summary["planned_step86_activation_feature_count"] == 1
    assert summary["step85_driver_run_dir_count"] == 0
    assert summary["step85_vtr_count"] == 0
    assert summary["step85_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
