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


STEP = 151
DEFAULT_STEP150_SUMMARY = Path("outputs") / "step150_official_monitor_error_localization" / "error_localization_summary.json"
DEFAULT_HYPOTHESES = Path("outputs") / "step150_official_monitor_error_localization" / "solver_bug_hypotheses.json"
DEFAULT_DISPLACEMENT_METRICS = Path("outputs") / "step150_official_monitor_error_localization" / "displacement_error_metrics.json"
DEFAULT_FORCE_METRICS = Path("outputs") / "step150_official_monitor_error_localization" / "force_error_metrics.json"
DEFAULT_PHASE_LAG_METRICS = Path("outputs") / "step150_official_monitor_error_localization" / "phase_lag_metrics.json"
DEFAULT_STEP148_SUMMARY = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_reproduction_summary.json"
DEFAULT_GEOMETRY_REPORT = Path("outputs") / "step148_our_solver_fluent_official_case" / "geometry_mapping_report.json"
DEFAULT_UNIT_REPORT = Path("outputs") / "step148_our_solver_fluent_official_case" / "unit_mapping_report.json"
DEFAULT_COUPLING_REPORT = Path("outputs") / "step148_our_solver_fluent_official_case" / "coupling_diagnostics_summary.json"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step151_targeted_solver_fix"

OUTPUT_FILES = [
    "step151_fix_plan.json",
    "step151_fix_report.json",
    "post_fix_step148_summary.json",
    "post_fix_step150_summary.json",
    "error_delta_report.json",
    "report.md",
]

CATEGORY_PLANS: dict[str, dict[str, Any]] = {
    "geometry_mapping_error": {
        "priority_surfaces": [
            "official mesh/proxy geometry mapping",
            "flap dimensions",
            "flap base/fixed constraint",
            "monitor point location",
            "duct height/length/thickness",
            "coordinate frame",
        ],
        "planned_reports": ["geometry_mapping_report.json", "official_geometry_gap_report.json"],
        "planned_tests": ["tests/test_official_geometry_mapping_contract.py"],
        "planned_modules": [
            "experiments/steps/step148_our_solver_fluent_official_case_reproduction.py",
            "src/mpm_lbm/sim/runtime_geometry",
        ],
        "official_mesh_metadata_mapped": False,
        "proxy_geometry_gap_reported": True,
        "monitor_point_mapping_error_reduced": False,
    },
    "unit_mapping_error": {
        "priority_surfaces": [
            "length scaling",
            "force scaling",
            "time-step scaling",
            "density and material units",
        ],
        "planned_reports": ["unit_mapping_fix_report.json"],
        "planned_tests": ["tests/test_fsi_time_mapping_contract.py"],
        "planned_modules": ["src/mpm_lbm/sim/units", "src/mpm_lbm/sim/drivers/fsi_config.py"],
    },
    "fluid_boundary_error": {
        "priority_surfaces": [
            "duct inlet/outlet boundary semantics",
            "wall treatment",
            "flow-rate target",
            "pressure/velocity boundary consistency",
        ],
        "planned_reports": ["fluid_boundary_fix_report.json"],
        "planned_tests": ["tests/test_fsi_monitor_extraction_contract.py"],
        "planned_modules": ["src/mpm_lbm/sim/lbm"],
    },
    "structural_model_error": {
        "priority_surfaces": [
            "MPM Young's modulus",
            "solid density",
            "damping",
            "flap thickness / mass / volume",
            "fixed-base mask",
            "material unit scaling",
        ],
        "planned_reports": ["structural_mapping_fix_report.json"],
        "planned_tests": ["tests/test_fsi_time_mapping_contract.py"],
        "planned_modules": ["src/mpm_lbm/sim/mpm", "src/mpm_lbm/sim/drivers/fsi_config.py"],
    },
    "coupling_force_transfer_error": {
        "priority_surfaces": [
            "fluid force sign convention",
            "force area weighting",
            "reaction force accumulation",
            "force-to-particle distribution",
            "force units",
            "force monitor extraction",
        ],
        "planned_reports": ["coupling_force_transfer_fix_report.json"],
        "planned_tests": ["tests/test_fsi_force_transfer_units.py"],
        "planned_modules": ["src/mpm_lbm/sim/coupling", "src/mpm_lbm/sim/lbm"],
    },
    "solid_to_fluid_motion_error": {
        "priority_surfaces": [
            "solid boundary velocity projection",
            "moving-boundary interpolation",
            "solid-to-fluid displacement transfer",
            "coupling stencil support",
        ],
        "planned_reports": ["solid_to_fluid_motion_fix_report.json"],
        "planned_tests": ["tests/test_fsi_monitor_extraction_contract.py"],
        "planned_modules": ["src/mpm_lbm/sim/coupling", "src/mpm_lbm/sim/drivers/fsi_driver.py"],
    },
    "time_integration_or_subcycling_error": {
        "priority_surfaces": [
            "FSI coupling interval",
            "LBM steps per official FSI time",
            "MPM dt",
            "substep force accumulation",
            "monitor sampling time",
        ],
        "planned_reports": ["time_mapping_fix_report.json"],
        "planned_tests": ["tests/test_fsi_time_mapping_contract.py"],
        "planned_modules": ["src/mpm_lbm/sim/drivers/fsi_driver.py", "src/mpm_lbm/sim/drivers/fsi_config.py"],
    },
    "monitor_extraction_error": {
        "priority_surfaces": [
            "flap-tip monitor point selection",
            "component direction",
            "total displacement definition",
            "force component/magnitude definition",
            "CSV extraction alignment",
        ],
        "planned_reports": ["monitor_extraction_fix_report.json"],
        "planned_tests": ["tests/test_fsi_monitor_extraction_contract.py"],
        "planned_modules": ["experiments/steps/step148_our_solver_fluent_official_case_reproduction.py"],
    },
    "numerical_stability_error": {
        "priority_surfaces": [
            "finite-state monitors",
            "solver stability counters",
            "coupling residual growth",
            "time-window consistency",
        ],
        "planned_reports": ["numerical_stability_fix_report.json"],
        "planned_tests": ["tests/test_fsi_time_mapping_contract.py"],
        "planned_modules": ["src/mpm_lbm/sim/drivers", "src/mpm_lbm/sim/diagnostics"],
    },
}


