import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP38_REQUIRED_FILES = [
    "STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_GOAL.md",
    "STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_REPORT.md",
    "docs/38_controlled_tethered_jet_cycle_diagnostics_prototype.md",
    "configs/step38_cycle_static_48_moving_boundary.json",
    "configs/step38_cycle_experimental_48_moving_boundary.json",
    "configs/step38_cycle_static_48_link_area.json",
    "configs/step38_cycle_experimental_48_link_area.json",
    "src/jet_cycle_proxy_diagnostics.py",
    "src/tethered_cycle_diagnostics.py",
    "baseline_tests/step38_common.py",
    "baseline_tests/run_step38_cycle_driver.py",
    "baseline_tests/run_step38_cycle_proxy_diagnostics.py",
    "baseline_tests/run_step38_static_vs_experimental_cycle_comparison.py",
    "baseline_tests/run_step38_engineering_vs_link_area_cycle_comparison.py",
    "baseline_tests/run_step38_wall_velocity_cycle_quality.py",
    "baseline_tests/run_step38_force_impulse_proxy_summary.py",
    "baseline_tests/run_step38_tethered_no_free_body_guard.py",
    "baseline_tests/run_step38_quality_report_aggregation.py",
    "baseline_tests/run_step38_step37_regression_guard.py",
    "baseline_tests/run_step38_artifact_manifest.py",
    "tests/test_step38_tethered_jet_cycle_diagnostics_contract.py",
]

STEP38_OUTPUT_FILES = [
    "outputs/step38_cycle_driver/cycle_driver_results.csv",
    "outputs/step38_cycle_driver/cycle_driver_results.json",
    "outputs/step38_cycle_driver/cycle_driver_results.npz",
    "outputs/step38_cycle_driver/experimental_48_moving_boundary/wall_velocity_application_timeseries.csv",
    "outputs/step38_cycle_driver/experimental_48_moving_boundary/wall_velocity_application_timeseries.json",
    "outputs/step38_cycle_driver/experimental_48_link_area/wall_velocity_application_timeseries.csv",
    "outputs/step38_cycle_driver/experimental_48_link_area/wall_velocity_application_timeseries.json",
    "outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.csv",
    "outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.json",
    "outputs/step38_static_vs_experimental_cycle_comparison/static_vs_experimental_cycle.csv",
    "outputs/step38_static_vs_experimental_cycle_comparison/static_vs_experimental_cycle.json",
    "outputs/step38_engineering_vs_link_area_cycle_comparison/engineering_vs_link_area_cycle.csv",
    "outputs/step38_engineering_vs_link_area_cycle_comparison/engineering_vs_link_area_cycle.json",
    "outputs/step38_wall_velocity_cycle_quality/wall_velocity_cycle_quality.csv",
    "outputs/step38_wall_velocity_cycle_quality/wall_velocity_cycle_quality.json",
    "outputs/step38_force_impulse_proxy_summary/force_impulse_proxy_summary.csv",
    "outputs/step38_force_impulse_proxy_summary/force_impulse_proxy_summary.json",
    "outputs/step38_tethered_no_free_body_guard/tethered_no_free_body_guard.csv",
    "outputs/step38_tethered_no_free_body_guard/tethered_no_free_body_guard.json",
    "outputs/step38_quality_report_aggregation/quality_report_summary.csv",
    "outputs/step38_quality_report_aggregation/quality_report_summary.json",
    "outputs/step38_step37_regression_guard/step37_regression_guard.csv",
    "outputs/step38_step37_regression_guard/step37_regression_guard.json",
    "outputs/step38_artifact_manifest/artifact_manifest.csv",
    "outputs/step38_artifact_manifest/artifact_summary.csv",
    "outputs/step38_artifact_manifest/artifact_summary.json",
]

