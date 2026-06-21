import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PHASE_SEQUENCE = [0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5]
PREFIX_PHASES = [0.0, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35]
TRANSITION_PHASES = [0.35, 0.375, 0.4, 0.425, 0.45, 0.5]

STEP49_REQUIRED_FILES = [
    "STEP49_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_20STEP_COUPLING_ENVELOPE_GOAL.md",
    "STEP49_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_20STEP_COUPLING_ENVELOPE_REPORT.md",
    "docs/49_controlled_runtime_geometry_wall_velocity_20step_coupling_envelope.md",
    "configs/step49_runtime_geometry_wall_velocity_20step_envelope.json",
    "configs/step49_original_static_32_20step.json",
    "configs/step49_runtime_geometry_only_32_20step.json",
    "configs/step49_wall_velocity_only_32_20step.json",
    "configs/step49_runtime_geometry_plus_wall_velocity_32_20step.json",
    "src/runtime_geometry_wall_velocity_20step_config.py",
    "src/runtime_geometry_wall_velocity_20step_envelope.py",
    "src/runtime_geometry_wall_velocity_20step_diagnostics.py",
    "src/runtime_geometry_wall_velocity_20step_state_guard.py",
    "baseline_tests/step49_common.py",
    "baseline_tests/run_step49_20step_config_validation.py",
    "baseline_tests/run_step49_20step_envelope_matrix.py",
    "baseline_tests/run_step49_20step_envelope_quality.py",
    "baseline_tests/run_step49_component_effect_20step_envelope.py",
    "baseline_tests/run_step49_phase_progression_20step_diagnostics.py",
    "baseline_tests/run_step49_early_refill_transition_diagnostics.py",
    "baseline_tests/run_step49_mass_force_bounceback_20step_envelope.py",
    "baseline_tests/run_step49_step48_prefix_comparison.py",
    "baseline_tests/run_step49_state_mutation_guard.py",
    "baseline_tests/run_step49_step48_regression_guard.py",
    "baseline_tests/run_step49_artifact_manifest.py",
    "tests/test_step49_runtime_geometry_wall_velocity_20step_envelope_contract.py",
]

STEP49_OUTPUT_FILES = [
    "outputs/step49_20step_config_validation/twenty_step_config_validation.csv",
    "outputs/step49_20step_config_validation/twenty_step_config_validation.json",
    "outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.csv",
    "outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.json",
    "outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.npz",
    "outputs/step49_20step_envelope_quality/twenty_step_envelope_quality.csv",
    "outputs/step49_20step_envelope_quality/twenty_step_envelope_quality.json",
    "outputs/step49_component_effect_20step_envelope/component_effect_20step_envelope.csv",
    "outputs/step49_component_effect_20step_envelope/component_effect_20step_envelope.json",
    "outputs/step49_phase_progression_20step_diagnostics/phase_progression_20step_diagnostics.csv",
    "outputs/step49_phase_progression_20step_diagnostics/phase_progression_20step_diagnostics.json",
    "outputs/step49_early_refill_transition_diagnostics/early_refill_transition_diagnostics.csv",
    "outputs/step49_early_refill_transition_diagnostics/early_refill_transition_diagnostics.json",
    "outputs/step49_mass_force_bounceback_20step_envelope/mass_force_bounceback_20step_envelope.csv",
    "outputs/step49_mass_force_bounceback_20step_envelope/mass_force_bounceback_20step_envelope.json",
    "outputs/step49_step48_prefix_comparison/step48_prefix_comparison.csv",
    "outputs/step49_step48_prefix_comparison/step48_prefix_comparison.json",
    "outputs/step49_state_mutation_guard/state_mutation_guard.csv",
    "outputs/step49_state_mutation_guard/state_mutation_guard.json",
    "outputs/step49_step48_regression_guard/step48_regression_guard.csv",
    "outputs/step49_step48_regression_guard/step48_regression_guard.json",
    "outputs/step49_artifact_manifest/artifact_manifest.csv",
    "outputs/step49_artifact_manifest/artifact_summary.csv",
    "outputs/step49_artifact_manifest/artifact_summary.json",
]

