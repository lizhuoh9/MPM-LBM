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

STEP51_REQUIRED_FILES = [
    "STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_GOAL.md",
    "STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_REPORT.md",
    "docs/51_controlled_runtime_geometry_wall_velocity_transfer_comparison.md",
    "configs/step51_transfer_comparison_one_cycle_envelope.json",
    "configs/step51_engineering_original_static_32_40step.json",
    "configs/step51_engineering_runtime_geometry_only_32_40step.json",
    "configs/step51_engineering_wall_velocity_only_32_40step.json",
    "configs/step51_engineering_runtime_geometry_plus_wall_velocity_32_40step.json",
    "configs/step51_link_area_original_static_32_40step.json",
    "configs/step51_link_area_runtime_geometry_only_32_40step.json",
    "configs/step51_link_area_wall_velocity_only_32_40step.json",
    "configs/step51_link_area_runtime_geometry_plus_wall_velocity_32_40step.json",
    "src/runtime_geometry_wall_velocity_transfer_config.py",
    "src/runtime_geometry_wall_velocity_transfer_envelope.py",
    "src/runtime_geometry_wall_velocity_transfer_diagnostics.py",
    "src/runtime_geometry_wall_velocity_transfer_state_guard.py",
    "baseline_tests/step51_common.py",
    "baseline_tests/run_step51_transfer_config_validation.py",
    "baseline_tests/run_step51_transfer_comparison_matrix.py",
    "baseline_tests/run_step51_transfer_envelope_quality.py",
    "baseline_tests/run_step51_engineering_vs_link_area_comparison.py",
    "baseline_tests/run_step51_link_area_envelope.py",
    "baseline_tests/run_step51_component_effect_by_transfer.py",
    "baseline_tests/run_step51_cycle_closure_by_transfer.py",
    "baseline_tests/run_step51_step50_engineering_prefix_comparison.py",
    "baseline_tests/run_step51_mass_force_bounceback_transfer_envelope.py",
    "baseline_tests/run_step51_state_mutation_guard.py",
    "baseline_tests/run_step51_step50_regression_guard.py",
    "baseline_tests/run_step51_artifact_manifest.py",
    "tests/test_step51_one_cycle_transfer_comparison_contract.py",
]

STEP51_OUTPUT_FILES = [
    "outputs/step51_transfer_config_validation/transfer_config_validation.csv",
    "outputs/step51_transfer_config_validation/transfer_config_validation.json",
    "outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.csv",
    "outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json",
    "outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.npz",
    "outputs/step51_transfer_envelope_quality/transfer_envelope_quality.csv",
    "outputs/step51_transfer_envelope_quality/transfer_envelope_quality.json",
    "outputs/step51_engineering_vs_link_area_comparison/engineering_vs_link_area_comparison.csv",
    "outputs/step51_engineering_vs_link_area_comparison/engineering_vs_link_area_comparison.json",
    "outputs/step51_link_area_envelope/link_area_envelope.csv",
    "outputs/step51_link_area_envelope/link_area_envelope.json",
    "outputs/step51_component_effect_by_transfer/component_effect_by_transfer.csv",
    "outputs/step51_component_effect_by_transfer/component_effect_by_transfer.json",
    "outputs/step51_cycle_closure_by_transfer/cycle_closure_by_transfer.csv",
    "outputs/step51_cycle_closure_by_transfer/cycle_closure_by_transfer.json",
    "outputs/step51_step50_engineering_prefix_comparison/step50_engineering_comparison.csv",
    "outputs/step51_step50_engineering_prefix_comparison/step50_engineering_comparison.json",
    "outputs/step51_mass_force_bounceback_transfer_envelope/mass_force_bounceback_transfer_envelope.csv",
    "outputs/step51_mass_force_bounceback_transfer_envelope/mass_force_bounceback_transfer_envelope.json",
    "outputs/step51_state_mutation_guard/state_mutation_guard.csv",
    "outputs/step51_state_mutation_guard/state_mutation_guard.json",
    "outputs/step51_step50_regression_guard/step50_regression_guard.csv",
    "outputs/step51_step50_regression_guard/step50_regression_guard.json",
    "outputs/step51_artifact_manifest/artifact_manifest.csv",
    "outputs/step51_artifact_manifest/artifact_summary.csv",
    "outputs/step51_artifact_manifest/artifact_summary.json",
]

