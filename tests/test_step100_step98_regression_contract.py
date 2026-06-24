import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step100_step98_regression_guard_passes():
    payload = read_json("outputs/step100_step98_regression_guard/step98_regression_guard.json")
    summary = payload["summary"]

    assert summary["step100_step98_regression_guard_pass"] is True
    assert summary["step98_48cube_taichi_ggui_visualization_smoke_matrix_pass"] is True
    assert summary["step98_48cube_taichi_ggui_visualization_quality_pass"] is True
    assert summary["step98_activation_guard_pass"] is True
    assert summary["step98_output_guard_pass"] is True
    assert summary["step98_artifact_budget_pass"] is True
    assert summary["step98_activation_feature_count"] == 5
    assert summary["step98_completed_lbm_steps"] == 1
    assert summary["step98_n_grid"] == 48
    assert summary["step98_grid_48_enabled_count"] == 1
    assert summary["step98_grid_64_enabled_count"] == 0
    assert summary["step98_squid_proxy_enabled_count"] == 1
    assert summary["step98_runtime_geometry_enabled_count"] == 1
    assert summary["step98_wall_velocity_enabled_count"] == 1
    assert summary["step98_ggui_screenshot_count"] == 1
    assert summary["step98_ggui_video_count"] == 0
    assert summary["step98_vtr_count"] == 0
    assert summary["step98_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
