import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step101_48cube_10step_taichi_ggui_visualization_guard_passes():
    payload = read_json(
        "outputs/step101_48cube_10step_taichi_ggui_visualization_guard/"
        "48cube_10step_taichi_ggui_visualization_guard.json"
    )
    summary = payload["summary"]

    assert summary["step101_48cube_10step_taichi_ggui_visualization_guard_pass"] is True
    assert summary["guard_row_count"] > 0
    assert summary["guard_pass_count"] == summary["guard_row_count"]
    assert summary["step101_activation_feature_count"] == 0
    assert summary["planned_step102_activation_feature_count"] == 5
    assert summary["planned_step102_n_grid"] == 48
    assert summary["planned_step102_n_lbm_steps"] == 10
    assert summary["from_step100_duration_expansion"] is True
    assert summary["ggui_visualization_planned_for_step102"] is True
    assert summary["ggui_screenshot_allowed_for_step102"] is True
    assert summary["ggui_video_allowed_for_step102"] is False
    assert summary["squid_proxy_planned_for_step102"] is True
    assert summary["runtime_geometry_planned_for_step102"] is True
    assert summary["wall_velocity_planned_for_step102"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step102"] is True
    assert summary["vtr_output_planned_for_step102"] is False
    assert summary["particle_npy_output_planned_for_step102"] is False
    assert summary["video_output_planned_for_step102"] is False
    assert summary["real_geometry_planned_for_step102"] is False
    assert summary["real_geometry_candidate_data_planned_for_step102"] is False
    assert summary["link_area_planned_for_step102"] is False
    assert summary["grid_64_planned_for_step102"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
