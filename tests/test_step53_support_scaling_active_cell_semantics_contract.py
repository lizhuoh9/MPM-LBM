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

REQUIRED_FILES = [
    "STEP53_CONTROLLED_48_SUPPORT_SCALING_ACTIVE_CELL_SEMANTICS_GOAL.md",
    "STEP53_CONTROLLED_48_SUPPORT_SCALING_ACTIVE_CELL_SEMANTICS_REPORT.md",
    "docs/53_controlled_48_support_scaling_active_cell_semantics.md",
    "configs/step53_support_scaling_active_cell_semantics_audit.json",
    "configs/step53_step51_step52_reference_artifacts.json",
    "configs/step53_metric_semantics_policy.json",
    "src/runtime_geometry_wall_velocity_support_scaling_config.py",
    "src/runtime_geometry_wall_velocity_support_scaling_audit.py",
    "src/runtime_geometry_wall_velocity_support_scaling_diagnostics.py",
    "src/runtime_geometry_wall_velocity_support_scaling_claim_guard.py",
    "src/runtime_geometry_wall_velocity_support_scaling_artifact_guard.py",
    "baseline_tests/step53_common.py",
    "baseline_tests/run_step53_reference_artifact_validation.py",
    "baseline_tests/run_step53_phasewise_support_scaling_audit.py",
    "baseline_tests/run_step53_active_cell_semantics_audit.py",
    "baseline_tests/run_step53_applied_wall_support_scaling_audit.py",
    "baseline_tests/run_step53_bounceback_support_scaling_audit.py",
    "baseline_tests/run_step53_metric_claim_guard.py",
    "baseline_tests/run_step53_step52_regression_guard.py",
    "baseline_tests/run_step53_artifact_manifest.py",
    "tests/test_step53_support_scaling_active_cell_semantics_contract.py",
]

OUTPUT_FILES = [
    "outputs/step53_reference_artifact_validation/reference_artifact_validation.csv",
    "outputs/step53_reference_artifact_validation/reference_artifact_summary.csv",
    "outputs/step53_reference_artifact_validation/reference_artifact_validation.json",
    "outputs/step53_phasewise_support_scaling_audit/phasewise_support_scaling.csv",
    "outputs/step53_phasewise_support_scaling_audit/phasewise_support_scaling_summary.csv",
    "outputs/step53_phasewise_support_scaling_audit/phasewise_support_scaling.json",
    "outputs/step53_active_cell_semantics_audit/active_cell_semantics.csv",
    "outputs/step53_active_cell_semantics_audit/active_cell_semantics_summary.csv",
    "outputs/step53_active_cell_semantics_audit/active_cell_semantics.json",
    "outputs/step53_applied_wall_support_scaling_audit/applied_wall_support_scaling.csv",
    "outputs/step53_applied_wall_support_scaling_audit/applied_wall_support_scaling_summary.csv",
    "outputs/step53_applied_wall_support_scaling_audit/applied_wall_support_scaling.json",
    "outputs/step53_bounceback_support_scaling_audit/bounceback_support_scaling.csv",
    "outputs/step53_bounceback_support_scaling_audit/bounceback_support_scaling_summary.csv",
    "outputs/step53_bounceback_support_scaling_audit/bounceback_support_scaling.json",
    "outputs/step53_metric_claim_guard/metric_claim_guard.csv",
    "outputs/step53_metric_claim_guard/metric_claim_guard_summary.csv",
    "outputs/step53_metric_claim_guard/metric_claim_guard.json",
    "outputs/step53_step52_regression_guard/step52_regression_guard.csv",
    "outputs/step53_step52_regression_guard/step52_regression_guard_summary.csv",
    "outputs/step53_step52_regression_guard/step52_regression_guard.json",
    "outputs/step53_artifact_manifest/artifact_manifest.csv",
    "outputs/step53_artifact_manifest/artifact_summary.csv",
    "outputs/step53_artifact_manifest/artifact_summary.json",
]

LOG_MARKERS = {
    "logs/step53_reference_artifact_validation.log": "[OK] Step 53 reference artifact validation finished",
    "logs/step53_phasewise_support_scaling_audit.log": "[OK] Step 53 phasewise support scaling audit finished",
    "logs/step53_active_cell_semantics_audit.log": "[OK] Step 53 active-cell semantics audit finished",
    "logs/step53_applied_wall_support_scaling_audit.log": "[OK] Step 53 applied wall support scaling audit finished",
    "logs/step53_bounceback_support_scaling_audit.log": "[OK] Step 53 bounce-back support scaling audit finished",
    "logs/step53_metric_claim_guard.log": "[OK] Step 53 metric claim guard finished",
    "logs/step53_step52_regression_guard.log": "[OK] Step 53 Step 52 regression guard finished",
    "logs/step53_artifact_manifest.log": "[OK] Step 53 artifact manifest finished",
}

