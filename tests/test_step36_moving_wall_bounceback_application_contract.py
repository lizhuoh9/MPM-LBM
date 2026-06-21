import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP36_REQUIRED_FILES = [
    "STEP36_CONTROLLED_MOVING_WALL_BOUNCEBACK_VELOCITY_APPLICATION_SMOKE_GOAL.md",
    "STEP36_CONTROLLED_MOVING_WALL_BOUNCEBACK_VELOCITY_APPLICATION_SMOKE_REPORT.md",
    "docs/36_controlled_moving_wall_bounceback_velocity_application_smoke.md",
    "configs/step36_wall_velocity_application_solid_vel_experimental.json",
    "configs/step36_static_32_moving_boundary.json",
    "configs/step36_experimental_32_moving_boundary.json",
    "configs/step36_static_48_moving_boundary.json",
    "configs/step36_experimental_48_moving_boundary.json",
    "configs/step36_static_48_link_area.json",
    "configs/step36_experimental_48_link_area.json",
    "src/wall_velocity_application_config.py",
    "src/wall_velocity_application.py",
    "baseline_tests/step36_common.py",
    "baseline_tests/run_step36_wall_velocity_application_config_validation.py",
    "baseline_tests/run_step36_wall_velocity_application_report.py",
    "baseline_tests/run_step36_static_regression_smoke.py",
    "baseline_tests/run_step36_experimental_application_smoke.py",
    "baseline_tests/run_step36_static_vs_experimental_comparison.py",
    "baseline_tests/run_step36_mass_force_stability_diagnostics.py",
    "baseline_tests/run_step36_wall_velocity_application_quality.py",
    "baseline_tests/run_step36_quality_report_aggregation.py",
    "baseline_tests/run_step36_step35_regression_guard.py",
    "baseline_tests/run_step36_artifact_manifest.py",
    "tests/test_step36_moving_wall_bounceback_application_contract.py",
]

STEP36_OUTPUT_FILES = [
    "outputs/step36_wall_velocity_application_config_validation/application_config_validation.csv",
    "outputs/step36_wall_velocity_application_config_validation/application_config_validation_summary.csv",
    "outputs/step36_wall_velocity_application_config_validation/application_config_validation.json",
    "outputs/step36_wall_velocity_application_report/application_report.json",
    "outputs/step36_wall_velocity_application_report/application_report_summary.csv",
    "outputs/step36_static_regression_smoke/static_regression_results.csv",
    "outputs/step36_static_regression_smoke/static_regression_results.json",
    "outputs/step36_static_regression_smoke/static_regression_results.npz",
    "outputs/step36_experimental_application_smoke/experimental_application_results.csv",
    "outputs/step36_experimental_application_smoke/experimental_application_results.json",
    "outputs/step36_experimental_application_smoke/experimental_application_results.npz",
    "outputs/step36_static_vs_experimental_comparison/static_vs_experimental.csv",
    "outputs/step36_static_vs_experimental_comparison/static_vs_experimental.json",
    "outputs/step36_mass_force_stability_diagnostics/mass_force_stability.csv",
    "outputs/step36_mass_force_stability_diagnostics/mass_force_stability.json",
    "outputs/step36_wall_velocity_application_quality/application_quality.csv",
    "outputs/step36_wall_velocity_application_quality/application_quality.json",
    "outputs/step36_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step36_quality_report_aggregation/quality_report_summary.json",
    "outputs/step36_step35_regression_guard/step35_regression_guard.csv",
    "outputs/step36_step35_regression_guard/step35_regression_guard.json",
    "outputs/step36_artifact_manifest/artifact_manifest.csv",
    "outputs/step36_artifact_manifest/artifact_summary.csv",
    "outputs/step36_artifact_manifest/artifact_summary.json",
]

