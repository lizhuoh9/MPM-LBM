import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP45_REQUIRED_FILES = [
    "STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_GOAL.md",
    "STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_REPORT.md",
    "docs/45_controlled_runtime_geometry_projection_integration_smoke.md",
    "configs/step45_runtime_geometry_projection_integration.json",
    "configs/step45_original_32_static_1step.json",
    "configs/step45_displaced_phase035_32_moving_boundary_1step.json",
    "configs/step45_displaced_phase035_32_link_area_1step.json",
    "src/runtime_geometry_projection_config.py",
    "src/runtime_geometry_projection.py",
    "src/runtime_geometry_projection_quality.py",
    "src/runtime_geometry_projection_consistency.py",
    "src/runtime_geometry_projection_state_guard.py",
    "baseline_tests/step45_common.py",
    "baseline_tests/run_step45_projection_integration_config_validation.py",
    "baseline_tests/run_step45_runtime_projection_integration.py",
    "baseline_tests/run_step45_runtime_projection_quality.py",
    "baseline_tests/run_step45_original_vs_runtime_projection_comparison.py",
    "baseline_tests/run_step45_projection_phase_closure.py",
    "baseline_tests/run_step45_step44_projection_alignment.py",
    "baseline_tests/run_step45_runtime_projection_state_guard.py",
    "baseline_tests/run_step45_ultrashort_projection_driver_smoke.py",
    "baseline_tests/run_step45_step44_regression_guard.py",
    "baseline_tests/run_step45_artifact_manifest.py",
    "tests/test_step45_runtime_geometry_projection_integration_contract.py",
]

STEP45_OUTPUT_FILES = [
    "outputs/step45_projection_integration_config_validation/projection_integration_config_validation.csv",
    "outputs/step45_projection_integration_config_validation/projection_integration_config_validation.json",
    "outputs/step45_runtime_projection_integration/runtime_projection_integration.csv",
    "outputs/step45_runtime_projection_integration/runtime_projection_integration.json",
    "outputs/step45_runtime_projection_quality/runtime_projection_quality.csv",
    "outputs/step45_runtime_projection_quality/runtime_projection_quality.json",
    "outputs/step45_original_vs_runtime_projection_comparison/original_vs_runtime_projection.csv",
    "outputs/step45_original_vs_runtime_projection_comparison/original_vs_runtime_projection.json",
    "outputs/step45_projection_phase_closure/projection_phase_closure.csv",
    "outputs/step45_projection_phase_closure/projection_phase_closure.json",
    "outputs/step45_step44_projection_alignment/step44_projection_alignment.csv",
    "outputs/step45_step44_projection_alignment/step44_projection_alignment.json",
    "outputs/step45_runtime_projection_state_guard/runtime_projection_state_guard.csv",
    "outputs/step45_runtime_projection_state_guard/runtime_projection_state_guard.json",
    "outputs/step45_ultrashort_projection_driver_smoke/ultrashort_projection_driver_smoke.csv",
    "outputs/step45_ultrashort_projection_driver_smoke/ultrashort_projection_driver_smoke.json",
    "outputs/step45_step44_regression_guard/step44_regression_guard.csv",
    "outputs/step45_step44_regression_guard/step44_regression_guard.json",
    "outputs/step45_artifact_manifest/artifact_manifest.csv",
    "outputs/step45_artifact_manifest/artifact_summary.csv",
    "outputs/step45_artifact_manifest/artifact_summary.json",
]

