import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


STEP145_OUTPUT_ROOT = ROOT / "outputs" / "step145_mass_neutral_long_window_forensics"
STEP145_GOAL = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "145" / "goal.md"
STEP145_REPORT = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "145" / "report.md"

EXPECTED_WINDOWS = [
    "0_100",
    "100_200",
    "200_250",
    "250_300",
    "300_400",
    "400_500",
    "tail_80pct_diagnostic",
    "tail_20pct_hard_gate",
]

EXPECTED_REQUIRED_INPUT_KEYS = {
    "step144_decision_summary",
    "step144_long_window_comparison",
    "step144_finite_stability_report",
    "step144_flow_development_diagnostics_csv",
    "step144_flow_development_diagnostics_summary",
    "step144_boundary_flux_timeseries_csv",
    "step144_density_drift_timeseries_csv",
    "step143_decision_summary",
    "step143_mass_neutral_comparison",
    "step140_failure_mechanism_summary",
}

FORBIDDEN_EXECUTION_TEXT = [
    "--allow-large-real-rows",
    "--phase step145",
    "STEP145_PHASE",
    "step145_mass_neutral_long_window_forensics_phase",
    "selected96_execution_allowed\": true",
    "validation_claim_allowed\": true",
]


def test_step145_contract_surface_is_artifact_only_and_declares_required_inputs():
    from experiments.steps.step145_mass_neutral_long_window_forensics import (
        REQUIRED_INPUT_KEYS,
        WINDOW_SPECS,
    )

    assert [window["name"] for window in WINDOW_SPECS] == EXPECTED_WINDOWS
    assert set(REQUIRED_INPUT_KEYS) == EXPECTED_REQUIRED_INPUT_KEYS