def run_step151_targeted_solver_fix(
    step150_summary: Path | str = DEFAULT_STEP150_SUMMARY,
    hypotheses: Path | str = DEFAULT_HYPOTHESES,
    displacement_metrics: Path | str = DEFAULT_DISPLACEMENT_METRICS,
    force_metrics: Path | str = DEFAULT_FORCE_METRICS,
    phase_lag_metrics: Path | str = DEFAULT_PHASE_LAG_METRICS,
    step148_summary: Path | str = DEFAULT_STEP148_SUMMARY,
    geometry_report: Path | str = DEFAULT_GEOMETRY_REPORT,
    unit_report: Path | str = DEFAULT_UNIT_REPORT,
    coupling_report: Path | str = DEFAULT_COUPLING_REPORT,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    paths = {
        "step150_summary": Path(step150_summary),
        "hypotheses": Path(hypotheses),
        "displacement_metrics": Path(displacement_metrics),
        "force_metrics": Path(force_metrics),
        "phase_lag_metrics": Path(phase_lag_metrics),
        "step148_summary": Path(step148_summary),
        "geometry_report": Path(geometry_report),
        "unit_report": Path(unit_report),
        "coupling_report": Path(coupling_report),
    }
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if force:
        _clear_known_outputs(output_dir)

    source = _read_json_optional(paths["step150_summary"])
    source_hypotheses = _read_json_optional(paths["hypotheses"]) or {}
    metrics = {
        "displacement": _read_json_optional(paths["displacement_metrics"]),
        "force": _read_json_optional(paths["force_metrics"]),
        "phase_lag": _read_json_optional(paths["phase_lag_metrics"]),
        "step148": _read_json_optional(paths["step148_summary"]),
        "geometry": _read_json_optional(paths["geometry_report"]),
        "unit": _read_json_optional(paths["unit_report"]),
        "coupling": _read_json_optional(paths["coupling_report"]),
    }

    blocked_reasons = _precondition_failures(source, source_hypotheses)
    if blocked_reasons:
        return _write_blocked_outputs(output_dir, paths, source, source_hypotheses, metrics, blocked_reasons)

    top_category = _top_category(source, source_hypotheses)
    if top_category not in BUG_CATEGORIES:
        return _write_unknown_category_outputs(output_dir, paths, source, source_hypotheses, metrics, top_category)

    return _write_plan_ready_outputs(output_dir, paths, source, source_hypotheses, metrics, top_category)


def _precondition_failures(source: dict[str, Any] | None, hypotheses: dict[str, Any]) -> list[str]:
    if source is None:
        return ["step150_summary_missing"]
    failures = []
    if source.get("status") != "error_localization_complete":
        failures.append(f"source_step150_status={source.get('status')}")
    if not bool(source.get("error_metrics_present", False)):
        failures.append("error_metrics_present=false")
    if not bool(source.get("solver_bug_hypotheses_present", False)):
        failures.append("solver_bug_hypotheses_present=false")
    if not bool(source.get("next_code_fix_step_identified", False)):
        failures.append("next_code_fix_step_identified=false")
    if not _top_category(source, hypotheses):
        failures.append("top_bug_category_missing")
    if not hypotheses.get("hypotheses"):
        failures.append("hypotheses_missing")
    return failures


def _top_category(source: dict[str, Any] | None, hypotheses: dict[str, Any]) -> str | None:
    if source is None:
        return None
    top = source.get("top_bug_category") or hypotheses.get("top_category")
    return str(top) if top else None


def _write_blocked_outputs(
    output_dir: Path,
    paths: dict[str, Path],
    source: dict[str, Any] | None,
    hypotheses: dict[str, Any],
    metrics: dict[str, Any],
    blocked_reasons: list[str],
) -> dict[str, Any]:
    summary = _base_summary(paths, source, hypotheses, metrics)
    summary.update(
        {
            "status": "blocked_by_missing_error_localization",
            "reason": "Step150 has no real official comparison",
            "blocked_reasons": blocked_reasons,
            "source_top_bug_category": _top_category(source, hypotheses),
            "requires_solver_patch": False,
            "requires_human_review": False,
            "targeted_fix_applied": False,
            "solver_code_modified": False,
            "modified_modules": [],
            "planned_modules": [],
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
        "actions": [],
        "solver_code_modified": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    _write_all_outputs(output_dir, summary, plan)
    return summary


def _write_unknown_category_outputs(
    output_dir: Path,
    paths: dict[str, Path],
    source: dict[str, Any],
    hypotheses: dict[str, Any],
    metrics: dict[str, Any],
    top_category: str | None,
) -> dict[str, Any]:
    summary = _base_summary(paths, source, hypotheses, metrics)
    summary.update(
        {
            "status": "blocked_by_unknown_bug_category",
            "reason": "Step150 produced an unregistered top bug category",
            "blocked_reasons": [f"unknown_top_bug_category={top_category}"],
            "source_top_bug_category": top_category,
            "requires_solver_patch": False,
            "requires_human_review": True,
            "targeted_fix_applied": False,
            "solver_code_modified": False,
            "modified_modules": [],
            "planned_modules": [],
            "post_fix_step148_run_executed": False,
            "post_fix_step150_comparison_executed": False,
            "error_delta_report_present": True,
            "primary_metric_improved": False,
        }
    )
    plan = {
        "step": STEP,
        "status": summary["status"],
        "source_top_bug_category": top_category,
        "actions": [],
        "requires_human_review": True,
        "solver_code_modified": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    _write_all_outputs(output_dir, summary, plan)
    return summary


def _write_plan_ready_outputs(
    output_dir: Path,
    paths: dict[str, Path],
    source: dict[str, Any],
    hypotheses: dict[str, Any],
    metrics: dict[str, Any],
    top_category: str,
) -> dict[str, Any]:
    category_plan = dict(CATEGORY_PLANS[top_category])
    summary = _base_summary(paths, source, hypotheses, metrics)
    summary.update(
        {
            "status": "targeted_fix_plan_ready",
            "reason": "Step150 completed official error localization; targeted solver patch is planned but not applied in this runner",
            "blocked_reasons": [],
            "source_top_bug_category": top_category,
            "requires_solver_patch": True,
            "requires_human_review": False,
            "targeted_fix_applied": False,
            "solver_code_modified": False,
            "modified_modules": [],
            "planned_modules": list(category_plan.get("planned_modules", [])),
            "planned_tests": list(category_plan.get("planned_tests", [])),
            "post_fix_step148_run_executed": False,
            "post_fix_step150_comparison_executed": False,
            "error_delta_report_present": True,
            "primary_metric_improved": False,
        }
    )
    plan = {
        "step": STEP,
        "status": summary["status"],
        "source_step150_status": summary["source_step150_status"],
        "source_top_bug_category": top_category,
        "top_hypothesis": _top_hypothesis(hypotheses, top_category),
        "requires_solver_patch": True,
        "targeted_fix_applied": False,
        "solver_code_modified": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    plan.update(category_plan)
    _write_all_outputs(output_dir, summary, plan)
    return summary


def _base_summary(
    paths: dict[str, Path],
    source: dict[str, Any] | None,
    hypotheses: dict[str, Any],
    metrics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step": STEP,
        "step150_summary": _display_path(paths["step150_summary"]),
        "hypotheses": _display_path(paths["hypotheses"]),
        "displacement_metrics": _display_path(paths["displacement_metrics"]),
        "force_metrics": _display_path(paths["force_metrics"]),
        "phase_lag_metrics": _display_path(paths["phase_lag_metrics"]),
        "step148_summary": _display_path(paths["step148_summary"]),
        "geometry_report": _display_path(paths["geometry_report"]),
        "unit_report": _display_path(paths["unit_report"]),
        "coupling_report": _display_path(paths["coupling_report"]),
        "source_step150_status": None if source is None else source.get("status"),
        "source_official_reference_loaded": False if source is None else bool(source.get("official_reference_loaded", False)),
        "source_solver_monitor_loaded": False if source is None else bool(source.get("solver_monitor_loaded", False)),
        "source_error_metrics_present": False if source is None else bool(source.get("error_metrics_present", False)),
        "source_solver_bug_hypotheses_present": False
        if source is None
        else bool(source.get("solver_bug_hypotheses_present", False)),
        "source_next_code_fix_step_identified": False
        if source is None
        else bool(source.get("next_code_fix_step_identified", False)),
        "source_hypothesis_count": len(hypotheses.get("hypotheses", [])),
        "source_displacement_metrics_status": _status(metrics.get("displacement")),
        "source_force_metrics_status": _status(metrics.get("force")),
        "source_phase_lag_metrics_status": _status(metrics.get("phase_lag")),
        "fabricated_metrics_used": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _write_all_outputs(output_dir: Path, summary: dict[str, Any], plan: dict[str, Any]) -> None:
    _write_json(output_dir / "step151_fix_plan.json", plan)
    _write_json(output_dir / "step151_fix_report.json", summary)
    _write_json(
        output_dir / "post_fix_step148_summary.json",
        {
            "step": STEP,
            "status": "not_executed",
            "post_fix_step148_run_executed": False,
            "reason": "Step151 has not applied a solver patch",
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    _write_json(
        output_dir / "post_fix_step150_summary.json",
        {
            "step": STEP,
            "status": "not_executed",
            "post_fix_step150_comparison_executed": False,
            "reason": "Step151 has not applied a solver patch",
            "validation_claim_allowed": False,
            "selected96_execution_allowed": False,
        },
    )
    _write_json(
        output_dir / "error_delta_report.json",
        {
            "step": STEP,
            "status": "not_computed",
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
        "# Step151 Targeted Solver Fix From Official Error Localization",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Source Step150 status: `{summary.get('source_step150_status')}`",
        f"- Source top bug category: `{summary.get('source_top_bug_category')}`",
        f"- Solver code modified: `{summary.get('solver_code_modified')}`",
        f"- Targeted fix applied: `{summary.get('targeted_fix_applied')}`",
        f"- Requires solver patch: `{summary.get('requires_solver_patch')}`",
        f"- Post-fix Step148 run executed: `{summary.get('post_fix_step148_run_executed')}`",
        f"- Post-fix Step150 comparison executed: `{summary.get('post_fix_step150_comparison_executed')}`",
        f"- Primary metric improved: `{summary.get('primary_metric_improved')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        f"- Selected96 execution allowed: `{summary.get('selected96_execution_allowed')}`",
        "",
        "Step151 reads Step150 official error localization before allowing a solver fix.",
        "When Step150 has no real official comparison, Step151 writes a blocked result and does not modify solver code.",
    ]
    priority_surfaces = plan.get("priority_surfaces") or []
    if priority_surfaces:
        lines.append("")
        lines.append("Priority surfaces:")
        for item in priority_surfaces:
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
        doc_report = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "151" / "report.md"
        doc_report.parent.mkdir(parents=True, exist_ok=True)
        doc_report.write_text(text, encoding="utf-8")


def _top_hypothesis(hypotheses: dict[str, Any], category: str) -> dict[str, Any] | None:
    for item in hypotheses.get("hypotheses", []):
        if item.get("category") == category:
            return item
    items = hypotheses.get("hypotheses", [])
    return items[0] if items else None


def _status(payload: Any) -> str | None:
    return payload.get("status") if isinstance(payload, dict) else None


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
    parser.add_argument("--step150-summary", type=Path, default=DEFAULT_STEP150_SUMMARY)
    parser.add_argument("--hypotheses", type=Path, default=DEFAULT_HYPOTHESES)
    parser.add_argument("--displacement-metrics", type=Path, default=DEFAULT_DISPLACEMENT_METRICS)
    parser.add_argument("--force-metrics", type=Path, default=DEFAULT_FORCE_METRICS)
    parser.add_argument("--phase-lag-metrics", type=Path, default=DEFAULT_PHASE_LAG_METRICS)
    parser.add_argument("--step148-summary", type=Path, default=DEFAULT_STEP148_SUMMARY)
    parser.add_argument("--geometry-report", type=Path, default=DEFAULT_GEOMETRY_REPORT)
    parser.add_argument("--unit-report", type=Path, default=DEFAULT_UNIT_REPORT)
    parser.add_argument("--coupling-report", type=Path, default=DEFAULT_COUPLING_REPORT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step151_targeted_solver_fix(
        step150_summary=args.step150_summary,
        hypotheses=args.hypotheses,
        displacement_metrics=args.displacement_metrics,
        force_metrics=args.force_metrics,
        phase_lag_metrics=args.phase_lag_metrics,
        step148_summary=args.step148_summary,
        geometry_report=args.geometry_report,
        unit_report=args.unit_report,
        coupling_report=args.coupling_report,
        output_dir=args.output_dir,
        force=args.force,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
