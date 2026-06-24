import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP100_ROW = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run"


def test_step100_48cube_5step_taichi_ggui_visualization_run_matrix_passes():
    payload = read_json(
        "outputs/step100_48cube_5step_taichi_ggui_visualization_run_matrix/"
        "48cube_5step_taichi_ggui_visualization_run_matrix.json"
    )
    summary = payload["summary"]
    row = payload["rows"][0]

    assert summary["step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["required_stable_count"] == 1
    assert summary["activation_feature_count"] == 5
    assert summary["grid_48_enabled_count"] == 1
    assert summary["grid_64_enabled_count"] == 0
    assert summary["ggui_visualization_enabled_count"] == 1
    assert summary["ggui_renderer_called_count"] == 1
    assert summary["ggui_screenshot_count"] == 1
    assert summary["ggui_video_file_count"] == 0
    assert summary["vtr_output_count"] == 0
    assert summary["particle_npy_output_count"] == 0
    assert summary["min_completed_lbm_steps"] == 5
    assert summary["min_diagnostics_row_count"] >= 6
    assert summary["runtime_code_changed"] is False
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] == "48cube_5step_taichi_ggui_visualization_run_only"

    assert row["row_name"] == STEP100_ROW
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["n_grid"] == 48
    assert row["n_particles"] == 1024
    assert row["n_lbm_steps"] == 5
    assert row["completed_lbm_steps"] == 5
    assert row["total_mpm_substeps"] >= 5
    assert row["diagnostics_row_count"] >= 6
    assert row["stable"] is True
    assert row["from_step98_duration_expansion"] is True
    assert row["previous_step98_n_grid"] == 48
    assert row["previous_step98_n_lbm_steps"] == 1
    assert row["step100_n_grid"] == 48
    assert row["step100_n_lbm_steps"] == 5
    assert row["only_new_dimension_from_step98"] == "n_lbm_steps_5"
    assert row["grid_48_enabled"] is True
    assert row["grid_64_enabled"] is False
    assert row["ggui_visualization_enabled"] is True
    assert row["ggui_window_created"] is True
    assert row["ggui_scene_created"] is True
    assert row["ggui_camera_configured"] is True
    assert row["ggui_rendered_frame_count"] >= 1
    assert row["ggui_screenshot_exists"] is True
    assert row["ggui_screenshot_file_count"] == 1
    assert row["ggui_screenshot_size_bytes"] > 0
    assert row["ggui_video_enabled"] is False
    assert row["ggui_render_report_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
