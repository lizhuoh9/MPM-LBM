import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP98_ROW = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_1step_ggui_visual_smoke"


def test_step97_48cube_taichi_ggui_visualization_expansion_plan_passes():
    payload = read_json(
        "outputs/step97_48cube_taichi_ggui_visualization_expansion_plan/"
        "48cube_taichi_ggui_visualization_expansion_plan.json"
    )
    summary = payload["summary"]

    assert summary["step97_48cube_taichi_ggui_visualization_expansion_plan_pass"] is True
    assert summary["step"] == "Step97"
    assert summary["previous_step"] == "Step96"
    assert summary["previous_commit"] == "9ec9877b1f997777a9b43792c52b0f2b84d3814e"
    assert summary["activation_kind"] == "48cube_taichi_ggui_visualization_expansion_plan_only"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["ggui_run_allowed"] is False
    assert summary["screenshot_output_allowed_in_step97"] is False
    assert summary["step98_allowed"] is True
    assert summary["step98_allowed_row_name"] == STEP98_ROW
    assert summary["step98_allowed_n_grid"] == 48
    assert summary["step98_allowed_n_particles"] == 1024
    assert summary["step98_allowed_n_lbm_steps"] == 1
    assert summary["step98_allowed_mpm_substeps_per_lbm_step"] == 1
    assert summary["from_step96_grid_expansion"] is True
    assert summary["previous_step96_n_grid"] == 32
    assert summary["planned_step98_n_grid"] == 48
    assert summary["from_step96_duration_reduction"] is True
    assert summary["previous_step96_n_lbm_steps"] == 10
    assert summary["planned_step98_n_lbm_steps"] == 1
    assert summary["grid_expansion_smoke_isolation_reason"] == "48^3 grid-expansion smoke isolation."
    assert summary["ggui_visualization_planned_for_step98"] is True
    assert summary["ggui_screenshot_allowed_for_step98"] is True
    assert summary["ggui_video_allowed_for_step98"] is False
    assert summary["step97_activation_feature_count"] == 0
    assert summary["planned_step98_activation_feature_count"] == 5
    assert summary["write_vtk_allowed"] is False
    assert summary["write_particles_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["video_output_allowed"] is False
    assert summary["squid_proxy_planned_for_step98"] is True
    assert summary["runtime_geometry_planned_for_step98"] is True
    assert summary["wall_velocity_planned_for_step98"] is True
    assert summary["grid_48_planned_for_step98"] is True
    assert summary["grid_64_allowed"] is False
    assert summary["target_u_lbm_allowed_for_step98"] == [0.0, 0.0, 0.0]
    assert summary["real_geometry_allowed"] is False
    assert summary["real_geometry_candidate_data_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["solver_behavior_changed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
