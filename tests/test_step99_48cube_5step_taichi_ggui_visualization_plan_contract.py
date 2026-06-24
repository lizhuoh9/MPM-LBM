import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP100_ROW = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run"


def test_step99_48cube_5step_taichi_ggui_visualization_plan_passes():
    payload = read_json(
        "outputs/step99_48cube_5step_taichi_ggui_visualization_plan/"
        "48cube_5step_taichi_ggui_visualization_plan.json"
    )
    summary = payload["summary"]

    assert summary["step99_48cube_5step_taichi_ggui_visualization_plan_pass"] is True
    assert summary["step"] == "Step99"
    assert summary["previous_step"] == "Step98"
    assert summary["previous_commit"] == "3142aea8361fd67c4799143ee56f95b8a09b3286"

    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["ggui_run_allowed"] is False
    assert summary["screenshot_output_allowed_in_step99"] is False

    assert summary["step100_allowed"] is True
    assert summary["step100_allowed_row_name"] == STEP100_ROW
    assert summary["step100_allowed_n_grid"] == 48
    assert summary["step100_allowed_n_particles"] == 1024
    assert summary["step100_allowed_n_lbm_steps"] == 5
    assert summary["step100_allowed_mpm_substeps_per_lbm_step"] == 1

    assert summary["from_step98_duration_expansion"] is True
    assert summary["previous_step98_n_grid"] == 48
    assert summary["previous_step98_n_lbm_steps"] == 1
    assert summary["planned_step100_n_grid"] == 48
    assert summary["planned_step100_n_lbm_steps"] == 5
    assert summary["only_new_dimension_from_step98"] == "n_lbm_steps_5"

    assert summary["ggui_visualization_planned_for_step100"] is True
    assert summary["ggui_screenshot_allowed_for_step100"] is True
    assert summary["ggui_video_allowed_for_step100"] is False

    assert summary["write_vtk_allowed"] is False
    assert summary["write_particles_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["video_output_allowed"] is False
    assert summary["grid_64_allowed"] is False
    assert summary["real_geometry_allowed"] is False
    assert summary["real_geometry_candidate_data_allowed"] is False
    assert summary["link_area_allowed"] is False

    assert summary["step99_activation_feature_count"] == 0
    assert summary["planned_step100_activation_feature_count"] == 5
    assert summary["solver_behavior_changed"] is False
    assert summary["physical_validation_claim_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
