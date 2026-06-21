import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STEP46_REQUIRED_FILES = [
    "STEP46_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_STEP_COUPLING_SMOKE_GOAL.md",
    "STEP46_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_STEP_COUPLING_SMOKE_REPORT.md",
    "docs/46_controlled_runtime_geometry_wall_velocity_one_step_coupling_smoke.md",
    "configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json",
    "configs/step46_original_static_32_1step.json",
    "configs/step46_runtime_geometry_only_32_phase035_1step.json",
    "configs/step46_wall_velocity_only_32_phase035_1step.json",
    "configs/step46_runtime_geometry_plus_wall_velocity_32_phase035_1step.json",
    "src/runtime_geometry_wall_velocity_coupling_config.py",
    "src/runtime_geometry_wall_velocity_coupling.py",
    "src/runtime_geometry_wall_velocity_diagnostics.py",
    "src/runtime_geometry_wall_velocity_state_guard.py",
    "baseline_tests/step46_common.py",
    "baseline_tests/run_step46_coupling_smoke_config_validation.py",
    "baseline_tests/run_step46_one_step_coupling_smoke_matrix.py",
    "baseline_tests/run_step46_coupling_smoke_quality.py",
    "baseline_tests/run_step46_component_effect_comparison.py",
    "baseline_tests/run_step46_mass_force_bounceback_diagnostics.py",
    "baseline_tests/run_step46_state_mutation_guard.py",
    "baseline_tests/run_step46_step45_regression_guard.py",
    "baseline_tests/run_step46_artifact_manifest.py",
    "tests/test_step46_runtime_geometry_wall_velocity_coupling_smoke_contract.py",
]

STEP46_OUTPUT_FILES = [
    "outputs/step46_coupling_smoke_config_validation/coupling_smoke_config_validation.csv",
    "outputs/step46_coupling_smoke_config_validation/coupling_smoke_config_validation.json",
    "outputs/step46_one_step_coupling_smoke_matrix/one_step_coupling_smoke_matrix.csv",
    "outputs/step46_one_step_coupling_smoke_matrix/one_step_coupling_smoke_matrix.json",
    "outputs/step46_one_step_coupling_smoke_matrix/one_step_coupling_smoke_matrix.npz",
    "outputs/step46_coupling_smoke_quality/coupling_smoke_quality.csv",
    "outputs/step46_coupling_smoke_quality/coupling_smoke_quality.json",
    "outputs/step46_component_effect_comparison/component_effect_comparison.csv",
    "outputs/step46_component_effect_comparison/component_effect_comparison.json",
    "outputs/step46_mass_force_bounceback_diagnostics/mass_force_bounceback_diagnostics.csv",
    "outputs/step46_mass_force_bounceback_diagnostics/mass_force_bounceback_diagnostics.json",
    "outputs/step46_state_mutation_guard/state_mutation_guard.csv",
    "outputs/step46_state_mutation_guard/state_mutation_guard.json",
    "outputs/step46_step45_regression_guard/step45_regression_guard.csv",
    "outputs/step46_step45_regression_guard/step45_regression_guard.json",
    "outputs/step46_artifact_manifest/artifact_manifest.csv",
    "outputs/step46_artifact_manifest/artifact_summary.csv",
    "outputs/step46_artifact_manifest/artifact_summary.json",
]

