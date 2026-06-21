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

ROW_NAMES = [
    "engineering_static_48_40step",
    "engineering_runtime_geometry_plus_wall_velocity_48_40step",
]

STEP52_REQUIRED_FILES = [
    "STEP52_CONTROLLED_48_ENGINEERING_ONE_CYCLE_FEASIBILITY_GOAL.md",
    "STEP52_CONTROLLED_48_ENGINEERING_ONE_CYCLE_FEASIBILITY_REPORT.md",
    "docs/52_controlled_48_engineering_one_cycle_feasibility.md",
    "configs/step52_48_engineering_one_cycle_feasibility.json",
    "configs/step52_engineering_static_48_40step.json",
    "configs/step52_engineering_runtime_geometry_plus_wall_velocity_48_40step.json",
    "configs/step52_step51_reference_summary.json",
    "src/runtime_geometry_wall_velocity_48_feasibility_config.py",
    "src/runtime_geometry_wall_velocity_48_feasibility_envelope.py",
    "src/runtime_geometry_wall_velocity_48_feasibility_diagnostics.py",
    "src/runtime_geometry_wall_velocity_48_feasibility_state_guard.py",
    "baseline_tests/step52_common.py",
    "baseline_tests/run_step52_48_config_validation.py",
    "baseline_tests/run_step52_48_feasibility_matrix.py",
    "baseline_tests/run_step52_48_feasibility_quality.py",
    "baseline_tests/run_step52_48_vs_step51_engineering_scaling_comparison.py",
    "baseline_tests/run_step52_cycle_closure.py",
    "baseline_tests/run_step52_mass_force_bounceback_envelope.py",
    "baseline_tests/run_step52_state_mutation_guard.py",
    "baseline_tests/run_step52_step51_regression_guard.py",
    "baseline_tests/run_step52_artifact_manifest.py",
    "tests/test_step52_48_engineering_one_cycle_feasibility_contract.py",
]

STEP52_OUTPUT_FILES = [
    "outputs/step52_48_config_validation/config_validation.csv",
    "outputs/step52_48_config_validation/config_validation.json",
    "outputs/step52_48_config_validation/config_summary.csv",
    "outputs/step52_48_feasibility_matrix/feasibility_matrix.csv",
    "outputs/step52_48_feasibility_matrix/feasibility_matrix.json",
    "outputs/step52_48_feasibility_matrix/feasibility_matrix.npz",
    "outputs/step52_48_feasibility_quality/feasibility_quality.csv",
    "outputs/step52_48_feasibility_quality/feasibility_quality.json",
    "outputs/step52_48_vs_step51_engineering_scaling_comparison/scaling_comparison.csv",
    "outputs/step52_48_vs_step51_engineering_scaling_comparison/scaling_comparison.json",
    "outputs/step52_cycle_closure/cycle_closure.csv",
    "outputs/step52_cycle_closure/cycle_closure.json",
    "outputs/step52_mass_force_bounceback_envelope/mass_force_bounceback_envelope.csv",
    "outputs/step52_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json",
    "outputs/step52_state_mutation_guard/state_mutation_guard.csv",
    "outputs/step52_state_mutation_guard/state_mutation_guard.json",
    "outputs/step52_step51_regression_guard/step51_regression_guard.csv",
    "outputs/step52_step51_regression_guard/step51_regression_guard.json",
    "outputs/step52_artifact_manifest/artifact_manifest.csv",
    "outputs/step52_artifact_manifest/artifact_summary.csv",
    "outputs/step52_artifact_manifest/artifact_summary.json",
]

