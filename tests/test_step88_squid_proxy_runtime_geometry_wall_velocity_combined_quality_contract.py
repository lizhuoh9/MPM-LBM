import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step88_combined_quality_passes():
    payload = read_json(
        "outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality/"
        "squid_proxy_runtime_geometry_wall_velocity_combined_quality.json"
    )
    summary = payload["summary"]

    assert summary["step88_squid_proxy_runtime_geometry_wall_velocity_combined_quality_pass"] is True
    assert summary["geometry_quality_report_pass_count"] == 1
    assert summary["geometry_motion_interface_report_pass_count"] == 1
    assert summary["wall_velocity_application_report_pass_count"] == 1
    assert summary["boundary_motion_interface_report_pass_count"] == 1
    assert summary["finite_wall_velocity_report_count"] == 1
    assert summary["capped_wall_velocity_report_count"] == 1
    assert summary["finite_max_grid_reaction_norm_count"] == 1
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["mutation_flag_enabled_count_max"] == 0
    assert summary["pass_count"] == summary["row_count"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
