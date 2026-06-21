import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP37_REQUIRED_FILES = [
    "STEP37_CONTROLLED_MOVING_WALL_APPLICATION_SHORT_WINDOW_ENVELOPE_GOAL.md",
    "STEP37_CONTROLLED_MOVING_WALL_APPLICATION_SHORT_WINDOW_ENVELOPE_REPORT.md",
    "docs/37_controlled_moving_wall_application_short_window_envelope.md",
    "configs/step37_static_48_moving_boundary.json",
    "configs/step37_experimental_48_moving_boundary.json",
    "configs/step37_static_48_link_area.json",
    "configs/step37_experimental_48_link_area.json",
    "src/wall_velocity_application_envelope.py",
    "baseline_tests/step37_common.py",
    "baseline_tests/run_step37_application_window_driver.py",
    "baseline_tests/run_step37_application_envelope_summary.py",
    "baseline_tests/run_step37_static_vs_experimental_envelope.py",
    "baseline_tests/run_step37_engineering_vs_link_area_envelope.py",
    "baseline_tests/run_step37_mass_force_bounceback_envelope.py",
    "baseline_tests/run_step37_wall_velocity_timeseries_quality.py",
    "baseline_tests/run_step37_quality_report_aggregation.py",
    "baseline_tests/run_step37_step36_regression_guard.py",
    "baseline_tests/run_step37_artifact_manifest.py",
    "tests/test_step37_wall_velocity_application_envelope_contract.py",
]

STEP37_OUTPUT_FILES = [
    "outputs/step37_application_window_driver/application_window_results.csv",
    "outputs/step37_application_window_driver/application_window_results.json",
    "outputs/step37_application_window_driver/application_window_results.npz",
    "outputs/step37_application_window_driver/experimental_48_moving_boundary/wall_velocity_application_timeseries.csv",
    "outputs/step37_application_window_driver/experimental_48_moving_boundary/wall_velocity_application_timeseries.json",
    "outputs/step37_application_window_driver/experimental_48_link_area/wall_velocity_application_timeseries.csv",
    "outputs/step37_application_window_driver/experimental_48_link_area/wall_velocity_application_timeseries.json",
    "outputs/step37_application_envelope_summary/application_envelope.csv",
    "outputs/step37_application_envelope_summary/application_envelope.json",
    "outputs/step37_static_vs_experimental_envelope/static_vs_experimental_envelope.csv",
    "outputs/step37_static_vs_experimental_envelope/static_vs_experimental_envelope.json",
    "outputs/step37_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.csv",
    "outputs/step37_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.json",
    "outputs/step37_mass_force_bounceback_envelope/mass_force_bounceback_envelope.csv",
    "outputs/step37_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json",
    "outputs/step37_wall_velocity_timeseries_quality/wall_velocity_timeseries_quality.csv",
    "outputs/step37_wall_velocity_timeseries_quality/wall_velocity_timeseries_quality.json",
    "outputs/step37_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step37_quality_report_aggregation/quality_report_summary.json",
    "outputs/step37_step36_regression_guard/step36_regression_guard.csv",
    "outputs/step37_step36_regression_guard/step36_regression_guard.json",
    "outputs/step37_artifact_manifest/artifact_manifest.csv",
    "outputs/step37_artifact_manifest/artifact_summary.csv",
    "outputs/step37_artifact_manifest/artifact_summary.json",
]

STEP37_LOG_MARKERS = {
    "logs/step37_application_window_driver.log": "[OK] Step 37 application window driver finished",
    "logs/step37_application_envelope_summary.log": "[OK] Step 37 application envelope summary finished",
    "logs/step37_static_vs_experimental_envelope.log": "[OK] Step 37 static vs experimental envelope finished",
    "logs/step37_engineering_vs_link_area_envelope.log": "[OK] Step 37 engineering vs link-area envelope finished",
    "logs/step37_mass_force_bounceback_envelope.log": "[OK] Step 37 mass force bounceback envelope finished",
    "logs/step37_wall_velocity_timeseries_quality.log": "[OK] Step 37 wall velocity timeseries quality finished",
    "logs/step37_quality_report_aggregation.log": "[OK] Step 37 quality report aggregation finished",
    "logs/step37_step36_regression_guard.log": "[OK] Step 37 Step 36 regression guard finished",
    "logs/step37_artifact_manifest.log": "[OK] Step 37 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 37 is controlled moving-wall application short-window envelope.",
    "Step 37 remains opt-in and experimental.",
    "Step 37 uses the existing solid_vel channel.",
    "Step 37 does not change moving bounce-back formulas.",
    "Step 37 does not implement a jet model.",
    "Step 37 does not implement squid swimming.",
    "Step 37 does not implement real squid validation.",
    "The default boundary_motion_mode remains static.",
    "The default wall_velocity_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "squid swimming is implemented",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "jet model is implemented",
    "jet propulsion is validated",
    "free-body motion is implemented",
    "two-phase flow is implemented",
    "contact angle physics is implemented",
    "moving bounce-back formula is changed",
    "default wall velocity application is enabled",
]


