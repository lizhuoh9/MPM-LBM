import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP41_REQUIRED_FILES = [
    "STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_GOAL.md",
    "STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_REPORT.md",
    "docs/41_controlled_jet_cycle_proxy_selected_parameter_64_feasibility.md",
    "configs/step41_wall_velocity_application_scale_0050_64.json",
    "configs/step41_64_static_moving_boundary.json",
    "configs/step41_64_experimental_moving_boundary_scale_0050.json",
    "configs/step41_64_static_link_area.json",
    "configs/step41_64_experimental_link_area_scale_0050.json",
    "src/selected_parameter_64_feasibility.py",
    "baseline_tests/step41_common.py",
    "baseline_tests/run_step41_selected_parameter_config_validation.py",
    "baseline_tests/run_step41_64_selected_parameter_driver.py",
    "baseline_tests/run_step41_64_feasibility_summary.py",
    "baseline_tests/run_step41_static_vs_experimental_64_comparison.py",
    "baseline_tests/run_step41_engineering_vs_link_area_64_comparison.py",
    "baseline_tests/run_step41_wall_velocity_64_quality.py",
    "baseline_tests/run_step41_cycle_proxy_64_diagnostics.py",
    "baseline_tests/run_step41_force_impulse_64_summary.py",
    "baseline_tests/run_step41_tethered_no_free_body_guard.py",
    "baseline_tests/run_step41_quality_report_aggregation.py",
    "baseline_tests/run_step41_step40_regression_guard.py",
    "baseline_tests/run_step41_artifact_manifest.py",
    "tests/test_step41_selected_parameter_64_feasibility_contract.py",
]

STEP41_OUTPUT_FILES = [
    "outputs/step41_selected_parameter_config_validation/selected_parameter_config_validation.csv",
    "outputs/step41_selected_parameter_config_validation/selected_parameter_config_validation.json",
    "outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.csv",
    "outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json",
    "outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.npz",
    "outputs/step41_64_selected_parameter_driver/step41_64_experimental_moving_boundary_scale_0050/wall_velocity_application_timeseries.csv",
    "outputs/step41_64_selected_parameter_driver/step41_64_experimental_link_area_scale_0050/wall_velocity_application_timeseries.csv",
    "outputs/step41_64_feasibility_summary/feasibility_summary.csv",
    "outputs/step41_64_feasibility_summary/feasibility_summary.json",
    "outputs/step41_static_vs_experimental_64_comparison/static_vs_experimental_64.csv",
    "outputs/step41_static_vs_experimental_64_comparison/static_vs_experimental_64.json",
    "outputs/step41_engineering_vs_link_area_64_comparison/engineering_vs_link_area_64.csv",
    "outputs/step41_engineering_vs_link_area_64_comparison/engineering_vs_link_area_64.json",
    "outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.csv",
    "outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json",
    "outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.csv",
    "outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.json",
    "outputs/step41_force_impulse_64_summary/force_impulse_64_summary.csv",
    "outputs/step41_force_impulse_64_summary/force_impulse_64_summary.json",
    "outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.csv",
    "outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json",
    "outputs/step41_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step41_quality_report_aggregation/quality_report_summary.json",
    "outputs/step41_step40_regression_guard/step40_regression_guard.csv",
    "outputs/step41_step40_regression_guard/step40_regression_guard.json",
    "outputs/step41_artifact_manifest/artifact_manifest.csv",
    "outputs/step41_artifact_manifest/artifact_summary.csv",
    "outputs/step41_artifact_manifest/artifact_summary.json",
]

