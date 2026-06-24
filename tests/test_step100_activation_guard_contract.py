import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP100_ROW = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run"


def test_step100_activation_guard_passes():
    payload = read_json("outputs/step100_activation_guard/activation_guard.json")
    summary = payload["summary"]

    assert summary["step100_activation_guard_pass"] is True
    assert summary["activation_feature_count"] == 5
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 1
    assert summary["ggui_visualization_enabled_count"] == 1
    assert summary["grid_48_enabled_count"] == 1
    assert summary["grid_64_enabled_count"] == 0
    assert summary["ggui_renderer_called_count"] == 1
    assert summary["ggui_screenshot_count"] == 1
    assert summary["real_geometry_candidate_enabled_count"] == 0
    assert summary["real_geometry_enabled_count"] == 0
    assert summary["link_area_enabled_count"] == 0
    assert summary["write_vtk_count"] == 0
    assert summary["write_particles_count"] == 0
    assert summary["required_row_name"] == STEP100_ROW


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
