import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step84_step83_regression_guard_passes():
    payload = read_json("outputs/step84_step83_regression_guard/step83_regression_guard.json")
    summary = payload["summary"]
    assert summary["step84_step83_regression_guard_pass"] is True
    assert summary["step83_runtime_geometry_wall_velocity_combined_activation_plan_pass"] is True
    assert summary["step83_runtime_geometry_wall_velocity_combined_activation_guard_pass"] is True
    assert summary["step83_step82_regression_guard_pass"] is True
    assert summary["step83_step80_regression_guard_pass"] is True
    assert summary["step83_output_guard_pass"] is True
    assert summary["step83_artifact_budget_pass"] is True
    assert summary["step83_activation_feature_count"] == 0
    assert summary["planned_step84_activation_feature_count"] == 2
    assert summary["step83_driver_run_dir_count"] == 0
    assert summary["step83_vtr_count"] == 0
    assert summary["step83_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
