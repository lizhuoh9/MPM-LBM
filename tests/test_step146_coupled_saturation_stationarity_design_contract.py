import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


STEP146_OUTPUT_ROOT = ROOT / "outputs" / "step146_coupled_saturation_stationarity_design"
STEP146_GOAL = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "146" / "goal.md"
STEP146_REPORT = ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "146" / "report.md"
STEP146_DESIGN = (
    ROOT
    / "docs"
    / "campaigns"
    / "fluent_duct_flap"
    / "steps"
    / "146"
    / "coupled_saturation_stationarity_design.md"
)

EXPECTED_SOURCE_INPUT_KEYS = {
    "step145_summary",
    "step145_saturation",
    "step145_stationarity",
    "step145_controller",
    "step144_decision",
    "step144_comparison",
}

FORBIDDEN_RUNNER_TEXT = [
    "step121_lbm_boundary_real_campaign_and_gate_correction",
    "FSIDriver3D",
    "LBMFluid3D",
    "Taichi",
    "taichi as ti",
    "--allow-large-real-rows",
    "--phase step146",
    "selected96_execution_allowed\": true",
    "selected_candidate_surface_review_allowed\": true",
    "validation_claim_allowed\": true",
    "step146_500step_probe_allowed\": true",
]


def test_step146_generator_declares_only_source_artifacts_and_stays_artifact_only():
    from experiments.steps.step146_coupled_saturation_stationarity_design_report import (
        SOURCE_INPUT_PATHS,
    )

    assert set(SOURCE_INPUT_PATHS) == EXPECTED_SOURCE_INPUT_KEYS

    source = (
        ROOT / "experiments" / "steps" / "step146_coupled_saturation_stationarity_design_report.py"
    ).read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_RUNNER_TEXT:
        assert forbidden not in source


def test_step146_missing_input_writes_missing_input_without_readiness(tmp_path):
    from experiments.steps.step146_coupled_saturation_stationarity_design_report import (
        run_step146_design_report,
    )

    summary = run_step146_design_report(
        step145_summary=tmp_path / "missing_step145_summary.json",
        step145_saturation=ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "saturation_segment_report.json",
        step145_stationarity=ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "stationarity_segment_report.json",
        step145_controller=ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "controller_lag_segment_report.json",
        step144_decision=ROOT / "outputs" / "step144_mass_neutral_final48" / "step144_decision_summary.json",
        step144_comparison=ROOT
        / "outputs"
        / "step144_mass_neutral_final48"
        / "step144_long_window_comparison.json",
        output_dir=tmp_path / "step146_out",
        force=True,
    )

    assert summary["status"] == "missing_input"
    assert summary["missing_input"] is True
    assert summary["design_readiness_present"] is False
    assert summary["recommended_design"] is None
    assert summary["step147_250step_diagnostic_proposal_allowed"] is False
    assert summary["step146_500step_probe_allowed"] is False
    assert (tmp_path / "step146_out" / "step146_design_readiness_report.json").is_file()
    assert (tmp_path / "step146_out" / "step146_design_readiness_report.md").is_file()


