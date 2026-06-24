import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step101_step100_regression_guard_passes():
    payload = read_json("outputs/step101_step100_regression_guard/step100_regression_guard.json")
    summary = payload["summary"]

    assert summary["step101_step100_regression_guard_pass"] is True
    assert summary["step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass"] is True
    assert summary["step100_48cube_5step_taichi_ggui_visualization_quality_pass"] is True
    assert summary["step100_activation_guard_pass"] is True
    assert summary["step100_output_guard_pass"] is True
    assert summary["step100_step99_regression_guard_pass"] is True
    assert summary["step100_step98_regression_guard_pass"] is True
    assert summary["step100_step96_regression_guard_pass"] is True
    assert summary["step100_artifact_budget_pass"] is True
    assert summary["step100_activation_feature_count"] == 5
    assert summary["step100_completed_lbm_steps"] == 5
    assert summary["step100_n_grid"] == 48
    assert summary["step100_grid_48_enabled_count"] == 1
    assert summary["step100_grid_64_enabled_count"] == 0
    assert summary["step100_squid_proxy_enabled_count"] == 1
    assert summary["step100_runtime_geometry_enabled_count"] == 1
    assert summary["step100_wall_velocity_enabled_count"] == 1
    assert summary["step100_ggui_screenshot_count"] == 1
    assert summary["step100_ggui_video_count"] == 0
    assert summary["step100_vtr_count"] == 0
    assert summary["step100_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