STEP51_LOG_MARKERS = {
    "logs/step51_transfer_config_validation.log": "[OK] Step 51 transfer config validation finished",
    "logs/step51_transfer_comparison_matrix.log": "[OK] Step 51 transfer comparison matrix finished",
    "logs/step51_transfer_envelope_quality.log": "[OK] Step 51 transfer envelope quality finished",
    "logs/step51_engineering_vs_link_area_comparison.log": "[OK] Step 51 engineering vs link-area comparison finished",
    "logs/step51_link_area_envelope.log": "[OK] Step 51 link-area envelope finished",
    "logs/step51_component_effect_by_transfer.log": "[OK] Step 51 component effect by transfer finished",
    "logs/step51_cycle_closure_by_transfer.log": "[OK] Step 51 cycle closure by transfer finished",
    "logs/step51_step50_engineering_prefix_comparison.log": "[OK] Step 51 Step 50 engineering prefix comparison finished",
    "logs/step51_mass_force_bounceback_transfer_envelope.log": "[OK] Step 51 mass force bounce-back transfer envelope finished",
    "logs/step51_state_mutation_guard.log": "[OK] Step 51 state mutation guard finished",
    "logs/step51_step50_regression_guard.log": "[OK] Step 51 Step 50 regression guard finished",
    "logs/step51_artifact_manifest.log": "[OK] Step 51 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 51 is controlled one-cycle runtime geometry plus wall velocity transfer comparison.",
    "Step 51 compares engineering and link_area_experimental diagnostically.",
    "Step 51 remains 32^3 and one-cycle.",
    "Step 51 remains non-persistent.",
    "Step 51 does not validate real jet propulsion.",
    "Step 51 does not implement squid swimming.",
    "Step 51 does not change moving bounce-back formulas.",
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
    "link_area is physically validated",
    "link_area is superior",
]

ROW_NAMES = [
    "engineering_original_static_32_40step",
    "engineering_runtime_geometry_only_32_40step",
    "engineering_wall_velocity_only_32_40step",
    "engineering_runtime_geometry_plus_wall_velocity_32_40step",
    "link_area_original_static_32_40step",
    "link_area_runtime_geometry_only_32_40step",
    "link_area_wall_velocity_only_32_40step",
    "link_area_runtime_geometry_plus_wall_velocity_32_40step",
]


