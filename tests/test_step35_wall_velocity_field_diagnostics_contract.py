import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP35_REQUIRED_FILES = [
    "STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_GOAL.md",
    "STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_REPORT.md",
    "docs/35_controlled_squid_proxy_wall_velocity_field_diagnostics.md",
    "configs/step35_squid_proxy_wall_velocity_field.json",
    "configs/step35_squid_proxy_wall_velocity_sampling.json",
    "src/wall_velocity_config.py",
    "src/wall_velocity_field.py",
    "src/wall_velocity_quality.py",
    "src/wall_velocity_consistency.py",
    "baseline_tests/step35_common.py",
    "baseline_tests/run_step35_wall_velocity_config_validation.py",
    "baseline_tests/run_step35_generate_wall_velocity_field.py",
    "baseline_tests/run_step35_wall_velocity_quality.py",
    "baseline_tests/run_step35_wall_velocity_repeatability.py",
    "baseline_tests/run_step35_motion_velocity_consistency.py",
    "baseline_tests/run_step35_grid_coverage_diagnostics.py",
    "baseline_tests/run_step35_no_lbm_update_guard.py",
    "baseline_tests/run_step35_step34_regression_guard.py",
    "baseline_tests/run_step35_artifact_manifest.py",
    "tests/test_step35_wall_velocity_field_diagnostics_contract.py",
]

STEP35_OUTPUT_FILES = [
    "outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.csv",
    "outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation_summary.csv",
    "outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.json",
    "outputs/step35_wall_velocity_field/wall_velocity_field.csv",
    "outputs/step35_wall_velocity_field/wall_velocity_field.json",
    "outputs/step35_wall_velocity_quality/wall_velocity_quality.csv",
    "outputs/step35_wall_velocity_quality/wall_velocity_quality.json",
    "outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.csv",
    "outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.json",
    "outputs/step35_motion_velocity_consistency/motion_velocity_consistency.csv",
    "outputs/step35_motion_velocity_consistency/motion_velocity_consistency.json",
    "outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.csv",
    "outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.json",
    "outputs/step35_no_lbm_update_guard/no_lbm_update_guard.csv",
    "outputs/step35_no_lbm_update_guard/no_lbm_update_guard.json",
    "outputs/step35_step34_regression_guard/step34_regression_guard.csv",
    "outputs/step35_step34_regression_guard/step34_regression_guard.json",
    "outputs/step35_artifact_manifest/artifact_manifest.csv",
    "outputs/step35_artifact_manifest/artifact_summary.csv",
    "outputs/step35_artifact_manifest/artifact_summary.json",
]

STEP35_LOG_MARKERS = {
    "logs/step35_wall_velocity_config_validation.log": "[OK] Step 35 wall velocity config validation finished",
    "logs/step35_generate_wall_velocity_field.log": "[OK] Step 35 generate wall velocity field finished",
    "logs/step35_wall_velocity_quality.log": "[OK] Step 35 wall velocity quality finished",
    "logs/step35_wall_velocity_repeatability.log": "[OK] Step 35 wall velocity repeatability finished",
    "logs/step35_motion_velocity_consistency.log": "[OK] Step 35 motion velocity consistency finished",
    "logs/step35_grid_coverage_diagnostics.log": "[OK] Step 35 grid coverage diagnostics finished",
    "logs/step35_no_lbm_update_guard.log": "[OK] Step 35 no LBM update guard finished",
    "logs/step35_step34_regression_guard.log": "[OK] Step 35 Step 34 regression guard finished",
    "logs/step35_artifact_manifest.log": "[OK] Step 35 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 35 is controlled squid proxy moving-wall velocity field diagnostics.",
    "Step 35 generates diagnostic wall velocity fields only.",
    "Step 35 does not apply moving wall velocity to LBM.",
    "Step 35 does not update LBM populations.",
    "Step 35 does not change moving bounce-back formulas.",
    "Step 35 does not implement a jet model.",
    "Step 35 does not implement squid swimming.",
    "Step 35 does not implement new FSI physics.",
    "The default boundary_motion_mode remains static.",
    "The default quality_check_enabled remains false.",
    "The default quality_check_strict remains false.",
    "The default reaction_transfer_mode remains engineering.",
]

FORBIDDEN_CLAIMS = [
    "moving wall velocity is applied to LBM",
    "LBM populations are updated by wall velocity",
    "moving bounce-back formula is changed",
    "jet model is implemented",
    "squid actuation is implemented",
    "squid swimming is implemented",
    "mantle contraction is integrated into the driver",
    "funnel actuation is integrated into the driver",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "implements two_phase",
    "implements contact_angle",
]


