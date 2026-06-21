import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PHASE_SEQUENCE = [
    0.0, 0.025, 0.05, 0.075, 0.1,
    0.125, 0.15, 0.175, 0.2, 0.225,
    0.25, 0.275, 0.3, 0.325, 0.35,
    0.375, 0.4, 0.425, 0.45, 0.475,
    0.5, 0.525, 0.55, 0.575, 0.6,
    0.625, 0.65, 0.675, 0.7, 0.725,
    0.75, 0.775, 0.8, 0.825, 0.85,
    0.875, 0.9, 0.925, 0.95, 0.975,
]
PREFIX_PHASES = [0.0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.5]

STEP50_REQUIRED_FILES = [
    "STEP50_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_CYCLE_COUPLING_DIAGNOSTIC_ENVELOPE_GOAL.md",
    "STEP50_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_CYCLE_COUPLING_DIAGNOSTIC_ENVELOPE_REPORT.md",
    "docs/50_controlled_runtime_geometry_wall_velocity_one_cycle_coupling_diagnostic_envelope.md",
    "configs/step50_runtime_geometry_wall_velocity_one_cycle_envelope.json",
    "configs/step50_original_static_32_40step.json",
    "configs/step50_runtime_geometry_only_32_40step.json",
    "configs/step50_wall_velocity_only_32_40step.json",
    "configs/step50_runtime_geometry_plus_wall_velocity_32_40step.json",
    "src/runtime_geometry_wall_velocity_one_cycle_config.py",
    "src/runtime_geometry_wall_velocity_one_cycle_envelope.py",
    "src/runtime_geometry_wall_velocity_one_cycle_diagnostics.py",
    "src/runtime_geometry_wall_velocity_one_cycle_state_guard.py",
    "baseline_tests/step50_common.py",
    "baseline_tests/run_step50_one_cycle_config_validation.py",
    "baseline_tests/run_step50_one_cycle_envelope_matrix.py",
    "baseline_tests/run_step50_one_cycle_envelope_quality.py",
    "baseline_tests/run_step50_component_effect_one_cycle_envelope.py",
    "baseline_tests/run_step50_phase_progression_one_cycle_diagnostics.py",
    "baseline_tests/run_step50_contraction_refill_segment_diagnostics.py",
    "baseline_tests/run_step50_cycle_closure_diagnostics.py",
    "baseline_tests/run_step50_mass_force_bounceback_one_cycle_envelope.py",
    "baseline_tests/run_step50_step49_prefix_comparison.py",
    "baseline_tests/run_step50_state_mutation_guard.py",
    "baseline_tests/run_step50_step49_regression_guard.py",
    "baseline_tests/run_step50_artifact_manifest.py",
    "tests/test_step50_runtime_geometry_wall_velocity_one_cycle_envelope_contract.py",
]

STEP50_OUTPUT_FILES = [
    "outputs/step50_one_cycle_config_validation/one_cycle_config_validation.csv",
    "outputs/step50_one_cycle_config_validation/one_cycle_config_validation.json",
    "outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.csv",
    "outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.json",
    "outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.npz",
    "outputs/step50_one_cycle_envelope_quality/one_cycle_envelope_quality.csv",
    "outputs/step50_one_cycle_envelope_quality/one_cycle_envelope_quality.json",
    "outputs/step50_component_effect_one_cycle_envelope/component_effect_one_cycle_envelope.csv",
    "outputs/step50_component_effect_one_cycle_envelope/component_effect_one_cycle_envelope.json",
    "outputs/step50_phase_progression_one_cycle_diagnostics/phase_progression_one_cycle_diagnostics.csv",
    "outputs/step50_phase_progression_one_cycle_diagnostics/phase_progression_one_cycle_diagnostics.json",
    "outputs/step50_contraction_refill_segment_diagnostics/contraction_refill_segment_diagnostics.csv",
    "outputs/step50_contraction_refill_segment_diagnostics/contraction_refill_segment_diagnostics.json",
    "outputs/step50_cycle_closure_diagnostics/cycle_closure_diagnostics.csv",
    "outputs/step50_cycle_closure_diagnostics/cycle_closure_diagnostics.json",
    "outputs/step50_mass_force_bounceback_one_cycle_envelope/mass_force_bounceback_one_cycle_envelope.csv",
    "outputs/step50_mass_force_bounceback_one_cycle_envelope/mass_force_bounceback_one_cycle_envelope.json",
    "outputs/step50_step49_prefix_comparison/step49_prefix_comparison.csv",
    "outputs/step50_step49_prefix_comparison/step49_prefix_comparison.json",
    "outputs/step50_state_mutation_guard/state_mutation_guard.csv",
    "outputs/step50_state_mutation_guard/state_mutation_guard.json",
    "outputs/step50_step49_regression_guard/step49_regression_guard.csv",
    "outputs/step50_step49_regression_guard/step49_regression_guard.json",
    "outputs/step50_artifact_manifest/artifact_manifest.csv",
    "outputs/step50_artifact_manifest/artifact_summary.csv",
    "outputs/step50_artifact_manifest/artifact_summary.json",
]

