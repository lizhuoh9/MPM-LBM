import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step96_taichi_ggui_10step_visualization_quality_passes():
    payload = read_json(
        "outputs/step96_taichi_ggui_10step_visualization_quality/"
        "taichi_ggui_10step_visualization_quality.json"
    )
    summary = payload["summary"]

    assert summary["step96_taichi_ggui_10step_visualization_quality_pass"] is True
    assert summary["geometry_quality_report_pass_count"] == 1
    assert summary["geometry_motion_interface_report_pass_count"] == 1
    assert summary["wall_velocity_application_report_pass_count"] == 1
    assert summary["boundary_motion_interface_report_pass_count"] == 1
    assert summary["ggui_render_report_pass_count"] == 1
    assert summary["ggui_screenshot_exists_count"] == 1
    assert summary["mutation_flag_enabled_count_max"] == 0
    assert summary["from_step94_duration_expansion_count"] == 1
    assert summary["from_step92_adds_ggui_visualization_count"] == 1


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
