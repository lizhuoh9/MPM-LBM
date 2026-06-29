import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP139_ROOT = ROOT / "outputs" / "step139_planeflux_final48"
STEP140_OUTPUT_ROOT = ROOT / "outputs" / "step140_long_window_drift_forensics"
STEP139_RUN_COMMIT = "4e43162a641085e56a4ba72c8bc013e58cb08cc3"
STEP139_REPORT_COMMIT = "b83c1514e325c3bb5f29d73f8adeab13f6ac623d"
STEP141_RUN_COMMIT = "90fa5798754942cd8f7de2a1c24a483804667478"
STEP143_RUN_COMMIT = "5ec833f13602c8fb010693fc376f92088b24d93b"
STEP143_FINAL_COMMIT = "618cf188827e0b9538e5279e8ab042fabd92a0b2"

EXPECTED_REPORTS = [
    "mass_drift_segment_report.json",
    "flux_stationarity_segment_report.json",
    "controller_response_segment_report.json",
    "x_profile_evolution_report.json",
    "step140_failure_mechanism_summary.json",
    "step140_failure_mechanism_summary.md",
]


def test_step140_parser_generates_forensics_reports_from_step139_only(tmp_path):
    from experiments.steps.step140_long_window_drift_forensics import (
        DEFAULT_WINDOWS,
        run_step140_forensics,
    )

    output_dir = tmp_path / "step140"
    summary = run_step140_forensics(STEP139_ROOT, output_dir, force=True)

    assert [window["name"] for window in DEFAULT_WINDOWS][:6] == [
        "0_100",
        "100_200",
        "200_250",
        "250_300",
        "300_400",
        "400_500",
    ]
    assert summary["status"] == "mechanism_classified"
    assert summary["input_step"] == 139
    assert summary["input_row_completed_500"] is True
    assert summary["input_final_hard_gate_pass"] is False
    assert summary["new_lbm_run_executed"] is False
    assert summary["new_parameter_tuning_executed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["segment_count"] >= 6
    assert summary["mass_drift_failure_classified"] is True
    assert summary["outlet_cv_failure_classified"] is True
    assert summary["flux_mean_failure_classified"] is True
    assert summary["mechanism_summary_present"] is True
    assert len(summary["next_experiment_recommendations"]) <= 1
    assert summary["dominant_failure_mechanism"] in {
        "mass_accumulation_with_outlet_stationarity_drift",
        "mixed_long_window_drift",
    }
    assert summary["step139_input_root"].endswith("outputs/step139_planeflux_final48")

    for name in EXPECTED_REPORTS:
        assert (output_dir / name).is_file(), name


def test_step140_segment_reports_have_required_windows_and_claim_flags(tmp_path):
    from experiments.steps.step140_long_window_drift_forensics import run_step140_forensics

    output_dir = tmp_path / "step140"
    run_step140_forensics(STEP139_ROOT, output_dir, force=True)

    mass = _read_json(output_dir / "mass_drift_segment_report.json")
    flux = _read_json(output_dir / "flux_stationarity_segment_report.json")
    controller = _read_json(output_dir / "controller_response_segment_report.json")
    profile = _read_json(output_dir / "x_profile_evolution_report.json")

    for payload in (mass, flux, controller, profile):
        assert payload["step"] == 140
        assert payload["source_step"] == 139
        assert payload["new_lbm_run_executed"] is False
        assert payload["selected96_execution_allowed"] is False
        assert payload["validation_claim_allowed"] is False
        names = [segment["name"] for segment in payload["segments"]]
        for required in ["0_100", "100_200", "200_250", "250_300", "300_400", "400_500"]:
            assert required in names

    mass_250_300 = _segment(mass, "250_300")
    mass_400_500 = _segment(mass, "400_500")
    assert "mass_total_delta_rel" in mass_250_300["metrics"]
    assert mass_400_500["metrics"]["mass_total_delta_rel"]["final"] > 0.005

    flux_tail = _segment(flux, "tail_20pct_hard_gate")
    assert flux_tail["metrics"]["flux_imbalance_rel"]["mean"] > 0.1
    assert flux_tail["metrics"]["outlet_flux"]["cv"] > 0.1
    assert 0.98 <= flux_tail["metrics"]["near_outlet_to_outlet_flux_ratio"]["mean"] <= 1.01

    controller_tail = _segment(controller, "tail_20pct_hard_gate")
    assert controller_tail["metrics"]["controller_saturation_fraction_run"]["max"] == 0.0
    assert "controller_authority_ratio" in controller_tail["metrics"]
    assert profile["x_profile_source_field"] == "x_profile_flux_samples"
    assert profile["segments"]


def test_step140_missing_inputs_emit_missing_input_report(tmp_path):
    from experiments.steps.step140_long_window_drift_forensics import run_step140_forensics

    missing_root = tmp_path / "missing_step139"
    output_dir = tmp_path / "out"
    summary = run_step140_forensics(missing_root, output_dir, force=True)

    assert summary["status"] == "missing_input"
    assert summary["missing_input"] is True
    assert summary["mechanism_summary_present"] is False
    assert summary["new_lbm_run_executed"] is False
    assert summary["new_parameter_tuning_executed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["mechanism_summary"] is None
    assert (output_dir / "step140_failure_mechanism_summary.json").is_file()


def test_step140_does_not_add_phase_or_selected96_runtime_surface():
    step121 = (ROOT / "experiments" / "steps" / "step121_lbm_boundary_real_campaign_and_gate_correction.py").read_text(
        encoding="utf-8"
    )
    parser = (ROOT / "experiments" / "steps" / "step140_long_window_drift_forensics.py").read_text(encoding="utf-8")

    assert "STEP140_LONG_WINDOW_DRIFT_FORENSICS_PHASE" not in step121
    assert "step121_step140" not in step121.lower()
    assert "STEP140_SUMMARY_RELATIVE_PATH" in step121
    assert "STEP141_DENSITY_FEEDBACK_ISOLATION_PHASE" in step121
    for forbidden in [
        "run_step120_row",
        "create_step120_lbm",
        "resolve_step121_phase_specs",
        "--phase",
        "selected-static",
        "selected96_duct",
        "selected96_static",
    ]:
        assert forbidden not in parser


def test_step139_reconciliation_records_actual_paths_and_commit_semantics():
    goal = (ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "139" / "goal.md").read_text(
        encoding="utf-8"
    )
    report = (ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "139" / "report.md").read_text(
        encoding="utf-8"
    )
    active = _read_json(ROOT / "docs" / "current" / "ACTIVE_CAMPAIGN.json")
    status = (ROOT / "docs" / "current" / "STATUS.md").read_text(encoding="utf-8")

    for actual_path in [
        "docs/GENERIC_SOLVER_ARCHITECTURE_CONTRACT.md",
        "docs/campaigns/fluent_duct_flap/fluent_official_local_execution_guard.md",
        "configs/fluent_official_2way_fsi_local_execution_schema.json",
        "configs/fluent_official_monitor_export_schema.json",
        "outputs/fluent_official_local_execution_prep/guard_report.json",
    ]:
        assert actual_path in goal
        assert actual_path in report

    for stale_path in [
        "docs/architecture/GENERIC_FSI_SOLVER_CONTRACT.md",
        "docs/architecture/BENCHMARK_ADAPTER_CONTRACT.md",
        "docs/architecture/VALIDATION_CLAIM_BOUNDARY.md",
        "fluent_official_local_execution_plan.md",
    ]:
        assert stale_path not in goal

    assert active["step139_code_commit_at_run"] == STEP139_RUN_COMMIT
    assert active["step141_code_commit_at_run"] == STEP141_RUN_COMMIT
    assert active["step143_code_commit_at_run"] == STEP143_RUN_COMMIT
    assert active["final_repository_head_after_step143_push"] == STEP143_FINAL_COMMIT
    assert active["current_code_commit"] == STEP143_FINAL_COMMIT
    assert active["code_commit_at_run"] == STEP143_FINAL_COMMIT
    assert active["repository_head_at_report"] == STEP143_FINAL_COMMIT
    assert "code_commit_at_run" in status
    assert STEP139_RUN_COMMIT in status
    assert STEP141_RUN_COMMIT in status


def test_committed_step140_outputs_exist_and_are_artifact_only():
    summary_path = STEP140_OUTPUT_ROOT / "step140_failure_mechanism_summary.json"
    assert summary_path.is_file()
    summary = _read_json(summary_path)

    assert summary["status"] == "mechanism_classified"
    assert summary["step"] == 140
    assert summary["source_step"] == 139
    assert summary["new_lbm_run_executed"] is False
    assert summary["new_parameter_tuning_executed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert len(summary["next_experiment_recommendations"]) <= 1
    for name in EXPECTED_REPORTS:
        assert (STEP140_OUTPUT_ROOT / name).is_file(), name

    tracked = _tracked_files()
    assert "experiments/steps/step140_long_window_drift_forensics.py" in tracked
    assert "experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py" in tracked


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _segment(report: dict, name: str) -> dict:
    return next(segment for segment in report["segments"] if segment["name"] == name)


def _tracked_files():
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return set(result.stdout.splitlines())