STEP45_LOG_MARKERS = {
    "logs/step45_projection_integration_config_validation.log": "[OK] Step 45 projection integration config validation finished",
    "logs/step45_runtime_projection_integration.log": "[OK] Step 45 runtime projection integration finished",
    "logs/step45_runtime_projection_quality.log": "[OK] Step 45 runtime projection quality finished",
    "logs/step45_original_vs_runtime_projection_comparison.log": "[OK] Step 45 original-vs-runtime projection comparison finished",
    "logs/step45_projection_phase_closure.log": "[OK] Step 45 projection phase closure finished",
    "logs/step45_step44_projection_alignment.log": "[OK] Step 45 Step 44 projection alignment finished",
    "logs/step45_runtime_projection_state_guard.log": "[OK] Step 45 runtime projection state guard finished",
    "logs/step45_ultrashort_projection_driver_smoke.log": "[OK] Step 45 ultra-short projection driver smoke finished",
    "logs/step45_step44_regression_guard.log": "[OK] Step 45 Step 44 regression guard finished",
    "logs/step45_artifact_manifest.log": "[OK] Step 45 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 45 is controlled runtime geometry projection integration smoke.",
    "Step 45 uses transient projection state only.",
    "Step 45 does not persist projected state.",
    "Step 45 does not persist displaced geometry.",
    "Step 45 does not write displaced particles.",
    "Step 45 does not update default driver geometry.",
    "Step 45 does not persist LBM solid_phi updates.",
    "Step 45 does not update dynamic_solid.",
    "Step 45 does not change moving bounce-back formulas.",
    "The default geometry_motion_mode remains static.",
    "The default geometry_motion_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "full coupled geometry motion is implemented",
    "production moving geometry is implemented",
    "driver geometry is persistently updated",
    "MPM particles are persistently displaced",
    "LBM solid_phi is persistently updated",
    "dynamic_solid is persistently updated",
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


def test_step45_required_artifacts_exist():
    missing = [path for path in STEP45_REQUIRED_FILES + STEP45_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP45_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step45_projection_integration_config_is_valid():
    config = read_json("configs/step45_runtime_geometry_projection_integration.json")
    assert config["projection_integration_id"] == "step45_runtime_geometry_projection_integration_smoke"
    assert config["diagnostic_geometry_update_config_path"] == "configs/step44_diagnostic_geometry_update.json"
    assert config["geometry_motion_interface_config_path"] == "configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json"
    assert config["displacement_artifact_path"] == "outputs/step42_geometry_displacement/geometry_displacement.json"
    assert config["step44_projection_artifact_path"] == "outputs/step44_projection_only_smoke/projection_only_smoke.json"
    assert config["selected_phases"] == SELECTED_PHASES
    assert config["grid_sizes"] == [32, 48]
    assert config["tracked_regions"] == TRACKED_REGIONS
    assert config["integration_mode"] == "transient_projection_only"
    assert _all_step45_flags_false(config)
    assert config["diagnostic_only"] is True
    assert config["deterministic"] is True

    summary = read_json("outputs/step45_projection_integration_config_validation/projection_integration_config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["selected_phase_count"]) == 5
    assert summary["selected_phases"] == SELECTED_PHASES
    assert summary["grid_sizes"] == [32, 48]
    assert summary["tracked_regions"] == TRACKED_REGIONS
    assert summary["all_mutation_flags_false"] is True


def test_step45_runtime_projection_integration_is_valid():
    payload = read_json("outputs/step45_runtime_projection_integration/runtime_projection_integration.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 10
    assert int(summary["grid_size_count"]) == 2
    assert int(summary["phase_count"]) == 5
    assert int(summary["projection_pass_count"]) == 10
    assert summary["runtime_projection_integration_pass"] is True
    assert summary["transient_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True
    assert summary["selected_phases"] == SELECTED_PHASES
    assert summary["grid_sizes"] == [32, 48]
    for row in payload["rows"]:
        assert row["projection_pass"] is True
        assert float(row["projected_mass"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert int(row["boundary_cell_count"]) >= 0
        assert 0.0 <= float(row["solid_phi_min"]) <= float(row["solid_phi_max"]) <= 1.0
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert row["transient_only"] is True
        assert row["persist_projected_state"] is False
        assert row["apply_to_default_lbm_state"] is False


def test_step45_runtime_projection_quality_is_valid():
    summary = read_json("outputs/step45_runtime_projection_quality/runtime_projection_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["finite_pass"] is True
    assert summary["bounds_pass"] is True
    assert summary["active_cell_pass"] is True
    assert summary["projected_mass_pass"] is True
    assert summary["solid_phi_bounds_pass"] is True
    assert summary["phase_coverage_pass"] is True
    assert summary["grid_coverage_pass"] is True
    assert summary["transient_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True


def test_step45_original_vs_runtime_projection_comparison_is_valid():
    payload = read_json("outputs/step45_original_vs_runtime_projection_comparison/original_vs_runtime_projection.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 10
    assert summary["comparison_pass"] is True
    assert summary["phase0_close_to_original"] is True
    assert summary["phase1_close_to_original"] is True
    assert summary["midcycle_projection_delta_nonzero"] is True
    for row in payload["rows"]:
        assert row["comparison_pass"] is True
        assert math.isfinite(float(row["projected_mass_delta"]))
        assert math.isfinite(float(row["active_cell_delta"]))
        assert math.isfinite(float(row["bbox_delta"]))


def test_step45_projection_phase_closure_is_valid():
    payload = read_json("outputs/step45_projection_phase_closure/projection_phase_closure.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 2
    assert summary["closure_pass"] is True
    for row in payload["rows"]:
        assert row["closure_pass"] is True
        assert float(row["phase0_phase1_projected_mass_delta"]) <= 1.0e-8
        assert int(row["phase0_phase1_active_cell_delta"]) <= 1
        assert float(row["phase0_phase1_bbox_delta"]) <= 1.0


def test_step45_step44_projection_alignment_is_valid():
    payload = read_json("outputs/step45_step44_projection_alignment/step44_projection_alignment.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 10
    assert int(summary["alignment_pass_count"]) == 10
    assert summary["alignment_pass"] is True
    for row in payload["rows"]:
        assert row["alignment_pass"] is True
        assert math.isfinite(float(row["projected_mass_delta"]))
        assert math.isfinite(float(row["active_cell_count_delta"]))
        assert math.isfinite(float(row["solid_phi_min_delta"]))
        assert math.isfinite(float(row["solid_phi_max_delta"]))


def test_step45_runtime_projection_state_guard_is_valid():
    summary = read_json("outputs/step45_runtime_projection_state_guard/runtime_projection_state_guard.json")["summary"]
    assert summary["guard_pass"] is True
    assert summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
    assert summary["region_mask_hash_before"] == summary["region_mask_hash_after"]
    assert int(summary["driver_state_mutation_count"]) == 0
    assert int(summary["default_lbm_state_mutation_count"]) == 0
    assert int(summary["default_mpm_state_mutation_count"]) == 0
    assert int(summary["default_projection_state_mutation_count"]) == 0
    assert int(summary["dynamic_solid_mutation_count"]) == 0
    assert int(summary["persistent_projected_state_count"]) == 0
    assert int(summary["displaced_particle_output_count"]) == 0
    assert int(summary["dense_displacement_output_count"]) == 0
    assert int(summary["vtr_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step45_ultrashort_projection_driver_smoke_is_valid():
    payload = read_json("outputs/step45_ultrashort_projection_driver_smoke/ultrashort_projection_driver_smoke.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 3
    assert int(summary["stable_count"]) == 3
    assert int(summary["diagnostic_copy_only_count"]) == 2
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


def test_step45_step44_regression_guard_is_valid():
    payload = read_json("outputs/step45_step44_regression_guard/step44_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 7
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step45_default_modes_remain_unchanged():
    text = read_text("src/fsi_config.py")
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step45_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/45_controlled_runtime_geometry_projection_integration_smoke.md",
            "STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step45_artifact_budget_is_valid():
    summary = read_json("outputs/step45_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step45_total_size_mb"]) < 15.0
    assert float(summary["total_size_mb"]) < 340.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step45_vtr_count"]) == 0
    assert int(summary["step45_particle_npy_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step45_report_acceptance_complete():
    report = read_text("STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_REPORT.md")
    assert "## 16. Acceptance Checklist" in report
    assert "## 17. Decision For Step 46" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step45_no_persistent_geometry_outputs():
    summary = read_json("outputs/step45_artifact_manifest/artifact_summary.json")
    assert int(summary["step45_vtr_count"]) == 0
    assert int(summary["step45_particle_npy_count"]) == 0
    assert int(summary["step45_displaced_particle_output_count"]) == 0
    assert int(summary["step45_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step45_no_full_coupled_geometry_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/45_controlled_runtime_geometry_projection_integration_smoke.md",
            "STEP45_CONTROLLED_RUNTIME_GEOMETRY_PROJECTION_INTEGRATION_SMOKE_REPORT.md",
            "outputs/step45_ultrashort_projection_driver_smoke/ultrashort_projection_driver_smoke.json",
        ]
    )
    required_disabled = [
        '"persist_projected_state": false',
        '"transient_only": true',
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


def _all_step45_flags_false(config):
    return all(
        config[field] is False
        for field in (
            "persist_projected_state",
            "persist_displaced_geometry",
            "write_displaced_particles",
            "write_dense_displacement_field",
            "write_vtk",
            "apply_to_driver_state",
            "apply_to_default_lbm_state",
            "apply_to_default_mpm_state",
            "apply_to_default_projection_state",
            "update_dynamic_solid",
            "recompute_production_boundary_links",
            "mutate_original_geometry",
        )
    )
