import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step95_taichi_ggui_10step_visualization_plan_passes():
    payload = read_json(
        "outputs/step95_taichi_ggui_10step_visualization_plan/"
        "taichi_ggui_10step_visualization_plan.json"
    )
    summary = payload["summary"]

    assert summary["step95_taichi_ggui_10step_visualization_plan_pass"] is True
    assert summary["previous_step"] == "Step94"
    assert summary["previous_commit"] == "a255713f9148f8046b81595d6e2ce4152920d057"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["ggui_run_allowed"] is False
    assert summary["screenshot_output_allowed_in_step95"] is False
    assert summary["step96_allowed"] is True
    assert summary["step96_allowed_row_name"] == (
        "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_ggui_visual_run"
    )
    assert summary["step96_allowed_n_grid"] == 32
    assert summary["step96_allowed_n_particles"] == 1024
    assert summary["step96_allowed_n_lbm_steps"] == 10
    assert summary["step96_allowed_mpm_substeps_per_lbm_step"] == 1
    assert summary["from_step94_duration_expansion"] is True
    assert summary["previous_step94_n_lbm_steps"] == 1
    assert summary["planned_step96_n_lbm_steps"] == 10
    assert summary["from_step92_adds_ggui_visualization"] is True
    assert summary["previous_step92_n_lbm_steps"] == 10
    assert summary["ggui_visualization_planned_for_step96"] is True
    assert summary["ggui_interactive_window_allowed_for_step96"] is True
    assert summary["ggui_screenshot_allowed_for_step96"] is True
    assert summary["ggui_video_allowed_for_step96"] is False
    assert summary["step95_activation_feature_count"] == 0
    assert summary["planned_step96_activation_feature_count"] == 4
    assert summary["write_vtk_allowed"] is False
    assert summary["write_particles_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["video_output_allowed"] is False
    assert summary["squid_proxy_planned_for_step96"] is True
    assert summary["runtime_geometry_planned_for_step96"] is True
    assert summary["wall_velocity_planned_for_step96"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step96"] is True
    assert summary["target_u_lbm_allowed_for_step96"] == [0.0, 0.0, 0.0]
    assert summary["real_geometry_allowed"] is False
    assert summary["real_geometry_candidate_data_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["grid_48_allowed"] is False
    assert summary["grid_64_allowed"] is False
    assert summary["solver_behavior_changed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
