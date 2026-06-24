import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP98_ROW = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke"


def test_step97_48cube_taichi_ggui_visualization_expansion_guard_passes():
    payload = read_json(
        "outputs/step97_48cube_taichi_ggui_visualization_expansion_guard/"
        "48cube_taichi_ggui_visualization_expansion_guard.json"
    )
    summary = payload["summary"]

    assert summary["step97_48cube_taichi_ggui_visualization_expansion_guard_pass"] is True
    assert summary["step98_allowed_row_name"] == STEP98_ROW
    assert summary["step97_activation_feature_count"] == 0
    assert summary["planned_step98_activation_feature_count"] == 5
    assert summary["planned_step98_n_grid"] == 48
    assert summary["planned_step98_duration_lbm_steps"] == 1
    assert summary["previous_step96_n_grid"] == 32
    assert summary["previous_step96_n_lbm_steps"] == 10
    assert summary["duration_reduction_for_grid_expansion_isolation"] is True
    assert summary["ggui_visualization_planned_for_step98"] is True
    assert summary["ggui_screenshot_allowed_for_step98"] is True
    assert summary["ggui_video_allowed_for_step98"] is False
    assert summary["write_vtk_planned_for_step98"] is False
    assert summary["write_particles_allowed_for_step98"] is False
    assert summary["vtr_output_planned_for_step98"] is False
    assert summary["particle_npy_output_planned_for_step98"] is False
    assert summary["video_output_planned_for_step98"] is False
    assert summary["squid_proxy_planned_for_step98"] is True
    assert summary["runtime_geometry_planned_for_step98"] is True
    assert summary["wall_velocity_planned_for_step98"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step98"] is True
    assert summary["grid_48_planned_for_step98"] is True
    assert summary["grid_64_planned_for_step98"] is False
    assert summary["real_geometry_planned_for_step98"] is False
    assert summary["real_geometry_candidate_data_planned_for_step98"] is False
    assert summary["link_area_planned_for_step98"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
