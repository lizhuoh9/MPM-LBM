import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step93_taichi_ggui_visualization_enablement_plan_passes():
    payload = read_json(
        "outputs/step93_taichi_ggui_visualization_enablement_plan/"
        "taichi_ggui_visualization_enablement_plan.json"
    )
    summary = payload["summary"]

    assert summary["step93_taichi_ggui_visualization_enablement_plan_pass"] is True
    assert summary["previous_step"] == "Step92"
    assert summary["previous_commit"] == "40a67ece3b6e8d77fb6356fe5e97dc25a3037372"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["step94_allowed"] is True
    assert summary["step94_allowed_row_name"] == (
        "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke"
    )
    assert summary["step94_allowed_n_grid"] == 32
    assert summary["step94_allowed_n_particles"] == 1024
    assert summary["step94_allowed_n_lbm_steps"] == 1
    assert summary["step94_allowed_mpm_substeps_per_lbm_step"] == 1
    assert summary["ggui_visualization_planned_for_step94"] is True
    assert summary["ggui_interactive_window_allowed_for_step94"] is True
    assert summary["ggui_screenshot_allowed_for_step94"] is True
    assert summary["ggui_video_allowed_for_step94"] is False
    assert summary["write_vtk_allowed"] is False
    assert summary["write_particles_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["previous_step92_n_lbm_steps"] == 10
    assert summary["planned_step94_n_lbm_steps"] == 1
    assert summary["duration_reduction_for_visualization_isolation"] is True
    assert summary["only_new_feature_from_step92"] == "taichi_ggui_visualization"
    assert summary["step93_activation_feature_count"] == 0
    assert summary["planned_step94_activation_feature_count"] == 4
    assert summary["squid_proxy_planned_for_step94"] is True
    assert summary["runtime_geometry_planned_for_step94"] is True
    assert summary["wall_velocity_planned_for_step94"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step94"] is True
    assert summary["target_u_lbm_allowed_for_step94"] == [0.0, 0.0, 0.0]
    assert summary["real_geometry_allowed"] is False
    assert summary["real_geometry_candidate_data_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["grid_48_allowed"] is False
    assert summary["grid_64_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
