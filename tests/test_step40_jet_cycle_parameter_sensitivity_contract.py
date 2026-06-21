import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP40_REQUIRED_FILES = [
    "STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_GOAL.md",
    "STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_REPORT.md",
    "docs/40_controlled_jet_cycle_proxy_parameter_sensitivity_smoke.md",
    "configs/step40_wall_velocity_application_scale_0025.json",
    "configs/step40_wall_velocity_application_scale_0050.json",
    "configs/step40_wall_velocity_application_scale_0075.json",
    "configs/step40_static_48_moving_boundary.json",
    "configs/step40_static_48_link_area.json",
    "configs/step40_experimental_48_moving_boundary_scale_0025.json",
    "configs/step40_experimental_48_moving_boundary_scale_0050.json",
    "configs/step40_experimental_48_moving_boundary_scale_0075.json",
    "configs/step40_experimental_48_link_area_scale_0025.json",
    "configs/step40_experimental_48_link_area_scale_0050.json",
    "configs/step40_experimental_48_link_area_scale_0075.json",
    "src/jet_cycle_parameter_sensitivity.py",
    "baseline_tests/step40_common.py",
    "baseline_tests/run_step40_parameter_config_validation.py",
    "baseline_tests/run_step40_parameter_sweep_driver.py",
    "baseline_tests/run_step40_parameter_sensitivity_summary.py",
    "baseline_tests/run_step40_static_vs_parameter_comparison.py",
    "baseline_tests/run_step40_engineering_vs_link_area_parameter_comparison.py",
    "baseline_tests/run_step40_cap_saturation_diagnostics.py",
    "baseline_tests/run_step40_force_impulse_parameter_response.py",
    "baseline_tests/run_step40_tethered_no_free_body_guard.py",
    "baseline_tests/run_step40_quality_report_aggregation.py",
    "baseline_tests/run_step40_step39_regression_guard.py",
    "baseline_tests/run_step40_artifact_manifest.py",
    "tests/test_step40_jet_cycle_parameter_sensitivity_contract.py",
]

STEP40_OUTPUT_FILES = [
    "outputs/step40_parameter_config_validation/parameter_config_validation.csv",
    "outputs/step40_parameter_config_validation/parameter_config_validation.json",
    "outputs/step40_parameter_sweep_driver/parameter_sweep_results.csv",
    "outputs/step40_parameter_sweep_driver/parameter_sweep_results.json",
    "outputs/step40_parameter_sweep_driver/parameter_sweep_results.npz",
    "outputs/step40_parameter_sweep_driver/experimental_48_moving_boundary_scale_0025/wall_velocity_application_timeseries.csv",
    "outputs/step40_parameter_sweep_driver/experimental_48_moving_boundary_scale_0050/wall_velocity_application_timeseries.csv",
    "outputs/step40_parameter_sweep_driver/experimental_48_moving_boundary_scale_0075/wall_velocity_application_timeseries.csv",
    "outputs/step40_parameter_sweep_driver/experimental_48_link_area_scale_0025/wall_velocity_application_timeseries.csv",
    "outputs/step40_parameter_sweep_driver/experimental_48_link_area_scale_0050/wall_velocity_application_timeseries.csv",
    "outputs/step40_parameter_sweep_driver/experimental_48_link_area_scale_0075/wall_velocity_application_timeseries.csv",
    "outputs/step40_parameter_sensitivity_summary/parameter_sensitivity_summary.csv",
    "outputs/step40_parameter_sensitivity_summary/parameter_sensitivity_summary.json",
    "outputs/step40_static_vs_parameter_comparison/static_vs_parameter_comparison.csv",
    "outputs/step40_static_vs_parameter_comparison/static_vs_parameter_comparison.json",
    "outputs/step40_engineering_vs_link_area_parameter_comparison/engineering_vs_link_area_parameter.csv",
    "outputs/step40_engineering_vs_link_area_parameter_comparison/engineering_vs_link_area_parameter.json",
    "outputs/step40_cap_saturation_diagnostics/cap_saturation_diagnostics.csv",
    "outputs/step40_cap_saturation_diagnostics/cap_saturation_diagnostics.json",
    "outputs/step40_force_impulse_parameter_response/force_impulse_parameter_response.csv",
    "outputs/step40_force_impulse_parameter_response/force_impulse_parameter_response.json",
    "outputs/step40_tethered_no_free_body_guard/tethered_no_free_body_guard.csv",
    "outputs/step40_tethered_no_free_body_guard/tethered_no_free_body_guard.json",
    "outputs/step40_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step40_quality_report_aggregation/quality_report_summary.json",
    "outputs/step40_step39_regression_guard/step39_regression_guard.csv",
    "outputs/step40_step39_regression_guard/step39_regression_guard.json",
    "outputs/step40_artifact_manifest/artifact_manifest.csv",
    "outputs/step40_artifact_manifest/artifact_summary.csv",
    "outputs/step40_artifact_manifest/artifact_summary.json",
]

