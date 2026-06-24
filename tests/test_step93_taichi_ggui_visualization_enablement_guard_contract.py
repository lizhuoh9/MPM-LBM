import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step93_taichi_ggui_visualization_enablement_guard_passes():
    payload = read_json(
        "outputs/step93_taichi_ggui_visualization_enablement_guard/"
        "taichi_ggui_visualization_enablement_guard.json"
    )
    summary = payload["summary"]

    assert summary["step93_taichi_ggui_visualization_enablement_guard_pass"] is True
    assert summary["guard_pass_count"] == summary["guard_row_count"]
    assert summary["step93_activation_feature_count"] == 0
    assert summary["planned_step94_activation_feature_count"] == 4
    assert summary["planned_step94_duration_lbm_steps"] == 1
    assert summary["previous_step92_n_lbm_steps"] == 10
    assert summary["duration_reduction_for_visualization_isolation"] is True
    assert summary["ggui_visualization_smoke_isolation"] is True
    assert summary["only_new_feature_from_step92"] == "taichi_ggui_visualization"
    assert summary["ggui_visualization_planned_for_step94"] is True
    assert summary["ggui_interactive_window_allowed_for_step94"] is True
    assert summary["ggui_screenshot_allowed_for_step94"] is True
    assert summary["ggui_video_allowed_for_step94"] is False
    assert summary["write_vtk_planned_for_step94"] is False
    assert summary["write_particles_allowed_for_step94"] is False
    assert summary["vtr_route_allowed_for_step94"] is False
    assert summary["particle_npy_output_planned_for_step94"] is False
    assert summary["squid_proxy_planned_for_step94"] is True
    assert summary["runtime_geometry_planned_for_step94"] is True
    assert summary["wall_velocity_planned_for_step94"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step94"] is True
    assert summary["geometry_motion_application_mode_planned_for_step94"] == "diagnostic_only"
    assert summary["wall_velocity_application_mode_planned_for_step94"] == "solid_vel_experimental"
    assert summary["target_lbm_field_planned_for_step94"] == "solid_vel"
    assert summary["target_u_lbm_planned_for_step94"] == [0.0, 0.0, 0.0]
    assert summary["real_geometry_planned_for_step94"] is False
    assert summary["real_geometry_candidate_data_planned_for_step94"] is False
    assert summary["link_area_planned_for_step94"] is False
    assert summary["grid_48_planned_for_step94"] is False
    assert summary["grid_64_planned_for_step94"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