REQUIRED_SCOPE = [
    "Step 53 is a controlled post-processing audit over accepted Step 51 and Step 52 artifacts.",
    "Step 53 reads committed JSON artifacts only and adds no new solver rows.",
    "Step 53 keeps runtime behavior diagnostic-only and non-persistent.",
    "Step 53 does not validate real jets.",
    "Step 53 does not validate jet propulsion.",
    "Step 53 does not implement squid swimming.",
    "Step 53 does not change moving bounce-back formulas.",
    "Step 53 is not a grid-convergence result.",
]


def test_step53_required_artifacts_exist():
    missing = [path for path in REQUIRED_FILES + OUTPUT_FILES if not (ROOT / path).is_file()]
    assert missing == []
    missing_logs = [path for path, marker in LOG_MARKERS.items() if marker not in read_text(path)]
    assert missing_logs == []


def test_step53_config_and_policy_are_narrow():
    config = read_json("configs/step53_support_scaling_active_cell_semantics_audit.json")
    assert config["audit_id"] == "step53_controlled_48_support_scaling_active_cell_semantics"
    assert config["phase_sequence"] == PHASE_SEQUENCE
    assert config["diagnostic_only"] is True
    assert config["post_processing_only"] is True
    for key in [
        "requires_new_solver_rows",
        "introduces_new_transfer_mode",
        "rerun_physics_matrix",
        "allow_48_link_area",
        "allow_multi_cycle",
        "allow_64_grid",
        "modify_solver_formulas",
        "modify_default_behavior",
        "write_vtk",
        "write_particles",
        "write_dense_displacement_field",
        "write_displaced_particles",
        "persist_projected_state",
        "persist_displaced_geometry",
        "persist_lbm_solid_vel",
    ]:
        assert config[key] is False

    policy = read_json("configs/step53_metric_semantics_policy.json")
    assert policy["active_cell_count_is_grid_convergence_metric"] is False
    assert policy["active_cell_count_growth_required"] is False
    assert policy["active_cell_count_growth_must_be_reported"] is True
    assert policy["applied_cell_count_growth_required"] is True
    assert policy["grid_convergence_claim_allowed"] is False
    assert policy["physical_validation_claim_allowed"] is False
    assert policy["production_readiness_claim_allowed"] is False
    assert policy["applied_cell_growth_is_physical_validation"] is False
    assert policy["bb_link_used_as_area_convergence_metric"] is False
    assert policy["force_impulse_interpretation"] == "diagnostic_proxy_only"


def test_step53_reference_artifact_validation_passes():
    payload = read_json("outputs/step53_reference_artifact_validation/reference_artifact_validation.json")
    summary = payload["summary"]
    assert summary["reference_validation_pass"] is True
    assert summary["diagnostic_only"] is True
    assert summary["post_processing_only"] is True
    assert summary["no_new_solver_rows"] is True
    assert summary["no_new_transfer_mode"] is True
    assert int(summary["phase_count"]) == 40
    assert int(summary["row_count"]) == int(summary["pass_count"])


def test_step53_phasewise_support_scaling_passes():
    payload = read_json("outputs/step53_phasewise_support_scaling_audit/phasewise_support_scaling.json")
    summary = payload["summary"]
    rows = payload["rows"]
    assert summary["phasewise_audit_pass"] is True
    assert int(summary["matched_phase_count"]) == 40
    assert [float(row["phase"]) for row in rows] == PHASE_SEQUENCE
    assert summary["all_values_finite"] is True
    assert summary["all_ratios_finite"] is True
    assert int(summary["active_cell_count_48"]) >= int(summary["active_cell_count_32"])
    assert summary["active_cell_count_growth_observed"] is False
    assert summary["active_cell_count_non_decreasing"] is True
    assert int(summary["applied_cell_count_32"]) == 648
    assert int(summary["applied_cell_count_48"]) == 2136
    assert summary["applied_cell_count_growth_observed"] is True
    assert float(summary["applied_cell_count_ratio_48_vs_32"]) > 1.0
    assert int(summary["bb_link_count_48"]) > 0
    assert float(summary["rho_min_48"]) > 0.95
    assert float(summary["rho_max_48"]) < 1.05
    assert float(summary["lbm_max_v_48"]) < 0.1
    assert summary["force_impulse_ratios_finite"] is True
    assert summary["force_impulse_interpretation"] == "diagnostic_proxy_only"
    assert summary["grid_convergence_claim"] is False
    assert summary["physical_validation_claim"] is False
    assert summary["production_readiness_claim"] is False

    for row in rows:
        assert finite_values(row)
        assert bool(row["all_values_finite"]) is True
        assert bool(row["all_ratios_finite"]) is True


