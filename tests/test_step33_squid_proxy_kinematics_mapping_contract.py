import csv
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP33_REQUIRED_FILES = [
    "STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_GOAL.md",
    "STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_REPORT.md",
    "docs/33_controlled_squid_proxy_kinematics_mapping.md",
    "src/squid_motion_mapping_config.py",
    "src/squid_motion_mapping.py",
    "src/squid_motion_quality.py",
    "src/squid_motion_projection_diagnostics.py",
    "configs/step33_squid_proxy_motion_mapping.json",
    "configs/step33_squid_proxy_motion_sampling.json",
    "baseline_tests/step33_common.py",
    "baseline_tests/run_step33_motion_mapping_config_validation.py",
    "baseline_tests/run_step33_generate_motion_mapping.py",
    "baseline_tests/run_step33_motion_quality.py",
    "baseline_tests/run_step33_motion_repeatability.py",
    "baseline_tests/run_step33_motion_grid_diagnostics.py",
    "baseline_tests/run_step33_schedule_motion_consistency.py",
    "baseline_tests/run_step33_step32_regression_guard.py",
    "baseline_tests/run_step33_artifact_manifest.py",
    "tests/test_step33_squid_proxy_kinematics_mapping_contract.py",
]

STEP33_OUTPUT_FILES = [
    "outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation.csv",
    "outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation.json",
    "outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation_summary.csv",
    "outputs/step33_motion_mapping/motion_mapping.csv",
    "outputs/step33_motion_mapping/motion_mapping.json",
    "outputs/step33_motion_quality/motion_quality.csv",
    "outputs/step33_motion_quality/motion_quality.json",
    "outputs/step33_motion_repeatability/motion_repeatability.csv",
    "outputs/step33_motion_repeatability/motion_repeatability.json",
    "outputs/step33_motion_grid_diagnostics/motion_grid_diagnostics.csv",
    "outputs/step33_motion_grid_diagnostics/motion_grid_diagnostics.json",
    "outputs/step33_schedule_motion_consistency/schedule_motion_consistency.csv",
    "outputs/step33_schedule_motion_consistency/schedule_motion_consistency.json",
    "outputs/step33_step32_regression_guard/step32_regression_guard.csv",
    "outputs/step33_step32_regression_guard/step32_regression_guard.json",
    "outputs/step33_artifact_manifest/artifact_manifest.csv",
    "outputs/step33_artifact_manifest/artifact_summary.csv",
    "outputs/step33_artifact_manifest/artifact_summary.json",
]

STEP33_LOG_MARKERS = {
    "logs/step33_motion_mapping_config_validation.log": "[OK] Step 33 motion mapping config validation finished",
    "logs/step33_generate_motion_mapping.log": "[OK] Step 33 generate motion mapping finished",
    "logs/step33_motion_quality.log": "[OK] Step 33 motion quality finished",
    "logs/step33_motion_repeatability.log": "[OK] Step 33 motion repeatability finished",
    "logs/step33_motion_grid_diagnostics.log": "[OK] Step 33 motion grid diagnostics finished",
    "logs/step33_schedule_motion_consistency.log": "[OK] Step 33 schedule-motion consistency finished",
    "logs/step33_step32_regression_guard.log": "[OK] Step 33 Step 32 regression guard finished",
    "logs/step33_artifact_manifest.log": "[OK] Step 33 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 33 is controlled squid proxy kinematics mapping to boundary-motion diagnostics.",
    "Step 33 maps schedules to displacement and velocity proxies only.",
    "Step 33 does not integrate kinematics into FSIDriver3D.",
    "Step 33 does not apply moving wall velocity to LBM.",
    "Step 33 does not implement a jet model.",
    "Step 33 does not implement squid swimming.",
    "Step 33 does not implement new FSI physics.",
    "The default quality_check_enabled remains false.",
    "The default quality_check_strict remains false.",
    "The default reaction_transfer_mode remains engineering.",
    "The moving bounce-back formula is unchanged.",
    "PenaltyFSICoupler3D, MovingBoundaryFSICoupler3D, and LinkAreaMovingBoundaryCoupler3D are unchanged.",
]

