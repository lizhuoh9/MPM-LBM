import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step96_step92_regression_guard_passes():
    payload = read_json("outputs/step96_step92_regression_guard/step92_regression_guard.json")
    summary = payload["summary"]

    assert summary["step96_step92_regression_guard_pass"] is True
    assert summary["step92_first_user_simulation_10step_dry_run_matrix_pass"] is True
    assert summary["step92_first_user_simulation_10step_dry_run_quality_pass"] is True
    assert summary["step92_activation_guard_pass"] is True
    assert summary["step92_output_guard_pass"] is True
    assert summary["step92_artifact_budget_pass"] is True
    assert summary["step92_activation_feature_count"] == 3
    assert summary["step92_squid_proxy_enabled_count"] == 1
    assert summary["step92_runtime_geometry_enabled_count"] == 1
    assert summary["step92_wall_velocity_enabled_count"] == 1
    assert summary["step92_completed_lbm_steps"] == 10
    assert summary["vtr_file_count"] == 0
    assert summary["step92_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