def test_step53_active_cell_semantics_passes():
    summary = read_json("outputs/step53_active_cell_semantics_audit/active_cell_semantics.json")["summary"]
    assert summary["semantics_pass"] is True
    assert int(summary["active_cell_count_32"]) == 648
    assert int(summary["active_cell_count_48"]) == 648
    assert summary["active_cell_count_growth_observed"] is False
    assert summary["active_cell_count_non_decreasing"] is True
    assert summary["active_cell_count_used_as_grid_convergence_metric"] is False
    assert summary["active_cell_count_growth_required_for_pass"] is False
    assert summary["active_cell_semantics_status"] in {
        "resolution_invariant_under_current_diagnostic",
        "non_decreasing_but_not_resolution_scaling",
        "unresolved_requires_metric_rename_or_projection_audit",
    }
    if summary["active_cell_semantics_status"] == "unresolved_requires_metric_rename_or_projection_audit":
        assert summary["step54_link_area_allowed"] is False
    assert summary["grid_convergence_claim"] is False
    assert summary["physical_validation_claim"] is False
    assert summary["production_readiness_claim"] is False


def test_step53_applied_wall_support_passes():
    summary = read_json("outputs/step53_applied_wall_support_scaling_audit/applied_wall_support_scaling.json")["summary"]
    assert summary["applied_wall_support_audit_pass"] is True
    assert int(summary["applied_cell_count_32"]) == 648
    assert int(summary["applied_cell_count_48"]) == 2136
    assert summary["applied_cell_count_growth_observed"] is True
    assert float(summary["applied_cell_count_ratio_48_vs_32"]) == 3.2962962962962963
    assert math.isfinite(float(summary["applied_cell_fraction_32"]))
    assert math.isfinite(float(summary["applied_cell_fraction_48"]))
    assert math.isfinite(float(summary["applied_cell_fraction_ratio"]))
    assert summary["applied_cell_growth_is_physical_validation"] is False
    assert summary["wall_support_growth_claim"] == "diagnostic_only"


def test_step53_bounceback_support_passes():
    summary = read_json("outputs/step53_bounceback_support_scaling_audit/bounceback_support_scaling.json")["summary"]
    assert summary["bounceback_support_audit_pass"] is True
    assert int(summary["bb_link_count_32"]) == 3888
    assert int(summary["bb_link_count_48"]) == 3888
    assert float(summary["bb_link_count_ratio"]) == 1.0
    assert summary["bb_link_growth_observed"] is False
    assert summary["bb_link_non_decreasing"] is True
    assert summary["bb_link_used_as_area_convergence_metric"] is False
    assert summary["bb_link_support_status"] in {
        "resolution_invariant_under_current_diagnostic",
        "non_decreasing_but_not_area_convergence",
        "unresolved_requires_boundary_link_metric_audit",
    }


def test_step53_claim_and_regression_guards_pass():
    claim = read_json("outputs/step53_metric_claim_guard/metric_claim_guard.json")["summary"]
    assert claim["claim_guard_pass"] is True
    assert int(claim["forbidden_claim_count"]) == 0
    assert int(claim["required_flag_count"]) == int(claim["required_false_flag_pass_count"])
    assert claim["force_impulse_interpretation"] == "diagnostic_proxy_only"

    regression = read_json("outputs/step53_step52_regression_guard/step52_regression_guard.json")["summary"]
    assert regression["regression_pass"] is True
    assert int(regression["row_count"]) == 9
    assert int(regression["pass_count"]) == 9


def test_step53_artifact_manifest_passes():
    summary = read_json("outputs/step53_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert float(summary["step53_total_size_mb"]) < 5.0
    assert float(summary["total_size_mb"]) < 400.0
    assert int(summary["large_file_count"]) == 0
    assert int(summary["step53_vtr_count"]) == 0
    assert int(summary["step53_particle_npy_count"]) == 0
    assert int(summary["step53_dense_displacement_output_count"]) == 0
    assert int(summary["step53_displaced_particle_output_count"]) == 0
    assert int(summary["scan_data_file_count"]) == 0
    assert int(summary["raw_candidate_large_file_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert int(summary["geo_all_fluid_dat_count_added"]) == 0


def test_step53_docs_and_report_scope_boundaries():
    docs = read_text("docs/53_controlled_48_support_scaling_active_cell_semantics.md")
    report = read_text("STEP53_CONTROLLED_48_SUPPORT_SCALING_ACTIVE_CELL_SEMANTICS_REPORT.md")
    for phrase in REQUIRED_SCOPE:
        assert phrase in docs
        assert phrase in report
    assert "wall-application support growth" in docs
    assert "active_cell_semantics_status = non_decreasing_but_not_resolution_scaling" in report
    assert "Step 54 may therefore consider a\ndiagnostic-only 48^3 `link_area_experimental` two-row comparison" in report


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def finite_values(row):
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
