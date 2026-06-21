import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PHASE_SEQUENCE = [0.0, 0.05, 0.1, 0.2, 0.35]

STEP47_REQUIRED_FILES = [
    "STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_GOAL.md",
    "STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_REPORT.md",
    "docs/47_controlled_runtime_geometry_wall_velocity_short_step_coupling_envelope.md",
    "configs/step47_runtime_geometry_wall_velocity_short_step_envelope.json",
    "configs/step47_original_static_32_5step.json",
    "configs/step47_runtime_geometry_only_32_5step.json",
    "configs/step47_wall_velocity_only_32_5step.json",
    "configs/step47_runtime_geometry_plus_wall_velocity_32_5step.json",
    "src/runtime_geometry_wall_velocity_envelope_config.py",
    "src/runtime_geometry_wall_velocity_envelope.py",
    "src/runtime_geometry_wall_velocity_envelope_diagnostics.py",
    "src/runtime_geometry_wall_velocity_envelope_state_guard.py",
    "baseline_tests/step47_common.py",
    "baseline_tests/run_step47_short_step_config_validation.py",
    "baseline_tests/run_step47_short_step_envelope_matrix.py",
    "baseline_tests/run_step47_short_step_envelope_quality.py",
    "baseline_tests/run_step47_component_effect_envelope.py",
    "baseline_tests/run_step47_phase_progression_diagnostics.py",
    "baseline_tests/run_step47_mass_force_bounceback_envelope.py",
    "baseline_tests/run_step47_state_mutation_guard.py",
    "baseline_tests/run_step47_step46_regression_guard.py",
    "baseline_tests/run_step47_artifact_manifest.py",
    "tests/test_step47_runtime_geometry_wall_velocity_short_step_envelope_contract.py",
]

STEP47_OUTPUT_FILES = [
    "outputs/step47_short_step_config_validation/short_step_config_validation.csv",
    "outputs/step47_short_step_config_validation/short_step_config_validation.json",
    "outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.csv",
    "outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.json",
    "outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.npz",
    "outputs/step47_short_step_envelope_quality/short_step_envelope_quality.csv",
    "outputs/step47_short_step_envelope_quality/short_step_envelope_quality.json",
    "outputs/step47_component_effect_envelope/component_effect_envelope.csv",
    "outputs/step47_component_effect_envelope/component_effect_envelope.json",
    "outputs/step47_phase_progression_diagnostics/phase_progression_diagnostics.csv",
    "outputs/step47_phase_progression_diagnostics/phase_progression_diagnostics.json",
    "outputs/step47_mass_force_bounceback_envelope/mass_force_bounceback_envelope.csv",
    "outputs/step47_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json",
    "outputs/step47_state_mutation_guard/state_mutation_guard.csv",
    "outputs/step47_state_mutation_guard/state_mutation_guard.json",
    "outputs/step47_step46_regression_guard/step46_regression_guard.csv",
    "outputs/step47_step46_regression_guard/step46_regression_guard.json",
    "outputs/step47_artifact_manifest/artifact_manifest.csv",
    "outputs/step47_artifact_manifest/artifact_summary.csv",
    "outputs/step47_artifact_manifest/artifact_summary.json",
]

STEP47_LOG_MARKERS = {
    "logs/step47_short_step_config_validation.log": "[OK] Step 47 short-step config validation finished",
    "logs/step47_short_step_envelope_matrix.log": "[OK] Step 47 short-step envelope matrix finished",
    "logs/step47_short_step_envelope_quality.log": "[OK] Step 47 short-step envelope quality finished",
    "logs/step47_component_effect_envelope.log": "[OK] Step 47 component effect envelope finished",
    "logs/step47_phase_progression_diagnostics.log": "[OK] Step 47 phase progression diagnostics finished",
    "logs/step47_mass_force_bounceback_envelope.log": "[OK] Step 47 mass force bounce-back envelope finished",
    "logs/step47_state_mutation_guard.log": "[OK] Step 47 state mutation guard finished",
    "logs/step47_step46_regression_guard.log": "[OK] Step 47 Step 46 regression guard finished",
    "logs/step47_artifact_manifest.log": "[OK] Step 47 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 47 is controlled runtime geometry plus wall velocity short-step coupling envelope.",
    "Step 47 is opt-in and engineering-only.",
    "Step 47 runs a 32^3 five-step envelope.",
    "Step 47 does not run a full-cycle moving-geometry simulation.",
    "Step 47 does not persist displaced geometry.",
    "Step 47 does not persist projected state.",
    "Step 47 does not change moving bounce-back formulas.",
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
    "original_static_32_5step",
    "runtime_geometry_only_32_5step",
    "wall_velocity_only_32_5step",
    "runtime_geometry_plus_wall_velocity_32_5step",
]