STEP49_LOG_MARKERS = {
    "logs/step49_20step_config_validation.log": "[OK] Step 49 20-step config validation finished",
    "logs/step49_20step_envelope_matrix.log": "[OK] Step 49 20-step envelope matrix finished",
    "logs/step49_20step_envelope_quality.log": "[OK] Step 49 20-step envelope quality finished",
    "logs/step49_component_effect_20step_envelope.log": "[OK] Step 49 component effect 20-step envelope finished",
    "logs/step49_phase_progression_20step_diagnostics.log": "[OK] Step 49 phase progression 20-step diagnostics finished",
    "logs/step49_early_refill_transition_diagnostics.log": "[OK] Step 49 early refill transition diagnostics finished",
    "logs/step49_mass_force_bounceback_20step_envelope.log": "[OK] Step 49 mass force bounce-back 20-step envelope finished",
    "logs/step49_step48_prefix_comparison.log": "[OK] Step 49 Step 48 prefix comparison finished",
    "logs/step49_state_mutation_guard.log": "[OK] Step 49 state mutation guard finished",
    "logs/step49_step48_regression_guard.log": "[OK] Step 49 Step 48 regression guard finished",
    "logs/step49_artifact_manifest.log": "[OK] Step 49 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 49 is controlled runtime geometry plus wall velocity 20-step coupling envelope.",
    "Step 49 is opt-in and engineering-only.",
    "Step 49 runs a 32^3 twenty-step envelope.",
    "Step 49 does not run a full-cycle moving-geometry simulation.",
    "Step 49 does not persist displaced geometry.",
    "Step 49 does not persist projected state.",
    "Step 49 does not change moving bounce-back formulas.",
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
    "LBM solid_vel is persistently updated",
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
    "original_static_32_20step",
    "runtime_geometry_only_32_20step",
    "wall_velocity_only_32_20step",
    "runtime_geometry_plus_wall_velocity_32_20step",
]


