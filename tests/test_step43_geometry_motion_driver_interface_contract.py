import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP43_REQUIRED_FILES = [
    "STEP43_CONTROLLED_SQUID_PROXY_GEOMETRY_MOTION_DRIVER_INTERFACE_CONTRACT_GOAL.md",
    "STEP43_CONTROLLED_SQUID_PROXY_GEOMETRY_MOTION_DRIVER_INTERFACE_CONTRACT_REPORT.md",
    "docs/43_controlled_squid_proxy_geometry_motion_driver_interface.md",
    "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json",
    "configs/step43_static_48_moving_boundary.json",
    "configs/step43_diagnostic_geometry_motion_48_moving_boundary.json",
    "configs/step43_static_48_link_area.json",
    "configs/step43_diagnostic_geometry_motion_48_link_area.json",
    "src/geometry_motion_config.py",
    "src/geometry_motion_interface.py",
    "baseline_tests/step43_common.py",
    "baseline_tests/run_step43_geometry_motion_config_validation.py",
    "baseline_tests/run_step43_geometry_motion_interface_report.py",
    "baseline_tests/run_step43_static_driver_regression.py",
    "baseline_tests/run_step43_diagnostic_geometry_motion_noop_smoke.py",
    "baseline_tests/run_step43_static_vs_diagnostic_noop_comparison.py",
    "baseline_tests/run_step43_no_geometry_state_mutation_guard.py",
    "baseline_tests/run_step43_quality_report_aggregation.py",
    "baseline_tests/run_step43_step42_regression_guard.py",
    "baseline_tests/run_step43_artifact_manifest.py",
    "tests/test_step43_geometry_motion_driver_interface_contract.py",
]

STEP43_OUTPUT_FILES = [
    "outputs/step43_geometry_motion_config_validation/geometry_motion_config_validation.csv",
    "outputs/step43_geometry_motion_config_validation/geometry_motion_config_validation.json",
    "outputs/step43_geometry_motion_interface_report/geometry_motion_interface_report.json",
    "outputs/step43_geometry_motion_interface_report/geometry_motion_interface_summary.csv",
    "outputs/step43_static_driver_regression/static_driver_results.csv",
    "outputs/step43_static_driver_regression/static_driver_results.json",
    "outputs/step43_static_driver_regression/static_driver_results.npz",
    "outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.csv",
    "outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.json",
    "outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.npz",
    "outputs/step43_static_vs_diagnostic_noop_comparison/static_vs_diagnostic_noop.csv",
    "outputs/step43_static_vs_diagnostic_noop_comparison/static_vs_diagnostic_noop.json",
    "outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.csv",
    "outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.json",
    "outputs/step43_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step43_quality_report_aggregation/quality_report_summary.json",
    "outputs/step43_step42_regression_guard/step42_regression_guard.csv",
    "outputs/step43_step42_regression_guard/step42_regression_guard.json",
    "outputs/step43_artifact_manifest/artifact_manifest.csv",
    "outputs/step43_artifact_manifest/artifact_summary.csv",
    "outputs/step43_artifact_manifest/artifact_summary.json",
]

STEP43_LOG_MARKERS = {
    "logs/step43_geometry_motion_config_validation.log": "[OK] Step 43 geometry motion config validation finished",
    "logs/step43_geometry_motion_interface_report.log": "[OK] Step 43 geometry motion interface report finished",
    "logs/step43_static_driver_regression.log": "[OK] Step 43 static driver regression finished",
    "logs/step43_diagnostic_geometry_motion_noop_smoke.log": "[OK] Step 43 diagnostic geometry motion no-op smoke finished",
    "logs/step43_static_vs_diagnostic_noop_comparison.log": "[OK] Step 43 static-vs-diagnostic no-op comparison finished",
    "logs/step43_no_geometry_state_mutation_guard.log": "[OK] Step 43 no geometry state mutation guard finished",
    "logs/step43_quality_report_aggregation.log": "[OK] Step 43 quality report aggregation finished",
    "logs/step43_step42_regression_guard.log": "[OK] Step 43 Step 42 regression guard finished",
    "logs/step43_artifact_manifest.log": "[OK] Step 43 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 43 is controlled squid proxy geometry motion driver interface.",
    "Step 43 defines a guarded driver interface only.",
    "Step 43 keeps geometry motion diagnostic-only.",
    "Step 43 does not update driver geometry.",
    "Step 43 does not displace MPM particles.",
    "Step 43 does not update LBM solid_phi.",
    "Step 43 does not update dynamic_solid.",
    "Step 43 does not recompute boundary links from displaced geometry.",
    "Step 43 does not change moving bounce-back formulas.",
    "The default geometry_motion_mode remains static.",
    "The default geometry_motion_application_mode remains disabled.",
    "The default boundary_motion_mode remains static.",
    "The default wall_velocity_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "driver geometry is updated",
    "geometry displacement is integrated into FSIDriver3D",
    "MPM particles are displaced by Step 43",
    "LBM solid_phi is updated by geometry motion",
    "LBM solid_vel is updated by geometry motion",
    "dynamic_solid is updated by geometry motion",
    "projection is updated from displaced geometry",
    "boundary links are recomputed from displaced geometry",
    "moving bounce-back formula is changed",
    "squid swimming is implemented",
    "free-body motion is implemented",
    "real jet validation",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
]