def test_step145_missing_step144_input_returns_missing_input_without_synthetic_mechanism(tmp_path):
    from experiments.steps.step145_mass_neutral_long_window_forensics import run_step145_forensics

    summary = run_step145_forensics(
        step144_root=tmp_path / "missing_step144",
        step143_root=ROOT / "outputs" / "step143_mass_neutral_design_diagnostic",
        step140_root=ROOT / "outputs" / "step140_long_window_drift_forensics",
        output_dir=tmp_path / "step145_out",
        force=True,
    )

    assert summary["status"] == "missing_input"
    assert summary["missing_input"] is True
    assert summary["dominant_failure_mechanism"] is None
    assert summary["mechanism_summary_present"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected_candidate_surface_review_allowed"] is False
    assert (tmp_path / "step145_out" / "step145_failure_mechanism_summary.json").is_file()


def test_step145_does_not_add_step121_or_selected_execution_surface():
    step121_source = (
        ROOT / "experiments" / "steps" / "step121_lbm_boundary_real_campaign_and_gate_correction.py"
    ).read_text(encoding="utf-8")
    step145_source = (
        ROOT / "experiments" / "steps" / "step145_mass_neutral_long_window_forensics.py"
    ).read_text(encoding="utf-8")

    assert "STEP145" not in step121_source
    assert "step145_mass_neutral_long_window_forensics" not in step121_source
    for forbidden in FORBIDDEN_EXECUTION_TEXT:
        assert forbidden not in step145_source


def test_step145_runner_generates_required_reports_from_existing_artifacts(tmp_path):
    from experiments.steps.step145_mass_neutral_long_window_forensics import run_step145_forensics

    out = tmp_path / "step145_out"
    summary = run_step145_forensics(
        step144_root=ROOT / "outputs" / "step144_mass_neutral_final48",
        step143_root=ROOT / "outputs" / "step143_mass_neutral_design_diagnostic",
        step140_root=ROOT / "outputs" / "step140_long_window_drift_forensics",
        output_dir=out,
        force=True,
    )

    assert summary["status"] == "mechanism_classified"
    assert summary["dominant_failure_mechanism"] in {
        "mass_neutral_cap_saturation_dominant",
        "stationarity_drift_dominant",
        "controller_lag_or_slew_dominant",
        "mass_neutral_actuator_insufficient",
        "mixed_saturation_stationarity_failure",
        "mechanism_unresolved",
    }
    assert summary["source_step144_decision_case"] == "mass_neutral_flow_stationarity_long_window_failure"
    assert summary["new_lbm_run_executed"] is False
    assert summary["new_parameter_tuning_executed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected_candidate_surface_review_allowed"] is False
    assert summary["step146_250step_diagnostic_proposal_allowed"] is True
    assert summary["step146_500step_probe_allowed"] is False
    assert summary["next_experiment_recommendation_count"] <= 1

    for name in [
        "saturation_segment_report.json",
        "stationarity_segment_report.json",
        "mass_neutral_error_segment_report.json",
        "controller_lag_segment_report.json",
        "step145_failure_mechanism_summary.json",
        "step145_failure_mechanism_summary.md",
    ]:
        assert (out / name).is_file()

    saturation = _read_json(out / "saturation_segment_report.json")
    stationarity = _read_json(out / "stationarity_segment_report.json")
    controller = _read_json(out / "controller_lag_segment_report.json")
    mass_error = _read_json(out / "mass_neutral_error_segment_report.json")

    assert [segment["name"] for segment in saturation["segments"]] == EXPECTED_WINDOWS
    tail_sat = _segment(saturation, "tail_20pct_hard_gate")
    assert "mass_neutral_feedback_saturation_fraction" in tail_sat["summary_metrics"]
    assert tail_sat["summary_metrics"]["mass_neutral_feedback_saturation_fraction"]["available"] is True

    tail_stationarity = _segment(stationarity, "tail_20pct_hard_gate")
    assert "outlet_flux" in tail_stationarity["metrics"]
    assert tail_stationarity["metrics"]["outlet_flux"]["cv"] is not None
    assert "flux_imbalance_rel" in tail_stationarity["metrics"]
    assert tail_stationarity["metrics"]["flux_imbalance_rel"]["mean"] is not None

    tail_controller = _segment(controller, "tail_20pct_hard_gate")
    assert "controller_authority_ratio" in tail_controller["metrics"]
    assert "controller_filtered_flux_error" in tail_controller["metrics"]

    assert mass_error["step143_to_step144_250_vs_500"]["step143_best_mass_abs"] == 0.0031636249081530357
    assert mass_error["step143_to_step144_250_vs_500"]["step144_final_mass_abs"] == 0.007345390662776274


def test_committed_step145_outputs_and_docs_preserve_step144_failure_and_blocked_state():
    assert STEP145_GOAL.is_file()
    assert STEP145_REPORT.is_file()

    summary = _read_json(STEP145_OUTPUT_ROOT / "step145_failure_mechanism_summary.json")
    saturation = _read_json(STEP145_OUTPUT_ROOT / "saturation_segment_report.json")
    stationarity = _read_json(STEP145_OUTPUT_ROOT / "stationarity_segment_report.json")
    controller = _read_json(STEP145_OUTPUT_ROOT / "controller_lag_segment_report.json")

    assert summary["step"] == 145
    assert summary["status"] == "mechanism_classified"
    assert summary["source_step"] == 144
    assert summary["source_step144_decision_case"] == "mass_neutral_flow_stationarity_long_window_failure"
    assert summary["new_lbm_run_executed"] is False
    assert summary["new_parameter_tuning_executed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected_candidate_surface_review_allowed"] is False
    assert summary["next_experiment_recommendation_count"] <= 1

    assert [segment["name"] for segment in saturation["segments"]] == EXPECTED_WINDOWS
    assert [segment["name"] for segment in stationarity["segments"]] == EXPECTED_WINDOWS
    assert [segment["name"] for segment in controller["segments"]] == EXPECTED_WINDOWS

    current_status = (ROOT / "docs" / "current" / "STATUS.md").read_text(encoding="utf-8")
    current_gates = (ROOT / "docs" / "current" / "VALIDATION_GATES.md").read_text(encoding="utf-8")
    report = STEP145_REPORT.read_text(encoding="utf-8")

    required_text = [
        "Step144 failed the final hard gate",
        "Step145 did not run a new LBM row",
        "Step145 did not add a Step121 phase",
        "Step145 did not run selected96",
        "Step145 did not run selected-static",
        "Step145 did not run 96^3",
        "Step145 did not run Fluent",
        "Step145 did not run FSI",
        "Step145 does not make a validation claim",
        "Step145 keeps selected-candidate-surface review blocked",
        "Step145 keeps selected96 blocked",
    ]
    for text in required_text:
        assert text in report

    for text in [
        "Step144 failed the final hard gate",
        "selected96 remains blocked",
        "selected-candidate-surface review remains blocked",
        "validation claim remains blocked",
    ]:
        assert text in current_status
        assert text in current_gates


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _segment(report, name):
    return next(segment for segment in report["segments"] if segment["name"] == name)