STEP36_LOG_MARKERS = {
    "logs/step36_wall_velocity_application_config_validation.log": "[OK] Step 36 wall velocity application config validation finished",
    "logs/step36_wall_velocity_application_report.log": "[OK] Step 36 wall velocity application report finished",
    "logs/step36_static_regression_smoke.log": "[OK] Step 36 static regression smoke finished",
    "logs/step36_experimental_application_smoke.log": "[OK] Step 36 experimental application smoke finished",
    "logs/step36_static_vs_experimental_comparison.log": "[OK] Step 36 static vs experimental comparison finished",
    "logs/step36_mass_force_stability_diagnostics.log": "[OK] Step 36 mass force stability diagnostics finished",
    "logs/step36_wall_velocity_application_quality.log": "[OK] Step 36 wall velocity application quality finished",
    "logs/step36_quality_report_aggregation.log": "[OK] Step 36 quality report aggregation finished",
    "logs/step36_step35_regression_guard.log": "[OK] Step 36 Step 35 regression guard finished",
    "logs/step36_artifact_manifest.log": "[OK] Step 36 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 36 is controlled moving-wall bounce-back velocity application smoke.",
    "Step 36 is opt-in and experimental.",
    "It applies wall velocity only through the existing `solid_vel` channel",
    "Step 36 does not change moving bounce-back formulas.",
    "Step 36 does not update LBM populations outside the existing bounce-back step.",
    "Step 36 does not implement a jet model.",
    "Step 36 does not implement squid swimming.",
    "Step 36 does not implement real squid validation.",
    "The default `boundary_motion_mode` remains static.",
    "The default `wall_velocity_application_mode` remains disabled.",
    "The default `quality_check_enabled` remains false.",
    "The default `quality_check_strict` remains false.",
    "The default `reaction_transfer_mode` remains engineering.",
]

FORBIDDEN_CLAIMS = [
    "jet model is implemented",
    "squid swimming is implemented",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "implements two_phase",
    "implements contact_angle",
]


def test_step36_required_artifacts_exist():
    missing = [path for path in STEP36_REQUIRED_FILES + STEP36_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step36_config_defaults_are_safe():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in text
    assert "boundary_motion_config_path: Optional[str] = None" in text
    assert "boundary_motion_report_enabled: bool = False" in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "wall_velocity_application_config_path: Optional[str] = None" in text
    assert "wall_velocity_application_report_enabled: bool = False" in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step36_application_config_validation_is_valid():
    payload = read_json("outputs/step36_wall_velocity_application_config_validation/application_config_validation.json")
    config = payload["config"]
    summary = payload["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["row_count"]) == 19
    assert int(summary["pass_count"]) == 19
    assert config["application_mode"] == "solid_vel_experimental"
    assert config["target_lbm_field"] == "solid_vel"
    assert config["application_policy"] == "additive_capped"
    assert float(config["wall_velocity_scale"]) == 0.05
    assert float(config["wall_velocity_cap_lbm"]) == 0.01
    assert config["apply_to_lbm_solid_vel"] is True
    assert config["apply_to_lbm_populations"] is False
    assert config["apply_to_mpm"] is False
    assert config["apply_to_projector"] is False
    assert config["modify_bounceback_formula"] is False
    assert config["jet_model_enabled"] is False
    assert config["actuation_claim_enabled"] is False


def test_step36_application_report_is_valid():
    summary = read_json("outputs/step36_wall_velocity_application_report/application_report.json")["summary"]
    assert summary["report_pass"] is True
    assert int(summary["n_grid"]) == 48
    assert int(summary["wall_velocity_row_count"]) == 63
    assert int(summary["applied_cell_count"]) > 0
    assert summary["finite_pass"] is True
    assert summary["cap_pass"] is True
    assert float(summary["max_capped_velocity_norm"]) <= float(summary["wall_velocity_cap_lbm"])
    assert summary["apply_to_lbm_populations"] is False
    assert summary["modify_bounceback_formula"] is False


def test_step36_static_regression_smoke_is_valid():
    payload = read_json("outputs/step36_static_regression_smoke/static_regression_results.json")
    summary = payload["summary"]
    assert int(summary["driver_row_count"]) == 3
    assert int(summary["stable_count"]) == 3
    assert int(summary["quality_pass_count"]) == 3
    assert int(summary["application_report_count"]) == 0
    assert int(summary["static_application_row_count"]) == 3
    assert int(summary["experimental_application_row_count"]) == 0
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["wall_velocity_application_mode"] == "disabled" for row in payload["rows"])
    assert all(int(row["applied_cell_count"]) == 0 for row in payload["rows"])


def test_step36_experimental_application_smoke_is_valid():
    payload = read_json("outputs/step36_experimental_application_smoke/experimental_application_results.json")
    summary = payload["summary"]
    assert int(summary["driver_row_count"]) == 3
    assert int(summary["stable_count"]) == 3
    assert int(summary["quality_pass_count"]) == 3
    assert int(summary["application_report_count"]) == 3
    assert int(summary["experimental_application_row_count"]) == 3
    assert int(summary["min_applied_cell_count"]) > 0
    assert float(summary["max_applied_velocity_norm"]) <= 0.01
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["wall_velocity_application_report_pass"] is True for row in payload["rows"])
    assert all(int(row["driver_application_report_count"]) == 5 for row in payload["rows"])