def test_step146_wrong_step145_decision_blocks_readiness(tmp_path):
    from experiments.steps.step146_coupled_saturation_stationarity_design_report import (
        run_step146_design_report,
    )

    inputs = _copy_source_inputs(tmp_path / "inputs")
    step145_summary = _read_json(inputs["step145_summary"])
    step145_summary["decision_case"] = "stationarity_drift_dominant"
    step145_summary["dominant_failure_mechanism"] = "stationarity_drift_dominant"
    _write_json(inputs["step145_summary"], step145_summary)

    summary = run_step146_design_report(output_dir=tmp_path / "step146_out", force=True, **inputs)

    assert summary["status"] == "blocked_by_source_decision"
    assert summary["missing_input"] is False
    assert summary["design_readiness_present"] is False
    assert summary["recommended_design"] is None
    assert summary["step147_250step_diagnostic_proposal_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["selected_candidate_surface_review_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["step146_500step_probe_allowed"] is False


def test_step146_runner_generates_design_readiness_from_existing_artifacts(tmp_path):
    from experiments.steps.step146_coupled_saturation_stationarity_design_report import (
        run_step146_design_report,
    )

    summary = run_step146_design_report(
        step145_summary=ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "step145_failure_mechanism_summary.json",
        step145_saturation=ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "saturation_segment_report.json",
        step145_stationarity=ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "stationarity_segment_report.json",
        step145_controller=ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "controller_lag_segment_report.json",
        step144_decision=ROOT / "outputs" / "step144_mass_neutral_final48" / "step144_decision_summary.json",
        step144_comparison=ROOT
        / "outputs"
        / "step144_mass_neutral_final48"
        / "step144_long_window_comparison.json",
        output_dir=tmp_path / "step146_out",
        force=True,
    )

    assert summary["status"] == "design_ready"
    assert summary["source_step145_decision_case"] == "mixed_saturation_stationarity_failure"
    assert summary["source_step145_dominant_failure_mechanism"] == "mixed_saturation_stationarity_failure"
    assert summary["source_step144_decision_case"] == "mass_neutral_flow_stationarity_long_window_failure"
    assert summary["design_only"] is True
    assert summary["artifact_only"] is True
    assert summary["new_lbm_run_executed"] is False
    assert summary["new_parameter_tuning_executed"] is False
    assert summary["step121_phase_added"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["selected_static_execution_allowed"] is False
    assert summary["selected_candidate_surface_review_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["step146_500step_probe_allowed"] is False
    assert summary["step147_250step_diagnostic_proposal_allowed"] is True
    assert summary["recommended_design"] == (
        "saturation_aware_mass_neutral_relief_with_stationarity_damping"
    )
    assert summary["fallback_design"] == "outlet_population_projection_report_only"
    assert summary["recommended_step147_phase"] == "planeflux_saturation_stationarity48"
    assert summary["recommended_step147_row_role"] == "saturation_stationarity_diagnostic_48"
    assert summary["max_step147_rows"] == 4
    assert summary["max_step147_steps"] == 250
    assert summary["step144_final_mass_abs"] == 0.007345390662776274
    assert summary["step144_flux_imbalance_rel_tail_mean"] == 0.1023209978570283
    assert summary["step144_outlet_flux_tail_cv"] == 0.11500661338208944
    assert summary["step144_mass_neutral_feedback_saturation_fraction_tail"] == 0.9374677783363148

    assert (tmp_path / "step146_out" / "step146_design_readiness_report.json").is_file()
    assert (tmp_path / "step146_out" / "step146_design_readiness_report.md").is_file()
    markdown = (tmp_path / "step146_out" / "step146_design_readiness_report.md").read_text(
        encoding="utf-8"
    )
    assert "Design A" in markdown
    assert "Design B" in markdown
    assert "selected96" in markdown
    assert "blocked" in markdown


def test_step146_remains_artifact_only_after_step147_phase_lands():
    step146_source = (
        ROOT / "experiments" / "steps" / "step146_coupled_saturation_stationarity_design_report.py"
    ).read_text(encoding="utf-8")
    step121_source = (
        ROOT / "experiments" / "steps" / "step121_lbm_boundary_real_campaign_and_gate_correction.py"
    ).read_text(encoding="utf-8")

    assert "run_step120_matrix" not in step146_source
    assert "step121_lbm_boundary_real_campaign_and_gate_correction" not in step146_source
    assert "step146_coupled_saturation_stationarity_design_report" not in step121_source
    assert "STEP147_SATURATION_STATIONARITY_PHASE" in step121_source
    assert "STEP147_SATURATION_STATIONARITY_ROLE" in step121_source
    assert "STEP146_READINESS_RELATIVE_PATH" in step121_source


def test_committed_step146_outputs_docs_and_reading_order_preserve_blocked_state():
    assert STEP146_GOAL.is_file()
    assert STEP146_REPORT.is_file()
    assert STEP146_DESIGN.is_file()

    summary = _read_json(STEP146_OUTPUT_ROOT / "step146_design_readiness_report.json")
    assert summary["step"] == 146
    assert summary["status"] == "design_ready"
    assert summary["source_step145_decision_case"] == "mixed_saturation_stationarity_failure"
    assert summary["source_step144_decision_case"] == "mass_neutral_flow_stationarity_long_window_failure"
    assert summary["design_only"] is True
    assert summary["artifact_only"] is True
    assert summary["new_lbm_run_executed"] is False
    assert summary["step121_phase_added"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["selected_candidate_surface_review_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["step146_500step_probe_allowed"] is False
    assert summary["step147_250step_diagnostic_proposal_allowed"] is True

    status = (ROOT / "docs" / "current" / "STATUS.md").read_text(encoding="utf-8")
    gates = (ROOT / "docs" / "current" / "VALIDATION_GATES.md").read_text(encoding="utf-8")
    reading_order = (ROOT / "docs" / "current" / "READING_ORDER.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    report = STEP146_REPORT.read_text(encoding="utf-8")
    design = STEP146_DESIGN.read_text(encoding="utf-8")

    required_text = [
        "Step146 is design-only and artifact-only",
        "Step144 failed the final hard gate",
        "mixed_saturation_stationarity_failure",
        "Step146 did not run a new LBM row",
        "Step146 did not add a Step121 phase",
        "Step146 did not run selected96",
        "Step146 does not make a validation claim",
        "selected-candidate-surface review remains blocked",
        "selected96 remains blocked",
        "500-step probe remains blocked",
    ]
    for text in required_text:
        assert text in report

    for text in [
        "Step146 is design-only and artifact-only",
        "mixed_saturation_stationarity_failure",
        "selected96 remains blocked",
        "selected-candidate-surface review remains blocked",
        "validation claim remains blocked",
    ]:
        assert text in status
        assert text in gates

    assert "docs/campaigns/fluent_duct_flap/steps/146/goal.md" in reading_order
    assert "outputs/step146_coupled_saturation_stationarity_design/step146_design_readiness_report.json" in reading_order
    assert "Step146" in readme
    assert "validation claim remains blocked" in readme
    assert "Design A" in design
    assert "Design B" in design


def _copy_source_inputs(target: Path) -> dict[str, Path]:
    target.mkdir(parents=True, exist_ok=True)
    source_paths = {
        "step145_summary": ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "step145_failure_mechanism_summary.json",
        "step145_saturation": ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "saturation_segment_report.json",
        "step145_stationarity": ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "stationarity_segment_report.json",
        "step145_controller": ROOT
        / "outputs"
        / "step145_mass_neutral_long_window_forensics"
        / "controller_lag_segment_report.json",
        "step144_decision": ROOT / "outputs" / "step144_mass_neutral_final48" / "step144_decision_summary.json",
        "step144_comparison": ROOT
        / "outputs"
        / "step144_mass_neutral_final48"
        / "step144_long_window_comparison.json",
    }
    copied = {}
    for key, source in source_paths.items():
        destination = target / source.name
        shutil.copyfile(source, destination)
        copied[key] = destination
    return copied


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload):
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
