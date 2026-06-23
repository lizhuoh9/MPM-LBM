import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step89_step88_regression_guard_passes():
    payload = read_json("outputs/step89_step88_regression_guard/step88_regression_guard.json")
    summary = payload["summary"]

    assert summary["step89_step88_regression_guard_pass"] is True
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["step88_artifact_budget_pass"] is True
    assert summary["step88_activation_feature_count"] == 3
    assert summary["step88_squid_proxy_enabled_count"] == 1
    assert summary["step88_runtime_geometry_enabled_count"] == 1
    assert summary["step88_wall_velocity_enabled_count"] == 1
    assert summary["step88_combined_runtime_geometry_wall_velocity_enabled_count"] == 1
    assert summary["step88_real_geometry_candidate_enabled_count"] == 0
    assert summary["step88_link_area_enabled_count"] == 0
    assert summary["step88_vtr_count"] == 0
    assert summary["step88_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
