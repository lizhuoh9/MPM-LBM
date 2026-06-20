import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP34_REQUIRED_FILES = [
    "STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_GOAL.md",
    "STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md",
    "docs/34_controlled_squid_proxy_boundary_motion_driver_interface.md",
    "src/boundary_motion_config.py",
    "src/boundary_motion_interface.py",
    "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
    "configs/step34_squid_proxy_static_48_none.json",
    "configs/step34_squid_proxy_static_48_penalty.json",
    "configs/step34_squid_proxy_static_48_moving_boundary.json",
    "configs/step34_squid_proxy_static_48_link_area.json",
    "configs/step34_squid_proxy_prescribed_interface_48_moving_boundary.json",
    "configs/step34_squid_proxy_prescribed_interface_48_link_area.json",
    "baseline_tests/step34_common.py",
    "baseline_tests/run_step34_boundary_motion_config_validation.py",
    "baseline_tests/run_step34_boundary_motion_interface_report.py",
    "baseline_tests/run_step34_static_driver_regression.py",
    "baseline_tests/run_step34_prescribed_interface_noop_smoke.py",
    "baseline_tests/run_step34_step31_static_comparison.py",
    "baseline_tests/run_step34_noop_state_guard.py",
    "baseline_tests/run_step34_quality_report_aggregation.py",
    "baseline_tests/run_step34_step33_regression_guard.py",
    "baseline_tests/run_step34_artifact_manifest.py",
    "tests/test_step34_boundary_motion_driver_interface_contract.py",
]

STEP34_OUTPUT_FILES = [
    "outputs/step34_boundary_motion_config_validation/boundary_motion_config_validation.csv",
    "outputs/step34_boundary_motion_config_validation/boundary_motion_config_validation.json",
    "outputs/step34_boundary_motion_config_validation/boundary_motion_config_validation_summary.csv",
    "outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report.json",
    "outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report_summary.csv",
    "outputs/step34_static_driver_regression/static_driver_results.csv",
    "outputs/step34_static_driver_regression/static_driver_results.npz",
    "outputs/step34_static_driver_regression/static_driver_results.json",
    "outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.csv",
    "outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.npz",
    "outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.json",
    "outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_comparison.csv",
    "outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_comparison.json",
    "outputs/step34_step31_static_comparison/step31_static_comparison.csv",
    "outputs/step34_step31_static_comparison/step31_static_comparison.json",
    "outputs/step34_noop_state_guard/noop_state_guard.csv",
    "outputs/step34_noop_state_guard/noop_state_guard.json",
    "outputs/step34_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step34_quality_report_aggregation/quality_report_summary.json",
    "outputs/step34_step33_regression_guard/step33_regression_guard.csv",
    "outputs/step34_step33_regression_guard/step33_regression_guard.json",
    "outputs/step34_artifact_manifest/artifact_manifest.csv",
    "outputs/step34_artifact_manifest/artifact_summary.csv",
    "outputs/step34_artifact_manifest/artifact_summary.json",
]

STEP34_LOG_MARKERS = {
    "logs/step34_boundary_motion_config_validation.log": "[OK] Step 34 boundary motion config validation finished",
    "logs/step34_boundary_motion_interface_report.log": "[OK] Step 34 boundary motion interface report finished",
    "logs/step34_static_driver_regression.log": "[OK] Step 34 static driver regression finished",
    "logs/step34_prescribed_interface_noop_smoke.log": "[OK] Step 34 prescribed interface no-op smoke finished",
    "logs/step34_step31_static_comparison.log": "[OK] Step 34 Step 31 static comparison finished",
    "logs/step34_noop_state_guard.log": "[OK] Step 34 no-op state guard finished",
    "logs/step34_quality_report_aggregation.log": "[OK] Step 34 quality report aggregation finished",
    "logs/step34_step33_regression_guard.log": "[OK] Step 34 Step 33 regression guard finished",
    "logs/step34_artifact_manifest.log": "[OK] Step 34 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 34 is controlled squid proxy boundary-motion driver interface.",
    "Step 34 defines a guarded driver interface only.",
    "Step 34 keeps prescribed kinematics diagnostic-only.",
    "Step 34 does not apply moving wall velocity to LBM.",
    "Step 34 does not implement a jet model.",
    "Step 34 does not implement squid swimming.",
    "Step 34 does not implement new FSI physics.",
    "The default boundary_motion_mode remains static.",
    "The default quality_check_enabled remains false.",
    "The default quality_check_strict remains false.",
    "The default reaction_transfer_mode remains engineering.",
    "The moving bounce-back formula is unchanged.",
    "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
]