STEP50_LOG_MARKERS = {
    "logs/step50_one_cycle_config_validation.log": "[OK] Step 50 one-cycle config validation finished",
    "logs/step50_one_cycle_envelope_matrix.log": "[OK] Step 50 one-cycle envelope matrix finished",
    "logs/step50_one_cycle_envelope_quality.log": "[OK] Step 50 one-cycle envelope quality finished",
    "logs/step50_component_effect_one_cycle_envelope.log": "[OK] Step 50 component effect one-cycle envelope finished",
    "logs/step50_phase_progression_one_cycle_diagnostics.log": "[OK] Step 50 phase progression one-cycle diagnostics finished",
    "logs/step50_contraction_refill_segment_diagnostics.log": "[OK] Step 50 contraction refill segment diagnostics finished",
    "logs/step50_cycle_closure_diagnostics.log": "[OK] Step 50 cycle closure diagnostics finished",
    "logs/step50_mass_force_bounceback_one_cycle_envelope.log": "[OK] Step 50 mass force bounce-back one-cycle envelope finished",
    "logs/step50_step49_prefix_comparison.log": "[OK] Step 50 Step 49 prefix comparison finished",
    "logs/step50_state_mutation_guard.log": "[OK] Step 50 state mutation guard finished",
    "logs/step50_step49_regression_guard.log": "[OK] Step 50 Step 49 regression guard finished",
    "logs/step50_artifact_manifest.log": "[OK] Step 50 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 50 is controlled runtime geometry plus wall velocity one-cycle coupling diagnostic envelope.",
    "Step 50 is opt-in and engineering-only.",
    "Step 50 runs a 32^3 one-cycle diagnostic envelope.",
    "Step 50 remains non-persistent.",
    "Step 50 does not implement a production moving-geometry solver.",
    "Step 50 does not validate real jet propulsion.",
    "Step 50 does not implement squid swimming.",
    "Step 50 does not change moving bounce-back formulas.",
    "The default geometry_motion_mode remains static.",
    "The default geometry_motion_application_mode remains disabled.",
    "The default boundary_motion_mode remains static.",
    "The default wall_velocity_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
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
    "jet propulsion is validated",
    "real squid simulation is validated",
    "production-ready sharp-interface FSI",
]

ROW_NAMES = [
    "original_static_32_40step",
    "runtime_geometry_only_32_40step",
    "wall_velocity_only_32_40step",
    "runtime_geometry_plus_wall_velocity_32_40step",
]