def test_step36_static_vs_experimental_comparison_is_valid():
    payload = read_json("outputs/step36_static_vs_experimental_comparison/static_vs_experimental.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 3
    assert int(summary["pass_count"]) == 3
    assert summary["comparison_pass"] is True
    assert all(row["comparison_pass"] is True for row in payload["rows"])


def test_step36_mass_force_stability_diagnostics_are_valid():
    payload = read_json("outputs/step36_mass_force_stability_diagnostics/mass_force_stability.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 3
    assert int(summary["pass_count"]) == 3
    assert summary["stability_pass"] is True
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert int(summary["max_lbm_population_update_count"]) == 0


def test_step36_wall_velocity_application_quality_is_valid():
    payload = read_json("outputs/step36_wall_velocity_application_quality/application_quality.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 3
    assert int(summary["pass_count"]) == 3
    assert summary["quality_pass"] is True
    assert int(summary["min_applied_cell_count"]) > 0
    assert float(summary["max_applied_velocity_norm"]) <= 0.01
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["quality_pass"] is True for row in payload["rows"])


def test_step36_quality_report_aggregation_is_valid():
    summary = read_json("outputs/step36_quality_report_aggregation/quality_report_summary.json")["summary"]
    assert int(summary["quality_report_count"]) == 6
    assert int(summary["pass_count"]) == 6
    assert int(summary["strict_count"]) == 6
    assert int(summary["disabled_application_report_count"]) == 3
    assert int(summary["experimental_application_report_count"]) == 3
    assert int(summary["warning_count"]) == 0
    assert int(summary["error_count"]) == 0


def test_step36_step35_regression_guard_is_valid():
    payload = read_json("outputs/step36_step35_regression_guard/step35_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 15
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step36_default_modes_remain_unchanged():
    for config_path in [
        "configs/step36_static_32_moving_boundary.json",
        "configs/step36_static_48_moving_boundary.json",
        "configs/step36_static_48_link_area.json",
    ]:
        config = read_json(config_path)
        assert config["boundary_motion_mode"] == "static"
        assert config["wall_velocity_application_mode"] == "disabled"
        assert config["wall_velocity_application_config_path"] is None
        assert config["wall_velocity_application_report_enabled"] is False


def test_step36_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/36_controlled_moving_wall_bounceback_velocity_application_smoke.md",
            "STEP36_CONTROLLED_MOVING_WALL_BOUNCEBACK_VELOCITY_APPLICATION_SMOKE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step36_artifact_budget_is_valid():
    summary = read_json("outputs/step36_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step36_total_size_mb"]) < 15.0
    assert float(summary["total_size_mb"]) < 220.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step36_vtr_count"]) == 0
    assert int(summary["step36_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step36_artifact_manifest/artifact_manifest.csv")
    step36_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step36")]
    assert not [path for path in step36_paths if path.endswith(".vtr")]
    assert not [path for path in step36_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step36_report_acceptance_complete():
    report = read_text("STEP36_CONTROLLED_MOVING_WALL_BOUNCEBACK_VELOCITY_APPLICATION_SMOKE_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Application Config Validation",
        "## 5. Application Report",
        "## 6. Static Regression Smoke",
        "## 7. Experimental Application Smoke",
        "## 8. Static Vs Experimental Comparison",
        "## 9. Mass Force Stability Diagnostics",
        "## 10. Wall Velocity Application Quality",
        "## 11. Quality Report Aggregation",
        "## 12. Step 35 Regression Guard",
        "## 13. Artifact Manifest Summary",
        "## 14. Verification Commands",
        "## 15. GitHub Sync Information",
        "## 16. Acceptance Checklist",
        "## 17. Decision For Step 37",
    ]
    assert [section for section in required_sections if section not in report] == []

    required_checks = [
        "- [x] Application config validation passes.",
        "- [x] Application report passes.",
        "- [x] Static regression smoke passes.",
        "- [x] Experimental application smoke passes.",
        "- [x] Static vs experimental comparison passes.",
        "- [x] Mass force stability diagnostics pass.",
        "- [x] Wall velocity application quality passes.",
        "- [x] Quality report aggregation passes.",
        "- [x] Step 35 regression guard passes.",
        "- [x] No `external/taichi_LBM3D` edits.",
        "- [x] No Step 36 `.vtr` outputs.",
        "- [x] No Step 36 particle `.npy` outputs.",
        "- [x] `logs/step36_pytest.log` exists.",
        "- [x] Full pytest passes.",
        "- [x] Step 36 contract test passes.",
        "- [x] Step 36 artifacts are pushed to `origin/main`.",
    ]
    assert [check for check in required_checks if check not in report] == []

    assert (ROOT / "logs/step36_pytest.log").is_file()
    for path, marker in STEP36_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str):
    return json.loads(read_text(relative_path))


def read_csv_rows(relative_path: str) -> list[dict]:
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
