import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP44_REQUIRED_FILES = [
    "STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_GOAL.md",
    "STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_REPORT.md",
    "docs/44_controlled_squid_proxy_diagnostic_geometry_update_smoke.md",
    "configs/step44_diagnostic_geometry_update.json",
    "configs/step44_original_32_static_1step.json",
    "configs/step44_displaced_copy_32_phase035_1step.json",
    "src/diagnostic_geometry_update_config.py",
    "src/diagnostic_geometry_update.py",
    "src/diagnostic_geometry_projection.py",
    "src/diagnostic_geometry_state_guard.py",
    "baseline_tests/step44_common.py",
    "baseline_tests/run_step44_diagnostic_update_config_validation.py",
    "baseline_tests/run_step44_runtime_displaced_copy.py",
    "baseline_tests/run_step44_runtime_copy_quality.py",
    "baseline_tests/run_step44_projection_only_smoke.py",
    "baseline_tests/run_step44_original_vs_displaced_comparison.py",
    "baseline_tests/run_step44_cycle_phase_closure.py",
    "baseline_tests/run_step44_state_mutation_guard.py",
    "baseline_tests/run_step44_optional_1step_driver_smoke.py",
    "baseline_tests/run_step44_step43_regression_guard.py",
    "baseline_tests/run_step44_artifact_manifest.py",
    "tests/test_step44_diagnostic_geometry_update_smoke_contract.py",
]

STEP44_OUTPUT_FILES = [
    "outputs/step44_diagnostic_update_config_validation/diagnostic_update_config_validation.csv",
    "outputs/step44_diagnostic_update_config_validation/diagnostic_update_config_validation.json",
    "outputs/step44_runtime_displaced_copy/runtime_displaced_copy.csv",
    "outputs/step44_runtime_displaced_copy/runtime_displaced_copy.json",
    "outputs/step44_runtime_copy_quality/runtime_copy_quality.csv",
    "outputs/step44_runtime_copy_quality/runtime_copy_quality.json",
    "outputs/step44_projection_only_smoke/projection_only_smoke.csv",
    "outputs/step44_projection_only_smoke/projection_only_smoke.json",
    "outputs/step44_original_vs_displaced_comparison/original_vs_displaced.csv",
    "outputs/step44_original_vs_displaced_comparison/original_vs_displaced.json",
    "outputs/step44_cycle_phase_closure/cycle_phase_closure.csv",
    "outputs/step44_cycle_phase_closure/cycle_phase_closure.json",
    "outputs/step44_state_mutation_guard/state_mutation_guard.csv",
    "outputs/step44_state_mutation_guard/state_mutation_guard.json",
    "outputs/step44_optional_1step_driver_smoke/one_step_driver_smoke.csv",
    "outputs/step44_optional_1step_driver_smoke/one_step_driver_smoke.json",
    "outputs/step44_step43_regression_guard/step43_regression_guard.csv",
    "outputs/step44_step43_regression_guard/step43_regression_guard.json",
    "outputs/step44_artifact_manifest/artifact_manifest.csv",
    "outputs/step44_artifact_manifest/artifact_summary.csv",
    "outputs/step44_artifact_manifest/artifact_summary.json",
]

STEP44_LOG_MARKERS = {
    "logs/step44_diagnostic_update_config_validation.log": "[OK] Step 44 diagnostic update config validation finished",
    "logs/step44_runtime_displaced_copy.log": "[OK] Step 44 runtime displaced copy finished",
    "logs/step44_runtime_copy_quality.log": "[OK] Step 44 runtime copy quality finished",
    "logs/step44_projection_only_smoke.log": "[OK] Step 44 projection-only smoke finished",
    "logs/step44_original_vs_displaced_comparison.log": "[OK] Step 44 original-vs-displaced comparison finished",
    "logs/step44_cycle_phase_closure.log": "[OK] Step 44 cycle phase closure finished",
    "logs/step44_state_mutation_guard.log": "[OK] Step 44 state mutation guard finished",
    "logs/step44_optional_1step_driver_smoke.log": "[OK] Step 44 optional one-step driver smoke finished",
    "logs/step44_step43_regression_guard.log": "[OK] Step 44 Step 43 regression guard finished",
    "logs/step44_artifact_manifest.log": "[OK] Step 44 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 44 is controlled squid proxy diagnostic geometry update smoke.",
    "Step 44 uses a runtime diagnostic geometry copy only.",
    "Step 44 does not persist displaced geometry.",
    "Step 44 does not write displaced particles.",
    "Step 44 does not update driver geometry state.",
    "Step 44 does not update LBM solid_phi.",
    "Step 44 does not update dynamic_solid.",
    "Step 44 does not change moving bounce-back formulas.",
    "The default geometry_motion_mode remains static.",
    "The default geometry_motion_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "full coupled geometry motion is implemented",
    "driver geometry is persistently updated",
    "MPM particles are persistently displaced",
    "LBM solid_phi is updated by runtime geometry",
    "dynamic_solid is updated by runtime geometry",
    "production boundary links are recomputed",
    "moving bounce-back formula is changed",
    "squid swimming is implemented",
    "free-body motion is implemented",
    "real jet validation",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
]