def test_step50_required_artifacts_exist():
    missing = [path for path in STEP50_REQUIRED_FILES + STEP50_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP50_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step50_one_cycle_config_is_valid():
    config = read_json("configs/step50_runtime_geometry_wall_velocity_one_cycle_envelope.json")
    assert config["one_cycle_envelope_id"] == "step50_runtime_geometry_wall_velocity_one_cycle_envelope"
    assert config["base_step49_config_path"] == "configs/step49_runtime_geometry_wall_velocity_20step_envelope.json"
    assert config["runtime_projection_config_path"] == "configs/step45_runtime_geometry_projection_integration.json"
    assert config["wall_velocity_application_config_path"] == "configs/step41_wall_velocity_application_scale_0050_64.json"
    assert int(config["n_grid"]) == 32
    assert int(config["n_lbm_steps"]) == 40
    assert int(config["mpm_substeps_per_lbm_step"]) == 5
    assert int(config["cycle_period_steps"]) == 40
    assert [float(value) for value in config["phase_sequence"]] == PHASE_SEQUENCE
    assert float(config["closure_phase"]) == 1.0
    assert config["coupling_mode"] == "moving_boundary"
    assert config["reaction_transfer_mode"] == "engineering"
    assert config["enable_runtime_geometry_projection"] is True
    assert config["enable_wall_velocity_application"] is True
    assert _all_step50_flags_false(config)
    assert config["diagnostic_only"] is True

    for descriptor_path in [
        "configs/step50_original_static_32_40step.json",
        "configs/step50_runtime_geometry_only_32_40step.json",
        "configs/step50_wall_velocity_only_32_40step.json",
        "configs/step50_runtime_geometry_plus_wall_velocity_32_40step.json",
    ]:
        descriptor = read_json(descriptor_path)
        assert int(descriptor["n_grid"]) == 32
        assert int(descriptor["n_lbm_steps"]) == 40
        assert int(descriptor["mpm_substeps_per_lbm_step"]) == 5
        assert int(descriptor["cycle_period_steps"]) == 40
        assert [float(value) for value in descriptor["phase_sequence"]] == PHASE_SEQUENCE
        assert float(descriptor["closure_phase"]) == 1.0
        assert descriptor["reaction_transfer_mode"] == "engineering"
        assert "link_area" not in json.dumps(descriptor)

    summary = read_json("outputs/step50_one_cycle_config_validation/one_cycle_config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["n_grid"]) == 32
    assert int(summary["n_lbm_steps"]) == 40
    assert int(summary["mpm_substeps_per_lbm_step"]) == 5
    assert int(summary["cycle_period_steps"]) == 40
    assert int(summary["phase_count"]) == 40
    assert [float(value) for value in summary["phase_sequence"]] == PHASE_SEQUENCE
    assert summary["phase_starts_at_0"] is True
    assert summary["phase_ends_at_0975"] is True
    assert summary["closure_phase_is_1"] is True
    assert summary["all_mutation_flags_false"] is True


def test_step50_one_cycle_envelope_matrix_is_valid():
    payload = read_json("outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["step_count_per_row"]) == 40
    assert summary["matrix_pass"] is True
    assert sorted(row["row_name"] for row in rows) == sorted(ROW_NAMES)
    assert int(summary["completed_lbm_steps_min"]) >= 40
    assert int(summary["total_mpm_substeps_min"]) >= 200
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
        assert int(row["completed_lbm_steps"]) >= 40
        assert int(row["total_mpm_substeps"]) >= 200
        assert int(row["cycle_period_steps"]) == 40
        assert [float(value) for value in row["phase_sequence"]] == PHASE_SEQUENCE
        assert float(row["closure_phase"]) == 1.0
        assert len(row["step_records"]) == 40
        assert row["one_cycle_diagnostic_envelope"] is True
        assert row["diagnostic_only"] is True
        assert row["persist_projected_state"] is False
        assert row["persist_displaced_geometry"] is False
        assert row["persist_lbm_solid_vel"] is False
        assert row["complete_cycle_claim"] is False
        assert row["production_geometry_claim"] is False
        for step in row["step_records"]:
            assert step["row_name"] == row["row_name"]
            assert int(step["cycle_index"]) == 0
            assert int(step["step_index"]) in range(40)
            assert float(step["phase"]) in PHASE_SEQUENCE
            assert float(step["projected_mass"]) > 0.0
            assert int(step["active_cell_count"]) > 0
            assert int(step["bb_link_count"]) > 0
            assert float(step["rho_min"]) > 0.95
            assert float(step["rho_max"]) < 1.05
            assert not step["has_nan"]
            assert not step["has_inf"]

    by_name = {row["row_name"]: row for row in rows}
    assert int(by_name["original_static_32_40step"]["applied_cell_count_max"]) == 0
    assert int(by_name["runtime_geometry_only_32_40step"]["active_cell_count_delta_from_original_max"]) > 0
    assert int(by_name["wall_velocity_only_32_40step"]["applied_cell_count_max"]) > 0
    assert by_name["runtime_geometry_plus_wall_velocity_32_40step"]["runtime_geometry_projection_enabled"] is True
    assert by_name["runtime_geometry_plus_wall_velocity_32_40step"]["wall_velocity_application_enabled"] is True
    assert int(by_name["runtime_geometry_plus_wall_velocity_32_40step"]["active_cell_count_delta_from_original_max"]) > 0
    assert int(by_name["runtime_geometry_plus_wall_velocity_32_40step"]["applied_cell_count_max"]) > 0


def test_step50_one_cycle_envelope_quality_is_valid():
    summary = read_json("outputs/step50_one_cycle_envelope_quality/one_cycle_envelope_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["step_count_pass"] is True
    assert summary["stability_pass"] is True
    assert summary["projection_pass"] is True
    assert summary["wall_velocity_pass"] is True
    assert summary["combined_row_pass"] is True
    assert summary["cycle_phase_pass"] is True
    assert summary["contraction_refill_pass"] is True
    assert summary["closure_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True


def test_step50_component_effect_one_cycle_envelope_is_valid():
    payload = read_json("outputs/step50_component_effect_one_cycle_envelope/component_effect_one_cycle_envelope.json")
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


def test_step50_phase_progression_one_cycle_diagnostics_is_valid():
    payload = read_json("outputs/step50_phase_progression_one_cycle_diagnostics/phase_progression_one_cycle_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["phase_count"]) == 40
    assert [float(value) for value in summary["phase_sequence"]] == PHASE_SEQUENCE
    assert summary["phase_sequence_pass"] is True
    assert summary["runtime_geometry_phase_response_pass"] is True
    assert summary["wall_velocity_phase_response_pass"] is True
    assert summary["combined_phase_response_pass"] is True
    assert summary["phase0_to_phase035_projection_delta_nonzero"] is True
    assert summary["phase035_to_phase0975_refill_response_finite"] is True
    assert summary["phase_progression_pass"] is True
    for row in payload["rows"]:
        assert row["progression_pass"] is True
        assert math.isfinite(float(row["active_cell_count_delta_phase0_to_phase035"]))
        assert math.isfinite(float(row["active_cell_count_delta_phase035_to_phase0975"]))
        assert math.isfinite(float(row["max_applied_velocity_delta_phase0_to_phase0975"]))


def test_step50_contraction_refill_segment_diagnostics_is_valid():
    payload = read_json("outputs/step50_contraction_refill_segment_diagnostics/contraction_refill_segment_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["contraction_phase_count"]) > 0
    assert int(summary["refill_phase_count"]) > 0
    assert summary["contraction_segment_pass"] is True
    assert summary["refill_segment_pass"] is True
    assert summary["segment_pass"] is True
    assert summary["runtime_geometry_active_cell_count_bounded"] is True
    assert summary["wall_velocity_applied_cell_count_positive"] is True
    assert summary["wall_velocity_cap_pass"] is True
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0
    for row in payload["rows"]:
        assert row["contraction_segment_pass"] is True
        assert row["refill_segment_pass"] is True
        assert row["segment_pass"] is True
        assert int(row["contraction_bb_link_count_min"]) > 0
        assert int(row["refill_bb_link_count_min"]) > 0


def test_step50_cycle_closure_diagnostics_is_valid():
    payload = read_json("outputs/step50_cycle_closure_diagnostics/cycle_closure_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 4
    assert float(summary["closure_phase"]) == 1.0
    assert summary["closure_pass"] is True
    assert summary["geometry_projection_closure_pass"] is True
    assert summary["wall_velocity_closure_pass"] is True
    assert summary["cycle_proxy_closure_pass"] is True
    assert float(summary["phase0_phase1_projected_mass_delta_max"]) <= 1.0e-8
    assert int(summary["phase0_phase1_active_cell_delta_max"]) == 0
    assert float(summary["phase0_phase1_applied_velocity_delta_max"]) <= float(summary["wall_velocity_closure_tolerance"])
    assert float(summary["wall_velocity_closure_tolerance"]) <= 5.0e-4
    for row in payload["rows"]:
        assert row["closure_pass"] is True
        assert row["diagnostic_only"] is True
        assert row["persist_projected_state"] is False
        assert row["persist_displaced_geometry"] is False


def test_step50_mass_force_bounceback_one_cycle_envelope_is_valid():
    payload = read_json("outputs/step50_mass_force_bounceback_one_cycle_envelope/mass_force_bounceback_one_cycle_envelope.json")
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


def test_step50_step49_prefix_comparison_is_valid():
    payload = read_json("outputs/step50_step49_prefix_comparison/step49_prefix_comparison.json")
    summary = payload["summary"]
    assert int(summary["matched_phase_count"]) == 20
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


def test_step50_state_mutation_guard_is_valid():
    summary = read_json("outputs/step50_state_mutation_guard/state_mutation_guard.json")["summary"]
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


def test_step50_step49_regression_guard_is_valid():
    payload = read_json("outputs/step50_step49_regression_guard/step49_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 9
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step50_default_modes_remain_unchanged():
    text = read_text("src/fsi_config.py")
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step50_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/50_controlled_runtime_geometry_wall_velocity_one_cycle_coupling_diagnostic_envelope.md",
            "STEP50_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_CYCLE_COUPLING_DIAGNOSTIC_ENVELOPE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step50_artifact_budget_is_valid():
    summary = read_json("outputs/step50_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step50_total_size_mb"]) < 30.0
    assert float(summary["total_size_mb"]) < 390.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step50_vtr_count"]) == 0
    assert int(summary["step50_particle_npy_count"]) == 0
    assert int(summary["step50_displaced_particle_output_count"]) == 0
    assert int(summary["step50_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step50_report_acceptance_complete():
    report = read_text("STEP50_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_CYCLE_COUPLING_DIAGNOSTIC_ENVELOPE_REPORT.md")
    for heading in [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. One-Cycle Config Validation",
        "## 5. One-Cycle Envelope Matrix",
        "## 6. One-Cycle Envelope Quality",
        "## 7. Component Effect One-Cycle Envelope",
        "## 8. Phase Progression One-Cycle Diagnostics",
        "## 9. Contraction Refill Segment Diagnostics",
        "## 10. Cycle Closure Diagnostics",
        "## 11. Mass Force Bounce-Back One-Cycle Envelope",
        "## 12. Step 49 Prefix Comparison",
        "## 13. State Mutation Guard",
        "## 14. Step 49 Regression Guard",
        "## 15. Artifact Manifest Summary",
        "## 16. Verification Commands",
        "## 17. GitHub Sync Information",
        "## 18. Acceptance Checklist",
        "## 19. Decision For Step 51",
    ]:
        assert heading in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step50_no_persistent_geometry_outputs():
    summary = read_json("outputs/step50_artifact_manifest/artifact_summary.json")
    assert int(summary["step50_vtr_count"]) == 0
    assert int(summary["step50_particle_npy_count"]) == 0
    assert int(summary["step50_displaced_particle_output_count"]) == 0
    assert int(summary["step50_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step50_no_physical_validation_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/50_controlled_runtime_geometry_wall_velocity_one_cycle_coupling_diagnostic_envelope.md",
            "STEP50_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_ONE_CYCLE_COUPLING_DIAGNOSTIC_ENVELOPE_REPORT.md",
            "outputs/step50_one_cycle_envelope_matrix/one_cycle_envelope_matrix.json",
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
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step50_no_formula_changes():
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
        if "Step 50" in text or "runtime_geometry_wall_velocity_one_cycle" in text:
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


def _all_step50_flags_false(config):
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
