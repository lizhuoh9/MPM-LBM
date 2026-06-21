import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP42_REQUIRED_FILES = [
    "STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_GOAL.md",
    "STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_REPORT.md",
    "docs/42_controlled_squid_proxy_prescribed_geometry_displacement_diagnostics.md",
    "configs/step42_squid_proxy_geometry_displacement.json",
    "configs/step42_squid_proxy_displacement_sampling.json",
    "src/geometry_displacement_config.py",
    "src/geometry_displacement_field.py",
    "src/geometry_displacement_quality.py",
    "src/geometry_displacement_consistency.py",
    "src/geometry_displacement_grid_diagnostics.py",
    "baseline_tests/step42_common.py",
    "baseline_tests/run_step42_displacement_config_validation.py",
    "baseline_tests/run_step42_generate_geometry_displacement.py",
    "baseline_tests/run_step42_displacement_quality.py",
    "baseline_tests/run_step42_displacement_repeatability.py",
    "baseline_tests/run_step42_schedule_displacement_consistency.py",
    "baseline_tests/run_step42_motion_displacement_consistency.py",
    "baseline_tests/run_step42_grid_displacement_diagnostics.py",
    "baseline_tests/run_step42_cycle_closure_diagnostics.py",
    "baseline_tests/run_step42_no_driver_update_guard.py",
    "baseline_tests/run_step42_step41_regression_guard.py",
    "baseline_tests/run_step42_artifact_manifest.py",
    "tests/test_step42_geometry_displacement_diagnostics_contract.py",
]

STEP42_OUTPUT_FILES = [
    "outputs/step42_displacement_config_validation/displacement_config_validation.csv",
    "outputs/step42_displacement_config_validation/displacement_config_validation.json",
    "outputs/step42_geometry_displacement/geometry_displacement.csv",
    "outputs/step42_geometry_displacement/geometry_displacement.json",
    "outputs/step42_geometry_displacement/geometry_displacement_summary.npz",
    "outputs/step42_displacement_quality/displacement_quality.csv",
    "outputs/step42_displacement_quality/displacement_quality.json",
    "outputs/step42_displacement_repeatability/displacement_repeatability.csv",
    "outputs/step42_displacement_repeatability/displacement_repeatability.json",
    "outputs/step42_schedule_displacement_consistency/schedule_displacement_consistency.csv",
    "outputs/step42_schedule_displacement_consistency/schedule_displacement_consistency.json",
    "outputs/step42_motion_displacement_consistency/motion_displacement_consistency.csv",
    "outputs/step42_motion_displacement_consistency/motion_displacement_consistency.json",
    "outputs/step42_grid_displacement_diagnostics/grid_displacement_diagnostics.csv",
    "outputs/step42_grid_displacement_diagnostics/grid_displacement_diagnostics.json",
    "outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.csv",
    "outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.json",
    "outputs/step42_no_driver_update_guard/no_driver_update_guard.csv",
    "outputs/step42_no_driver_update_guard/no_driver_update_guard.json",
    "outputs/step42_step41_regression_guard/step41_regression_guard.csv",
    "outputs/step42_step41_regression_guard/step41_regression_guard.json",
    "outputs/step42_artifact_manifest/artifact_manifest.csv",
    "outputs/step42_artifact_manifest/artifact_summary.csv",
    "outputs/step42_artifact_manifest/artifact_summary.json",
]

STEP42_LOG_MARKERS = {
    "logs/step42_displacement_config_validation.log": "[OK] Step 42 displacement config validation finished",
    "logs/step42_generate_geometry_displacement.log": "[OK] Step 42 generate geometry displacement finished",
    "logs/step42_displacement_quality.log": "[OK] Step 42 displacement quality finished",
    "logs/step42_displacement_repeatability.log": "[OK] Step 42 displacement repeatability finished",
    "logs/step42_schedule_displacement_consistency.log": "[OK] Step 42 schedule-displacement consistency finished",
    "logs/step42_motion_displacement_consistency.log": "[OK] Step 42 motion-displacement consistency finished",
    "logs/step42_grid_displacement_diagnostics.log": "[OK] Step 42 grid displacement diagnostics finished",
    "logs/step42_cycle_closure_diagnostics.log": "[OK] Step 42 cycle closure diagnostics finished",
    "logs/step42_no_driver_update_guard.log": "[OK] Step 42 no driver update guard finished",
    "logs/step42_step41_regression_guard.log": "[OK] Step 42 Step 41 regression guard finished",
    "logs/step42_artifact_manifest.log": "[OK] Step 42 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 42 is controlled squid proxy prescribed geometry displacement diagnostics.",
    "Step 42 derives displacement diagnostics only.",
    "Step 42 does not update driver geometry.",
    "Step 42 does not displace MPM particles in FSIDriver3D.",
    "Step 42 does not update LBM solid_phi.",
    "Step 42 does not update dynamic_solid.",
    "Step 42 does not change moving bounce-back formulas.",
    "Step 42 remains diagnostic-only.",
    "The default boundary_motion_mode remains static.",
    "The default wall_velocity_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "geometry displacement is integrated into FSIDriver3D",
    "driver geometry is updated",
    "MPM particles are displaced by Step 42",
    "LBM solid_phi is updated by displaced geometry",
    "dynamic_solid is updated by displaced geometry",
    "moving bounce-back formula is changed",
    "real jet validation",
    "jet propulsion is validated",
    "squid swimming is implemented",
    "free-body motion is implemented",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
    "default wall velocity application is enabled",
]