STEP41_LOG_MARKERS = {
    "logs/step41_selected_parameter_config_validation.log": "[OK] Step 41 selected parameter config validation finished",
    "logs/step41_64_selected_parameter_driver.log": "[OK] Step 41 64 selected parameter driver finished",
    "logs/step41_64_feasibility_summary.log": "[OK] Step 41 64 feasibility summary finished",
    "logs/step41_static_vs_experimental_64_comparison.log": "[OK] Step 41 static vs experimental 64 comparison finished",
    "logs/step41_engineering_vs_link_area_64_comparison.log": "[OK] Step 41 engineering vs link-area 64 comparison finished",
    "logs/step41_wall_velocity_64_quality.log": "[OK] Step 41 wall velocity 64 quality finished",
    "logs/step41_cycle_proxy_64_diagnostics.log": "[OK] Step 41 cycle proxy 64 diagnostics finished",
    "logs/step41_force_impulse_64_summary.log": "[OK] Step 41 force impulse 64 summary finished",
    "logs/step41_tethered_no_free_body_guard.log": "[OK] Step 41 tethered no-free-body guard finished",
    "logs/step41_quality_report_aggregation.log": "[OK] Step 41 quality report aggregation finished",
    "logs/step41_step40_regression_guard.log": "[OK] Step 41 Step 40 regression guard finished",
    "logs/step41_artifact_manifest.log": "[OK] Step 41 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 41 is controlled jet-cycle proxy selected-parameter 64^3 feasibility.",
    "Step 41 selects one accepted wall velocity scale from Step 40.",
    "Step 41 remains tethered and proxy-only.",
    "Step 41 does not validate a real jet.",
    "Step 41 does not validate jet propulsion.",
    "Step 41 does not implement free-body motion.",
    "Step 41 does not implement squid swimming.",
    "Step 41 does not implement real squid validation.",
    "Step 41 does not change moving bounce-back formulas.",
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
    "64^3 validates propulsion",
]

APPLICATION_CONFIG = "configs/step41_wall_velocity_application_scale_0050_64.json"

DRIVER_CONFIGS = [
    "configs/step41_64_static_moving_boundary.json",
    "configs/step41_64_experimental_moving_boundary_scale_0050.json",
    "configs/step41_64_static_link_area.json",
    "configs/step41_64_experimental_link_area_scale_0050.json",
]


