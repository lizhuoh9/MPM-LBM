import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step90_first_user_simulation_dry_run_matrix_passes():
    payload = read_json("outputs/step90_first_user_simulation_dry_run_matrix/first_user_simulation_dry_run_matrix.json")
    summary = payload["summary"]
    row = payload["rows"][0]

    assert summary["step90_first_user_simulation_dry_run_matrix_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["required_stable_count"] == 1
    assert summary["activation_feature_count"] == 3
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 1
    assert summary["real_geometry_candidate_enabled_count"] == 0
    assert summary["link_area_enabled_count"] == 0
    assert summary["min_completed_lbm_steps"] == 5
    assert summary["min_diagnostics_row_count"] >= 6

    assert row["row_name"] == (
        "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run"
    )
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geometry_type"] == "squid_proxy"
    assert row["completed_lbm_steps"] == 5
    assert row["diagnostics_row_count"] >= 6
    assert row["stable"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