STEP38_LOG_MARKERS = {
    "logs/step38_cycle_driver.log": "[OK] Step 38 cycle driver finished",
    "logs/step38_cycle_proxy_diagnostics.log": "[OK] Step 38 cycle proxy diagnostics finished",
    "logs/step38_static_vs_experimental_cycle_comparison.log": "[OK] Step 38 static vs experimental cycle comparison finished",
    "logs/step38_engineering_vs_link_area_cycle_comparison.log": "[OK] Step 38 engineering vs link-area cycle comparison finished",
    "logs/step38_wall_velocity_cycle_quality.log": "[OK] Step 38 wall velocity cycle quality finished",
    "logs/step38_force_impulse_proxy_summary.log": "[OK] Step 38 force impulse proxy summary finished",
    "logs/step38_tethered_no_free_body_guard.log": "[OK] Step 38 tethered no-free-body guard finished",
    "logs/step38_quality_report_aggregation.log": "[OK] Step 38 quality report aggregation finished",
    "logs/step38_step37_regression_guard.log": "[OK] Step 38 Step 37 regression guard finished",
    "logs/step38_artifact_manifest.log": "[OK] Step 38 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 38 is controlled tethered jet-cycle diagnostics prototype.",
    "Step 38 uses proxy cavity-volume and funnel-aperture diagnostics only.",
    "Step 38 does not validate a real jet.",
    "Step 38 does not implement free-body motion.",
    "Step 38 does not implement squid swimming.",
    "Step 38 does not implement real squid validation.",
    "Step 38 does not change moving bounce-back formulas.",
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
]


def test_step38_required_artifacts_exist():
    missing = [path for path in STEP38_REQUIRED_FILES + STEP38_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP38_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step38_driver_configs_are_valid():
    configs = [
        read_json("configs/step38_cycle_static_48_moving_boundary.json"),
        read_json("configs/step38_cycle_experimental_48_moving_boundary.json"),
        read_json("configs/step38_cycle_static_48_link_area.json"),
        read_json("configs/step38_cycle_experimental_48_link_area.json"),
    ]
    assert len(configs) == 4
    assert all(config["coupling_mode"] == "moving_boundary" for config in configs)
    assert all(config["geometry_type"] == "squid_proxy" for config in configs)
    assert all(config["geometry_config_path"] == "configs/step30_squid_proxy_geometry.json" for config in configs)
    assert all(int(config["n_grid"]) == 48 for config in configs)
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
    assert all(config["boundary_motion_mode"] == "prescribed_kinematic" for config in experimental)
    assert all(config["boundary_motion_config_path"] == "configs/step34_boundary_motion_interface_prescribed_kinematic.json" for config in experimental)
    assert all(config["wall_velocity_application_config_path"] == "configs/step36_wall_velocity_application_solid_vel_experimental.json" for config in experimental)


def test_step38_cycle_driver_is_valid():
    payload = read_json("outputs/step38_cycle_driver/cycle_driver_results.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["quality_pass_count"]) == 4
    assert int(summary["static_row_count"]) == 2
    assert int(summary["experimental_row_count"]) == 2
    assert int(summary["min_completed_lbm_steps"]) >= 40
    assert int(summary["min_total_mpm_substeps"]) >= 200
    assert float(summary["min_rho_min_global"]) > 0.95
    assert float(summary["max_rho_max_global"]) < 1.05
    assert float(summary["max_lbm_max_v_global"]) < 0.1
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["stable"] is True for row in rows)
    assert all(int(row["completed_lbm_steps"]) >= 40 for row in rows)
    assert all(int(row["total_mpm_substeps"]) >= 200 for row in rows)
    experimental = [row for row in rows if row["mode_class"] == "experimental"]
    assert all(int(row["application_report_count"]) >= 40 for row in experimental)
    assert all(float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) for row in experimental)


