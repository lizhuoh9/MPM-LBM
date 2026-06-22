import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step88_combined_smoke_matrix_passes():
    payload = read_json(
        "outputs/step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix/"
        "squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix.json"
    )
    summary = payload["summary"]
    rows = payload["rows"]
    assert len(rows) == 1
    row = rows[0]

    assert summary["step88_squid_proxy_runtime_geometry_wall_velocity_combined_smoke_matrix_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["required_stable_count"] == 1
    assert summary["activation_feature_count"] == 3
    assert summary["squid_proxy_enabled_count"] == 1
    assert summary["procedural_geometry_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 1
    assert summary["real_geometry_candidate_enabled_count"] == 0
    assert summary["real_geometry_enabled_count"] == 0
    assert summary["link_area_enabled_count"] == 0
    assert summary["grid_48_enabled_count"] == 0
    assert summary["grid_64_enabled_count"] == 0
    assert summary["write_vtk_count"] == 0
    assert summary["write_particles_count"] == 0
    assert summary["physics_feature_expansion"] == (
        "squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_only"
    )

    assert row["row_name"] == (
        "canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke"
    )
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geometry_type"] == "squid_proxy"
    assert row["geometry_config_path"] == "configs/step85_squid_proxy_geometry_1024.json"
    assert row["target_u_lbm"] == [0.0, 0.0, 0.0]
    assert row["completed_lbm_steps"] == 3
    assert row["total_mpm_substeps"] >= 3
    assert row["diagnostics_row_count"] >= 4
    assert row["stable"] is True
    assert row["has_nan"] is False
    assert row["has_inf"] is False


def test_step88_driver_reports_exist_and_pass():
    run_dir = (
        "outputs/step88_driver_runs/"
        "canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke/"
    )
    geometry_quality = read_json(run_dir + "geometry_quality_report.json")
    geometry_motion = read_json(run_dir + "geometry_motion_interface_report.json")["summary"]
    boundary_motion = read_json(run_dir + "boundary_motion_interface_report.json")["summary"]
    wall_velocity = read_json(run_dir + "wall_velocity_application_report.json")["summary"]

    assert geometry_quality["gate"]["pass"] is True
    assert geometry_quality["gate"]["strict"] is False
    assert geometry_quality["report"]["geometry_type"] == "squid_proxy"
    assert geometry_motion["diagnostic_only"] is True
    assert geometry_motion["no_op_pass"] is True
    assert geometry_motion["mutation_flag_enabled_count"] == 0
    assert boundary_motion["diagnostic_only"] is True
    assert boundary_motion["boundary_motion_mode"] == "prescribed_kinematic"
    assert wall_velocity["report_pass"] is True
    assert wall_velocity["application_mode"] == "solid_vel_experimental"
    assert wall_velocity["target_lbm_field"] == "solid_vel"
    assert wall_velocity["apply_to_lbm_solid_vel"] is True
    assert wall_velocity["apply_to_lbm_populations"] is False
    assert wall_velocity["modify_bounceback_formula"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