STEP46_LOG_MARKERS = {
    "logs/step46_coupling_smoke_config_validation.log": "[OK] Step 46 coupling smoke config validation finished",
    "logs/step46_one_step_coupling_smoke_matrix.log": "[OK] Step 46 one-step coupling smoke matrix finished",
    "logs/step46_coupling_smoke_quality.log": "[OK] Step 46 coupling smoke quality finished",
    "logs/step46_component_effect_comparison.log": "[OK] Step 46 component effect comparison finished",
    "logs/step46_mass_force_bounceback_diagnostics.log": "[OK] Step 46 mass force bounce-back diagnostics finished",
    "logs/step46_state_mutation_guard.log": "[OK] Step 46 state mutation guard finished",
    "logs/step46_step45_regression_guard.log": "[OK] Step 46 Step 45 regression guard finished",
    "logs/step46_artifact_manifest.log": "[OK] Step 46 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 46 is controlled runtime geometry plus wall velocity one-step coupling smoke.",
    "Step 46 is opt-in and ultra-short.",
    "Step 46 combines transient runtime geometry projection with solid_vel wall velocity application.",
    "Step 46 does not persist displaced geometry.",
    "Step 46 does not persist projected state.",
    "Step 46 does not run a full-cycle moving-geometry simulation.",
    "Step 46 does not change moving bounce-back formulas.",
    "The default geometry_motion_mode remains static.",
    "The default geometry_motion_application_mode remains disabled.",
    "The default boundary_motion_mode remains static.",
    "The default wall_velocity_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "full-cycle moving geometry is implemented",
    "production moving geometry is implemented",
    "driver geometry is persistently updated",
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

ROW_NAMES = [
    "original_static_32_1step",
    "runtime_geometry_only_32_phase035_1step",
    "wall_velocity_only_32_phase035_1step",
    "runtime_geometry_plus_wall_velocity_32_phase035_1step",
]


def test_step46_required_artifacts_exist():
    missing = [path for path in STEP46_REQUIRED_FILES + STEP46_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP46_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step46_coupling_smoke_config_is_valid():
    config = read_json("configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json")
    assert config["coupling_smoke_id"] == "step46_runtime_geometry_wall_velocity_one_step"
    assert config["runtime_projection_config_path"] == "configs/step45_runtime_geometry_projection_integration.json"
    assert config["diagnostic_geometry_update_config_path"] == "configs/step44_diagnostic_geometry_update.json"
    assert config["wall_velocity_application_config_path"] == "configs/step41_wall_velocity_application_scale_0050_64.json"
    assert config["phase"] == 0.35
    assert config["n_grid"] == 32
    assert config["n_lbm_steps"] == 1
    assert config["mpm_substeps_per_lbm_step"] == 1
    assert config["coupling_mode"] == "moving_boundary"
    assert config["reaction_transfer_mode"] == "engineering"
    assert config["enable_runtime_geometry_projection"] is True
    assert config["enable_wall_velocity_application"] is True
    assert _all_step46_flags_false(config)
    assert config["diagnostic_only"] is True

    summary = read_json("outputs/step46_coupling_smoke_config_validation/coupling_smoke_config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert summary["phase"] == 0.35
    assert int(summary["n_grid"]) == 32
    assert int(summary["n_lbm_steps"]) == 1
    assert int(summary["mpm_substeps_per_lbm_step"]) == 1
    assert summary["all_mutation_flags_false"] is True


def test_step46_one_step_coupling_smoke_matrix_is_valid():
    payload = read_json("outputs/step46_one_step_coupling_smoke_matrix/one_step_coupling_smoke_matrix.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["original_static_row_count"]) == 1
    assert int(summary["geometry_only_row_count"]) == 1
    assert int(summary["wall_velocity_only_row_count"]) == 1
    assert int(summary["combined_row_count"]) == 1
    assert summary["matrix_pass"] is True
    assert sorted(row["row_name"] for row in rows) == sorted(ROW_NAMES)
    for row in rows:
        assert row["stable"] is True
        assert int(row["completed_lbm_steps"]) >= 1
        assert int(row["total_mpm_substeps"]) >= 1
        assert float(row["rho_min"]) > 0.95
        assert float(row["rho_max"]) < 1.05
        assert float(row["lbm_max_v"]) < 0.1
        assert float(row["projected_mass"]) > 0.0
        assert int(row["active_cell_count"]) > 0
        assert int(row["bb_link_count"]) > 0
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert row["diagnostic_only"] is True
        assert row["persist_projected_state"] is False
        assert row["persist_displaced_geometry"] is False

    by_name = {row["row_name"]: row for row in rows}
    assert by_name["original_static_32_1step"]["runtime_geometry_projection_enabled"] is False
    assert by_name["original_static_32_1step"]["wall_velocity_application_enabled"] is False
    assert by_name["runtime_geometry_only_32_phase035_1step"]["runtime_geometry_projection_enabled"] is True
    assert by_name["runtime_geometry_only_32_phase035_1step"]["wall_velocity_application_enabled"] is False
    assert by_name["wall_velocity_only_32_phase035_1step"]["runtime_geometry_projection_enabled"] is False
    assert by_name["wall_velocity_only_32_phase035_1step"]["wall_velocity_application_enabled"] is True
    assert int(by_name["wall_velocity_only_32_phase035_1step"]["applied_cell_count"]) > 0
    assert by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["runtime_geometry_projection_enabled"] is True
    assert by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["wall_velocity_application_enabled"] is True
    assert int(by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["applied_cell_count"]) > 0


def test_step46_coupling_smoke_quality_is_valid():
    summary = read_json("outputs/step46_coupling_smoke_quality/coupling_smoke_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["stability_pass"] is True
    assert summary["projection_pass"] is True
    assert summary["wall_velocity_pass"] is True
    assert summary["combined_row_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True


def test_step46_component_effect_comparison_is_valid():
    payload = read_json("outputs/step46_component_effect_comparison/component_effect_comparison.json")
    summary = payload["summary"]
    assert int(summary["comparison_count"]) >= 5
    assert summary["comparison_pass"] is True
    assert summary["geometry_only_projection_delta_nonzero"] is True
    assert summary["wall_velocity_only_applied_velocity_nonzero"] is True
    assert summary["combined_has_geometry_and_wall_velocity"] is True
    for row in payload["rows"]:
        assert row["comparison_pass"] is True
        assert math.isfinite(float(row["projected_mass_delta"]))
        assert math.isfinite(float(row["active_cell_delta"]))
        assert math.isfinite(float(row["applied_velocity_delta"]))
        assert math.isfinite(float(row["hydro_force_delta"]))


def test_step46_mass_force_bounceback_diagnostics_is_valid():
    payload = read_json("outputs/step46_mass_force_bounceback_diagnostics/mass_force_bounceback_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 4
    assert summary["diagnostics_pass"] is True
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert math.isfinite(float(summary["bb_max_correction_global"]))
    assert int(summary["bb_link_count_min"]) > 0
    assert math.isfinite(float(summary["hydro_force_max_norm_global"]))
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0
    for row in payload["rows"]:
        assert row["diagnostics_pass"] is True
        if row["wall_velocity_application_enabled"]:
            assert float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12


def test_step46_state_mutation_guard_is_valid():
    summary = read_json("outputs/step46_state_mutation_guard/state_mutation_guard.json")["summary"]
    assert summary["guard_pass"] is True
    assert summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
    assert int(summary["default_driver_state_mutation_count"]) == 0
    assert int(summary["default_lbm_state_mutation_count"]) == 0
    assert int(summary["default_mpm_state_mutation_count"]) == 0
    assert int(summary["default_projection_state_mutation_count"]) == 0
    assert int(summary["persistent_projected_state_count"]) == 0
    assert int(summary["persistent_displaced_geometry_count"]) == 0
    assert int(summary["displaced_particle_output_count"]) == 0
    assert int(summary["dense_displacement_output_count"]) == 0
    assert int(summary["vtr_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step46_step45_regression_guard_is_valid():
    payload = read_json("outputs/step46_step45_regression_guard/step45_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 7
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step46_default_modes_remain_unchanged():
    text = read_text("src/fsi_config.py")
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step46_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/46_controlled_runtime_geometry_wall_velocity_one_step_coupling_smoke.md",
            "STEP46_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_STEP_COUPLING_SMOKE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step46_artifact_budget_is_valid():
    summary = read_json("outputs/step46_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step46_total_size_mb"]) < 10.0
    assert float(summary["total_size_mb"]) < 350.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step46_vtr_count"]) == 0
    assert int(summary["step46_particle_npy_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step46_report_acceptance_complete():
    report = read_text("STEP46_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_STEP_COUPLING_SMOKE_REPORT.md")
    assert "## 14. Acceptance Checklist" in report
    assert "## 15. Decision For Step 47" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step46_no_persistent_geometry_outputs():
    summary = read_json("outputs/step46_artifact_manifest/artifact_summary.json")
    assert int(summary["step46_vtr_count"]) == 0
    assert int(summary["step46_particle_npy_count"]) == 0
    assert int(summary["step46_displaced_particle_output_count"]) == 0
    assert int(summary["step46_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step46_no_full_cycle_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/46_controlled_runtime_geometry_wall_velocity_one_step_coupling_smoke.md",
            "STEP46_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_STEP_COUPLING_SMOKE_REPORT.md",
            "outputs/step46_one_step_coupling_smoke_matrix/one_step_coupling_smoke_matrix.json",
        ]
    )
    required_disabled = [
        '"full_cycle_moving_geometry_claim": false',
        '"production_moving_geometry_claim": false',
        '"persist_projected_state": false',
        '"persist_displaced_geometry": false',
    ]
    missing = [phrase for phrase in required_disabled if phrase not in combined]
    assert missing == []


def test_step46_no_formula_changes():
    protected_files = [
        "src/lbm_fluid.py",
        "src/projection.py",
        "src/coupling.py",
        "src/moving_boundary_coupling.py",
        "src/wall_velocity_application.py",
    ]
    offenders = []
    for path in protected_files:
        text = read_text(path)
        if "Step 46" in text or "runtime_geometry_wall_velocity" in text:
            offenders.append(path)
    assert offenders == []


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    full_path = ROOT / path
    if not full_path.is_file():
        return ""
    return full_path.read_text(encoding="utf-8")


def _all_step46_flags_false(config):
    return all(
        config[field] is False
        for field in (
            "persist_displaced_geometry",
            "persist_projected_state",
            "persist_lbm_solid_vel",
            "write_displaced_particles",
            "write_dense_displacement_field",
            "write_vtk",
            "write_particles",
            "update_default_driver_geometry",
            "update_default_lbm_state",
            "update_default_mpm_state",
            "update_default_projection_state",
            "update_dynamic_solid_persistently",
            "recompute_production_boundary_links",
            "modify_moving_bounceback_formula",
        )
    )