FORBIDDEN_CLAIMS = [
    "moving wall velocity is applied to LBM",
    "kinematics are integrated into FSIDriver3D",
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


def test_step33_required_artifacts_exist():
    missing = [path for path in STEP33_REQUIRED_FILES + STEP33_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step33_motion_mapping_config_is_valid():
    config = read_json("configs/step33_squid_proxy_motion_mapping.json")
    sampling = read_json("configs/step33_squid_proxy_motion_sampling.json")
    validation = read_json("outputs/step33_motion_mapping_config_validation/motion_mapping_config_validation.json")
    assert config["mapping_id"] == "step33_squid_proxy_boundary_motion_diagnostics"
    assert config["schedule_config_path"] == "configs/step32_squid_proxy_kinematics_schedule.json"
    assert config["region_config_path"] == "configs/step30_squid_proxy_region_config.json"
    assert config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json"
    assert int(config["sample_count"]) == 32768
    assert config["grid_sizes"] == [32, 48, 64]
    assert config["tracked_regions"] == ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"]
    assert config["mantle_motion_model"] == "radial_scale_proxy"
    assert config["cavity_motion_model"] == "volume_scale_proxy"
    assert config["funnel_motion_model"] == "aperture_scale_proxy"
    assert config["driver_integration_enabled"] is False
    assert config["lbm_wall_velocity_enabled"] is False
    assert config["jet_model_enabled"] is False
    assert config["actuation_enabled"] is False
    assert config["deterministic"] is True
    assert "motion diagnostics only" in config["scope_note"]
    assert "no driver integration" in config["scope_note"]
    assert sampling["motion_mapping_config_path"] == "configs/step33_squid_proxy_motion_mapping.json"
    assert int(sampling["expected_motion_row_count"]) == 243
    assert sampling["driver_integration_enabled"] is False
    assert sampling["lbm_wall_velocity_enabled"] is False
    assert sampling["jet_model_enabled"] is False
    assert sampling["actuation_enabled"] is False
    summary = validation["summary"]
    assert int(summary["row_count"]) >= 12
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert summary["validation_pass"] is True
    assert all(row["pass"] is True for row in validation["rows"])


def test_step33_motion_mapping_output_is_valid():
    payload = read_json("outputs/step33_motion_mapping/motion_mapping.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 243
    assert int(summary["expected_row_count"]) == 243
    assert int(summary["schedule_sample_count"]) == 81
    assert int(summary["tracked_region_count"]) == 3
    assert summary["tracked_regions"] == ["funnel_outlet_proxy", "mantle_cavity_proxy", "mantle_outer"]
    assert summary["finite_pass"] is True
    assert summary["bounds_pass"] is True
    assert int(summary["mantle_outer_nonzero_velocity_row_count"]) > 0
    assert int(summary["cavity_volume_rate_nonzero_row_count"]) > 0
    assert int(summary["funnel_aperture_rate_nonzero_row_count"]) > 0
    assert float(summary["mantle_outer_max_velocity_norm"]) > 0.0
    assert float(summary["mantle_outer_max_displacement_norm"]) > 0.0
    assert int(summary["driver_integration_enabled_count"]) == 0
    assert int(summary["lbm_wall_velocity_enabled_count"]) == 0
    assert int(summary["jet_model_enabled_count"]) == 0
    assert int(summary["actuation_enabled_count"]) == 0
    assert {row["region_id"] for row in rows} == {"mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"}
    assert all(row["finite_pass"] is True and row["bounds_pass"] is True for row in rows)
    assert all(row["driver_integration_enabled"] is False for row in rows)
    assert all(row["lbm_wall_velocity_enabled"] is False for row in rows)
    assert all(row["jet_model_enabled"] is False for row in rows)
    assert all(row["actuation_enabled"] is False for row in rows)


def test_step33_motion_quality_is_valid():
    payload = read_json("outputs/step33_motion_quality/motion_quality.json")
    summary = payload["summary"]
    for key in (
        "row_count_pass",
        "tracked_region_count_pass",
        "finite_pass",
        "bounds_pass",
        "mantle_motion_pass",
        "cavity_motion_pass",
        "funnel_motion_pass",
        "mantle_velocity_nonzero_during_cycle",
        "cavity_volume_rate_nonzero_during_cycle",
        "funnel_aperture_rate_nonzero_during_open_close",
        "driver_integration_disabled_pass",
        "lbm_wall_velocity_disabled_pass",
        "jet_model_disabled_pass",
        "actuation_disabled_pass",
        "quality_pass",
    ):
        assert summary[key] is True
    assert int(summary["row_count"]) == 243
    assert all(row["pass"] is True for row in payload["rows"])


def test_step33_motion_repeatability_is_valid():
    payload = read_json("outputs/step33_motion_repeatability/motion_repeatability.json")
    summary = payload["summary"]
    assert int(summary["row_count_first"]) == int(summary["row_count_second"]) == 243
    assert summary["motion_hash_first"] == summary["motion_hash_second"]
    assert summary["mantle_motion_hash_first"] == summary["mantle_motion_hash_second"]
    assert summary["cavity_motion_hash_first"] == summary["cavity_motion_hash_second"]
    assert summary["funnel_motion_hash_first"] == summary["funnel_motion_hash_second"]
    assert summary["repeatability_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step33_motion_grid_diagnostics_is_valid():
    payload = read_json("outputs/step33_motion_grid_diagnostics/motion_grid_diagnostics.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 9
    assert int(summary["grid_size_count"]) == 3
    assert int(summary["tracked_region_count"]) == 3
    assert int(summary["min_active_cell_count"]) > 0
    assert int(summary["min_sample_point_count"]) > 0
    assert float(summary["max_velocity_norm"]) >= 0.0
    assert float(summary["max_displacement_norm"]) >= 0.0
    assert summary["finite_pass"] is True
    assert summary["coverage_pass"] is True
    assert {int(row["grid_size"]) for row in rows} == {32, 48, 64}
    assert {row["region_id"] for row in rows} == {"mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"}
    assert all(int(row["active_cell_count"]) > 0 for row in rows)
    assert all(row["finite_pass"] is True and row["coverage_pass"] is True for row in rows)


def test_step33_schedule_motion_consistency_is_valid():
    payload = read_json("outputs/step33_schedule_motion_consistency/schedule_motion_consistency.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 9
    assert int(summary["pass_count"]) == 9
    assert int(summary["schedule_row_count"]) == 81
    assert int(summary["motion_sample_count"]) == 81
    assert summary["consistency_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step33_step32_regression_guard_is_valid():
    summary = read_json("outputs/step33_step32_regression_guard/step32_regression_guard.json")
    rows = read_csv_rows("outputs/step33_step32_regression_guard/step32_regression_guard.csv")
    assert int(summary["row_count"]) == 8
    assert int(summary["pass_count"]) == 8
    assert int(summary["step32_schedule_row_count"]) == 81
    assert summary["step32_quality_pass"] is True
    assert summary["step32_repeatability_pass"] is True
    assert summary["step32_region_mapping_pass"] is True
    assert int(summary["step32_large_file_count"]) == 0
    assert int(summary["step32_vtr_count"]) == 0
    assert int(summary["step32_particle_npy_count"]) == 0
    assert all(as_bool(row["pass"]) for row in rows)


def test_step33_default_modes_remain_unchanged():
    geometry_config = read_text("src/geometry_config.py")
    fsi_config = read_text("src/fsi_config.py")
    assert "quality_check_enabled: bool = False" in geometry_config
    assert "quality_check_strict: bool = False" in geometry_config
    assert "quality_check_enabled: bool = False" in fsi_config
    assert "quality_check_strict: bool = False" in fsi_config
    assert 'reaction_transfer_mode: str = "engineering"' in fsi_config

    formula_files = [
        "src/coupling.py",
        "src/moving_boundary_coupling.py",
        "src/link_area_coupling.py",
        "src/lbm_fluid.py",
        "src/mpm_solid.py",
        "src/projection.py",
    ]
    status = subprocess.run(["git", "status", "--short", *formula_files], cwd=ROOT, check=True, capture_output=True, text=True)
    assert status.stdout.strip() == ""


def test_step33_docs_scope_and_forbidden_claims_are_valid():
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
            "STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step33_artifact_budget_is_valid():
    summary = read_json("outputs/step33_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step33_total_size_mb"]) < 5.0
    assert float(summary["total_size_mb"]) < 195.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step33_vtr_count"]) == 0
    assert int(summary["step33_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step33_artifact_manifest/artifact_manifest.csv")
    step33_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step33")]
    assert not [path for path in step33_paths if path.endswith(".vtr")]
    assert not [path for path in step33_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step33_report_acceptance_complete():
    report = read_text("STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Motion Mapping Config Validation",
        "## 5. Generated Motion Mapping",
        "## 6. Motion Quality",
        "## 7. Motion Repeatability",
        "## 8. Motion Grid Diagnostics",
        "## 9. Schedule-Motion Consistency",
        "## 10. Step 32 Regression Guard",
        "## 11. Artifact Manifest Summary",
        "## 12. Verification Commands",
        "## 13. GitHub Sync Information",
        "## 14. Acceptance Checklist",
        "## 15. Decision For Step 34",
    ]
    missing_sections = [section for section in required_sections if section not in report]
    assert missing_sections == []

    required_checks = [
        "- [x] motion mapping config validation passes",
        "- [x] schedule config path exists",
        "- [x] region config path exists",
        "- [x] geometry config path exists",
        "- [x] tracked regions include mantle_outer",
        "- [x] tracked regions include mantle_cavity_proxy",
        "- [x] tracked regions include funnel_outlet_proxy",
        "- [x] driver integration flag is false",
        "- [x] LBM wall velocity flag is false",
        "- [x] jet model flag is false",
        "- [x] actuation flag is false",
        "- [x] generated motion mapping has expected row count",
        "- [x] motion mapping fields are finite",
        "- [x] displacement proxy fields are bounded",
        "- [x] velocity proxy fields are bounded",
        "- [x] mantle_outer motion diagnostics pass",
        "- [x] mantle_cavity_proxy motion diagnostics pass",
        "- [x] funnel_outlet_proxy motion diagnostics pass",
        "- [x] motion quality passes",
        "- [x] motion repeatability hash passes",
        "- [x] mantle motion hash repeats",
        "- [x] cavity motion hash repeats",
        "- [x] funnel motion hash repeats",
        "- [x] motion grid diagnostics pass at 32^3",
        "- [x] motion grid diagnostics pass at 48^3",
        "- [x] motion grid diagnostics pass at 64^3",
        "- [x] schedule-motion consistency passes",
        "- [x] Step 32 regression guard passes",
        "- [x] default quality_check_enabled remains false",
        "- [x] default quality_check_strict remains false",
        "- [x] default reaction_transfer_mode remains engineering",
        "- [x] no FSIDriver3D integration",
        "- [x] no LBM moving wall velocity application",
        "- [x] no jet model",
        "- [x] no mantle contraction driver claim",
        "- [x] no funnel actuation driver claim",
        "- [x] no squid swimming claim",
        "- [x] no real squid validation claim",
        "- [x] no new FSI physics",
        "- [x] no moving bounce-back formula changes",
        "- [x] no LBM formula changes",
        "- [x] no MPM constitutive formula changes",
        "- [x] no projection formula changes",
        "- [x] no external/taichi_LBM3D edits",
        "- [x] no Step 33 .vtr outputs",
        "- [x] no Step 33 particle .npy outputs",
        "- [x] artifact large_file_count == 0",
        "- [x] Step 33 output total-size budget passes",
        "- [x] repo artifact summary total_size_mb < 195",
        "- [x] logs/step33_pytest.log exists",
        "- [x] pytest -q passes",
        "- [x] Step 33 contract test passes",
        "- [x] git diff --check passes",
        "- [x] staged whitespace check passes",
        "- [x] pre-push hook passes",
        "- [x] Step 33 artifacts are pushed to origin/main",
    ]
    missing_checks = [check for check in required_checks if check not in report]
    assert missing_checks == []

    assert (ROOT / "logs/step33_pytest.log").is_file()
    for path, marker in STEP33_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def test_step33_no_driver_integration_claims():
    report = read_text("STEP33_CONTROLLED_SQUID_PROXY_KINEMATICS_MAPPING_REPORT.md")
    assert "No FSIDriver3D, LBM, MPM, moving bounce-back, link-area, or projection formula files were edited." in report
    external_status = subprocess.run(
        ["git", "status", "--short", "external/taichi_LBM3D"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert external_status.stdout.strip() == ""


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