def test_step47_required_artifacts_exist():
    missing = [path for path in STEP47_REQUIRED_FILES + STEP47_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP47_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step47_short_step_config_is_valid():
    config = read_json("configs/step47_runtime_geometry_wall_velocity_short_step_envelope.json")
    assert config["short_step_envelope_id"] == "step47_runtime_geometry_wall_velocity_short_step_envelope"
    assert config["base_coupling_smoke_config_path"] == "configs/step46_runtime_geometry_wall_velocity_coupling_smoke.json"
    assert config["runtime_projection_config_path"] == "configs/step45_runtime_geometry_projection_integration.json"
    assert config["wall_velocity_application_config_path"] == "configs/step41_wall_velocity_application_scale_0050_64.json"
    assert int(config["n_grid"]) == 32
    assert int(config["n_lbm_steps"]) == 5
    assert int(config["mpm_substeps_per_lbm_step"]) == 5
    assert [float(value) for value in config["phase_sequence"]] == PHASE_SEQUENCE
    assert config["coupling_mode"] == "moving_boundary"
    assert config["reaction_transfer_mode"] == "engineering"
    assert config["enable_runtime_geometry_projection"] is True
    assert config["enable_wall_velocity_application"] is True
    assert _all_step47_flags_false(config)
    assert config["diagnostic_only"] is True

    for descriptor_path in [
        "configs/step47_original_static_32_5step.json",
        "configs/step47_runtime_geometry_only_32_5step.json",
        "configs/step47_wall_velocity_only_32_5step.json",
        "configs/step47_runtime_geometry_plus_wall_velocity_32_5step.json",
    ]:
        descriptor = read_json(descriptor_path)
        assert int(descriptor["n_grid"]) == 32
        assert int(descriptor["n_lbm_steps"]) == 5
        assert int(descriptor["mpm_substeps_per_lbm_step"]) == 5
        assert [float(value) for value in descriptor["phase_sequence"]] == PHASE_SEQUENCE
        assert descriptor["reaction_transfer_mode"] == "engineering"
        assert "link_area" not in json.dumps(descriptor)

    summary = read_json("outputs/step47_short_step_config_validation/short_step_config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["n_grid"]) == 32
    assert int(summary["n_lbm_steps"]) == 5
    assert int(summary["mpm_substeps_per_lbm_step"]) == 5
    assert [float(value) for value in summary["phase_sequence"]] == PHASE_SEQUENCE
    assert summary["all_mutation_flags_false"] is True


def test_step47_short_step_envelope_matrix_is_valid():
    payload = read_json("outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 4
    assert int(summary["stable_count"]) == 4
    assert int(summary["step_count_per_row"]) == 5
    assert int(summary["original_static_row_count"]) == 1
    assert int(summary["geometry_only_row_count"]) == 1
    assert int(summary["wall_velocity_only_row_count"]) == 1
    assert int(summary["combined_row_count"]) == 1
    assert summary["matrix_pass"] is True
    assert sorted(row["row_name"] for row in rows) == sorted(ROW_NAMES)
    assert int(summary["completed_lbm_steps_min"]) >= 5
    assert int(summary["total_mpm_substeps_min"]) >= 25
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
        assert int(row["completed_lbm_steps"]) >= 5
        assert int(row["total_mpm_substeps"]) >= 25
        assert [float(value) for value in row["phase_sequence"]] == PHASE_SEQUENCE
        assert len(row["step_records"]) == 5
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
            assert int(step["step_index"]) in range(5)
            assert float(step["phase"]) in PHASE_SEQUENCE
            assert float(step["projected_mass"]) > 0.0
            assert int(step["active_cell_count"]) > 0
            assert int(step["bb_link_count"]) > 0
            assert float(step["rho_min"]) > 0.95
            assert float(step["rho_max"]) < 1.05
            assert not step["has_nan"]
            assert not step["has_inf"]

    by_name = {row["row_name"]: row for row in rows}
    assert by_name["original_static_32_5step"]["runtime_geometry_projection_enabled"] is False
    assert by_name["original_static_32_5step"]["wall_velocity_application_enabled"] is False
    assert int(by_name["original_static_32_5step"]["applied_cell_count_max"]) == 0
    assert by_name["runtime_geometry_only_32_5step"]["runtime_geometry_projection_enabled"] is True
    assert by_name["runtime_geometry_only_32_5step"]["wall_velocity_application_enabled"] is False
    assert int(by_name["runtime_geometry_only_32_5step"]["active_cell_count_delta_from_original_max"]) > 0
    assert by_name["wall_velocity_only_32_5step"]["runtime_geometry_projection_enabled"] is False
    assert by_name["wall_velocity_only_32_5step"]["wall_velocity_application_enabled"] is True
    assert int(by_name["wall_velocity_only_32_5step"]["applied_cell_count_max"]) > 0
    assert by_name["runtime_geometry_plus_wall_velocity_32_5step"]["runtime_geometry_projection_enabled"] is True
    assert by_name["runtime_geometry_plus_wall_velocity_32_5step"]["wall_velocity_application_enabled"] is True
    assert int(by_name["runtime_geometry_plus_wall_velocity_32_5step"]["applied_cell_count_max"]) > 0
    assert int(by_name["runtime_geometry_plus_wall_velocity_32_5step"]["active_cell_count_delta_from_original_max"]) > 0


def test_step47_short_step_envelope_quality_is_valid():
    summary = read_json("outputs/step47_short_step_envelope_quality/short_step_envelope_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["step_count_pass"] is True
    assert summary["stability_pass"] is True
    assert summary["projection_pass"] is True
    assert summary["wall_velocity_pass"] is True
    assert summary["combined_row_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True


def test_step47_component_effect_envelope_is_valid():
    payload = read_json("outputs/step47_component_effect_envelope/component_effect_envelope.json")
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


def test_step47_phase_progression_diagnostics_is_valid():
    payload = read_json("outputs/step47_phase_progression_diagnostics/phase_progression_diagnostics.json")
    summary = payload["summary"]
    assert int(summary["phase_count"]) == 5
    assert [float(value) for value in summary["phase_sequence"]] == PHASE_SEQUENCE
    assert summary["phase_sequence_pass"] is True
    assert summary["runtime_geometry_phase_response_pass"] is True
    assert summary["wall_velocity_phase_response_pass"] is True
    assert summary["combined_phase_response_pass"] is True
    assert summary["phase0_to_phase035_projection_delta_nonzero"] is True
    assert summary["phase0_to_phase035_wall_velocity_delta_finite"] is True
    assert summary["phase_progression_pass"] is True
    for row in payload["rows"]:
        assert row["progression_pass"] is True
        assert math.isfinite(float(row["active_cell_count_delta_phase0_to_phase035"]))
        assert math.isfinite(float(row["max_applied_velocity_delta_phase0_to_phase035"]))


def test_step47_mass_force_bounceback_envelope_is_valid():
    payload = read_json("outputs/step47_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json")
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


def test_step47_state_mutation_guard_is_valid():
    summary = read_json("outputs/step47_state_mutation_guard/state_mutation_guard.json")["summary"]
    assert summary["guard_pass"] is True
    assert summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
    assert summary["region_mask_hash_before"] == summary["region_mask_hash_after"]
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


def test_step47_step46_regression_guard_is_valid():
    payload = read_json("outputs/step47_step46_regression_guard/step46_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 8
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step47_default_modes_remain_unchanged():
    text = read_text("src/mpm_lbm/sim/drivers/fsi_config.py")
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step47_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/47_controlled_runtime_geometry_wall_velocity_short_step_coupling_envelope.md",
            "STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step47_artifact_budget_is_valid():
    summary = read_json("outputs/step47_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step47_total_size_mb"]) < 15.0
    assert float(summary["total_size_mb"]) < 360.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step47_vtr_count"]) == 0
    assert int(summary["step47_particle_npy_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step47_report_acceptance_complete():
    report = read_text("STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_REPORT.md")
    assert "## 15. Acceptance Checklist" in report
    assert "## 16. Decision For Step 48" in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step47_no_persistent_geometry_outputs():
    summary = read_json("outputs/step47_artifact_manifest/artifact_summary.json")
    assert int(summary["step47_vtr_count"]) == 0
    assert int(summary["step47_particle_npy_count"]) == 0
    assert int(summary["step47_displaced_particle_output_count"]) == 0
    assert int(summary["step47_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step47_no_full_cycle_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/47_controlled_runtime_geometry_wall_velocity_short_step_coupling_envelope.md",
            "STEP47_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_SHORT_STEP_COUPLING_ENVELOPE_REPORT.md",
            "outputs/step47_short_step_envelope_matrix/short_step_envelope_matrix.json",
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


def test_step47_no_formula_changes():
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
        if "Step 47" in text or "runtime_geometry_wall_velocity_envelope" in text:
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


def _all_step47_flags_false(config):
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
