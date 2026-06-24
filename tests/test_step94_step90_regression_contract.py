import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step94_step90_regression_guard_passes():
    payload = read_json("outputs/step94_step90_regression_guard/step90_regression_guard.json")
    summary = payload["summary"]

    assert summary["step94_step90_regression_guard_pass"] is True
    assert summary["step90_first_user_simulation_dry_run_matrix_pass"] is True
    assert summary["step90_first_user_simulation_dry_run_quality_pass"] is True
    assert summary["step90_activation_guard_pass"] is True
    assert summary["step90_output_guard_pass"] is True
    assert summary["step90_artifact_budget_pass"] is True
    assert summary["step90_activation_feature_count"] == 3
    assert summary["step90_squid_proxy_enabled_count"] == 1
    assert summary["step90_runtime_geometry_enabled_count"] == 1
    assert summary["step90_wall_velocity_enabled_count"] == 1
    assert summary["step90_completed_lbm_steps"] == 5
    assert summary["step90_vtr_count"] == 0
    assert summary["step90_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