TRACKED_REGIONS = ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"]


def test_step43_required_artifacts_exist():
    missing = [path for path in STEP43_REQUIRED_FILES + STEP43_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP43_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step43_fsi_config_geometry_motion_defaults_are_valid():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'VALID_GEOMETRY_MOTION_MODES = ("static", "prescribed_kinematic")' in text
    assert 'VALID_GEOMETRY_MOTION_APPLICATION_MODES = ("disabled", "diagnostic_only")' in text
    assert 'geometry_motion_mode: str = "static"' in text
    assert "geometry_motion_config_path: Optional[str] = None" in text
    assert "geometry_motion_report_enabled: bool = False" in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert "geometry_motion_application_config_path: Optional[str] = None" in text
    assert "geometry_motion_application_report_enabled: bool = False" in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text


def test_step43_geometry_motion_config_validation_is_valid():
    config = read_json("configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json")
    assert config["geometry_motion_id"] == "step43_geometry_motion_prescribed_diagnostic_only"
    assert config["geometry_motion_mode"] == "prescribed_kinematic"
    assert config["application_mode"] == "diagnostic_only"
    assert config["diagnostic_only"] is True
    assert config["displacement_config_path"] == "configs/step42_squid_proxy_geometry_displacement.json"
    assert config["displacement_artifact_path"] == "outputs/step42_geometry_displacement/geometry_displacement.json"
    assert config["apply_to_driver"] is False
    assert config["apply_to_mpm_particles"] is False
    assert config["apply_to_lbm_solid_phi"] is False
    assert config["apply_to_lbm_solid_vel"] is False
    assert config["apply_to_projection"] is False
    assert config["update_dynamic_solid"] is False
    assert config["recompute_boundary_links"] is False
    assert config["mutate_geometry_state"] is False

    payload = read_json("outputs/step43_geometry_motion_config_validation/geometry_motion_config_validation.json")
    summary = payload["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["displacement_row_count"]) == 243
    assert int(summary["phase_sample_count"]) == 81
    assert int(summary["tracked_region_count"]) == 3
    assert summary["tracked_regions"] == TRACKED_REGIONS
    assert summary["all_mutation_flags_false"] is True


def test_step43_geometry_motion_interface_report_is_valid():
    payload = read_json("outputs/step43_geometry_motion_interface_report/geometry_motion_interface_report.json")
    summary = payload["summary"]
    assert summary["geometry_motion_mode"] == "prescribed_kinematic"
    assert summary["application_mode"] == "diagnostic_only"
    assert summary["diagnostic_only"] is True
    assert int(summary["displacement_row_count"]) == 243
    assert int(summary["phase_sample_count"]) == 81
    assert int(summary["tracked_region_count"]) == 3
    assert summary["tracked_regions"] == TRACKED_REGIONS
    assert math.isfinite(float(summary["max_displacement_norm"]))
    assert summary["cycle_closure_pass"] is True
    assert summary["repeatability_pass"] is True
    assert summary["no_op_pass"] is True
    assert _mutation_flags_false(summary)


def test_step43_static_driver_regression_is_valid():
    payload = read_json("outputs/step43_static_driver_regression/static_driver_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 2
    assert int(summary["stable_count"]) == 2
    assert int(summary["quality_pass_count"]) == 2
    assert summary["geometry_motion_mode_all_static"] is True
    assert summary["geometry_motion_application_mode_all_disabled"] is True
    for row in rows:
        assert row["stable"] is True
        assert row["quality_pass"] is True
        assert row["geometry_motion_mode"] == "static"
        assert row["geometry_motion_application_mode"] == "disabled"
        assert int(row["completed_lbm_steps"]) >= 5
        assert int(row["total_mpm_substeps"]) >= 25
        assert float(row["rho_min_global"]) > 0.95
        assert float(row["rho_max_global"]) < 1.05
        assert float(row["lbm_max_v_global"]) < 0.1
        assert float(row["mpm_min_J_global"]) > 0.0
        assert float(row["projected_mass_min"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert row["geometry_motion_report_written"] is False


def test_step43_diagnostic_geometry_motion_noop_smoke_is_valid():
    payload = read_json("outputs/step43_diagnostic_geometry_motion_noop_smoke/diagnostic_noop_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 2
    assert int(summary["stable_count"]) == 2
    assert int(summary["quality_pass_count"]) == 2
    assert int(summary["geometry_motion_report_count"]) == 2
    assert summary["geometry_motion_mode_all_prescribed"] is True
    assert summary["geometry_motion_application_mode_all_diagnostic_only"] is True
    assert summary["no_op_pass_all"] is True
    for row in rows:
        assert row["stable"] is True
        assert row["quality_pass"] is True
        assert row["geometry_motion_mode"] == "prescribed_kinematic"
        assert row["geometry_motion_application_mode"] == "diagnostic_only"
        assert row["geometry_motion_report_written"] is True
        assert row["geometry_motion_no_op_pass"] is True
        assert int(row["completed_lbm_steps"]) >= 5
        assert int(row["total_mpm_substeps"]) >= 25
        assert float(row["rho_min_global"]) > 0.95
        assert float(row["rho_max_global"]) < 1.05
        assert float(row["lbm_max_v_global"]) < 0.1
        assert float(row["mpm_min_J_global"]) > 0.0
        assert float(row["projected_mass_min"]) > 0.0


def test_step43_static_vs_diagnostic_noop_comparison_is_valid():
    payload = read_json("outputs/step43_static_vs_diagnostic_noop_comparison/static_vs_diagnostic_noop.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["comparison_pass_count"]) == 2
    assert summary["comparison_pass"] is True
    for row in payload["rows"]:
        assert row["comparison_pass"] is True
        assert abs(float(row["rho_min_delta"])) <= 1.0e-6
        assert abs(float(row["rho_max_delta"])) <= 1.0e-6
        assert abs(float(row["lbm_max_v_delta"])) <= 1.0e-6
        assert abs(float(row["mpm_min_J_delta"])) <= 1.0e-6
        assert abs(float(row["projected_mass_delta"])) <= 1.0e-6
        assert int(row["active_cell_count_delta"]) == 0
        assert int(row["bb_link_count_delta"]) == 0
        assert abs(float(row["area_scale_delta"])) <= 1.0e-12


def test_step43_no_geometry_state_mutation_guard_is_valid():
    payload = read_json("outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.json")
    summary = payload["summary"]
    assert summary["guard_pass"] is True
    assert int(summary["mpm_particle_mutation_count"]) == 0
    assert int(summary["lbm_solid_phi_mutation_count"]) == 0
    assert int(summary["lbm_solid_vel_mutation_count"]) == 0
    assert int(summary["dynamic_solid_mutation_count"]) == 0
    assert int(summary["projection_call_from_geometry_motion_count"]) == 0
    assert int(summary["boundary_link_recompute_count"]) == 0
    assert int(summary["geometry_state_mutation_count"]) == 0
    assert int(summary["displaced_particle_output_count"]) == 0
    assert int(summary["dense_displacement_field_output_count"]) == 0


def test_step43_quality_report_aggregation_is_valid():
    summary = read_json("outputs/step43_quality_report_aggregation/quality_report_summary.json")["summary"]
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["warning_count"]) == 0
    assert int(summary["error_count"]) == 0


def test_step43_step42_regression_guard_is_valid():
    payload = read_json("outputs/step43_step42_regression_guard/step42_regression_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) >= 8
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert summary["regression_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step43_default_modes_remain_unchanged():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step43_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/43_controlled_squid_proxy_geometry_motion_driver_interface.md",
            "STEP43_CONTROLLED_SQUID_PROXY_GEOMETRY_MOTION_DRIVER_INTERFACE_CONTRACT_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step43_artifact_budget_is_valid():
    summary = read_json("outputs/step43_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step43_total_size_mb"]) < 10.0
    assert float(summary["total_size_mb"]) < 320.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step43_vtr_count"]) == 0
    assert int(summary["step43_particle_npy_count"]) == 0


def test_step43_report_acceptance_complete():
    report = read_text("STEP43_CONTROLLED_SQUID_PROXY_GEOMETRY_MOTION_DRIVER_INTERFACE_CONTRACT_REPORT.md")
    assert "## 15. Acceptance Checklist" in report
    assert "## 16. Decision For Step 44" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step43_no_driver_geometry_update_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json",
            "outputs/step43_geometry_motion_interface_report/geometry_motion_interface_report.json",
            "outputs/step43_no_geometry_state_mutation_guard/no_geometry_state_mutation_guard.json",
            "docs/43_controlled_squid_proxy_geometry_motion_driver_interface.md",
            "STEP43_CONTROLLED_SQUID_PROXY_GEOMETRY_MOTION_DRIVER_INTERFACE_CONTRACT_REPORT.md",
        ]
    )
    required_disabled = [
        '"apply_to_driver": false',
        '"apply_to_mpm_particles": false',
        '"apply_to_lbm_solid_phi": false',
        '"apply_to_lbm_solid_vel": false',
        '"apply_to_projection": false',
        '"update_dynamic_solid": false',
        '"recompute_boundary_links": false',
        '"mutate_geometry_state": false',
    ]
    missing = [phrase for phrase in required_disabled if phrase not in combined]
    assert missing == []


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    full_path = ROOT / path
    if not full_path.is_file():
        return ""
    return full_path.read_text(encoding="utf-8")


def _mutation_flags_false(summary):
    return all(
        summary[field] is False
        for field in (
            "apply_to_driver",
            "apply_to_mpm_particles",
            "apply_to_lbm_solid_phi",
            "apply_to_lbm_solid_vel",
            "apply_to_projection",
            "update_dynamic_solid",
            "recompute_boundary_links",
            "mutate_geometry_state",
        )
    )
