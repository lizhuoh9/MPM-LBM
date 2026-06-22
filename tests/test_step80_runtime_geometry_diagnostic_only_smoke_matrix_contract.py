import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step80_runtime_geometry_diagnostic_only_smoke_matrix_artifact_passes():
    payload = read_json("outputs/step80_runtime_geometry_diagnostic_only_smoke_matrix/runtime_geometry_diagnostic_only_smoke_matrix.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert len(rows) == 1
    row = rows[0]
    assert summary["step80_runtime_geometry_diagnostic_only_smoke_matrix_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["required_stable_count"] == 1
    assert summary["activation_feature_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 0
    assert summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 0
    assert summary["real_geometry_enabled_count"] == 0
    assert summary["squid_proxy_enabled_count"] == 0
    assert summary["link_area_enabled_count"] == 0
    assert summary["physics_feature_expansion"] == "diagnostic_only_only"
    assert row["row_name"] == "canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke"
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["completed_lbm_steps"] == 3
    assert row["total_mpm_substeps"] >= 3
    assert row["diagnostics_row_count"] >= 4
    assert row["stable"] is True
    assert row["has_nan"] is False
    assert row["has_inf"] is False


def test_step80_runtime_geometry_report_contract_passes():
    payload = read_json(
        "outputs/step80_driver_runs/canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke/geometry_motion_interface_report.json"
    )
    summary = payload["summary"]
    assert summary["no_op_pass"] is True
    assert summary["config_validation_pass"] is True
    assert summary["diagnostic_only"] is True
    assert summary["mutation_flag_enabled_count"] == 0
    assert summary["apply_to_driver"] is False
    assert summary["apply_to_mpm_particles"] is False
    assert summary["apply_to_lbm_solid_phi"] is False
    assert summary["apply_to_lbm_solid_vel"] is False
    assert summary["apply_to_projection"] is False
    assert summary["update_dynamic_solid"] is False
    assert summary["recompute_boundary_links"] is False
    assert summary["mutate_geometry_state"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