STEP40_LOG_MARKERS = {
    "logs/step40_parameter_config_validation.log": "[OK] Step 40 parameter config validation finished",
    "logs/step40_parameter_sweep_driver.log": "[OK] Step 40 parameter sweep driver finished",
    "logs/step40_parameter_sensitivity_summary.log": "[OK] Step 40 parameter sensitivity summary finished",
    "logs/step40_static_vs_parameter_comparison.log": "[OK] Step 40 static vs parameter comparison finished",
    "logs/step40_engineering_vs_link_area_parameter_comparison.log": "[OK] Step 40 engineering vs link-area parameter comparison finished",
    "logs/step40_cap_saturation_diagnostics.log": "[OK] Step 40 cap saturation diagnostics finished",
    "logs/step40_force_impulse_parameter_response.log": "[OK] Step 40 force impulse parameter response finished",
    "logs/step40_tethered_no_free_body_guard.log": "[OK] Step 40 tethered no-free-body guard finished",
    "logs/step40_quality_report_aggregation.log": "[OK] Step 40 quality report aggregation finished",
    "logs/step40_step39_regression_guard.log": "[OK] Step 40 Step 39 regression guard finished",
    "logs/step40_artifact_manifest.log": "[OK] Step 40 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 40 is controlled jet-cycle proxy parameter sensitivity smoke.",
    "Step 40 varies wall velocity scale only.",
    "Step 40 remains tethered and proxy-only.",
    "Step 40 does not validate a real jet.",
    "Step 40 does not validate jet propulsion.",
    "Step 40 does not implement free-body motion.",
    "Step 40 does not implement squid swimming.",
    "Step 40 does not implement real squid validation.",
    "Step 40 does not change moving bounce-back formulas.",
    "The default boundary_motion_mode remains static.",
    "The default wall_velocity_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "real jet validation",
    "jet propulsion is validated",
    "squid swimming is implemented",
    "free-body motion is implemented",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
    "final solver readiness",
    "two-phase flow is implemented",
    "contact angle physics is implemented",
    "moving bounce-back formula is changed",
    "default wall velocity application is enabled",
    "wall velocity scale physically validates propulsion",
]

APPLICATION_CONFIGS = [
    "configs/step40_wall_velocity_application_scale_0025.json",
    "configs/step40_wall_velocity_application_scale_0050.json",
    "configs/step40_wall_velocity_application_scale_0075.json",
]

DRIVER_CONFIGS = [
    "configs/step40_static_48_moving_boundary.json",
    "configs/step40_static_48_link_area.json",
    "configs/step40_experimental_48_moving_boundary_scale_0025.json",
    "configs/step40_experimental_48_moving_boundary_scale_0050.json",
    "configs/step40_experimental_48_moving_boundary_scale_0075.json",
    "configs/step40_experimental_48_link_area_scale_0025.json",
    "configs/step40_experimental_48_link_area_scale_0050.json",
    "configs/step40_experimental_48_link_area_scale_0075.json",
]