def test_step51_required_artifacts_exist():
    missing = [path for path in STEP51_REQUIRED_FILES + STEP51_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP51_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step51_transfer_config_is_valid():
    config = read_json("configs/step51_transfer_comparison_one_cycle_envelope.json")
    assert config["transfer_comparison_id"] == "step51_runtime_geometry_wall_velocity_transfer_comparison"
    assert config["base_step50_config_path"] == "configs/step50_runtime_geometry_wall_velocity_one_cycle_envelope.json"
    assert int(config["n_grid"]) == 32
    assert int(config["n_lbm_steps"]) == 40
    assert int(config["mpm_substeps_per_lbm_step"]) == 5
    assert int(config["cycle_period_steps"]) == 40
    assert [float(value) for value in config["phase_sequence"]] == PHASE_SEQUENCE
    assert float(config["closure_phase"]) == 1.0
    assert config["transfer_modes"] == ["engineering", "link_area_experimental"]
    assert config["coupling_mode"] == "moving_boundary"
    assert config["link_area_policy"] == "inverse_length"
    assert float(config["link_area_scale_min"]) == 0.25
    assert float(config["link_area_scale_max"]) == 2.0
    assert config["diagnostic_only"] is True
    assert _all_step51_flags_false(config)

    for descriptor_path in [
        path for path in STEP51_REQUIRED_FILES if path.startswith("configs/step51_") and path != "configs/step51_transfer_comparison_one_cycle_envelope.json"
    ]:
        descriptor = read_json(descriptor_path)
        assert int(descriptor["n_grid"]) == 32
        assert int(descriptor["n_lbm_steps"]) == 40
        assert int(descriptor["mpm_substeps_per_lbm_step"]) == 5
        assert int(descriptor["cycle_period_steps"]) == 40
        assert [float(value) for value in descriptor["phase_sequence"]] == PHASE_SEQUENCE
        assert float(descriptor["closure_phase"]) == 1.0
        assert descriptor["reaction_transfer_mode"] in {"engineering", "link_area_experimental"}

    summary = read_json("outputs/step51_transfer_config_validation/transfer_config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["n_grid"]) == 32
    assert int(summary["n_lbm_steps"]) == 40
    assert int(summary["mpm_substeps_per_lbm_step"]) == 5
    assert int(summary["cycle_period_steps"]) == 40
    assert int(summary["phase_count"]) == 40
    assert [float(value) for value in summary["phase_sequence"]] == PHASE_SEQUENCE
    assert summary["engineering_transfer_mode_exists"] is True
    assert summary["link_area_transfer_mode_exists"] is True
    assert summary["no_48_grid"] is True
    assert summary["no_64_grid"] is True
    assert summary["no_multi_cycle"] is True
    assert summary["all_mutation_flags_false"] is True


def test_step51_transfer_comparison_matrix_is_valid():
    payload = read_json("outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert int(summary["row_count"]) == 8
    assert int(summary["engineering_row_count"]) == 4
    assert int(summary["link_area_row_count"]) == 4
    assert int(summary["stable_count"]) == 8
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
        assert [float(value) for value in row["phase_sequence"]] == PHASE_SEQUENCE
        assert len(row["step_records"]) == 40
        assert row["one_cycle_diagnostic_envelope"] is True
        assert row["diagnostic_only"] is True
        assert row["persist_projected_state"] is False
        assert row["persist_displaced_geometry"] is False
        assert row["persist_lbm_solid_vel"] is False
        assert row["complete_cycle_claim"] is False
        assert row["production_geometry_claim"] is False
        assert 0.25 <= float(row["area_scale_min_observed"]) <= 2.0
        assert 0.25 <= float(row["area_scale_max_observed"]) <= 2.0
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
            assert 0.25 <= float(step["area_scale"]) <= 2.0
            assert not step["has_nan"]
            assert not step["has_inf"]


def test_step51_transfer_envelope_quality_is_valid():
    summary = read_json("outputs/step51_transfer_envelope_quality/transfer_envelope_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["step_count_pass"] is True
    assert summary["stability_pass"] is True
    assert summary["projection_pass"] is True
    assert summary["wall_velocity_pass"] is True
    assert summary["transfer_mode_pass"] is True
    assert summary["link_area_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True


def test_step51_engineering_vs_link_area_comparison_is_valid():
    payload = read_json("outputs/step51_engineering_vs_link_area_comparison/engineering_vs_link_area_comparison.json")
    summary = payload["summary"]
    assert int(summary["comparison_count"]) == 4
    assert summary["comparison_pass"] is True
    assert summary["both_transfer_modes_stable"] is True
    for row in payload["rows"]:
        assert row["comparison_pass"] is True
        assert row["both_transfer_modes_stable"] is True
        assert math.isfinite(float(row["projected_mass_delta_max_abs"]))
        assert math.isfinite(float(row["active_cell_count_delta_max_abs"]))
        assert math.isfinite(float(row["bb_link_count_delta_max_abs"]))
        assert math.isfinite(float(row["hydro_force_delta_max_abs"]))


def test_step51_link_area_envelope_is_valid():
    payload = read_json("outputs/step51_link_area_envelope/link_area_envelope.json")
    summary = payload["summary"]
    assert int(summary["link_area_row_count"]) == 4
    assert summary["area_scale_finite_pass"] is True
    assert float(summary["area_scale_min_observed"]) >= 0.25
    assert float(summary["area_scale_max_observed"]) <= 2.0
    assert summary["link_area_envelope_pass"] is True
    for row in payload["rows"]:
        assert row["link_area_row_pass"] is True
        assert 0.25 <= float(row["area_scale_final"]) <= 2.0


def test_step51_component_effect_by_transfer_is_valid():
    payload = read_json("outputs/step51_component_effect_by_transfer/component_effect_by_transfer.json")
    summary = payload["summary"]
    assert int(summary["transfer_mode_count"]) == 2
    assert int(summary["comparison_count"]) >= 10
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


def test_step51_cycle_closure_by_transfer_is_valid():
    payload = read_json("outputs/step51_cycle_closure_by_transfer/cycle_closure_by_transfer.json")
    summary = payload["summary"]
    assert int(summary["transfer_mode_count"]) == 2
    assert summary["closure_pass"] is True
    assert summary["engineering_closure_pass"] is True
    assert summary["link_area_closure_pass"] is True
    assert summary["geometry_projection_closure_pass"] is True
    assert summary["wall_velocity_closure_pass"] is True
    assert summary["cycle_proxy_closure_pass"] is True
    assert float(summary["phase0_phase1_projected_mass_delta_max"]) <= 1.0e-8
    assert int(summary["phase0_phase1_active_cell_delta_max"]) == 0
    assert float(summary["phase0_phase1_applied_velocity_delta_max"]) <= float(summary["wall_velocity_closure_tolerance"])


def test_step51_step50_engineering_prefix_comparison_is_valid():
    payload = read_json("outputs/step51_step50_engineering_prefix_comparison/step50_engineering_comparison.json")
    summary = payload["summary"]
    assert int(summary["engineering_row_pair_count"]) == 4
    assert int(summary["matched_phase_count"]) == 40
    assert [float(value) for value in summary["matched_phases"]] == PHASE_SEQUENCE
    assert summary["comparison_pass"] is True
    assert float(summary["max_projected_mass_delta"]) <= 1.0e-8
    assert float(summary["max_active_cell_count_delta"]) == 0.0
    assert float(summary["max_applied_velocity_delta"]) <= 1.0e-8


def test_step51_mass_force_bounceback_transfer_envelope_is_valid():
    payload = read_json("outputs/step51_mass_force_bounceback_transfer_envelope/mass_force_bounceback_transfer_envelope.json")
    summary = payload["summary"]
    assert int(summary["row_count"]) == 8
    assert summary["envelope_pass"] is True
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert math.isfinite(float(summary["bb_max_correction_global"]))
    assert int(summary["bb_link_count_min"]) > 0
    assert math.isfinite(float(summary["hydro_force_max_norm_global"]))
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0


def test_step51_state_mutation_guard_is_valid():
    summary = read_json("outputs/step51_state_mutation_guard/state_mutation_guard.json")["summary"]
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


def test_step51_step50_regression_guard_is_valid():
    payload = read_json("outputs/step51_step50_regression_guard/step50_regression_guard.json")
    summary = payload["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) >= 9
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert all(row["pass"] is True for row in payload["rows"])


def test_step51_default_modes_remain_unchanged():
    text = read_text("src/fsi_config.py")
    assert 'geometry_motion_mode: str = "static"' in text
    assert 'geometry_motion_application_mode: str = "disabled"' in text
    assert 'boundary_motion_mode: str = "static"' in text
    assert 'wall_velocity_application_mode: str = "disabled"' in text
    assert "quality_check_enabled: bool = False" in text
    assert "quality_check_strict: bool = False" in text
    assert 'reaction_transfer_mode: str = "engineering"' in text


def test_step51_docs_scope_and_forbidden_claims_are_valid():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/51_controlled_runtime_geometry_wall_velocity_transfer_comparison.md",
            "STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_REPORT.md",
        ]
    )
    missing = [phrase for phrase in REQUIRED_SCOPE if phrase not in combined]
    assert missing == []
    offenders = [claim for claim in FORBIDDEN_CLAIMS if claim in combined]
    assert offenders == []


def test_step51_artifact_budget_is_valid():
    summary = read_json("outputs/step51_artifact_manifest/artifact_summary.json")
    assert int(summary["large_file_count"]) == 0
    assert float(summary["step51_total_size_mb"]) < 40.0
    assert float(summary["total_size_mb"]) < 400.0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["step51_vtr_count"]) == 0
    assert int(summary["step51_particle_npy_count"]) == 0
    assert int(summary["step51_displaced_particle_output_count"]) == 0
    assert int(summary["step51_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step51_report_acceptance_complete():
    report = read_text("STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_REPORT.md")
    for heading in [
        "## 1. Goal",
        "## 2. Files Created And Updated",
        "## 3. Explicit Non-Goals",
        "## 4. Transfer Config Validation",
        "## 5. Transfer Comparison Matrix",
        "## 6. Transfer Envelope Quality",
        "## 7. Engineering Vs Link-Area Comparison",
        "## 8. Link-Area Envelope",
        "## 9. Component Effect By Transfer",
        "## 10. Cycle Closure By Transfer",
        "## 11. Step 50 Engineering Prefix Comparison",
        "## 12. Mass Force Bounce-Back Transfer Envelope",
        "## 13. State Mutation Guard",
        "## 14. Step 50 Regression Guard",
        "## 15. Artifact Manifest Summary",
        "## 16. Verification Commands",
        "## 17. GitHub Sync Information",
        "## 18. Acceptance Checklist",
        "## 19. Decision For Step 52",
    ]:
        assert heading in report
    unchecked = [line for line in report.splitlines() if line.startswith("- [ ]")]
    assert unchecked == []


def test_step51_no_persistent_geometry_outputs():
    summary = read_json("outputs/step51_artifact_manifest/artifact_summary.json")
    assert int(summary["step51_vtr_count"]) == 0
    assert int(summary["step51_particle_npy_count"]) == 0
    assert int(summary["step51_displaced_particle_output_count"]) == 0
    assert int(summary["step51_dense_displacement_output_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step51_no_physical_validation_claims():
    combined = "\n".join(
        read_text(path)
        for path in [
            "docs/51_controlled_runtime_geometry_wall_velocity_transfer_comparison.md",
            "STEP51_CONTROLLED_RUNTIME_GEOMETRY_WALL_VELOCITY_TRANSFER_COMPARISON_REPORT.md",
            "outputs/step51_transfer_comparison_matrix/transfer_comparison_matrix.json",
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


def test_step51_no_formula_changes():
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
        if "Step 51" in text or "runtime_geometry_wall_velocity_transfer" in text:
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


def _all_step51_flags_false(config):
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