def test_step41_required_artifacts_exist():
    missing = [path for path in STEP41_REQUIRED_FILES + STEP41_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP41_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step41_selected_parameter_configs_are_valid():
    application_config = read_json(APPLICATION_CONFIG)
    assert float(application_config["wall_velocity_scale"]) == 0.05
    assert float(application_config["wall_velocity_cap_lbm"]) == 0.01
    assert application_config["application_mode"] == "solid_vel_experimental"
    assert application_config["target_lbm_field"] == "solid_vel"
    assert application_config["application_policy"] == "additive_capped"
    assert application_config["apply_to_lbm_solid_vel"] is True
    assert application_config["apply_to_lbm_populations"] is False
    assert application_config["apply_to_mpm"] is False
    assert application_config["apply_to_projector"] is False
    assert application_config["modify_bounceback_formula"] is False
    assert application_config["jet_model_enabled"] is False
    assert application_config["actuation_claim_enabled"] is False

    configs = [read_json(path) for path in DRIVER_CONFIGS]
    assert len(configs) == 4
    assert all(config["coupling_mode"] == "moving_boundary" for config in configs)
    assert all(config["geometry_type"] == "squid_proxy" for config in configs)
    assert all(config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json" for config in configs)
    assert all(int(config["n_grid"]) == 64 for config in configs)
    assert all(int(config["n_particles"]) == 4096 for config in configs)
    assert all(int(config["n_lbm_steps"]) == 40 for config in configs)
    assert all(int(config["mpm_substeps_per_lbm_step"]) == 5 for config in configs)
    assert all(tuple(config["target_u_lbm"]) == (0.0, 0.0, 0.0) for config in configs)
    assert all(int(config["output_interval"]) == 1 for config in configs)
    assert all(config["quality_check_enabled"] is True and config["quality_check_strict"] is True for config in configs)
    assert all(config["write_vtk"] is False and config["write_particles"] is False for config in configs)
    static = [config for config in configs if config["wall_velocity_application_mode"] == "disabled"]
    experimental = [config for config in configs if config["wall_velocity_application_mode"] == "solid_vel_experimental"]
    assert len(static) == 2
    assert len(experimental) == 2
    assert all(config["boundary_motion_mode"] == "static" for config in static)
    assert all(config.get("wall_velocity_application_config_path") is None for config in static)
    assert all(config["boundary_motion_mode"] == "prescribed_kinematic" for config in experimental)
    assert all(config["boundary_motion_config_path"] == "configs/step34_boundary_motion_interface_prescribed_kinematic.json" for config in experimental)
    assert all(config["wall_velocity_application_config_path"] == APPLICATION_CONFIG for config in experimental)


def test_step41_64_selected_parameter_driver_is_valid():
    payload = read_json("outputs/step41_64_selected_parameter_driver/selected_parameter_64_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["quality_pass_count"]) == 4
    assert int(summary["static_row_count"]) == 2
    assert int(summary["experimental_row_count"]) == 2
    assert int(summary["engineering_row_count"]) == 2
    assert int(summary["link_area_row_count"]) == 2
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
    assert len(experimental) == 2
    assert all(float(row["wall_velocity_scale"]) == 0.05 for row in experimental)
    assert all(int(row["application_report_count"]) >= 40 for row in experimental)
    assert all(int(row["applied_cell_count_min"]) > 0 for row in experimental)
    assert all(float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12 for row in experimental)
    assert all(int(row["lbm_population_update_count_max"]) == 0 for row in experimental)
    assert all(row["modify_bounceback_formula_any"] is False for row in experimental)


def test_step41_64_feasibility_summary_is_valid():
    summary = read_json("outputs/step41_64_feasibility_summary/feasibility_summary.json")["summary"]
    assert int(summary["driver_row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert float(summary["selected_scale"]) == 0.05
    assert int(summary["n_grid"]) == 64
    assert summary["one_cycle_pass"] is True
    assert summary["feasibility_pass"] is True
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert float(summary["min_mpm_min_J_global"]) > 0.0
    assert float(summary["min_projected_mass_min"]) > 0.0
    assert int(summary["min_active_cell_count"]) > 0
    assert float(summary["max_applied_velocity_norm"]) <= 0.01 + 1.0e-12


def test_step41_static_vs_experimental_64_comparison_is_valid():
    payload = read_json("outputs/step41_static_vs_experimental_64_comparison/static_vs_experimental_64.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["comparison_pass_count"]) == 2
    assert summary["comparison_pass"] is True
    for row in payload["rows"]:
        assert row["both_stable"] is True
        assert row["comparison_pass"] is True
        assert math.isfinite(float(row["projected_mass_delta"]))
        assert abs(float(row["projected_mass_delta"])) <= 2.0e-3
        assert float(row["experimental_applied_velocity_max"]) > 0.0


def test_step41_engineering_vs_link_area_64_comparison_is_valid():
    payload = read_json("outputs/step41_engineering_vs_link_area_64_comparison/engineering_vs_link_area_64.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 1
    assert int(summary["comparison_pass_count"]) == 1
    assert summary["comparison_pass"] is True
    row = payload["rows"][0]
    assert row["both_stable"] is True
    assert row["comparison_pass"] is True
    assert float(row["wall_velocity_scale"]) == 0.05
    assert 0.25 <= float(row["link_area_scale_final"]) <= 2.0
    assert math.isfinite(float(row["projected_mass_delta"]))
    assert math.isfinite(float(row["max_applied_velocity_norm_delta"]))


def test_step41_wall_velocity_64_quality_is_valid():
    payload = read_json("outputs/step41_wall_velocity_64_quality/wall_velocity_64_quality.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert summary["quality_pass"] is True
    assert float(summary["selected_scale"]) == 0.05
    assert float(summary["cap_value"]) == 0.01
    assert int(summary["min_timeseries_row_count"]) >= 40
    assert int(summary["min_applied_cell_count"]) > 0
    assert float(summary["max_applied_velocity_norm"]) <= 0.01 + 1.0e-12
    assert int(summary["max_lbm_population_update_count"]) == 0
    for row in payload["rows"]:
        assert row["quality_pass"] is True
        assert row["repeatable_phase_sequence"] is True


def test_step41_cycle_proxy_64_diagnostics_is_valid():
    payload = read_json("outputs/step41_cycle_proxy_64_diagnostics/cycle_proxy_64_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["cycle_period_steps"]) == 40
    assert int(summary["cycle_count"]) == 1
    assert summary["cycle_proxy_64_pass"] is True
    assert summary["phase_alignment_pass"] is True
    assert summary["cavity_volume_cycle_pass"] is True
    assert summary["funnel_aperture_cycle_pass"] is True
    assert float(summary["expelled_volume_proxy"]) > 0.0
    assert float(summary["refill_volume_proxy"]) > 0.0
    assert abs(float(summary["net_cycle_volume_proxy"])) <= float(summary["net_cycle_tolerance"])


def test_step41_force_impulse_64_summary_is_valid():
    payload = read_json("outputs/step41_force_impulse_64_summary/force_impulse_64_summary.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 4
    assert int(summary["response_finite_pass_count"]) == 4
    assert summary["force_impulse_64_pass"] is True
    for row in payload["rows"]:
        assert row["response_finite_pass"] is True
        assert math.isfinite(float(row["hydro_force_max_norm"]))
        assert math.isfinite(float(row["bb_correction_integral_proxy"]))
        assert float(row["bb_link_count_integral_proxy"]) > 0.0
        assert math.isfinite(float(row["impulse_proxy"]))
        assert "proxy" in row["notes"]


def test_step41_tethered_no_free_body_guard_is_valid():
    payload = read_json("outputs/step41_tethered_no_free_body_guard/tethered_no_free_body_guard.json")
    summary = payload["summary"]
    assert summary["guard_pass"] is True
    assert int(summary["config_count"]) == 4
    assert int(summary["free_body_state_file_count"]) == 0
    assert int(summary["body_trajectory_output_count"]) == 0
    assert summary["rigid_body_integrator_enabled"] is False
    assert summary["body_position_state_enabled"] is False
    assert summary["swimming_displacement_claim_enabled"] is False
    assert summary["target_u_lbm_zero_for_cycle_configs"] is True


def test_step41_quality_report_aggregation_is_valid():
    summary = read_json("outputs/step41_quality_report_aggregation/quality_report_summary.json")["summary"]
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["warning_count"]) == 0
    assert int(summary["error_count"]) == 0


def test_step41_step40_regression_guard_is_valid():
    payload = read_json("outputs/step41_step40_regression_guard/step40_regression_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) >= 9
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert summary["regression_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step41_default_modes_remain_unchanged():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "wall_velocity_application_config_path: Optional[str] = None" in text
    assert "wall_velocity_application_report_enabled: bool = False" in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step41_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/41_controlled_jet_cycle_proxy_selected_parameter_64_feasibility.md",
            "STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step41_artifact_budget_is_valid():
    summary = read_json("outputs/step41_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step41_total_size_mb"]) < 20.0
    assert float(summary["total_size_mb"]) < 300.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step41_vtr_count"]) == 0
    assert int(summary["step41_particle_npy_count"]) == 0


def test_step41_report_acceptance_complete():
    report = read_text("STEP41_CONTROLLED_JET_CYCLE_PROXY_SELECTED_PARAMETER_64_FEASIBILITY_REPORT.md")
    assert "## 18. Acceptance Checklist" in report
    assert "## 19. Decision For Step 42" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    full_path = ROOT / path
    if not full_path.is_file():
        return ""
    return full_path.read_text(encoding="utf-8")
