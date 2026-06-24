import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step94_taichi_ggui_visualization_smoke_matrix_passes():
    payload = read_json(
        "outputs/step94_taichi_ggui_visualization_smoke_matrix/taichi_ggui_visualization_smoke_matrix.json"
    )
    summary = payload["summary"]
    row = payload["rows"][0]

    assert summary["step94_taichi_ggui_visualization_smoke_matrix_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["required_stable_count"] == 1
    assert summary["activation_feature_count"] == 4
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["ggui_visualization_enabled_count"] == 1
    assert summary["ggui_renderer_called_count"] == 1
    assert summary["ggui_screenshot_count"] == 1
    assert summary["ggui_video_file_count"] == 0
    assert summary["vtr_output_count"] == 0
    assert summary["particle_npy_output_count"] == 0

    assert row["row_name"] == (
        "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_1step_ggui_visual_smoke"
    )
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["completed_lbm_steps"] == 1
    assert row["diagnostics_row_count"] >= 2
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
    assert row["stable"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
