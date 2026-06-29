import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step152_current_blocked_step151_blocks_without_solver_change(tmp_path):
    import experiments.steps.step152_apply_targeted_solver_fix as step152

    paths = write_step151_fixture(
        tmp_path,
        report_overrides={
            "status": "blocked_by_missing_error_localization",
            "source_step150_status": "missing_official_monitor",
            "source_top_bug_category": None,
            "requires_solver_patch": False,
        },
        plan_overrides={"status": "blocked_by_missing_error_localization", "actions": []},
        step150_overrides={"status": "missing_official_monitor"},
    )

    summary = step152.run_step152_apply_targeted_solver_fix(**paths, output_dir=tmp_path / "out", force=True)

    assert summary["step"] == 152
    assert summary["status"] == "blocked_by_missing_targeted_fix_plan"
    assert summary["source_step151_status"] == "blocked_by_missing_error_localization"
    assert summary["source_step150_status"] == "missing_official_monitor"
    assert summary["solver_code_modified"] is False
    assert summary["targeted_fix_applied"] is False
    assert summary["post_fix_step148_run_executed"] is False
    assert summary["post_fix_step150_comparison_executed"] is False
    assert summary["primary_metric_improved"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False


def test_step152_missing_step151_report_blocks(tmp_path):
    import experiments.steps.step152_apply_targeted_solver_fix as step152

    summary = step152.run_step152_apply_targeted_solver_fix(
        step151_report=tmp_path / "missing_step151_fix_report.json",
        step151_plan=tmp_path / "missing_step151_fix_plan.json",
        step151_error_delta=tmp_path / "missing_error_delta_report.json",
        step150_summary=tmp_path / "missing_step150_summary.json",
        output_dir=tmp_path / "out",
        force=True,
    )

    assert summary["status"] == "blocked_by_missing_targeted_fix_plan"
    assert "step151_report_missing" in summary["blocked_reasons"]
    assert summary["solver_code_modified"] is False
    assert summary["validation_claim_allowed"] is False


def test_step152_ready_report_without_top_category_blocks(tmp_path):
    import experiments.steps.step152_apply_targeted_solver_fix as step152

    paths = write_step151_fixture(
        tmp_path,
        report_overrides={"status": "targeted_fix_plan_ready", "source_top_bug_category": None},
        plan_overrides={"status": "targeted_fix_plan_ready", "source_top_bug_category": None},
    )

    summary = step152.run_step152_apply_targeted_solver_fix(**paths, output_dir=tmp_path / "out", force=True)

    assert summary["status"] == "blocked_by_missing_targeted_fix_plan"
    assert "source_top_bug_category_missing" in summary["blocked_reasons"]
    assert summary["solver_code_modified"] is False
    assert summary["targeted_fix_applied"] is False


def test_step152_unknown_category_requires_review_without_solver_change(tmp_path):
    import experiments.steps.step152_apply_targeted_solver_fix as step152

    paths = write_step151_fixture(
        tmp_path,
        report_overrides={
            "status": "targeted_fix_plan_ready",
            "source_top_bug_category": "unregistered_error",
        },
        plan_overrides={
            "status": "targeted_fix_plan_ready",
            "source_top_bug_category": "unregistered_error",
        },
    )

    summary = step152.run_step152_apply_targeted_solver_fix(**paths, output_dir=tmp_path / "out", force=True)

    assert summary["status"] == "blocked_by_unknown_bug_category"
    assert summary["requires_human_review"] is True
    assert summary["source_top_bug_category"] == "unregistered_error"
    assert summary["solver_code_modified"] is False
    assert summary["targeted_fix_applied"] is False
    assert summary["validation_claim_allowed"] is False


def test_step152_geometry_mapping_ready_plan_requires_patch_without_fake_apply(tmp_path):
    import experiments.steps.step152_apply_targeted_solver_fix as step152

    out_dir = tmp_path / "out"
    paths = write_step151_fixture(
        tmp_path,
        report_overrides={
            "status": "targeted_fix_plan_ready",
            "source_top_bug_category": "geometry_mapping_error",
        },
        plan_overrides={
            "status": "targeted_fix_plan_ready",
            "source_top_bug_category": "geometry_mapping_error",
        },
    )

    summary = step152.run_step152_apply_targeted_solver_fix(**paths, output_dir=out_dir, force=True)
    plan = read_json(out_dir / "step152_patch_plan.json")

    assert summary["status"] == "targeted_fix_patch_required"
    assert summary["source_top_bug_category"] == "geometry_mapping_error"
    assert summary["patch_implementation_present"] is False
    assert summary["solver_code_modified"] is False
    assert summary["targeted_fix_applied"] is False
    assert plan["source_top_bug_category"] == "geometry_mapping_error"
    assert "monitor point location" in " ".join(plan["priority_surfaces"])
    assert "tests/test_official_geometry_mapping_contract.py" in plan["planned_tests"]
    assert read_json(out_dir / "modified_modules_report.json")["modified_modules"] == []


def test_step152_monitor_extraction_ready_plan_requires_patch_without_fake_apply(tmp_path):
    import experiments.steps.step152_apply_targeted_solver_fix as step152

    out_dir = tmp_path / "out"
    paths = write_step151_fixture(
        tmp_path,
        report_overrides={
            "status": "targeted_fix_plan_ready",
            "source_top_bug_category": "monitor_extraction_error",
        },
        plan_overrides={
            "status": "targeted_fix_plan_ready",
            "source_top_bug_category": "monitor_extraction_error",
        },
    )

    summary = step152.run_step152_apply_targeted_solver_fix(**paths, output_dir=out_dir, force=True)
    plan = read_json(out_dir / "step152_patch_plan.json")

    assert summary["status"] == "targeted_fix_patch_required"
    assert summary["source_top_bug_category"] == "monitor_extraction_error"
    assert "flap-tip monitor point selection" in " ".join(plan["priority_surfaces"])
    assert "tests/test_fsi_monitor_extraction_contract.py" in plan["planned_tests"]
    assert summary["post_fix_step148_run_executed"] is False
    assert summary["post_fix_step150_comparison_executed"] is False
    assert read_json(out_dir / "error_delta_report.json")["primary_metric_improved"] is False


def test_step152_blocked_outputs_write_placeholders(tmp_path):
    import experiments.steps.step152_apply_targeted_solver_fix as step152

    paths = write_step151_fixture(
        tmp_path,
        report_overrides={"status": "blocked_by_missing_error_localization"},
        plan_overrides={"status": "blocked_by_missing_error_localization", "actions": []},
        step150_overrides={"status": "missing_official_monitor"},
    )

    summary = step152.run_step152_apply_targeted_solver_fix(**paths, output_dir=tmp_path / "out", force=True)

    assert summary["status"] == "blocked_by_missing_targeted_fix_plan"
    assert read_json(tmp_path / "out" / "post_fix_step148_summary.json")["post_fix_step148_run_executed"] is False
    assert read_json(tmp_path / "out" / "post_fix_step150_summary.json")["post_fix_step150_comparison_executed"] is False
    error_delta = read_json(tmp_path / "out" / "error_delta_report.json")
    assert error_delta["error_delta_report_present"] is True
    assert error_delta["primary_metric_improved"] is False
    assert error_delta["validation_claim_allowed"] is False


def write_step151_fixture(
    tmp_path: Path,
    report_overrides: dict | None = None,
    plan_overrides: dict | None = None,
    step150_overrides: dict | None = None,
):
    report = {
        "step": 151,
        "status": "targeted_fix_plan_ready",
        "source_step150_status": "error_localization_complete",
        "source_top_bug_category": "geometry_mapping_error",
        "requires_solver_patch": True,
        "targeted_fix_applied": False,
        "solver_code_modified": False,
        "post_fix_step148_run_executed": False,
        "post_fix_step150_comparison_executed": False,
        "primary_metric_improved": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    report.update(report_overrides or {})
    plan = {
        "step": 151,
        "status": "targeted_fix_plan_ready",
        "source_step150_status": report.get("source_step150_status"),
        "source_top_bug_category": report.get("source_top_bug_category"),
        "requires_solver_patch": report.get("requires_solver_patch", True),
        "targeted_fix_applied": False,
        "solver_code_modified": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    plan.update(plan_overrides or {})
    step150 = {
        "step": 150,
        "status": "error_localization_complete",
        "error_metrics_present": True,
        "solver_bug_hypotheses_present": True,
        "next_code_fix_step_identified": True,
        "top_bug_category": report.get("source_top_bug_category"),
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    step150.update(step150_overrides or {})

    paths = {
        "step151_report": tmp_path / "step151_fix_report.json",
        "step151_plan": tmp_path / "step151_fix_plan.json",
        "step151_error_delta": tmp_path / "step151_error_delta_report.json",
        "step150_summary": tmp_path / "step150_summary.json",
        "hypotheses": tmp_path / "solver_bug_hypotheses.json",
        "displacement_metrics": tmp_path / "displacement_error_metrics.json",
        "force_metrics": tmp_path / "force_error_metrics.json",
        "phase_lag_metrics": tmp_path / "phase_lag_metrics.json",
        "step148_summary": tmp_path / "solver_reproduction_summary.json",
    }
    write_json(paths["step151_report"], report)
    write_json(paths["step151_plan"], plan)
    write_json(
        paths["step151_error_delta"],
        {
            "step": 151,
            "status": "not_computed",
            "primary_metric_improved": False,
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    write_json(paths["step150_summary"], step150)
    write_json(
        paths["hypotheses"],
        {
            "status": "hypotheses_generated",
            "top_category": report.get("source_top_bug_category"),
            "hypotheses": [{"category": report.get("source_top_bug_category"), "score": 0.9}],
        },
    )
    write_json(paths["displacement_metrics"], {"status": "metrics_ready"})
    write_json(paths["force_metrics"], {"status": "metrics_ready"})
    write_json(paths["phase_lag_metrics"], {"status": "metrics_ready"})
    write_json(paths["step148_summary"], {"status": "solver_reproduction_complete", "solver_monitor_rows": 26})
    return paths


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