STEP52_LOG_MARKERS = {
    "logs/step52_48_config_validation.log": "[OK] Step 52 48 config validation finished",
    "logs/step52_48_feasibility_matrix.log": "[OK] Step 52 48 feasibility matrix finished",
    "logs/step52_48_feasibility_quality.log": "[OK] Step 52 48 feasibility quality finished",
    "logs/step52_48_vs_step51_engineering_scaling_comparison.log": "[OK] Step 52 48 vs Step 51 engineering scaling comparison finished",
    "logs/step52_cycle_closure.log": "[OK] Step 52 cycle closure finished",
    "logs/step52_mass_force_bounceback_envelope.log": "[OK] Step 52 mass force bounce-back envelope finished",
    "logs/step52_state_mutation_guard.log": "[OK] Step 52 state mutation guard finished",
    "logs/step52_step51_regression_guard.log": "[OK] Step 52 Step 51 regression guard finished",
    "logs/step52_artifact_manifest.log": "[OK] Step 52 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 52 is a controlled 48^3 engineering one-cycle diagnostic feasibility probe.",
    "Step 52 runs exactly two engineering rows: static and runtime geometry plus wall velocity.",
    "Step 52 remains diagnostic-only and non-persistent.",
    "Step 52 does not validate real jet propulsion.",
    "Step 52 does not implement squid swimming.",
    "Step 52 does not change moving bounce-back formulas.",
    "Step 52 is not grid convergence validation.",
    "The default geometry_motion_mode remains static.",
    "The default geometry_motion_application_mode remains disabled.",
    "The default boundary_motion_mode remains static.",
    "The default wall_velocity_application_mode remains disabled.",
]

FORBIDDEN_CLAIMS = [
    "jet propulsion is validated",
    "real squid simulation is validated",
    "squid swimming is implemented",
    "free-body motion is implemented",
    "production moving geometry is implemented",
    "production-ready solver",
    "grid convergence is validated",
    "48^3 physical validation",
    "moving bounce-back formula is changed",
    "external solver was changed",
]