def test_step49_required_artifacts_exist():
    missing = [path for path in STEP49_REQUIRED_FILES + STEP49_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP49_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step49_20step_config_is_valid():
    config = read_json("configs/step49_runtime_geometry_wall_velocity_20step_envelope.json")
    assert config["twenty_step_envelope_id"] == "step49_runtime_geometry_wall_velocity_20step_envelope"
    assert config["base_step48_config_path"] == "configs/step48_runtime_geometry_wall_velocity_10step_envelope.json"
    assert config["runtime_projection_config_path"] == "configs/step45_runtime_geometry_projection_integration.json"
    assert config["wall_velocity_application_config_path"] == "configs/step41_wall_velocity_application_scale_0050_64.json"
    assert int(config["n_grid"]) == 32
    assert int(config["n_lbm_steps"]) == 20
    assert int(config["mpm_substeps_per_lbm_step"]) == 5
    assert [float(value) for value in config["phase_sequence"]] == PHASE_SEQUENCE
    assert config["coupling_mode"] == "moving_boundary"
    assert config["reaction_transfer_mode"] == "engineering"
    assert config["enable_runtime_geometry_projection"] is True
    assert config["enable_wall_velocity_application"] is True
    assert _all_step49_flags_false(config)
    assert config["diagnostic_only"] is True
    assert "full-cycle" in config["scope_note"]

    for descriptor_path in [
        "configs/step49_original_static_32_20step.json",
        "configs/step49_runtime_geometry_only_32_20step.json",
        "configs/step49_wall_velocity_only_32_20step.json",
        "configs/step49_runtime_geometry_plus_wall_velocity_32_20step.json",
    ]:
        descriptor = read_json(descriptor_path)
        assert int(descriptor["n_grid"]) == 32
        assert int(descriptor["n_lbm_steps"]) == 20
        assert int(descriptor["mpm_substeps_per_lbm_step"]) == 5
        assert [float(value) for value in descriptor["phase_sequence"]] == PHASE_SEQUENCE
        assert descriptor["reaction_transfer_mode"] == "engineering"
        assert "link_area" not in json.dumps(descriptor)

    summary = read_json("outputs/step49_20step_config_validation/twenty_step_config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["n_grid"]) == 32
    assert int(summary["n_lbm_steps"]) == 20
    assert int(summary["mpm_substeps_per_lbm_step"]) == 5
    assert [float(value) for value in summary["phase_sequence"]] == PHASE_SEQUENCE
    assert int(summary["phase_count"]) == 20
    assert summary["phase_contains_035"] is True
    assert summary["phase_ends_at_05"] is True
    assert summary["phase_nondecreasing"] is True
    assert summary["all_mutation_flags_false"] is True


def test_step49_20step_envelope_matrix_is_valid():
    payload = read_json("outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["step_count_per_row"]) == 20
    assert int(summary["original_static_row_count"]) == 1
    assert int(summary["geometry_only_row_count"]) == 1
    assert int(summary["wall_velocity_only_row_count"]) == 1
    assert int(summary["combined_row_count"]) == 1
    assert summary["matrix_pass"] is True
    assert sorted(row["row_name"] for row in rows) == sorted(ROW_NAMES)
    assert int(summary["completed_lbm_steps_min"]) >= 20
    assert int(summary["total_mpm_substeps_min"]) >= 100
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert float(summary["lbm_max_v_global"]) < 0.1
    assert float(summary["projected_mass_min"]) > 0.0
    assert int(summary["active_cell_count_min"]) > 0
    assert int(summary["bb_link_count_min"]) > 0
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0

    for row in rows:
        assert row["stable"] is True
        assert int(row["completed_lbm_steps"]) >= 20
        assert int(row["total_mpm_substeps"]) >= 100
        assert [float(value) for value in row["phase_sequence"]] == PHASE_SEQUENCE
        assert len(row["step_records"]) == 20
        assert float(row["rho_min_global"]) > 0.95
        assert float(row["rho_max_global"]) < 1.05
        assert float(row["lbm_max_v_global"]) < 0.1
        assert float(row["projected_mass_min"]) > 0.0
        assert int(row["active_cell_count_min"]) > 0
        assert int(row["bb_link_count_min"]) > 0
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert row["diagnostic_only"] is True
        assert row["persist_projected_state"] is False
        assert row["persist_displaced_geometry"] is False
        assert row["persist_lbm_solid_vel"] is False
        assert row["complete_cycle_claim"] is False
        assert row["production_geometry_claim"] is False
        for step in row["step_records"]:
            assert int(step["step_index"]) in range(20)
            assert float(step["phase"]) in PHASE_SEQUENCE
            assert float(step["projected_mass"]) > 0.0
            assert int(step["active_cell_count"]) > 0
            assert int(step["bb_link_count"]) > 0
            assert float(step["rho_min"]) > 0.95
            assert float(step["rho_max"]) < 1.05
            assert not step["has_nan"]
            assert not step["has_inf"]

    by_name = {row["row_name"]: row for row in rows}
    assert by_name["original_static_32_20step"]["runtime_geometry_projection_enabled"] is False
    assert by_name["original_static_32_20step"]["wall_velocity_application_enabled"] is False
    assert int(by_name["original_static_32_20step"]["applied_cell_count_max"]) == 0
    assert by_name["runtime_geometry_only_32_20step"]["runtime_geometry_projection_enabled"] is True
    assert by_name["runtime_geometry_only_32_20step"]["wall_velocity_application_enabled"] is False
    assert int(by_name["runtime_geometry_only_32_20step"]["active_cell_count_delta_from_original_max"]) > 0
    assert by_name["wall_velocity_only_32_20step"]["runtime_geometry_projection_enabled"] is False
    assert by_name["wall_velocity_only_32_20step"]["wall_velocity_application_enabled"] is True
    assert int(by_name["wall_velocity_only_32_20step"]["applied_cell_count_max"]) > 0
    assert by_name["runtime_geometry_plus_wall_velocity_32_20step"]["runtime_geometry_projection_enabled"] is True
    assert by_name["runtime_geometry_plus_wall_velocity_32_20step"]["wall_velocity_application_enabled"] is True
    assert int(by_name["runtime_geometry_plus_wall_velocity_32_20step"]["applied_cell_count_max"]) > 0
    assert int(by_name["runtime_geometry_plus_wall_velocity_32_20step"]["active_cell_count_delta_from_original_max"]) > 0


def test_step49_20step_envelope_quality_is_valid():
    summary = read_json("outputs/step49_20step_envelope_quality/twenty_step_envelope_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["step_count_pass"] is True
    assert summary["stability_pass"] is True
    assert summary["projection_pass"] is True
    assert summary["wall_velocity_pass"] is True
    assert summary["combined_row_pass"] is True
    assert summary["early_refill_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True


def test_step49_component_effect_20step_envelope_is_valid():
    payload = read_json("outputs/step49_component_effect_20step_envelope/component_effect_20step_envelope.json")
    summary = payload["summary"]
    assert int(summary["comparison_count"]) >= 5
    assert summary["comparison_pass"] is True
    assert summary["geometry_effect_active_cell_delta_nonzero"] is True
    assert summary["wall_velocity_effect_applied_velocity_nonzero"] is True
    assert summary["combined_has_geometry_and_wall_velocity"] is True
    for row in payload["rows"]:
        assert row["comparison_pass"] is True
        assert math.isfinite(float(row["projected_mass_delta_max_abs"]))
        assert math.isfinite(float(row["active_cell_delta_max_abs"]))
        assert math.isfinite(float(row["applied_velocity_delta_max_abs"]))
        assert math.isfinite(float(row["hydro_force_delta_max_abs"]))


def test_step49_phase_progression_20step_diagnostics_is_valid():
    payload = read_json("outputs/step49_phase_progression_20step_diagnostics/phase_progression_20step_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["phase_count"]) == 20
    assert [float(value) for value in summary["phase_sequence"]] == PHASE_SEQUENCE
    assert summary["phase_sequence_pass"] is True
    assert summary["runtime_geometry_phase_response_pass"] is True
    assert summary["wall_velocity_phase_response_pass"] is True
    assert summary["combined_phase_response_pass"] is True
    assert summary["phase0_to_phase035_projection_delta_nonzero"] is True
    assert summary["phase0_to_phase05_wall_velocity_delta_finite"] is True
    assert summary["phase_progression_pass"] is True
    for row in payload["rows"]:
        assert row["progression_pass"] is True
        assert math.isfinite(float(row["active_cell_count_delta_phase0_to_phase035"]))
        assert math.isfinite(float(row["max_applied_velocity_delta_phase0_to_phase05"]))


def test_step49_early_refill_transition_diagnostics_is_valid():
    payload = read_json("outputs/step49_early_refill_transition_diagnostics/early_refill_transition_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["transition_phase_count"]) >= 5
    assert [float(value) for value in summary["transition_phases"]] == TRANSITION_PHASES
    assert summary["transition_pass"] is True
    assert summary["runtime_geometry_active_cell_count_bounded"] is True
    assert summary["wall_velocity_applied_cell_count_positive"] is True
    assert summary["wall_velocity_cap_pass"] is True
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0
    for row in payload["rows"]:
        assert row["transition_pass"] is True
        assert int(row["transition_phase_count"]) >= 5
        assert math.isfinite(float(row["rho_min_transition"]))
        assert math.isfinite(float(row["rho_max_transition"]))
        assert int(row["bb_link_count_min_transition"]) > 0


def test_step49_mass_force_bounceback_20step_envelope_is_valid():
    payload = read_json("outputs/step49_mass_force_bounceback_20step_envelope/mass_force_bounceback_20step_envelope.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 4
    assert summary["envelope_pass"] is True
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert math.isfinite(float(summary["bb_max_correction_global"]))
    assert int(summary["bb_link_count_min"]) > 0
    assert math.isfinite(float(summary["hydro_force_max_norm_global"]))
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0
    for row in payload["rows"]:
        assert row["envelope_pass"] is True
        if row["wall_velocity_application_enabled"]:
            assert float(row["max_applied_velocity_norm"]) <= float(row["wall_velocity_cap_lbm"]) + 1.0e-12


def test_step49_step48_prefix_comparison_is_valid():
    payload = read_json("outputs/step49_step48_prefix_comparison/step48_prefix_comparison.json")
    summary = payload["summary"]
    assert int(summary["matched_phase_count"]) == 10
    assert [float(value) for value in summary["matched_phases"]] == PREFIX_PHASES
    assert int(summary["row_pair_count"]) == 4
    assert summary["comparison_pass"] is True
    assert int(summary["comparison_pass_count"]) == int(summary["row_pair_count"])
    for row in payload["rows"]:
        assert row["comparison_pass"] is True
        assert [float(value) for value in row["matched_phases"]] == PREFIX_PHASES
        assert math.isfinite(float(row["projected_mass_delta_max_abs"]))
        assert math.isfinite(float(row["active_cell_count_delta_max_abs"]))
        assert math.isfinite(float(row["applied_velocity_delta_max_abs"]))


def test_step49_state_mutation_guard_is_valid():
    summary = read_json("outputs/step49_state_mutation_guard/state_mutation_guard.json")["summary"]
    assert summary["guard_pass"] is True
    assert summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
    assert summary["region_mask_hash_before"] == summary["region_mask_hash_after"]
    assert int(summary["default_driver_state_mutation_count"]) == 0
    assert int(summary["default_lbm_state_mutation_count"]) == 0
    assert int(summary["default_mpm_state_mutation_count"]) == 0
    assert int(summary["default_projection_state_mutation_count"]) == 0
    assert int(summary["persistent_projected_state_count"]) == 0
    assert int(summary["persistent_displaced_geometry_count"]) == 0
    assert int(summary["persistent_lbm_solid_vel_count"]) == 0
    assert int(summary["displaced_particle_output_count"]) == 0
    assert int(summary["dense_displacement_output_count"]) == 0
    assert int(summary["vtr_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step49_step48_regression_guard_is_valid():
    payload = read_json("outputs/step49_step48_regression_guard/step48_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 11
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step49_default_modes_remain_unchanged():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step49_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/49_controlled_runtime_geometry_wall_velocity_20step_coupling_envelope.md",
            "STEP49_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_20STEP_COUPLING_ENVELOPE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step49_artifact_budget_is_valid():
    summary = read_json("outputs/step49_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step49_total_size_mb"]) < 25.0
    assert float(summary["total_size_mb"]) < 380.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step49_vtr_count"]) == 0
    assert int(summary["step49_particle_npy_count"]) == 0
    assert int(summary["step49_displaced_particle_output_count"]) == 0
    assert int(summary["step49_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step49_report_acceptance_complete():
    report = read_text("STEP49_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_20STEP_COUPLING_ENVELOPE_REPORT.md")
    for heading in [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. 20-Step Config Validation",
        "## 5. 20-Step Envelope Matrix",
        "## 6. 20-Step Envelope Quality",
        "## 7. Component Effect 20-Step Envelope",
        "## 8. Phase Progression 20-Step Diagnostics",
        "## 9. Early Refill Transition Diagnostics",
        "## 10. Mass Force Bounce-Back 20-Step Envelope",
        "## 11. Step 48 Prefix Comparison",
        "## 12. State Mutation Guard",
        "## 13. Step 48 Regression Guard",
        "## 14. Artifact Manifest Summary",
        "## 15. Verification Commands",
        "## 16. GitHub Sync Information",
        "## 17. Acceptance Checklist",
        "## 18. Decision For Step 50",
    ]:
        assert heading in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step49_no_persistent_geometry_outputs():
    summary = read_json("outputs/step49_artifact_manifest/artifact_summary.json")
    assert int(summary["step49_vtr_count"]) == 0
    assert int(summary["step49_particle_npy_count"]) == 0
    assert int(summary["step49_displaced_particle_output_count"]) == 0
    assert int(summary["step49_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step49_no_full_cycle_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/49_controlled_runtime_geometry_wall_velocity_20step_coupling_envelope.md",
            "STEP49_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_20STEP_COUPLING_ENVELOPE_REPORT.md",
            "outputs/step49_20step_envelope_matrix/twenty_step_envelope_matrix.json",
        ]
    )
    required_disabled = [
        '"complete_cycle_claim": false',
        '"production_geometry_claim": false',
        '"persist_projected_state": false',
        '"persist_displaced_geometry": false',
    ]
    missing = [phrase for phrase in required_disabled if phrase not in combined]
    assert missing == []


def test_step49_no_formula_changes():
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
        if "Step 49" in text or "runtime_geometry_wall_velocity_20step" in text:
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


def _all_step49_flags_false(config):
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