def test_step35_required_artifacts_exist():
    missing = [path for path in STEP35_REQUIRED_FILES + STEP35_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step35_wall_velocity_config_is_valid():
    payload = read_json("outputs/step35_wall_velocity_config_validation/wall_velocity_config_validation.json")
    config = payload["config"]
    summary = payload["summary"]
    assert config["velocity_field_id"] == "step35_squid_proxy_wall_velocity_diagnostic"
    assert config["boundary_motion_config_path"] == "configs/step34_boundary_motion_interface_prescribed_kinematic.json"
    assert config["motion_mapping_config_path"] == "configs/step33_squid_proxy_motion_mapping.json"
    assert config["schedule_config_path"] == "configs/step32_squid_proxy_kinematics_schedule.json"
    assert config["region_config_path"] == "configs/step30_squid_proxy_region_config.json"
    assert config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json"
    assert config["grid_sizes"] == [32, 48, 64]
    assert config["phase_samples"] == [0.0, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0]
    assert config["tracked_regions"] == ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"]
    assert config["wall_velocity_model"] == "diagnostic_proxy"
    assert config["funnel_axis"] == "+y"
    assert float(config["max_velocity_norm_allowed"]) == 1.0
    assert config["write_dense_field"] is False
    assert config["write_sparse_samples"] is False
    assert config["apply_to_lbm"] is False
    assert config["lbm_population_update_enabled"] is False
    assert config["moving_bounceback_update_enabled"] is False
    assert config["driver_integration_enabled"] is False
    assert config["jet_model_enabled"] is False
    assert config["actuation_enabled"] is False
    assert int(summary["row_count"]) == 29
    assert int(summary["pass_count"]) == 29
    assert summary["validation_pass"] is True
    assert int(summary["expected_wall_velocity_row_count"]) == 63


def test_step35_wall_velocity_field_is_valid():
    payload = read_json("outputs/step35_wall_velocity_field/wall_velocity_field.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 63
    assert int(summary["expected_row_count"]) == 63
    assert int(summary["grid_size_count"]) == 3
    assert int(summary["phase_sample_count"]) == 7
    assert int(summary["tracked_region_count"]) == 3
    assert summary["finite_pass"] is True
    assert summary["bounds_pass"] is True
    assert summary["coverage_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_lbm_update_pass"] is True
    assert summary["no_bounceback_update_pass"] is True
    assert summary["no_driver_integration_pass"] is True
    assert float(summary["max_velocity_norm"]) <= 1.0
    assert int(summary["min_active_cell_count"]) > 0
    assert int(summary["apply_to_lbm_count"]) == 0
    assert int(summary["lbm_population_update_enabled_count"]) == 0
    assert int(summary["moving_bounceback_update_enabled_count"]) == 0
    assert int(summary["driver_integration_enabled_count"]) == 0
    assert all(row["diagnostic_only"] is True for row in rows)
    assert all(row["apply_to_lbm"] is False for row in rows)


def test_step35_wall_velocity_quality_is_valid():
    summary = read_json("outputs/step35_wall_velocity_quality/wall_velocity_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["finite_pass"] is True
    assert summary["bounds_pass"] is True
    assert summary["coverage_pass"] is True
    assert summary["max_velocity_norm_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_lbm_update_pass"] is True
    assert summary["no_bounceback_update_pass"] is True
    assert summary["no_driver_integration_pass"] is True


def test_step35_wall_velocity_repeatability_is_valid():
    summary = read_json("outputs/step35_wall_velocity_repeatability/wall_velocity_repeatability.json")["summary"]
    assert int(summary["row_count_first"]) == 63
    assert int(summary["row_count_second"]) == 63
    assert summary["velocity_field_hash_first"] == summary["velocity_field_hash_second"]
    assert summary["mantle_velocity_hash_first"] == summary["mantle_velocity_hash_second"]
    assert summary["cavity_velocity_hash_first"] == summary["cavity_velocity_hash_second"]
    assert summary["funnel_velocity_hash_first"] == summary["funnel_velocity_hash_second"]
    assert summary["repeatability_pass"] is True


def test_step35_motion_velocity_consistency_is_valid():
    payload = read_json("outputs/step35_motion_velocity_consistency/motion_velocity_consistency.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 21
    assert int(summary["pass_count"]) == 21
    assert summary["phase_match_pass"] is True
    assert summary["region_match_pass"] is True
    assert summary["mantle_velocity_consistency_pass"] is True
    assert summary["cavity_rate_sign_consistency_pass"] is True
    assert summary["funnel_rate_sign_consistency_pass"] is True
    assert summary["consistency_pass"] is True
    assert all(row["consistency_pass"] is True for row in payload["rows"])


def test_step35_grid_coverage_diagnostics_is_valid():
    payload = read_json("outputs/step35_grid_coverage_diagnostics/grid_coverage_diagnostics.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 9
    assert int(summary["pass_count"]) == 9
    assert summary["coverage_pass"] is True
    assert int(summary["active_cell_count_min"]) > 0
    assert all(row["coverage_pass"] is True for row in rows)
    assert all(int(row["active_cell_count_min"]) > 0 for row in rows)
    assert all(int(row["velocity_nonzero_phase_count"]) > 0 for row in rows)


def test_step35_no_lbm_update_guard_is_valid():
    payload = read_json("outputs/step35_no_lbm_update_guard/no_lbm_update_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 8
    assert int(summary["pass_count"]) == 8
    assert summary["guard_pass"] is True
    assert int(summary["lbm_population_update_count"]) == 0
    assert int(summary["moving_bounceback_update_count"]) == 0
    assert int(summary["driver_integration_enabled_count"]) == 0
    assert int(summary["apply_to_lbm_count"]) == 0
    assert all(row["pass"] is True for row in payload["rows"])


def test_step35_step34_regression_guard_is_valid():
    summary = read_json("outputs/step35_step34_regression_guard/step34_regression_guard.json")
    assert int(summary["row_count"]) == 7
    assert int(summary["pass_count"]) == 7
    assert summary["regression_pass"] is True
    assert summary["step34_no_op_pass"] is True
    assert int(summary["step34_noop_state_guard_pass_count"]) == 2
    assert int(summary["step34_quality_report_count"]) == 6
    assert int(summary["step34_large_file_count"]) == 0
    assert int(summary["step34_vtr_count"]) == 0
    assert int(summary["step34_particle_npy_count"]) == 0


def test_step35_default_modes_remain_unchanged():
    fsi_config = read_text("src/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in fsi_config
    assert "boundary_motion_config_path: Optional[str] = None" in fsi_config
    assert "boundary_motion_report_enabled: bool = False" in fsi_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config
    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config


def test_step35_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/35_controlled_squid_proxy_wall_velocity_field_diagnostics.md",
            "STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step35_artifact_budget_is_valid():
    summary = read_json("outputs/step35_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step35_total_size_mb"]) < 5.0
    assert float(summary["total_size_mb"]) < 210.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step35_vtr_count"]) == 0
    assert int(summary["step35_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step35_artifact_manifest/artifact_manifest.csv")
    step35_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step35")]
    assert not [path for path in step35_paths if path.endswith(".vtr")]
    assert not [path for path in step35_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step35_report_acceptance_complete():
    report = read_text("STEP35_CONTROLLED_SQUID_PROXY_MOVING_WALL_VELOCITY_FIELD_DIAGNOSTIC_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Wall Velocity Config Validation",
        "## 5. Generated Wall Velocity Field",
        "## 6. Wall Velocity Quality",
        "## 7. Wall Velocity Repeatability",
        "## 8. Motion-Velocity Consistency",
        "## 9. Grid Coverage Diagnostics",
        "## 10. No LBM Update Guard",
        "## 11. Step 34 Regression Guard",
        "## 12. Artifact Manifest Summary",
        "## 13. Verification Commands",
        "## 14. GitHub Sync Information",
        "## 15. Acceptance Checklist",
        "## 16. Decision For Step 36",
    ]
    assert [section for section in required_sections if section not in report] == []

    required_checks = [
        "- [x] Wall velocity config validation passes.",
        "- [x] Generated wall velocity field has 63 rows.",
        "- [x] Velocity fields are finite.",
        "- [x] Velocity fields are bounded.",
        "- [x] Active cell coverage is positive.",
        "- [x] Wall velocity quality passes.",
        "- [x] Wall velocity repeatability hash passes.",
        "- [x] Motion-velocity consistency passes.",
        "- [x] Grid coverage diagnostics pass.",
        "- [x] No-LBM-update guard passes.",
        "- [x] LBM population update count is 0.",
        "- [x] Moving bounce-back update count is 0.",
        "- [x] Step 34 regression guard passes.",
        "- [x] No `external/taichi_LBM3D` edits.",
        "- [x] No Step 35 `.vtr` outputs.",
        "- [x] No Step 35 particle `.npy` outputs.",
        "- [x] `logs/step35_pytest.log` exists.",
        "- [x] Full pytest passes.",
        "- [x] Step 35 contract test passes.",
        "- [x] Step 35 artifacts are pushed to `origin/main`.",
    ]
    assert [check for check in required_checks if check not in report] == []

    assert (ROOT / "logs/step35_pytest.log").is_file()
    for path, marker in STEP35_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def test_step35_solver_formula_boundaries_are_valid():
    formula_files = [
        "src/coupling.py",
        "src/moving_boundary_coupling.py",
        "src/link_area_coupling.py",
        "src/lbm_fluid.py",
        "src/mpm_solid.py",
        "src/projection.py",
        "external/taichi_LBM3D",
    ]
    status = subprocess.run(["git", "status", "--short", *formula_files], cwd=ROOT, check=True, capture_output=True, text=True)
    assert status.stdout.strip() == ""


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str):
    return json.loads(read_text(relative_path))


def read_csv_rows(relative_path: str) -> list[dict]:
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