def test_step40_required_artifacts_exist():
    missing = [path for path in STEP40_REQUIRED_FILES + STEP40_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP40_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step40_parameter_configs_are_valid():
    application_configs = [read_json(path) for path in APPLICATION_CONFIGS]
    driver_configs = [read_json(path) for path in DRIVER_CONFIGS]
    assert len(application_configs) == 3
    assert sorted(float(config["wall_velocity_scale"]) for config in application_configs) == [0.025, 0.05, 0.075]
    assert all(float(config["wall_velocity_cap_lbm"]) == 0.01 for config in application_configs)
    assert all(config["application_mode"] == "solid_vel_experimental" for config in application_configs)
    assert all(config["target_lbm_field"] == "solid_vel" for config in application_configs)
    assert all(config["application_policy"] == "additive_capped" for config in application_configs)
    assert all(config["apply_to_lbm_solid_vel"] is True for config in application_configs)
    assert all(config["apply_to_lbm_populations"] is False for config in application_configs)
    assert all(config["modify_bounceback_formula"] is False for config in application_configs)
    assert all(config["jet_model_enabled"] is False for config in application_configs)
    assert all(config["actuation_claim_enabled"] is False for config in application_configs)

    assert len(driver_configs) == 8
    assert all(config["coupling_mode"] == "moving_boundary" for config in driver_configs)
    assert all(config["geometry_type"] == "squid_proxy" for config in driver_configs)
    assert all(config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json" for config in driver_configs)
    assert all(int(config["n_grid"]) == 48 for config in driver_configs)
    assert all(int(config["n_particles"]) == 4096 for config in driver_configs)
    assert all(int(config["n_lbm_steps"]) == 40 for config in driver_configs)
    assert all(int(config["mpm_substeps_per_lbm_step"]) == 5 for config in driver_configs)
    assert all(tuple(config["target_u_lbm"]) == (0.0, 0.0, 0.0) for config in driver_configs)
    assert all(int(config["output_interval"]) == 1 for config in driver_configs)
    assert all(config["quality_check_enabled"] is True and config["quality_check_strict"] is True for config in driver_configs)
    assert all(config["write_vtk"] is False and config["write_particles"] is False for config in driver_configs)
    static = [config for config in driver_configs if config["wall_velocity_application_mode"] == "disabled"]
    experimental = [config for config in driver_configs if config["wall_velocity_application_mode"] == "solid_vel_experimental"]
    assert len(static) == 2
    assert len(experimental) == 6
    assert all(config["boundary_motion_mode"] == "static" for config in static)
    assert all(config.get("wall_velocity_application_config_path") is None for config in static)
    assert all(config["boundary_motion_mode"] == "prescribed_kinematic" for config in experimental)
    assert all(config["boundary_motion_config_path"] == "configs/step34_boundary_motion_interface_prescribed_kinematic.json" for config in experimental)
    assert sorted(config["wall_velocity_application_config_path"] for config in experimental) == sorted(APPLICATION_CONFIGS * 2)


def test_step40_parameter_sweep_driver_is_valid():
    payload = read_json("outputs/step40_parameter_sweep_driver/parameter_sweep_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 8
    assert int(summary["stable_count"]) == 8
    assert int(summary["quality_pass_count"]) == 8
    assert int(summary["static_row_count"]) == 2
    assert int(summary["experimental_row_count"]) == 6
    assert int(summary["scale_count"]) == 3
    assert int(summary["transfer_mode_count"]) == 2
    assert int(summary["min_completed_lbm_steps"]) >= 40
    assert int(summary["min_total_mpm_substeps"]) >= 200
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert float(summary["min_mpm_min_J_global"]) > 0.0
    assert float(summary["min_projected_mass_min"]) > 0.0
    assert int(summary["min_active_cell_count"]) > 0
    assert int(summary["min_bb_link_count_max"]) > 0
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["stable"] is True for row in rows)
    experimental = [row for row in rows if row["mode_class"] == "experimental"]
    assert len(experimental) == 6
    assert all(int(row["application_report_count"]) >= 40 for row in experimental)
    assert all(int(row["applied_cell_count_min"]) > 0 for row in experimental)
    assert all(float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12 for row in experimental)
    assert all(int(row["lbm_population_update_count_max"]) == 0 for row in experimental)
    assert all(row["modify_bounceback_formula_any"] is False for row in experimental)


def test_step40_parameter_sensitivity_summary_is_valid():
    payload = read_json("outputs/step40_parameter_sensitivity_summary/parameter_sensitivity_summary.json")
    summary = payload["summary"]
    assert int(summary["experimental_row_count"]) == 6
    assert int(summary["scale_count"]) == 3
    assert int(summary["engineering_row_count"]) == 3
    assert int(summary["link_area_row_count"]) == 3
    assert summary["all_experimental_rows_stable"] is True
    assert float(summary["max_applied_velocity_norm"]) <= float(summary["cap_value"]) + 1.0e-12
    assert summary["applied_velocity_response_pass"] is True
    assert summary["parameter_sensitivity_pass"] is True
    assert all(row["response_pass"] is True for row in payload["rows"])


def test_step40_static_vs_parameter_comparison_is_valid():
    payload = read_json("outputs/step40_static_vs_parameter_comparison/static_vs_parameter_comparison.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 6
    assert int(summary["comparison_pass_count"]) == 6
    assert summary["comparison_pass"] is True
    for row in payload["rows"]:
        assert row["both_stable"] is True
        assert row["comparison_pass"] is True
        assert math.isfinite(float(row["projected_mass_delta"]))
        assert abs(float(row["projected_mass_delta"])) <= 1.0e-3
        assert float(row["experimental_applied_velocity_max"]) > 0.0


def test_step40_engineering_vs_link_area_parameter_comparison_is_valid():
    payload = read_json("outputs/step40_engineering_vs_link_area_parameter_comparison/engineering_vs_link_area_parameter.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 3
    assert int(summary["comparison_pass_count"]) == 3
    assert summary["comparison_pass"] is True
    assert sorted(float(row["wall_velocity_scale"]) for row in payload["rows"]) == [0.025, 0.05, 0.075]
    for row in payload["rows"]:
        assert row["both_stable"] is True
        assert row["comparison_pass"] is True
        assert 0.25 <= float(row["link_area_scale_final"]) <= 2.0
        assert math.isfinite(float(row["projected_mass_delta"]))


def test_step40_cap_saturation_diagnostics_is_valid():
    payload = read_json("outputs/step40_cap_saturation_diagnostics/cap_saturation_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 6
    assert float(summary["cap_value"]) == 0.01
    assert summary["cap_pass"] is True
    assert summary["cap_saturation_diagnostics_pass"] is True
    assert int(summary["cap_hit_count"]) >= 0
    for row in payload["rows"]:
        assert row["cap_pass"] is True
        assert float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12


def test_step40_force_impulse_parameter_response_is_valid():
    payload = read_json("outputs/step40_force_impulse_parameter_response/force_impulse_parameter_response.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 8
    assert int(summary["response_finite_pass_count"]) == 8
    assert summary["force_impulse_parameter_response_pass"] is True
    for row in payload["rows"]:
        assert row["response_finite_pass"] is True
        assert math.isfinite(float(row["hydro_force_max_norm"]))
        assert math.isfinite(float(row["bb_correction_integral_proxy"]))
        assert float(row["bb_link_count_integral_proxy"]) > 0.0
        assert math.isfinite(float(row["impulse_proxy"]))
        assert "proxy" in row["notes"]


def test_step40_tethered_no_free_body_guard_is_valid():
    payload = read_json("outputs/step40_tethered_no_free_body_guard/tethered_no_free_body_guard.json")
    summary = payload["summary"]
    assert summary["guard_pass"] is True
    assert int(summary["free_body_state_file_count"]) == 0
    assert int(summary["body_trajectory_output_count"]) == 0
    assert summary["rigid_body_integrator_enabled"] is False
    assert summary["body_position_state_enabled"] is False
    assert summary["swimming_displacement_claim_enabled"] is False
    assert summary["target_u_lbm_zero_for_cycle_configs"] is True


def test_step40_quality_report_aggregation_is_valid():
    summary = read_json("outputs/step40_quality_report_aggregation/quality_report_summary.json")["summary"]
    assert int(summary["quality_report_count"]) == 8
    assert int(summary["pass_count"]) == 8
    assert int(summary["strict_count"]) == 8
    assert int(summary["warning_count"]) == 0
    assert int(summary["error_count"]) == 0


def test_step40_step39_regression_guard_is_valid():
    payload = read_json("outputs/step40_step39_regression_guard/step39_regression_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) >= 9
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert summary["regression_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step40_default_modes_remain_unchanged():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "wall_velocity_application_config_path: Optional[str] = None" in text
    assert "wall_velocity_application_report_enabled: bool = False" in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step40_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/40_controlled_jet_cycle_proxy_parameter_sensitivity_smoke.md",
            "STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step40_artifact_budget_is_valid():
    summary = read_json("outputs/step40_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step40_total_size_mb"]) < 25.0
    assert float(summary["total_size_mb"]) < 280.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step40_vtr_count"]) == 0
    assert int(summary["step40_particle_npy_count"]) == 0


def test_step40_report_acceptance_complete():
    report = read_text("STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_REPORT.md")
    assert "## 17. Acceptance Checklist" in report
    assert "## 18. Decision For Step 41" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step40_no_physical_validation_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/40_controlled_jet_cycle_proxy_parameter_sensitivity_smoke.md",
            "STEP40_CONTROLLED_JET_CYCLE_PROXY_PARAMETER_SENSITIVITY_SMOKE_REPORT.md",
        ]
    )
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    full_path = ROOT / path
    if not full_path.is_file():
        return ""
    return full_path.read_text(encoding="utf-8")