TRACKED_REGIONS = ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"]


def test_step42_required_artifacts_exist():
    missing = [path for path in STEP42_REQUIRED_FILES + STEP42_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP42_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step42_displacement_config_is_valid():
    config = read_json("configs/step42_squid_proxy_geometry_displacement.json")
    sampling = read_json("configs/step42_squid_proxy_displacement_sampling.json")
    assert config["displacement_id"] == "step42_squid_proxy_geometry_displacement_diagnostics"
    assert config["schedule_config_path"] == "configs/step32_squid_proxy_kinematics_schedule.json"
    assert config["motion_mapping_config_path"] == "configs/step33_squid_proxy_motion_mapping.json"
    assert config["region_config_path"] == "configs/step30_squid_proxy_region_config.json"
    assert config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json"
    assert config["tracked_regions"] == TRACKED_REGIONS
    assert int(config["sample_count"]) == 32768
    assert int(config["phase_sample_count"]) == 81
    assert config["grid_sizes"] == [32, 48, 64]
    assert float(config["max_displacement_norm_allowed"]) == 0.25
    assert config["write_dense_displacement_field"] is False
    assert config["write_displaced_particles"] is False
    assert config["apply_to_driver"] is False
    assert config["apply_to_lbm"] is False
    assert config["apply_to_mpm"] is False
    assert config["apply_to_projection"] is False
    assert config["update_dynamic_solid"] is False
    assert config["driver_integration_enabled"] is False
    assert config["deterministic"] is True
    assert sampling["phase_sample_count"] == 81
    assert sampling["grid_sizes"] == [32, 48, 64]

    payload = read_json("outputs/step42_displacement_config_validation/displacement_config_validation.json")
    summary = payload["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["tracked_region_count"]) == 3
    assert int(summary["phase_sample_count"]) == 81
    assert summary["grid_sizes"] == [32, 48, 64]


def test_step42_geometry_displacement_output_is_valid():
    payload = read_json("outputs/step42_geometry_displacement/geometry_displacement.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 243
    assert int(summary["phase_sample_count"]) == 81
    assert int(summary["tracked_region_count"]) == 3
    assert summary["tracked_regions"] == TRACKED_REGIONS
    assert summary["finite_pass"] is True
    assert summary["bounds_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert float(summary["max_displacement_norm"]) <= float(summary["max_displacement_norm_allowed"]) + 1.0e-12
    assert all(row["diagnostic_only"] is True for row in rows)
    assert all(row["apply_to_driver"] is False for row in rows)
    assert all(row["apply_to_lbm"] is False for row in rows)
    assert all(row["apply_to_mpm"] is False for row in rows)
    assert all(row["apply_to_projection"] is False for row in rows)
    assert all(row["finite_pass"] is True and row["bounds_pass"] is True for row in rows)
    assert all(math.isfinite(float(row["bbox_min_x"])) for row in rows)
    assert all(math.isfinite(float(row["bbox_max_x"])) for row in rows)


def test_step42_displacement_quality_is_valid():
    summary = read_json("outputs/step42_displacement_quality/displacement_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["finite_pass"] is True
    assert summary["bounds_pass"] is True
    assert summary["coverage_pass"] is True
    assert summary["cycle_closure_pass"] is True
    assert summary["endpoint_repeatability_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_driver_update_pass"] is True
    assert summary["no_lbm_update_pass"] is True
    assert summary["no_mpm_update_pass"] is True
    assert summary["no_projection_update_pass"] is True
    assert summary["no_dense_field_pass"] is True
    assert summary["no_displaced_particles_pass"] is True


def test_step42_displacement_repeatability_is_valid():
    summary = read_json("outputs/step42_displacement_repeatability/displacement_repeatability.json")["summary"]
    assert int(summary["row_count_first"]) == 243
    assert int(summary["row_count_second"]) == 243
    assert summary["displacement_hash_first"] == summary["displacement_hash_second"]
    assert summary["mantle_displacement_hash_first"] == summary["mantle_displacement_hash_second"]
    assert summary["cavity_displacement_hash_first"] == summary["cavity_displacement_hash_second"]
    assert summary["funnel_displacement_hash_first"] == summary["funnel_displacement_hash_second"]
    assert summary["repeatability_pass"] is True


def test_step42_schedule_displacement_consistency_is_valid():
    summary = read_json("outputs/step42_schedule_displacement_consistency/schedule_displacement_consistency.json")["summary"]
    assert int(summary["schedule_row_count"]) == 81
    assert int(summary["displacement_sample_count"]) == 81
    assert summary["phase_samples_match"] is True
    assert summary["mantle_scale_consistency_pass"] is True
    assert summary["cavity_volume_scale_consistency_pass"] is True
    assert summary["funnel_aperture_scale_consistency_pass"] is True
    assert summary["consistency_pass"] is True


def test_step42_motion_displacement_consistency_is_valid():
    summary = read_json("outputs/step42_motion_displacement_consistency/motion_displacement_consistency.json")["summary"]
    assert int(summary["motion_mapping_row_count"]) == 243
    assert int(summary["displacement_row_count"]) == 243
    assert summary["phase_match_pass"] is True
    assert summary["region_match_pass"] is True
    assert summary["velocity_displacement_sign_pass"] is True
    assert summary["mantle_motion_displacement_pass"] is True
    assert summary["cavity_motion_displacement_pass"] is True
    assert summary["funnel_motion_displacement_pass"] is True
    assert summary["consistency_pass"] is True


def test_step42_grid_displacement_diagnostics_is_valid():
    payload = read_json("outputs/step42_grid_displacement_diagnostics/grid_displacement_diagnostics.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 9
    assert int(summary["grid_size_count"]) == 3
    assert int(summary["tracked_region_count"]) == 3
    assert summary["coverage_pass"] is True
    assert all(int(row["active_cell_count_min"]) > 0 for row in rows)
    assert all(int(row["active_cell_count_max"]) >= int(row["active_cell_count_min"]) for row in rows)
    assert all(math.isfinite(float(row["max_displacement_norm"])) for row in rows)
    assert all(row["coverage_pass"] is True for row in rows)


def test_step42_cycle_closure_diagnostics_is_valid():
    payload = read_json("outputs/step42_cycle_closure_diagnostics/cycle_closure_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 3
    assert summary["cycle_closure_pass"] is True
    for row in payload["rows"]:
        assert row["closure_pass"] is True
        assert float(row["phase0_phase1_displacement_delta"]) <= float(row["closure_tolerance"])


def test_step42_no_driver_update_guard_is_valid():
    summary = read_json("outputs/step42_no_driver_update_guard/no_driver_update_guard.json")["summary"]
    assert summary["guard_pass"] is True
    assert int(summary["driver_update_count"]) == 0
    assert int(summary["lbm_update_count"]) == 0
    assert int(summary["mpm_update_count"]) == 0
    assert int(summary["projection_update_count"]) == 0
    assert int(summary["dynamic_solid_update_count"]) == 0
    assert int(summary["displaced_particle_output_count"]) == 0
    assert int(summary["dense_displacement_field_output_count"]) == 0
    assert int(summary["fsidriver_integration_count"]) == 0


def test_step42_step41_regression_guard_is_valid():
    payload = read_json("outputs/step42_step41_regression_guard/step41_regression_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) >= 10
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert summary["regression_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step42_default_modes_remain_unchanged():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "wall_velocity_application_config_path: Optional[str] = None" in text
    assert "wall_velocity_application_report_enabled: bool = False" in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step42_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/42_controlled_squid_proxy_prescribed_geometry_displacement_diagnostics.md",
            "STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step42_artifact_budget_is_valid():
    summary = read_json("outputs/step42_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step42_total_size_mb"]) < 5.0
    assert float(summary["total_size_mb"]) < 310.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step42_vtr_count"]) == 0
    assert int(summary["step42_particle_npy_count"]) == 0


def test_step42_report_acceptance_complete():
    report = read_text("STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_REPORT.md")
    assert "## 17. Acceptance Checklist" in report
    assert "## 18. Decision For Step 43" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step42_no_driver_coupling_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "configs/step42_squid_proxy_geometry_displacement.json",
            "configs/step42_squid_proxy_displacement_sampling.json",
            "outputs/step42_no_driver_update_guard/no_driver_update_guard.json",
            "docs/42_controlled_squid_proxy_prescribed_geometry_displacement_diagnostics.md",
            "STEP42_CONTROLLED_SQUID_PROXY_PRESCRIBED_GEOMETRY_DISPLACEMENT_DIAGNOSTICS_REPORT.md",
        ]
    )
    required_disabled = [
        '"apply_to_driver": false',
        '"apply_to_lbm": false',
        '"apply_to_mpm": false',
        '"apply_to_projection": false',
        '"update_dynamic_solid": false',
        '"driver_integration_enabled": false',
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
