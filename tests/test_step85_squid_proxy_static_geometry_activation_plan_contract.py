import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step85_squid_proxy_static_geometry_activation_plan_passes():
    payload = read_json("outputs/step85_squid_proxy_static_geometry_activation_plan/squid_proxy_static_geometry_activation_plan.json")
    summary = payload["summary"]

    assert summary["step85_squid_proxy_static_geometry_activation_plan_pass"] is True
    assert summary["previous_commit"] == "29a130ccef93f095deeaa941b44003720f2291c5"
    assert summary["step85_activation_feature_count"] == 0
    assert summary["planned_step86_activation_feature_count"] == 1
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["squid_proxy_planned_for_step86"] is True
    assert summary["geometry_type_allowed_for_step86"] == "squid_proxy"
    assert summary["geometry_config_path_allowed_for_step86"] == "configs/step85_squid_proxy_geometry_1024.json"
    assert summary["runtime_geometry_allowed"] is False
    assert summary["wall_velocity_allowed"] is False
    assert summary["combined_runtime_geometry_wall_velocity_allowed"] is False
    assert summary["real_geometry_allowed"] is False
    assert summary["physical_validation_claim_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
