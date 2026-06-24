import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP102_ROW = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_10step_ggui_visual_run"


def test_step101_48cube_10step_taichi_ggui_visualization_plan_passes():
    payload = read_json(
        "outputs/step101_48cube_10step_taichi_ggui_visualization_plan/"
        "48cube_10step_taichi_ggui_visualization_plan.json"
    )
    summary = payload["summary"]

    assert summary["step101_48cube_10step_taichi_ggui_visualization_plan_pass"] is True
    assert summary["previous_step"] == "Step100"
    assert summary["previous_commit"] == "c0f74ad299451b1f27ce172bf77e7d497e8022a0"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["ggui_run_allowed"] is False
    assert summary["screenshot_output_allowed_in_step101"] is False
    assert summary["step102_allowed"] is True
    assert summary["step102_allowed_row_name"] == STEP102_ROW
    assert summary["step102_allowed_n_grid"] == 48
    assert summary["step102_allowed_n_particles"] == 1024
    assert summary["step102_allowed_n_lbm_steps"] == 10
    assert summary["from_step100_duration_expansion"] is True
    assert summary["previous_step100_n_grid"] == 48
    assert summary["previous_step100_n_lbm_steps"] == 5
    assert summary["planned_step102_n_grid"] == 48
    assert summary["planned_step102_n_lbm_steps"] == 10
    assert summary["only_new_dimension_from_step100"] == "n_lbm_steps_10"
    assert summary["ggui_visualization_planned_for_step102"] is True
    assert summary["ggui_screenshot_allowed_for_step102"] is True
    assert summary["ggui_video_allowed_for_step102"] is False
    assert summary["write_vtk_allowed"] is False
    assert summary["write_particles_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["video_output_allowed"] is False
    assert summary["grid_64_allowed"] is False
    assert summary["grid_convergence_claim_allowed"] is False
    assert summary["step101_activation_feature_count"] == 0
    assert summary["planned_step102_activation_feature_count"] == 5


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
