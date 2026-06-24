import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step100_48cube_5step_taichi_ggui_visualization_quality_passes():
    payload = read_json(
        "outputs/step100_48cube_5step_taichi_ggui_visualization_quality/"
        "48cube_5step_taichi_ggui_visualization_quality.json"
    )
    summary = payload["summary"]

    assert summary["step100_48cube_5step_taichi_ggui_visualization_quality_pass"] is True
    assert summary["source_matrix_row_count"] == 1
    assert summary["geometry_quality_report_pass_count"] == 1
    assert summary["geometry_motion_interface_report_pass_count"] == 1
    assert summary["wall_velocity_application_report_pass_count"] == 1
    assert summary["boundary_motion_interface_report_pass_count"] == 1
    assert summary["ggui_render_report_pass_count"] == 1
    assert summary["ggui_screenshot_exists_count"] == 1
    assert summary["finite_wall_velocity_report_count"] == 1
    assert summary["capped_wall_velocity_report_count"] == 1
    assert summary["finite_max_grid_reaction_norm_count"] == 1
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["from_step98_duration_expansion_count"] == 1
    assert summary["mutation_flag_enabled_count_max"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
