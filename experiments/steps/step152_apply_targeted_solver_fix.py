from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.steps.step149_fluent_official_vs_our_solver_error_localization import BUG_CATEGORIES
from experiments.steps.step151_targeted_solver_fix_from_official_error import CATEGORY_PLANS


STEP = 152
DEFAULT_STEP151_REPORT = Path("outputs") / "step151_targeted_solver_fix" / "step151_fix_report.json"
DEFAULT_STEP151_PLAN = Path("outputs") / "step151_targeted_solver_fix" / "step151_fix_plan.json"
DEFAULT_STEP151_ERROR_DELTA = Path("outputs") / "step151_targeted_solver_fix" / "error_delta_report.json"
DEFAULT_STEP150_SUMMARY = Path("outputs") / "step150_official_monitor_error_localization" / "error_localization_summary.json"
DEFAULT_HYPOTHESES = Path("outputs") / "step150_official_monitor_error_localization" / "solver_bug_hypotheses.json"
DEFAULT_DISPLACEMENT_METRICS = (
    Path("outputs") / "step150_official_monitor_error_localization" / "displacement_error_metrics.json"
)
DEFAULT_FORCE_METRICS = Path("outputs") / "step150_official_monitor_error_localization" / "force_error_metrics.json"
DEFAULT_PHASE_LAG_METRICS = Path("outputs") / "step150_official_monitor_error_localization" / "phase_lag_metrics.json"
DEFAULT_STEP148_SUMMARY = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_reproduction_summary.json"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step152_apply_targeted_solver_fix"

OUTPUT_FILES = [
    "step152_apply_summary.json",
    "step152_patch_plan.json",
    "modified_modules_report.json",
    "post_fix_step148_summary.json",
    "post_fix_step150_summary.json",
    "error_delta_report.json",
    "report.md",
]


