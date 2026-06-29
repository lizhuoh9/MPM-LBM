import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step151_missing_step150_summary_blocks_without_solver_change(tmp_path):
    import experiments.steps.step151_targeted_solver_fix_from_official_error as step151

    out_dir = tmp_path / "out"
    summary = step151.run_step151_targeted_solver_fix(
        step150_summary=tmp_path / "missing_step150_summary.json",
        hypotheses=tmp_path / "missing_hypotheses.json",
        output_dir=out_dir,
        force=True,
    )

    assert summary["step"] == 151
    assert summary["status"] == "blocked_by_missing_error_localization"
    assert summary["solver_code_modified"] is False
    assert summary["targeted_fix_applied"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert read_json(out_dir / "post_fix_step148_summary.json")["post_fix_step148_run_executed"] is False
    assert read_json(out_dir / "post_fix_step150_summary.json")["post_fix_step150_comparison_executed"] is False
    assert read_json(out_dir / "error_delta_report.json")["primary_metric_improved"] is False


def test_step151_current_missing_official_step150_state_blocks(tmp_path):
    import experiments.steps.step151_targeted_solver_fix_from_official_error as step151

    step150_summary = tmp_path / "step150_summary.json"
    hypotheses = tmp_path / "solver_bug_hypotheses.json"
    write_json(
        step150_summary,
        {
            "step": 150,
            "status": "missing_official_monitor",
            "official_reference_loaded": False,
            "solver_monitor_loaded": True,
            "solver_monitor_rows": 26,
            "error_metrics_present": False,
            "solver_bug_hypotheses_present": False,
            "next_code_fix_step_identified": False,
            "top_bug_category": None,
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    write_json(hypotheses, {"status": "missing_official_monitor", "hypotheses": []})

    summary = step151.run_step151_targeted_solver_fix(
        step150_summary=step150_summary,
        hypotheses=hypotheses,
        output_dir=tmp_path / "out",
        force=True,
    )

    assert summary["status"] == "blocked_by_missing_error_localization"
    assert summary["source_step150_status"] == "missing_official_monitor"
    assert "Step150 has no real official comparison" in summary["reason"]
    assert summary["solver_code_modified"] is False
    assert summary["error_delta_report_present"] is True


def test_step151_complete_step150_without_hypotheses_blocks(tmp_path):
    summary = run_with_step150_fixture(
        tmp_path,
        {
            "status": "error_localization_complete",
            "solver_bug_hypotheses_present": False,
            "next_code_fix_step_identified": True,
            "top_bug_category": "geometry_mapping_error",
        },
        {"status": "hypotheses_generated", "hypotheses": [], "top_category": "geometry_mapping_error"},
    )

    assert summary["status"] == "blocked_by_missing_error_localization"
    assert summary["solver_code_modified"] is False
    assert "solver_bug_hypotheses_present" in " ".join(summary["blocked_reasons"])


def test_step151_complete_step150_without_top_category_blocks(tmp_path):
    summary = run_with_step150_fixture(
        tmp_path,
        {
            "status": "error_localization_complete",
            "solver_bug_hypotheses_present": True,
            "next_code_fix_step_identified": True,
            "top_bug_category": None,
        },
        {"status": "hypotheses_generated", "hypotheses": [{"category": "geometry_mapping_error"}]},
    )

    assert summary["status"] == "blocked_by_missing_error_localization"
    assert summary["solver_code_modified"] is False
    assert "top_bug_category" in " ".join(summary["blocked_reasons"])


def test_step151_unknown_top_category_requires_review_without_solver_change(tmp_path):
    summary = run_with_step150_fixture(
        tmp_path,
        {
            "status": "error_localization_complete",
            "solver_bug_hypotheses_present": True,
            "next_code_fix_step_identified": True,
            "top_bug_category": "unregistered_error",
        },
        {
            "status": "hypotheses_generated",
            "top_category": "unregistered_error",
            "hypotheses": [{"category": "unregistered_error", "score": 0.9}],
        },
    )

    assert summary["status"] == "blocked_by_unknown_bug_category"
    assert summary["solver_code_modified"] is False
    assert summary["requires_human_review"] is True
    assert summary["validation_claim_allowed"] is False


def test_step151_geometry_mapping_complete_input_writes_targeted_plan(tmp_path):
    out_dir = tmp_path / "out"
    summary = run_with_step150_fixture(
        tmp_path,
        {
            "status": "error_localization_complete",
            "solver_bug_hypotheses_present": True,
            "next_code_fix_step_identified": True,
            "top_bug_category": "geometry_mapping_error",
        },
        {
            "status": "hypotheses_generated",
            "top_category": "geometry_mapping_error",
            "hypotheses": [{"category": "geometry_mapping_error", "score": 0.95}],
        },
        output_dir=out_dir,
    )

    plan = read_json(out_dir / "step151_fix_plan.json")
    assert summary["status"] == "targeted_fix_plan_ready"
    assert summary["source_top_bug_category"] == "geometry_mapping_error"
    assert summary["solver_code_modified"] is False
    assert summary["requires_solver_patch"] is True
    assert plan["official_mesh_metadata_mapped"] is False
    assert plan["proxy_geometry_gap_reported"] is True
    assert "monitor point location" in " ".join(plan["priority_surfaces"])
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False


def test_step151_monitor_extraction_complete_input_writes_targeted_plan(tmp_path):
    out_dir = tmp_path / "out"
    summary = run_with_step150_fixture(
        tmp_path,
        {
            "status": "error_localization_complete",
            "solver_bug_hypotheses_present": True,
            "next_code_fix_step_identified": True,
            "top_bug_category": "monitor_extraction_error",
        },
        {
            "status": "hypotheses_generated",
            "top_category": "monitor_extraction_error",
            "hypotheses": [{"category": "monitor_extraction_error", "score": 0.8}],
        },
        output_dir=out_dir,
    )

    plan = read_json(out_dir / "step151_fix_plan.json")
    assert summary["status"] == "targeted_fix_plan_ready"
    assert summary["source_top_bug_category"] == "monitor_extraction_error"
    assert "flap-tip monitor point selection" in " ".join(plan["priority_surfaces"])
    assert summary["post_fix_step148_run_executed"] is False
    assert summary["post_fix_step150_comparison_executed"] is False
    assert read_json(out_dir / "error_delta_report.json")["primary_metric_improved"] is False


def run_with_step150_fixture(tmp_path: Path, step150_overrides: dict, hypotheses_payload: dict, output_dir=None):
    import experiments.steps.step151_targeted_solver_fix_from_official_error as step151

    step150_summary = tmp_path / "step150_summary.json"
    hypotheses = tmp_path / "solver_bug_hypotheses.json"
    payload = {
        "step": 150,
        "status": "error_localization_complete",
        "official_reference_loaded": True,
        "solver_monitor_loaded": True,
        "error_metrics_present": True,
        "solver_bug_hypotheses_present": True,
        "next_code_fix_step_identified": True,
        "top_bug_category": "geometry_mapping_error",
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    payload.update(step150_overrides)
    write_json(step150_summary, payload)
    write_json(hypotheses, hypotheses_payload)

    return step151.run_step151_targeted_solver_fix(
        step150_summary=step150_summary,
        hypotheses=hypotheses,
        displacement_metrics=tmp_path / "displacement_error_metrics.json",
        force_metrics=tmp_path / "force_error_metrics.json",
        phase_lag_metrics=tmp_path / "phase_lag_metrics.json",
        step148_summary=tmp_path / "solver_reproduction_summary.json",
        geometry_report=tmp_path / "geometry_mapping_report.json",
        unit_report=tmp_path / "unit_mapping_report.json",
        coupling_report=tmp_path / "coupling_diagnostics_summary.json",
        output_dir=output_dir or (tmp_path / "out"),
        force=True,
    )


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