def test_step37_required_artifacts_exist():
    missing = [path for path in STEP37_REQUIRED_FILES + STEP37_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []


def test_step37_driver_configs_are_valid():
    configs = [
        read_json("configs/step37_static_48_moving_boundary.json"),
        read_json("configs/step37_experimental_48_moving_boundary.json"),
        read_json("configs/step37_static_48_link_area.json"),
        read_json("configs/step37_experimental_48_link_area.json"),
    ]
    assert len(configs) == 4
    assert all(config["coupling_mode"] == "moving_boundary" for config in configs)
    assert all(config["geometry_type"] == "squid_proxy" for config in configs)
    assert all(config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json" for config in configs)
    assert all(int(config["n_grid"]) == 48 for config in configs)
    assert all(int(config["n_particles"]) == 4096 for config in configs)
    assert all(int(config["n_lbm_steps"]) == 20 for config in configs)
    assert all(int(config["mpm_substeps_per_lbm_step"]) == 5 for config in configs)
    assert all(int(config["output_interval"]) == 1 for config in configs)
    assert all(config["quality_check_enabled"] is True and config["quality_check_strict"] is True for config in configs)
    assert all(config["write_vtk"] is False and config["write_particles"] is False for config in configs)
    static = [config for config in configs if config["wall_velocity_application_mode"] == "disabled"]
    experimental = [config for config in configs if config["wall_velocity_application_mode"] == "solid_vel_experimental"]
    assert len(static) == 2
    assert len(experimental) == 2
    assert all(config["boundary_motion_mode"] == "static" for config in static)
    assert all(config["boundary_motion_mode"] == "prescribed_kinematic" for config in experimental)
    assert all(config["wall_velocity_application_config_path"] == "configs/step36_wall_velocity_application_solid_vel_experimental.json" for config in experimental)


def test_step37_application_window_driver_is_valid():
    payload = read_json("outputs/step37_application_window_driver/application_window_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["quality_pass_count"]) == 4
    assert int(summary["static_row_count"]) == 2
    assert int(summary["experimental_row_count"]) == 2
    assert int(summary["min_completed_lbm_steps"]) >= 20
    assert int(summary["min_total_mpm_substeps"]) >= 100
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["stable"] is True for row in rows)
    assert all(int(row["completed_lbm_steps"]) >= 20 for row in rows)
    assert all(int(row["total_mpm_substeps"]) >= 100 for row in rows)


def test_step37_application_envelope_summary_is_valid():
    payload = read_json("outputs/step37_application_envelope_summary/application_envelope.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert summary["application_envelope_pass"] is True
    assert float(summary["max_applied_velocity_norm"]) <= 0.01
    for row in payload["rows"]:
        assert int(row["application_report_count"]) >= 20
        assert int(row["applied_cell_count_min"]) > 0
        assert int(row["applied_cell_count_max"]) >= int(row["applied_cell_count_min"])
        assert float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"])
        assert int(row["lbm_population_update_count_max"]) == 0


def test_step37_static_vs_experimental_envelope_is_valid():
    payload = read_json("outputs/step37_static_vs_experimental_envelope/static_vs_experimental_envelope.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert summary["comparison_pass"] is True
    assert all(row["comparison_pass"] is True for row in payload["rows"])
    assert all(row["both_stable"] is True for row in payload["rows"])
    assert all(float(row["experimental_applied_velocity_max"]) > 0.0 for row in payload["rows"])


def test_step37_engineering_vs_link_area_envelope_is_valid():
    payload = read_json("outputs/step37_engineering_vs_link_area_envelope/engineering_vs_link_area_envelope.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 1
    assert int(summary["pass_count"]) == 1
    assert summary["comparison_pass"] is True
    row = payload["rows"][0]
    assert row["both_stable"] is True
    assert 0.25 <= float(row["link_area_scale_final"]) <= 2.0
    assert row["comparison_pass"] is True


def test_step37_mass_force_bounceback_envelope_is_valid():
    payload = read_json("outputs/step37_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert summary["envelope_pass"] is True
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_applied_velocity_norm"]) <= 0.01
    assert all(row["envelope_pass"] is True for row in payload["rows"])


def test_step37_wall_velocity_timeseries_quality_is_valid():
    payload = read_json("outputs/step37_wall_velocity_timeseries_quality/wall_velocity_timeseries_quality.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert summary["quality_pass"] is True
    assert int(summary["min_timeseries_row_count"]) >= 20
    assert int(summary["min_applied_cell_count"]) > 0
    assert float(summary["max_applied_velocity_norm"]) <= 0.01
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["quality_pass"] is True for row in payload["rows"])


def test_step37_quality_report_aggregation_is_valid():
    summary = read_json("outputs/step37_quality_report_aggregation/quality_report_summary.json")["summary"]
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["warning_count"]) == 0
    assert int(summary["error_count"]) == 0


def test_step37_step36_regression_guard_is_valid():
    payload = read_json("outputs/step37_step36_regression_guard/step36_regression_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 8
    assert int(summary["pass_count"]) == 8
    assert summary["regression_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step37_default_modes_remain_unchanged():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "wall_velocity_application_config_path: Optional[str] = None" in text
    assert "wall_velocity_application_report_enabled: bool = False" in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step37_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/37_controlled_moving_wall_application_short_window_envelope.md",
            "STEP37_CONTROLLED_MOVING_WALL_APPLICATION_SHORT_WINDOW_ENVELOPE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step37_artifact_budget_is_valid():
    summary = read_json("outputs/step37_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step37_total_size_mb"]) < 20.0
    assert float(summary["total_size_mb"]) < 230.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["step37_vtr_count"]) == 0
    assert int(summary["step37_particle_npy_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    manifest_rows = read_csv_rows("outputs/step37_artifact_manifest/artifact_manifest.csv")
    step37_paths = [row["path"] for row in manifest_rows if row["path"].startswith("outputs/step37")]
    assert not [path for path in step37_paths if path.endswith(".vtr")]
    assert not [path for path in step37_paths if path.endswith(".npy") and "particle" in path.lower()]


def test_step37_report_acceptance_complete():
    report = read_text("STEP37_CONTROLLED_MOVING_WALL_APPLICATION_SHORT_WINDOW_ENVELOPE_REPORT.md")
    required_sections = [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Application Window Driver",
        "## 5. Application Envelope Summary",
        "## 6. Static Vs Experimental Envelope",
        "## 7. Engineering Vs Link-Area Envelope",
        "## 8. Mass Force Bounce-Back Envelope",
        "## 9. Wall Velocity Timeseries Quality",
        "## 10. Quality Report Aggregation",
        "## 11. Step 36 Regression Guard",
        "## 12. Artifact Manifest Summary",
        "## 13. Verification Commands",
        "## 14. GitHub Sync Information",
        "## 15. Acceptance Checklist",
        "## 16. Decision For Step 38",
    ]
    assert [section for section in required_sections if section not in report] == []
    required_checks = [
        "- [x] Application window driver runs 4 rows.",
        "- [x] Experimental rows write wall velocity application timeseries.",
        "- [x] Static vs experimental envelope passes.",
        "- [x] Engineering vs link-area envelope passes.",
        "- [x] Mass/force/bounce-back envelope passes.",
        "- [x] Wall velocity timeseries quality passes.",
        "- [x] Step 36 regression guard passes.",
        "- [x] No `external/taichi_LBM3D` edits.",
        "- [x] No Step 37 `.vtr` outputs.",
        "- [x] No Step 37 particle `.npy` outputs.",
        "- [x] `logs/step37_pytest.log` exists.",
        "- [x] Full pytest passes.",
        "- [x] Step 37 contract test passes.",
        "- [x] Step 37 artifacts are pushed to `origin/main`.",
    ]
    assert [check for check in required_checks if check not in report] == []
    assert (ROOT / "logs/step37_pytest.log").is_file()
    for path, marker in STEP37_LOG_MARKERS.items():
        assert (ROOT / path).is_file(), path
        assert marker in read_text(path), path


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def read_json(relative_path: str):
    return json.loads(read_text(relative_path))


def read_csv_rows(relative_path: str) -> list[dict]:
    with (ROOT / relative_path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
