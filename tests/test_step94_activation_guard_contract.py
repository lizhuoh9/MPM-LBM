import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step94_activation_guard_passes():
    payload = read_json("outputs/step94_activation_guard/activation_guard.json")
    summary = payload["summary"]

    assert summary["step94_activation_guard_pass"] is True
    assert summary["activation_feature_count"] == 4
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 1
    assert summary["ggui_visualization_enabled_count"] == 1
    assert summary["ggui_renderer_called_count"] == 1
    assert summary["ggui_screenshot_count"] == 1
    assert summary["real_geometry_candidate_enabled_count"] == 0
    assert summary["link_area_enabled_count"] == 0
    assert summary["write_vtk_count"] == 0
    assert summary["write_particles_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
