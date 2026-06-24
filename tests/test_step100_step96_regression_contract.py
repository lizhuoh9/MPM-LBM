import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step100_step96_regression_guard_passes():
    payload = read_json("outputs/step100_step96_regression_guard/step96_regression_guard.json")
    summary = payload["summary"]

    assert summary["step100_step96_regression_guard_pass"] is True
    assert summary["step96_taichi_ggui_10step_visualization_run_matrix_pass"] is True
    assert summary["step96_taichi_ggui_10step_visualization_quality_pass"] is True
    assert summary["step96_activation_guard_pass"] is True
    assert summary["step96_output_guard_pass"] is True
    assert summary["step96_artifact_budget_pass"] is True
    assert summary["step96_activation_feature_count"] == 4
    assert summary["step96_completed_lbm_steps"] == 10
    assert summary["step96_n_grid"] == 32
    assert summary["step96_squid_proxy_enabled_count"] == 1
    assert summary["step96_runtime_geometry_enabled_count"] == 1
    assert summary["step96_wall_velocity_enabled_count"] == 1
    assert summary["step96_ggui_screenshot_count"] == 1
    assert summary["step96_ggui_video_count"] == 0
    assert summary["step96_vtr_count"] == 0
    assert summary["step96_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
