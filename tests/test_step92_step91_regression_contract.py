import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step92_step91_regression_guard_passes():
    payload = read_json("outputs/step92_step91_regression_guard/step91_regression_guard.json")
    summary = payload["summary"]

    assert summary["step92_step91_regression_guard_pass"] is True
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["step91_artifact_budget_pass"] is True
    assert summary["step91_activation_feature_count"] == 0
    assert summary["planned_step92_activation_feature_count"] == 3
    assert summary["step92_allowed_row_name"] == (
        "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run"
    )
    assert summary["step92_allowed_n_lbm_steps"] == 10
    assert summary["step91_driver_run_dir_count"] == 0
    assert summary["step91_vtr_count"] == 0
    assert summary["step91_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