def test_step52_required_artifacts_exist():
    missing = [path for path in STEP52_REQUIRED_FILES + STEP52_OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in STEP52_LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step52_config_is_narrow_and_non_persistent():
    config = read_json("configs/step52_48_engineering_one_cycle_feasibility.json")
    assert config["feasibility_id"] == "step52_controlled_48_engineering_one_cycle_feasibility"
    assert config["base_step51_config_path"] == "configs/step51_transfer_comparison_one_cycle_envelope.json"
    assert int(config["n_grid"]) == 48
    assert int(config["n_lbm_steps"]) == 40
    assert int(config["mpm_substeps_per_lbm_step"]) == 5
    assert int(config["cycle_period_steps"]) == 40
    assert float(config["closure_phase"]) == 1.0
    assert [float(value) for value in config["phase_sequence"]] == PHASE_SEQUENCE
    assert config["transfer_mode"] == "engineering"
    assert config["coupling_mode"] == "moving_boundary"
    assert config["diagnostic_only"] is True
    assert _all_step52_flags_false(config)

    descriptors = [
        read_json("configs/step52_engineering_static_48_40step.json"),
        read_json("configs/step52_engineering_runtime_geometry_plus_wall_velocity_48_40step.json"),
    ]
    assert [descriptor["row_name"] for descriptor in descriptors] == ROW_NAMES
    for descriptor in descriptors:
        assert int(descriptor["n_grid"]) == 48
        assert int(descriptor["n_lbm_steps"]) == 40
        assert int(descriptor["mpm_substeps_per_lbm_step"]) == 5
        assert int(descriptor["cycle_period_steps"]) == 40
        assert [float(value) for value in descriptor["phase_sequence"]] == PHASE_SEQUENCE
        assert descriptor["reaction_transfer_mode"] == "engineering"
        assert descriptor["target_u_lbm"] == [0.0, 0.0, 0.0]
        assert descriptor["quality_check_enabled"] is True
        assert descriptor["quality_check_strict"] is True
        assert descriptor["diagnostic_only"] is True
        assert descriptor["write_vtk"] is False
        assert descriptor["write_particles"] is False
        assert descriptor["complete_cycle_claim"] is False
        assert descriptor["production_geometry_claim"] is False

    summary = read_json("outputs/step52_48_config_validation/config_validation.json")["summary"]
    assert summary["validation_pass"] is True
    assert int(summary["pass_count"]) == int(summary["row_count"])
    assert int(summary["n_grid"]) == 48
    assert int(summary["phase_count"]) == 40
    assert summary["phase_starts_at_0"] is True
    assert summary["phase_ends_at_0975"] is True
    assert summary["no_link_area_experimental_row"] is True
    assert summary["no_64_grid"] is True
    assert summary["no_multi_cycle"] is True
    assert summary["all_mutation_flags_false"] is True
    assert summary["modify_moving_bounceback_formula"] is False


def test_step52_feasibility_matrix_is_valid():
    payload = read_json("outputs/step52_48_feasibility_matrix/feasibility_matrix.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert summary["matrix_pass"] is True
    assert int(summary["row_count"]) == 2
    assert int(summary["static_row_count"]) == 1
    assert int(summary["combined_row_count"]) == 1
    assert int(summary["stable_count"]) == 2
    assert int(summary["step_count_per_row"]) == 40
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
    assert sorted(row["row_name"] for row in rows) == sorted(ROW_NAMES)

    for row in rows:
        assert int(row["n_grid"]) == 48
        assert row["reaction_transfer_mode"] == "engineering"
        assert row["stable"] is True
        assert row["diagnostic_only"] is True
        assert row["persist_projected_state"] is False
        assert row["persist_displaced_geometry"] is False
        assert row["persist_lbm_solid_vel"] is False
        assert row["complete_cycle_claim"] is False
        assert row["production_geometry_claim"] is False
        assert len(row["step_records"]) == 40
        for step in row["step_records"]:
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


def test_step52_quality_and_static_combined_effects_pass():
    summary = read_json("outputs/step52_48_feasibility_quality/feasibility_quality.json")["summary"]
    assert summary["quality_pass"] is True
    assert summary["row_count_pass"] is True
    assert summary["static_row_pass"] is True
    assert summary["combined_row_pass"] is True
    assert summary["step_count_pass"] is True
    assert summary["stability_pass"] is True
    assert summary["projection_pass"] is True
    assert summary["transfer_mode_pass"] is True
    assert summary["component_effect_pass"] is True
    assert summary["diagnostic_only_pass"] is True
    assert summary["no_persistent_state_pass"] is True


def test_step52_48_vs_step51_scaling_is_honest_and_finite():
    payload = read_json("outputs/step52_48_vs_step51_engineering_scaling_comparison/scaling_comparison.json")
    summary = payload["summary"]
    row = payload["rows"][0]
    assert summary["scaling_pass"] is True
    assert summary["all_ratios_finite"] is True
    assert summary["diagnostic_scaling_only"] is True
    assert summary["grid_convergence_claim"] is False
    assert summary["physical_validation_claim"] is False
    assert summary["active_cell_count_non_decreasing"] is True
    assert "active_cell_count_growth_observed" in summary
    assert summary["applied_cell_count_growth_observed"] is True
    assert int(row["active_cell_count_48"]) >= int(row["active_cell_count_32"])
    assert int(row["applied_cell_count_48"]) > int(row["applied_cell_count_32"])
    assert float(summary["applied_cell_count_ratio_48_vs_32"]) > 1.0
    assert finite_values(row)


def test_step52_cycle_closure_passes():
    payload = read_json("outputs/step52_cycle_closure/cycle_closure.json")
    summary = payload["summary"]
    assert summary["closure_pass"] is True
    assert int(summary["row_count"]) == 2
    assert int(summary["closure_pass_count"]) == 2
    assert summary["static_closure_pass"] is True
    assert summary["combined_closure_pass"] is True
    assert summary["geometry_projection_closure_pass"] is True
    assert summary["wall_velocity_closure_pass"] is True
    assert summary["cycle_proxy_closure_pass"] is True
    assert float(summary["phase0_phase1_projected_mass_delta_max"]) <= 1.0e-8
    assert int(summary["phase0_phase1_active_cell_delta_max"]) <= 0
    assert float(summary["phase0_phase1_applied_velocity_delta_max"]) <= float(summary["wall_velocity_closure_tolerance"])


def test_step52_mass_force_bounceback_envelope_passes():
    payload = read_json("outputs/step52_mass_force_bounceback_envelope/mass_force_bounceback_envelope.json")
    summary = payload["summary"]
    assert summary["envelope_pass"] is True
    assert int(summary["row_count"]) == 2
    assert int(summary["envelope_pass_count"]) == 2
    assert float(summary["rho_min_global"]) > 0.95
    assert float(summary["rho_max_global"]) < 1.05
    assert int(summary["bb_link_count_min"]) > 0
    assert float(summary["bb_max_correction_global"]) < 0.1
    assert math.isfinite(float(summary["hydro_force_max_norm_global"]))
    assert math.isfinite(float(summary["impulse_proxy_max_norm_global"]))
    assert int(summary["has_nan_count"]) == 0
    assert int(summary["has_inf_count"]) == 0


def test_step52_state_mutation_guard_passes():
    summary = read_json("outputs/step52_state_mutation_guard/state_mutation_guard.json")["summary"]
    assert summary["guard_pass"] is True
    for key in [
        "default_driver_state_mutation_count",
        "default_lbm_state_mutation_count",
        "default_mpm_state_mutation_count",
        "default_projection_state_mutation_count",
        "persistent_projected_state_count",
        "persistent_displaced_geometry_count",
        "persistent_lbm_solid_vel_count",
        "displaced_particle_output_count",
        "dense_displacement_output_count",
        "vtr_output_count",
        "particle_npy_output_count",
        "geo_all_fluid_dat_count_added",
    ]:
        assert int(summary[key]) == 0
    assert summary["original_geometry_hash_before"] == summary["original_geometry_hash_after"]
    assert summary["region_mask_hash_before"] == summary["region_mask_hash_after"]


def test_step52_step51_regression_guard_passes():
    summary = read_json("outputs/step52_step51_regression_guard/step51_regression_guard.json")["summary"]
    assert summary["regression_pass"] is True
    assert int(summary["row_count"]) == 10
    assert int(summary["pass_count"]) == 10


def test_step52_artifact_manifest_passes():
    summary = read_json("outputs/step52_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert float(summary["step52_total_size_mb"]) < 10.0
    assert float(summary["total_size_mb"]) < 400.0
    assert int(summary["large_file_count"]) == 0
    assert int(summary["step52_vtr_count"]) == 0
    assert int(summary["step52_particle_npy_count"]) == 0
    assert int(summary["step52_displaced_particle_output_count"]) == 0
    assert int(summary["step52_dense_displacement_output_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step52_docs_and_report_claim_boundaries():
    docs = read_text("docs/52_controlled_48_engineering_one_cycle_feasibility.md")
    report = read_text("STEP52_CONTROLLED_48_ENGINEERING_ONE_CYCLE_FEASIBILITY_REPORT.md")
    joined = f"{docs}\n{report}"
    for phrase in REQUIRED_SCOPE:
        assert phrase in docs
        assert phrase in report
    lower = joined.lower()
    for claim in FORBIDDEN_CLAIMS:
        assert claim.lower() not in lower
    assert "active_cell_count_growth_observed = false" in report
    assert "applied_cell_count_ratio_48_vs_32 =\n3.2962962962962963" in report


def test_step52_npz_is_compact_summary_only():
    path = ROOT / "outputs/step52_48_feasibility_matrix/feasibility_matrix.npz"
    assert path.is_file()
    assert path.stat().st_size < 32 * 1024


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _all_step52_flags_false(config):
    for key in [
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
    ]:
        assert key in config
        assert config[key] is False
    return True


def finite_values(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True