TRACKED_REGIONS = ["mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"]
SELECTED_PHASES = [0.0, 0.2, 0.35, 0.5, 1.0]


def test_step44_required_artifacts_exist():
    missing = [path for path in STEP44_REQUIRED_FILES + STEP44_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP44_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step44_diagnostic_update_config_is_valid():
    config = read_json("configs/step44_diagnostic_geometry_update.json")
    assert config["geometry_update_id"] == "step44_diagnostic_geometry_update_smoke"
    assert config["geometry_motion_interface_config_path"] == "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json"
    assert config["displacement_config_path"] == "configs/step42_squid_proxy_geometry_displacement.json"
    assert config["displacement_artifact_path"] == "outputs/step42_geometry_displacement/geometry_displacement.json"
    assert config["selected_phases"] == SELECTED_PHASES
    assert config["grid_sizes"] == [32, 48]
    assert config["tracked_regions"] == TRACKED_REGIONS
    assert config["update_mode"] == "runtime_copy_diagnostic"
    assert _all_step44_flags_false(config)
    assert config["diagnostic_only"] is True
    assert config["deterministic"] is True

    summary = read_json("outputs/step44_diagnostic_update_config_validation/diagnostic_update_config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["selected_phase_count"]) == 5
    assert summary["selected_phases"] == SELECTED_PHASES
    assert summary["grid_sizes"] == [32, 48]
    assert summary["tracked_regions"] == TRACKED_REGIONS
    assert summary["all_mutation_flags_false"] is True


def test_step44_runtime_displaced_copy_is_valid():
    payload = read_json("outputs/step44_runtime_displaced_copy/runtime_displaced_copy.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 15
    assert int(summary["phase_count"]) == 5
    assert int(summary["tracked_region_count"]) == 3
    assert summary["runtime_copy_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_output_pass"] is True
    assert summary["selected_phases"] == SELECTED_PHASES
    assert summary["tracked_regions"] == TRACKED_REGIONS
    assert len(rows) == 15
    for row in rows:
        assert int(row["point_count"]) > 0
        assert math.isfinite(float(row["displacement_norm_max"]))
        assert float(row["displacement_norm_max"]) <= 0.25 + 1.0e-12
        assert row["original_hash"]
        assert row["displaced_summary_hash"]
        assert row["bounds_pass"] is True
        assert row["finite_pass"] is True
        assert row["coverage_pass"] is True
        assert row["persist_displaced_geometry"] is False
        assert row["write_displaced_particles"] is False
        assert row["mutate_original_geometry"] is False


def test_step44_runtime_copy_quality_is_valid():
    summary = read_json("outputs/step44_runtime_copy_quality/runtime_copy_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["bounds_pass"] is True
    assert summary["coverage_pass"] is True
    assert summary["finite_pass"] is True
    assert summary["closure_support_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_output_pass"] is True
    assert int(summary["row_count"]) == 15


def test_step44_projection_only_smoke_is_valid():
    payload = read_json("outputs/step44_projection_only_smoke/projection_only_smoke.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 10
    assert int(summary["grid_size_count"]) == 2
    assert int(summary["phase_count"]) == 5
    assert int(summary["projection_pass_count"]) == 10
    assert summary["projection_smoke_pass"] is True
    for row in payload["rows"]:
        assert row["projection_pass"] is True
        assert float(row["projected_mass"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert 0.0 <= float(row["solid_phi_min"]) <= float(row["solid_phi_max"]) <= 1.0
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert row["diagnostic_only"] is True


def test_step44_original_vs_displaced_comparison_is_valid():
    payload = read_json("outputs/step44_original_vs_displaced_comparison/original_vs_displaced.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 15
    assert summary["comparison_pass"] is True
    assert summary["original_hash_stable"] is True
    assert summary["displacement_nonzero_for_midcycle_phases"] is True
    assert summary["phase0_displacement_close_to_rest"] is True
    assert summary["phase1_displacement_close_to_rest"] is True
    for row in payload["rows"]:
        assert row["comparison_pass"] is True
        assert math.isfinite(float(row["bbox_delta_norm"]))


def test_step44_cycle_phase_closure_is_valid():
    payload = read_json("outputs/step44_cycle_phase_closure/cycle_phase_closure.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 3
    assert summary["closure_pass"] is True
    assert summary["tracked_regions"] == TRACKED_REGIONS
    for row in payload["rows"]:
        assert row["closure_pass"] is True
        assert float(row["phase0_phase1_displacement_delta"]) <= 1.0e-12


def test_step44_state_mutation_guard_is_valid():
    summary = read_json("outputs/step44_state_mutation_guard/state_mutation_guard.json")["summary"]
    assert summary["guard_pass"] is True
    assert summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
    assert summary["region_mask_hash_before"] == summary["region_mask_hash_after"]
    assert int(summary["driver_state_mutation_count"]) == 0
    assert int(summary["lbm_state_mutation_count"]) == 0
    assert int(summary["mpm_state_mutation_count"]) == 0
    assert int(summary["projection_state_mutation_count"]) == 0
    assert int(summary["dynamic_solid_mutation_count"]) == 0
    assert int(summary["displaced_particle_output_count"]) == 0
    assert int(summary["dense_displacement_output_count"]) == 0
    assert int(summary["vtr_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step44_optional_1step_driver_smoke_is_valid():
    payload = read_json("outputs/step44_optional_1step_driver_smoke/one_step_driver_smoke.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert int(summary["stable_count"]) == 2
    assert summary["smoke_pass"] is True
    assert summary["full_coupled_geometry_claim"] is False
    assert summary["diagnostic_copy_only_reason"]
    for row in payload["rows"]:
        assert row["stable"] is True
        assert int(row["completed_lbm_steps"]) >= 1
        assert int(row["total_mpm_substeps"]) >= 1
        assert float(row["rho_min"]) > 0.95
        assert float(row["rho_max"]) < 1.05
        assert float(row["lbm_max_v"]) < 0.1
        assert float(row["projected_mass"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert row["quality_pass"] is True
        assert row["mutate_original_geometry"] is False


def test_step44_step43_regression_guard_is_valid():
    payload = read_json("outputs/step44_step43_regression_guard/step43_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 6
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step44_default_modes_remain_unchanged():
    text = read_text("src/fsi_config.py")
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step44_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/44_controlled_squid_proxy_diagnostic_geometry_update_smoke.md",
            "STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step44_artifact_budget_is_valid():
    summary = read_json("outputs/step44_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step44_total_size_mb"]) < 10.0
    assert float(summary["total_size_mb"]) < 330.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step44_vtr_count"]) == 0
    assert int(summary["step44_particle_npy_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step44_report_acceptance_complete():
    report = read_text("STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_REPORT.md")
    assert "## 16. Acceptance Checklist" in report
    assert "## 17. Decision For Step 45" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step44_no_persistent_geometry_outputs():
    summary = read_json("outputs/step44_artifact_manifest/artifact_summary.json")
    assert int(summary["step44_vtr_count"]) == 0
    assert int(summary["step44_particle_npy_count"]) == 0
    assert int(summary["step44_displaced_particle_output_count"]) == 0
    assert int(summary["step44_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step44_no_coupled_geometry_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/44_controlled_squid_proxy_diagnostic_geometry_update_smoke.md",
            "STEP44_CONTROLLED_SQUID_PROXY_DIAGNOSTIC_GEOMETRY_UPDATE_SMOKE_REPORT.md",
            "outputs/step44_optional_1step_driver_smoke/one_step_driver_smoke.json",
        ]
    )
    required_disabled = [
        '"mutate_original_geometry": false',
        '"diagnostic_copy_only": true',
        '"full_coupled_geometry_claim": false',
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


def _all_step44_flags_false(config):
    return all(
        config[field] is False
        for field in (
            "persist_displaced_geometry",
            "write_displaced_particles",
            "write_dense_displacement_field",
            "write_vtk",
            "apply_to_driver_state",
            "apply_to_lbm_state",
            "apply_to_mpm_state",
            "apply_to_projection_state",
            "update_dynamic_solid",
            "recompute_production_boundary_links",
            "mutate_original_geometry",
        )
    )