def run_step152_apply_targeted_solver_fix(
    step151_report: Path | str = DEFAULT_STEP151_REPORT,
    step151_plan: Path | str = DEFAULT_STEP151_PLAN,
    step151_error_delta: Path | str = DEFAULT_STEP151_ERROR_DELTA,
    step150_summary: Path | str = DEFAULT_STEP150_SUMMARY,
    hypotheses: Path | str = DEFAULT_HYPOTHESES,
    displacement_metrics: Path | str = DEFAULT_DISPLACEMENT_METRICS,
    force_metrics: Path | str = DEFAULT_FORCE_METRICS,
    phase_lag_metrics: Path | str = DEFAULT_PHASE_LAG_METRICS,
    step148_summary: Path | str = DEFAULT_STEP148_SUMMARY,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    paths = {
        "step151_report": Path(step151_report),
        "step151_plan": Path(step151_plan),
        "step151_error_delta": Path(step151_error_delta),
        "step150_summary": Path(step150_summary),
        "hypotheses": Path(hypotheses),
        "displacement_metrics": Path(displacement_metrics),
        "force_metrics": Path(force_metrics),
        "phase_lag_metrics": Path(phase_lag_metrics),
        "step148_summary": Path(step148_summary),
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if force:
        _clear_known_outputs(output_dir)

    source = {
        "step151_report": _read_json_optional(paths["step151_report"]),
        "step151_plan": _read_json_optional(paths["step151_plan"]),
        "step151_error_delta": _read_json_optional(paths["step151_error_delta"]),
        "step150_summary": _read_json_optional(paths["step150_summary"]),
        "hypotheses": _read_json_optional(paths["hypotheses"]),
        "displacement_metrics": _read_json_optional(paths["displacement_metrics"]),
        "force_metrics": _read_json_optional(paths["force_metrics"]),
        "phase_lag_metrics": _read_json_optional(paths["phase_lag_metrics"]),
        "step148_summary": _read_json_optional(paths["step148_summary"]),
    }

    blocked_reasons = _precondition_failures(source)
    if blocked_reasons:
        return _write_blocked_outputs(output_dir, paths, source, blocked_reasons)

    top_category = _source_top_bug_category(source)
    if top_category not in BUG_CATEGORIES or top_category not in CATEGORY_PLANS:
        return _write_unknown_category_outputs(output_dir, paths, source, top_category)

    return _write_patch_required_outputs(output_dir, paths, source, top_category)


def _precondition_failures(source: dict[str, Any]) -> list[str]:
    report = source["step151_report"]
    plan = source["step151_plan"]
    step150 = source["step150_summary"]
    failures = []
    if report is None:
        failures.append("step151_report_missing")
    if plan is None:
        failures.append("step151_plan_missing")
    if report is None:
        return failures

    if report.get("status") != "targeted_fix_plan_ready":
        failures.append(f"source_step151_status={report.get('status')}")
    if plan is not None and plan.get("status") != "targeted_fix_plan_ready":
        failures.append(f"source_step151_plan_status={plan.get('status')}")
    if _source_step150_status(source) != "error_localization_complete":
        failures.append(f"source_step150_status={_source_step150_status(source)}")
    if not _source_top_bug_category(source):
        failures.append("source_top_bug_category_missing")
    if not bool(report.get("requires_solver_patch", False)):
        failures.append("requires_solver_patch=false")
    if bool(report.get("solver_code_modified", False)):
        failures.append("pre_step152_solver_code_modified=true")
    if bool(report.get("targeted_fix_applied", False)):
        failures.append("pre_step152_targeted_fix_applied=true")
    if step150 is not None and not bool(step150.get("error_metrics_present", False)):
        failures.append("step150_error_metrics_present=false")
    if step150 is not None and not bool(step150.get("solver_bug_hypotheses_present", False)):
        failures.append("step150_solver_bug_hypotheses_present=false")
    return failures


def _write_blocked_outputs(
    output_dir: Path,
    paths: dict[str, Path],
    source: dict[str, Any],
    blocked_reasons: list[str],
) -> dict[str, Any]:
    summary = _base_summary(paths, source)
    summary.update(
        {
            "status": "blocked_by_missing_targeted_fix_plan",
            "reason": "Step151 did not produce a ready targeted solver-fix plan",
            "blocked_reasons": blocked_reasons,
            "requires_solver_patch": False,
            "requires_human_review": False,
            "patch_implementation_present": False,
            "targeted_fix_applied": False,
            "solver_code_modified": False,
            "modified_modules": [],
            "planned_modules": [],
            "planned_tests": [],
            "new_tests_added": False,
            "post_fix_step148_run_executed": False,
            "post_fix_step150_comparison_executed": False,
            "error_delta_report_present": True,
            "primary_metric_improved": False,
        }
    )
    plan = {
        "step": STEP,
        "status": summary["status"],
        "reason": summary["reason"],
        "blocked_reasons": blocked_reasons,
        "source_step151_status": summary["source_step151_status"],
        "source_step150_status": summary["source_step150_status"],
        "source_top_bug_category": summary["source_top_bug_category"],
        "actions": [],
        "patch_implementation_present": False,
        "solver_code_modified": False,
        "targeted_fix_applied": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    _write_all_outputs(output_dir, summary, plan)
    return summary


def _write_unknown_category_outputs(
    output_dir: Path,
    paths: dict[str, Path],
    source: dict[str, Any],
    top_category: str | None,
) -> dict[str, Any]:
    summary = _base_summary(paths, source)
    summary.update(
        {
            "status": "blocked_by_unknown_bug_category",
            "reason": "Step151 produced an unregistered top bug category",
            "blocked_reasons": [f"unknown_top_bug_category={top_category}"],
            "source_top_bug_category": top_category,
            "requires_solver_patch": False,
            "requires_human_review": True,
            "patch_implementation_present": False,
            "targeted_fix_applied": False,
            "solver_code_modified": False,
            "modified_modules": [],
            "planned_modules": [],
            "planned_tests": [],
            "new_tests_added": False,
            "post_fix_step148_run_executed": False,
            "post_fix_step150_comparison_executed": False,
            "error_delta_report_present": True,
            "primary_metric_improved": False,
        }
    )
    plan = {
        "step": STEP,
        "status": summary["status"],
        "reason": summary["reason"],
        "source_step151_status": summary["source_step151_status"],
        "source_step150_status": summary["source_step150_status"],
        "source_top_bug_category": top_category,
        "actions": [],
        "requires_human_review": True,
        "patch_implementation_present": False,
        "solver_code_modified": False,
        "targeted_fix_applied": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    _write_all_outputs(output_dir, summary, plan)
    return summary


def _write_patch_required_outputs(
    output_dir: Path,
    paths: dict[str, Path],
    source: dict[str, Any],
    top_category: str,
) -> dict[str, Any]:
    category_plan = dict(CATEGORY_PLANS[top_category])
    summary = _base_summary(paths, source)
    summary.update(
        {
            "status": "targeted_fix_patch_required",
            "reason": (
                "Step151 targeted plan is ready; Step152 requires an explicit "
                "category-specific patch implementation before solver code may be claimed modified"
            ),
            "blocked_reasons": [],
            "source_top_bug_category": top_category,
            "requires_solver_patch": True,
            "requires_human_review": False,
            "patch_implementation_present": False,
            "targeted_fix_applied": False,
            "solver_code_modified": False,
            "modified_modules": [],
            "planned_modules": list(category_plan.get("planned_modules", [])),
            "planned_tests": list(category_plan.get("planned_tests", [])),
            "new_tests_added": False,
            "post_fix_step148_run_executed": False,
            "post_fix_step150_comparison_executed": False,
            "error_delta_report_present": True,
            "primary_metric_improved": False,
        }
    )
    plan = {
        "step": STEP,
        "status": summary["status"],
        "reason": summary["reason"],
        "source_step151_status": summary["source_step151_status"],
        "source_step150_status": summary["source_step150_status"],
        "source_top_bug_category": top_category,
        "requires_solver_patch": True,
        "patch_implementation_present": False,
        "targeted_fix_applied": False,
        "solver_code_modified": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    plan.update(category_plan)
    _write_all_outputs(output_dir, summary, plan)
    return summary


def _base_summary(paths: dict[str, Path], source: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": STEP,
        "step151_report": _display_path(paths["step151_report"]),
        "step151_plan": _display_path(paths["step151_plan"]),
        "step151_error_delta": _display_path(paths["step151_error_delta"]),
        "step150_summary": _display_path(paths["step150_summary"]),
        "hypotheses": _display_path(paths["hypotheses"]),
        "displacement_metrics": _display_path(paths["displacement_metrics"]),
        "force_metrics": _display_path(paths["force_metrics"]),
        "phase_lag_metrics": _display_path(paths["phase_lag_metrics"]),
        "step148_summary": _display_path(paths["step148_summary"]),
        "source_step151_status": _status(source["step151_report"]),
        "source_step151_plan_status": _status(source["step151_plan"]),
        "source_step150_status": _source_step150_status(source),
        "source_top_bug_category": _source_top_bug_category(source),
        "source_step151_error_delta_status": _status(source["step151_error_delta"]),
        "source_step150_error_metrics_present": _bool_field(source["step150_summary"], "error_metrics_present"),
        "source_step150_solver_bug_hypotheses_present": _bool_field(
            source["step150_summary"], "solver_bug_hypotheses_present"
        ),
        "source_displacement_metrics_status": _status(source["displacement_metrics"]),
        "source_force_metrics_status": _status(source["force_metrics"]),
        "source_phase_lag_metrics_status": _status(source["phase_lag_metrics"]),
        "source_step148_status": _status(source["step148_summary"]),
        "fabricated_metrics_used": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _write_all_outputs(output_dir: Path, summary: dict[str, Any], plan: dict[str, Any]) -> None:
    _write_json(output_dir / "step152_apply_summary.json", summary)
    _write_json(output_dir / "step152_patch_plan.json", plan)
    _write_json(
        output_dir / "modified_modules_report.json",
        {
            "step": STEP,
            "status": "not_modified",
            "source_step151_status": summary.get("source_step151_status"),
            "source_top_bug_category": summary.get("source_top_bug_category"),
            "solver_code_modified": False,
            "targeted_fix_applied": False,
            "modified_modules": [],
            "new_tests_added": False,
            "reason": "No Step152 category-specific solver patch has been applied",
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    _write_json(
        output_dir / "post_fix_step148_summary.json",
        {
            "step": STEP,
            "status": "not_executed",
            "source_step151_status": summary.get("source_step151_status"),
            "post_fix_step148_run_executed": False,
            "reason": "Step152 has not applied a solver patch",
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    _write_json(
        output_dir / "post_fix_step150_summary.json",
        {
            "step": STEP,
            "status": "not_executed",
            "source_step151_status": summary.get("source_step151_status"),
            "post_fix_step150_comparison_executed": False,
            "reason": "Step152 has not applied a solver patch",
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    _write_json(
        output_dir / "error_delta_report.json",
        {
            "step": STEP,
            "status": "not_computed",
            "source_step151_status": summary.get("source_step151_status"),
            "source_step150_status": summary.get("source_step150_status"),
            "source_top_bug_category": summary.get("source_top_bug_category"),
            "error_delta_report_present": True,
            "primary_metric_improved": False,
            "reason": "No post-fix Step148/Step150 rerun has been executed",
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    _write_report(output_dir, summary, plan)


def _write_report(output_dir: Path, summary: dict[str, Any], plan: dict[str, Any]) -> None:
    lines = [
        "# Step152 Apply Targeted Solver Fix",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Source Step151 status: `{summary.get('source_step151_status')}`",
        f"- Source Step150 status: `{summary.get('source_step150_status')}`",
        f"- Source top bug category: `{summary.get('source_top_bug_category')}`",
        f"- Patch implementation present: `{summary.get('patch_implementation_present')}`",
        f"- Solver code modified: `{summary.get('solver_code_modified')}`",
        f"- Targeted fix applied: `{summary.get('targeted_fix_applied')}`",
        f"- Post-fix Step148 run executed: `{summary.get('post_fix_step148_run_executed')}`",
        f"- Post-fix Step150 comparison executed: `{summary.get('post_fix_step150_comparison_executed')}`",
        f"- Primary metric improved: `{summary.get('primary_metric_improved')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        f"- Selected96 execution allowed: `{summary.get('selected96_execution_allowed')}`",
        "",
        "Step152 only acts after Step151 has produced a real targeted fix plan from Step150 official error localization.",
        "If Step151 is blocked, Step152 writes blocked artifacts and does not modify solver runtime code.",
    ]
    priority_surfaces = plan.get("priority_surfaces") or []
    if priority_surfaces:
        lines.append("")
        lines.append("Priority surfaces:")
        for item in priority_surfaces:
            lines.append(f"- {item}")
    planned_tests = plan.get("planned_tests") or []
    if planned_tests:
        lines.append("")
        lines.append("Planned tests:")
        for item in planned_tests:
            lines.append(f"- {item}")
    blocked_reasons = summary.get("blocked_reasons") or []
    if blocked_reasons:
        lines.append("")
        lines.append("Blocked reasons:")
        for item in blocked_reasons:
            lines.append(f"- {item}")
    text = "\n".join(lines) + "\n"
    output_report = output_dir / "report.md"
    output_report.write_text(text, encoding="utf-8")
    if _is_default_output_dir(output_dir):
        doc_report = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "152" / "report.md"
        doc_report.parent.mkdir(parents=True, exist_ok=True)
        doc_report.write_text(text, encoding="utf-8")


def _source_step150_status(source: dict[str, Any]) -> str | None:
    report = source.get("step151_report")
    plan = source.get("step151_plan")
    step150 = source.get("step150_summary")
    for payload in (report, plan, step150):
        if isinstance(payload, dict):
            status = payload.get("source_step150_status") or payload.get("status")
            if status:
                return str(status)
    return None


def _source_top_bug_category(source: dict[str, Any]) -> str | None:
    report = source.get("step151_report")
    plan = source.get("step151_plan")
    step150 = source.get("step150_summary")
    hypotheses = source.get("hypotheses")
    for payload in (report, plan, step150, hypotheses):
        if isinstance(payload, dict):
            category = payload.get("source_top_bug_category") or payload.get("top_bug_category") or payload.get("top_category")
            if category:
                return str(category)
    return None


def _status(payload: Any) -> str | None:
    return payload.get("status") if isinstance(payload, dict) else None


def _bool_field(payload: Any, field: str) -> bool:
    return bool(payload.get(field, False)) if isinstance(payload, dict) else False


def _clear_known_outputs(output_dir: Path) -> None:
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            path.unlink()


def _read_json_optional(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _display_path(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except Exception:
        return str(path)


def _is_default_output_dir(output_dir: Path) -> bool:
    try:
        return output_dir.resolve() == (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()
    except Exception:
        return False


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step151-report", type=Path, default=DEFAULT_STEP151_REPORT)
    parser.add_argument("--step151-plan", type=Path, default=DEFAULT_STEP151_PLAN)
    parser.add_argument("--step151-error-delta", type=Path, default=DEFAULT_STEP151_ERROR_DELTA)
    parser.add_argument("--step150-summary", type=Path, default=DEFAULT_STEP150_SUMMARY)
    parser.add_argument("--hypotheses", type=Path, default=DEFAULT_HYPOTHESES)
    parser.add_argument("--displacement-metrics", type=Path, default=DEFAULT_DISPLACEMENT_METRICS)
    parser.add_argument("--force-metrics", type=Path, default=DEFAULT_FORCE_METRICS)
    parser.add_argument("--phase-lag-metrics", type=Path, default=DEFAULT_PHASE_LAG_METRICS)
    parser.add_argument("--step148-summary", type=Path, default=DEFAULT_STEP148_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step152_apply_targeted_solver_fix(
        step151_report=args.step151_report,
        step151_plan=args.step151_plan,
        step151_error_delta=args.step151_error_delta,
        step150_summary=args.step150_summary,
        hypotheses=args.hypotheses,
        displacement_metrics=args.displacement_metrics,
        force_metrics=args.force_metrics,
        phase_lag_metrics=args.phase_lag_metrics,
        step148_summary=args.step148_summary,
        output_dir=args.output_dir,
        force=args.force,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