def test_step38_cycle_proxy_diagnostics_are_valid():
    payload = read_json("outputs/step38_cycle_proxy_diagnostics/cycle_proxy_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["cycle_period_steps"]) == 40
    assert int(summary["schedule_row_count"]) == 81
    assert summary["phase_alignment_pass"] is True
    assert summary["cavity_volume_cycle_pass"] is True
    assert summary["funnel_aperture_cycle_pass"] is True
    assert float(summary["expelled_volume_proxy"]) > 0.0
    assert float(summary["refill_volume_proxy"]) > 0.0
    assert abs(float(summary["net_cycle_volume_proxy"])) <= max(1.0e-8, 1.0e-6 * float(summary["cavity_rest_volume"]))
    assert float(summary["funnel_aperture_max"]) > float(summary["funnel_aperture_min"])


def test_step38_static_vs_experimental_cycle_comparison_is_valid():
    payload = read_json("outputs/step38_static_vs_experimental_cycle_comparison/static_vs_experimental_cycle.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert summary["comparison_pass"] is True
    assert all(row["comparison_pass"] is True for row in payload["rows"])
    assert all(row["both_stable"] is True for row in payload["rows"])
    assert all(float(row["experimental_applied_velocity_max"]) > 0.0 for row in payload["rows"])
    assert all(math.isfinite(float(row["projected_mass_delta"])) for row in payload["rows"])


def test_step38_engineering_vs_link_area_cycle_comparison_is_valid():
    payload = read_json("outputs/step38_engineering_vs_link_area_cycle_comparison/engineering_vs_link_area_cycle.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 1
    assert int(summary["pass_count"]) == 1
    assert summary["comparison_pass"] is True
    row = payload["rows"][0]
    assert row["both_stable"] is True
    assert 0.25 <= float(row["link_area_scale_final"]) <= 2.0
    assert row["comparison_pass"] is True


def test_step38_wall_velocity_cycle_quality_is_valid():
    payload = read_json("outputs/step38_wall_velocity_cycle_quality/wall_velocity_cycle_quality.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["pass_count"]) == 2
    assert summary["quality_pass"] is True
    assert int(summary["min_timeseries_row_count"]) >= 40
    assert int(summary["min_applied_cell_count"]) > 0
    assert float(summary["max_applied_velocity_norm"]) <= 0.01
    assert int(summary["max_lbm_population_update_count"]) == 0
    assert all(row["phase_sequence_covers_full_cycle"] is True for row in payload["rows"])
    assert all(row["quality_pass"] is True for row in payload["rows"])


def test_step38_force_impulse_proxy_summary_is_valid():
    payload = read_json("outputs/step38_force_impulse_proxy_summary/force_impulse_proxy_summary.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert summary["impulse_proxy_summary_pass"] is True
    for row in payload["rows"]:
        assert row["impulse_proxy_finite_pass"] is True
        assert math.isfinite(float(row["hydro_force_max_norm_integral_proxy"]))
        assert math.isfinite(float(row["bb_correction_integral_proxy"]))
        assert float(row["bb_link_count_integral_proxy"]) > 0.0
        assert "proxy" in row["notes"]


def test_step38_tethered_no_free_body_guard_is_valid():
    payload = read_json("outputs/step38_tethered_no_free_body_guard/tethered_no_free_body_guard.json")
    summary = payload["summary"]
    assert summary["guard_pass"] is True
    assert int(summary["free_body_state_file_count"]) == 0
    assert summary["rigid_body_integrator_enabled"] is False
    assert summary["body_position_state_enabled"] is False
    assert summary["swimming_displacement_claim_enabled"] is False
    assert summary["target_u_lbm_zero_for_cycle_configs"] is True


def test_step38_quality_report_aggregation_is_valid():
    summary = read_json("outputs/step38_quality_report_aggregation/quality_report_summary.json")["summary"]
    assert int(summary["quality_report_count"]) == 4
    assert int(summary["pass_count"]) == 4
    assert int(summary["strict_count"]) == 4
    assert int(summary["warning_count"]) == 0
    assert int(summary["error_count"]) == 0


def test_step38_step37_regression_guard_is_valid():
    payload = read_json("outputs/step38_step37_regression_guard/step37_regression_guard.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) >= 8
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert summary["regression_pass"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def test_step38_default_modes_remain_unchanged():
    text = read_text("src/fsi_config.py")
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "wall_velocity_application_config_path: Optional[str] = None" in text
    assert "wall_velocity_application_report_enabled: bool = False" in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step38_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/38_controlled_tethered_jet_cycle_diagnostics_prototype.md",
            "STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step38_artifact_budget_is_valid():
    summary = read_json("outputs/step38_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step38_total_size_mb"]) < 25.0
    assert float(summary["total_size_mb"]) < 240.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step38_vtr_count"]) == 0
    assert int(summary["step38_particle_npy_count"]) == 0


def test_step38_report_acceptance_complete():
    report = read_text("STEP38_CONTROLLED_TETHERED_JET_CYCLE_DIAGNOSTICS_PROTOTYPE_REPORT.md")
    assert "## 16. Acceptance Checklist" in report
    assert "## 17. Decision For Step 39" in report
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


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
