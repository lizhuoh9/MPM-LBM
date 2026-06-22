import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step85_squid_proxy_static_geometry_activation_guard_passes():
    payload = read_json("outputs/step85_squid_proxy_static_geometry_activation_guard/squid_proxy_static_geometry_activation_guard.json")
    summary = payload["summary"]

    assert summary["step85_squid_proxy_static_geometry_activation_guard_pass"] is True
    assert summary["guard_pass_count"] == summary["guard_row_count"]
    assert summary["step85_activation_feature_count"] == 0
    assert summary["planned_step86_activation_feature_count"] == 1
    assert summary["planned_step86_feature"] == "squid_proxy_static_geometry"
    assert summary["planned_step86_row_name"] == "canonical_driver_squid_proxy_static_geometry_32_3step_smoke"
    assert summary["geometry_config_path_allowed_for_step86"] == "configs/step85_squid_proxy_geometry_1024.json"
    assert summary["geometry_quality_report_required_for_step86"] is True
    assert summary["squid_proxy_planned_for_step86"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