FORBIDDEN_CLAIMS = [
    "moving wall velocity is applied to LBM",
    "kinematics are active in FSIDriver3D",
    "mantle contraction is implemented in the driver",
    "funnel actuation is implemented in the driver",
    "jet model is implemented",
    "squid actuation is implemented",
    "squid swimming is implemented",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "strict momentum-conserving FSI is complete",
    "implements two_phase",
    "implements contact_angle",
]


def test_step34_required_artifacts_exist():
    missing = [path for path in STEP34_REQUIRED_FILES + STEP34_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step34_fsi_config_defaults_and_validation_are_valid():
    fsi_config = read_text("src/fsi_config.py")
    assert 'VALID_BOUNDARY_MOTION_MODES = ("static", "prescribed_kinematic")' in fsi_config
    assert 'boundary_motion_mode: str = "static"' in fsi_config
    assert "boundary_motion_config_path: Optional[str] = None" in fsi_config
    assert "boundary_motion_report_enabled: bool = False" in fsi_config
    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config
    assert "boundary_motion_mode must be one of" in fsi_config
    assert "boundary_motion_config_path must be None when boundary_motion_mode='static'" in fsi_config
    assert "boundary_motion_config_path is required when boundary_motion_mode='prescribed_kinematic'" in fsi_config


def test_step34_boundary_motion_config_validation_is_valid():
    payload = read_json("outputs/step34_boundary_motion_config_validation/boundary_motion_config_validation.json")
    config = read_json("configs/step34_boundary_motion_interface_prescribed_kinematic.json")
    summary = payload["summary"]
    assert config["interface_id"] == "step34_squid_proxy_boundary_motion_driver_interface"
    assert config["schedule_config_path"] == "configs/step32_squid_proxy_kinematics_schedule.json"
    assert config["motion_mapping_config_path"] == "configs/step33_squid_proxy_motion_mapping.json"
    assert int(config["expected_schedule_row_count"]) == 81
    assert int(config["expected_motion_row_count"]) == 243
    assert int(config["expected_tracked_region_count"]) == 3
    assert config["diagnostic_only"] is True
    for key, value in config.items():
        if key.endswith("_enabled"):
            assert value is False
    assert int(summary["row_count"]) == 21
    assert int(summary["pass_count"]) == 21
    assert summary["validation_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step34_boundary_motion_interface_report_is_valid():
    payload = read_json("outputs/step34_boundary_motion_interface_report/boundary_motion_interface_report.json")
    summary = payload["summary"]
    assert summary["boundary_motion_mode"] == "prescribed_kinematic"
    assert summary["diagnostic_only"] is True
    assert summary["config_validation_pass"] is True
    assert int(summary["schedule_row_count"]) == 81
    assert int(summary["motion_mapping_row_count"]) == 243
    assert int(summary["tracked_region_count"]) == 3
    assert summary["tracked_regions"] == ["funnel_outlet_proxy", "mantle_cavity_proxy", "mantle_outer"]
    assert summary["schedule_finite_pass"] is True
    assert summary["motion_finite_pass"] is True
    assert summary["motion_bounds_pass"] is True
    assert int(summary["execution_flag_enabled_count"]) == 0
    assert summary["no_op_pass"] is True
    for key, value in summary.items():
        if key.endswith("_enabled"):
            assert value is False


def test_step34_driver_configs_are_valid():
    configs = [read_json(path) for path in STEP34_REQUIRED_FILES if path.startswith("configs/step34_squid_proxy_")]
    assert len(configs) == 6
    static = [item for item in configs if item["boundary_motion_mode"] == "static"]
    prescribed = [item for item in configs if item["boundary_motion_mode"] == "prescribed_kinematic"]
    assert len(static) == 4
    assert len(prescribed) == 2
    modes = {(item["coupling_mode"], item["reaction_transfer_mode"]) for item in static}
    assert modes == {
        ("none", "engineering"),
        ("penalty", "engineering"),
        ("moving_boundary", "engineering"),
        ("moving_boundary", "link_area_experimental"),
    }
    for item in configs:
        assert item["geometry_type"] == "squid_proxy"
        assert item["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json"
        assert int(item["n_grid"]) == 48
        assert int(item["n_particles"]) == 4096
        assert int(item["n_lbm_steps"]) == 5
        assert int(item["mpm_substeps_per_lbm_step"]) == 5
        assert int(item["output_interval"]) == 1
        assert item["quality_check_enabled"] is True
        assert item["quality_check_strict"] is True
        assert item["write_vtk"] is False
        assert item["write_particles"] is False
    assert all(item["boundary_motion_config_path"] is None and item["boundary_motion_report_enabled"] is False for item in static)
    assert all(item["boundary_motion_config_path"] == "configs/step34_boundary_motion_interface_prescribed_kinematic.json" for item in prescribed)
    assert all(item["boundary_motion_report_enabled"] is True for item in prescribed)


def test_step34_static_driver_regression_is_valid():
    payload = read_json("outputs/step34_static_driver_regression/static_driver_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["driver_row_count"]) == 4
    assert int(summary["static_boundary_motion_row_count"]) == 4
    assert int(summary["boundary_report_count"]) == 0
    assert int(summary["boundary_no_op_pass_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["quality_pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert float(summary["min_mpm_min_J_global"]) > 0.0
    assert int(summary["max_boundary_motion_execution_flag_enabled_count"]) == 0
    assert all(row["boundary_motion_mode"] == "static" for row in rows)
    assert all(row["boundary_motion_report_written"] is False for row in rows)
    assert all(row["boundary_motion_no_op_pass"] is True for row in rows)


def test_step34_prescribed_interface_noop_smoke_is_valid():
    payload = read_json("outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    comparison = read_json("outputs/step34_prescribed_interface_noop_smoke/prescribed_interface_noop_comparison.json")
    assert int(summary["driver_row_count"]) == 2
    assert int(summary["prescribed_boundary_motion_row_count"]) == 2
    assert int(summary["boundary_report_count"]) == 2
    assert int(summary["boundary_no_op_pass_count"]) == 2
    assert int(summary["max_boundary_motion_execution_flag_enabled_count"]) == 0
    assert int(summary["stable_count"]) == 2
    assert all(row["boundary_motion_mode"] == "prescribed_kinematic" for row in rows)
    assert all(row["boundary_motion_report_written"] is True for row in rows)
    assert all(row["boundary_motion_no_op_pass"] is True for row in rows)
    assert all(int(row["boundary_motion_schedule_row_count"]) == 81 for row in rows)
    assert all(int(row["boundary_motion_motion_mapping_row_count"]) == 243 for row in rows)
    assert all(int(row["boundary_motion_tracked_region_count"]) == 3 for row in rows)
    assert comparison["summary"]["comparison_pass"] is True
    assert float(comparison["summary"]["max_abs_float_delta"]) <= 1.0e-6
    assert int(comparison["summary"]["int_mismatch_count"]) == 0


def test_step34_step31_static_comparison_is_valid():
    payload = read_json("outputs/step34_step31_static_comparison/step31_static_comparison.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert summary["comparison_pass"] is True
    assert float(summary["max_abs_float_delta"]) <= 1.0e-5
    assert int(summary["int_mismatch_count"]) == 0


def test_step34_noop_state_guard_is_valid():
    payload = read_json("outputs/step34_noop_state_guard/noop_state_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert summary["comparison_pass"] is True
    assert float(summary["max_abs_float_delta"]) <= 1.0e-6
    assert int(summary["int_mismatch_count"]) == 0
    assert int(summary["prescribed_report_count"]) == 2
    assert int(summary["prescribed_no_op_pass_count"]) == 2


def test_step34_quality_report_aggregation_is_valid():
    payload = read_json("outputs/step34_quality_report_aggregation/quality_report_summary.json")
    summary = payload["summary"]
    assert int(summary["quality_report_count"]) == 6
    assert int(summary["strict_count"]) == 6
    assert int(summary["pass_count"]) == 6
    assert int(summary["static_boundary_motion_report_count"]) == 4
    assert int(summary["prescribed_boundary_motion_report_count"]) == 2
    assert int(summary["error_count"]) == 0
    assert int(summary["warning_count"]) == 0
    assert int(summary["quality_report_max_size_bytes"]) < 100_000
    assert int(summary["procedural_row_count"]) == 6


def test_step34_step33_regression_guard_is_valid():
    summary = read_json("outputs/step34_step33_regression_guard/step33_regression_guard.json")
    rows = read_csv_rows("outputs/step34_step33_regression_guard/step33_regression_guard.csv")
    assert int(summary["row_count"]) == 8
    assert int(summary["pass_count"]) == 8
    assert int(summary["step33_motion_row_count"]) == 243
    assert summary["step33_motion_quality_pass"] is True
    assert summary["step33_repeatability_pass"] is True
    assert summary["step33_consistency_pass"] is True
    assert int(summary["step33_large_file_count"]) == 0
    assert int(summary["step33_vtr_count"]) == 0
    assert int(summary["step33_particle_npy_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step34_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "README.md",
            "docs/08_roadmap.md",
            "docs/09_api_reference.md",
            "docs/11_artifact_policy.md",
            "docs/12_geometry_ingestion.md",
            "docs/30_controlled_squid_proxy_region_geometry.md",
            "docs/31_controlled_squid_proxy_region_static_driver.md",
            "docs/32_controlled_squid_proxy_kinematics_schedule.md",
            "docs/33_controlled_squid_proxy_kinematics_mapping.md",
            "docs/34_controlled_squid_proxy_boundary_motion_driver_interface.md",
            "STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step34_artifact_budget_is_valid():
    summary = read_json("outputs/step34_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step34_total_size_mb"]) < 10.0
    assert float(summary["total_size_mb"]) < 205.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step34_vtr_count"]) == 0
    assert int(summary["step34_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step34_artifact_manifest/artifact_manifest.csv")
    step34_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step34")]
    assert not [path for path in step34_paths if path.endswith(".vtr")]
    assert not [path for path in step34_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step34_report_acceptance_complete():
    report = read_text("STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Boundary-Motion Config Validation",
        "## 5. Boundary-Motion Interface Report",
        "## 6. Static Driver Regression",
        "## 7. Prescribed Interface No-Op Smoke",
        "## 8. Step 31 Static Comparison",
        "## 9. No-Op State Guard",
        "## 10. Quality Report Aggregation",
        "## 11. Step 33 Regression Guard",
        "## 12. Artifact Manifest Summary",
        "## 13. Verification Commands",
        "## 14. GitHub Sync Information",
        "## 15. Acceptance Checklist",
        "## 16. Decision For Step 35",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] boundary-motion config validation passes",
        "- [x] diagnostic_only is true",
        "- [x] all boundary-motion execution flags are false",
        "- [x] interface report writes schedule_row_count == 81",
        "- [x] interface report writes motion_mapping_row_count == 243",
        "- [x] interface report writes tracked_region_count == 3",
        "- [x] interface report no_op_pass is true",
        "- [x] static none row passes",
        "- [x] static penalty row passes",
        "- [x] static moving_boundary engineering row passes",
        "- [x] static moving_boundary link_area row passes",
        "- [x] prescribed moving_boundary engineering row passes",
        "- [x] prescribed moving_boundary link_area row passes",
        "- [x] prescribed rows write boundary_motion_interface_report.json",
        "- [x] prescribed rows remain no-op relative to Step 34 static rows",
        "- [x] Step 31 static comparison passes",
        "- [x] Step 33 regression guard passes",
        "- [x] every Step 34 quality report passes strict gate",
        "- [x] default boundary_motion_mode remains static",
        "- [x] default quality_check_enabled remains false",
        "- [x] default quality_check_strict remains false",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no LBM population update",
        "- [x] no moving bounce-back formula changes",
        "- [x] no coupler formula changes",
        "- [x] no projection formula changes",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] no Step 34 .vtr outputs",
        "- [x] no Step 34 particle .npy outputs",
        "- [x] artifact large_file_count == 0",
        "- [x] Step 34 output total-size budget passes",
        "- [x] repo artifact summary total_size_mb < 205",
        "- [x] logs/step34_pytest.log exists",
        "- [x] full pytest passes",
        "- [x] Step 34 contract test passes",
        "- [x] git diff --check passes",
        "- [x] staged whitespace check passes",
        "- [x] pre-push hook passes",
        "- [x] Step 34 artifacts are pushed to origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step34_pytest.log").is_file()
    for path, marker in STEP34_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def test_step34_solver_formula_boundaries_are_valid():
    report = read_text("STEP34_CONTROLLED_SQUID_PROXY_BOUNDARY_MOTION_DRIVER_INTERFACE_REPORT.md")
    assert "The Step 34 driver change is limited to config validation and report writing." in report
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


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}
