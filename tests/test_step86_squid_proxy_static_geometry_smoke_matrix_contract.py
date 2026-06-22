import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step86_squid_proxy_static_geometry_smoke_matrix_passes():
    payload = read_json("outputs/step86_squid_proxy_static_geometry_smoke_matrix/squid_proxy_static_geometry_smoke_matrix.json")
    summary = payload["summary"]
    row = payload["rows"][0]

    assert summary["step86_squid_proxy_static_geometry_smoke_matrix_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["required_stable_count"] == 1
    assert summary["activation_feature_count"] == 1
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["procedural_geometry_enabled_count"] == 1
    assert summary["real_geometry_candidate_enabled_count"] == 0
    assert summary["real_geometry_enabled_count"] == 0
    assert summary["runtime_geometry_enabled_count"] == 0
    assert summary["wall_velocity_enabled_count"] == 0
    assert summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 0
    assert summary["link_area_enabled_count"] == 0

    assert row["row_name"] == "canonical_driver_squid_proxy_static_geometry_32_3step_smoke"
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geometry_type"] == "squid_proxy"
    assert row["geometry_config_path"] == "configs/step85_squid_proxy_geometry_1024.json"
    assert row["completed_lbm_steps"] == 3
    assert row["diagnostics_row_count"] >= 4
    assert row["stable"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
