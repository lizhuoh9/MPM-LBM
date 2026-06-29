from __future__ import annotations

import argparse
import math
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from experiments.steps.step116_regularized_lbm_duct_flow_baseline import (  # noqa: E402
    _finite_float,
    _read_json,
    _write_csv,
    _write_json,
)


STEP = 144
SOURCE_STEP = 143
STEP144_ROLE = "mass_neutral_final_evidence_candidate_48"
DEFAULT_PHASE_ROOT = Path("outputs") / "step144_mass_neutral_final48" / "mass_neutral_final48"
DEFAULT_STEP143_DECISION = Path("outputs") / "step143_mass_neutral_design_diagnostic" / "step143_decision_summary.json"
DEFAULT_STEP143_COMPARISON = (
    Path("outputs") / "step143_mass_neutral_design_diagnostic" / "step143_mass_neutral_comparison.json"
)
DEFAULT_OUTPUT_DIR = Path("outputs") / "step144_mass_neutral_final48"

COMPARISON_FIELDS = [
    "name",
    "row_role",
    "requested_nx",
    "executed_nx",
    "requested_n_steps",
    "steps_completed",
    "requested_window_completed",
    "simulation_backed_artifact",
    "finite_pass",
    "density_gate_pass",
    "population_gate_pass",
    "mach_gate_pass",
    "mass_drift_gate_pass",
    "first_failure_step",
    "first_failure_reason",
    "candidate_mass_acceptance_observed_abs",
    "candidate_mass_acceptance_gate_pass",
    "flow_development_gate_pass",
    "outlet_to_inlet_flux_ratio_tail_mean",
    "midplane_to_inlet_flux_ratio_tail_mean",
    "flux_imbalance_rel_tail_mean",
    "flux_imbalance_rel_tail_max",
    "outlet_flux_tail_cv",
    "collapse_first_x",
    "collapse_first_step",
    "limiter_activation_fraction",
    "controller_authority_ratio_tail_mean",
    "controller_saturation_fraction_tail",
    "drop_guard_activation_fraction_tail",
    "mass_neutral_rho_feedback_tail_mean",
    "mass_neutral_mass_error_tail_mean",
    "mass_neutral_mass_error_final",
    "mass_neutral_feedback_saturation_fraction_tail",
    "runtime_s",
    "selected96_claim_allowed",
    "validation_claim_allowed",
    "source_step",
    "source_step143_decision_hash",
    "source_step143_comparison_hash",
    "source_step143_best_row_name",
    "source_step143_best_row_solver_state_hash",
    "source_step143_best_row_run_manifest_hash",
    "source_step143_best_row_mass_neutral_activation_hash",
    "source_step143_decision_case",
    "mass_neutral_activation_hash",
    "solver_state_hash",
    "run_manifest_hash",
]


def run_step144_mass_neutral_final48_audit(
    phase_root: Path | str = DEFAULT_PHASE_ROOT,
    step143_decision: Path | str = DEFAULT_STEP143_DECISION,
    step143_comparison: Path | str = DEFAULT_STEP143_COMPARISON,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> Dict[str, Any]:
    del force
    phase_root = Path(phase_root)
    step143_decision = Path(step143_decision)
    step143_comparison = Path(step143_comparison)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    missing = _missing_inputs(phase_root, step143_decision, step143_comparison)
    if missing:
        return _write_missing_summary(output_dir, phase_root, step143_decision, step143_comparison, missing)

    decision = _read_json(step143_decision)
    comparison = _read_json(step143_comparison)
    source = _source_provenance(step143_decision, step143_comparison, decision, comparison)
    rows = [_comparison_row(report, source) for report in _finite_reports(phase_root)]
    rows.sort(key=lambda row: str(row.get("name") or ""))

    summary = _decision_summary(rows, phase_root, step143_decision, step143_comparison, source)
    payload = _comparison_payload(rows, phase_root, step143_decision, step143_comparison, summary, source)

    _write_json(output_dir / "step144_long_window_comparison.json", payload)
    _write_csv(output_dir / "step144_long_window_comparison.csv", rows, COMPARISON_FIELDS)
    _write_json(output_dir / "step144_decision_summary.json", summary)
    return summary


def _missing_inputs(phase_root: Path, step143_decision: Path, step143_comparison: Path) -> List[str]:
    missing: List[str] = []
    if not step143_decision.is_file():
        missing.append(str(step143_decision))
    if not step143_comparison.is_file():
        missing.append(str(step143_comparison))
    if not phase_root.is_dir():
        missing.append(str(phase_root))
        return missing
    if not _finite_reports(phase_root):
        missing.append(str(phase_root / "*" / "finite_stability_report.json"))
    return missing


def _finite_reports(phase_root: Path) -> List[Path]:
    if not phase_root.is_dir():
        return []
    return sorted(path for path in phase_root.rglob("finite_stability_report.json") if path.is_file())


def _source_provenance(
    step143_decision: Path,
    step143_comparison: Path,
    decision: Dict[str, Any],
    comparison: Dict[str, Any],
) -> Dict[str, Any]:
    best_name = decision.get("best_row_name")
    best = next((row for row in comparison.get("rows", []) if row.get("name") == best_name), {})
    return {
        "source_step143_decision_hash": sha256(step143_decision.read_bytes()).hexdigest(),
        "source_step143_decision_path": _display_path(step143_decision),
        "source_step143_comparison_hash": sha256(step143_comparison.read_bytes()).hexdigest(),
        "source_step143_comparison_path": _display_path(step143_comparison),
        "source_step143_best_row_name": best_name,
        "source_step143_best_row_solver_state_hash": best.get("solver_state_hash"),
        "source_step143_best_row_run_manifest_hash": best.get("run_manifest_hash"),
        "source_step143_best_row_mass_neutral_activation_hash": best.get("mass_neutral_activation_hash"),
        "source_step143_decision_case": decision.get("decision_case"),
        "step143_single_probe_allowed": bool(decision.get("step144_single_500step_probe_proposal_allowed")),
    }


def _comparison_row(report: Path, source: Dict[str, Any]) -> Dict[str, Any]:
    payload = _read_json(report)
    row = dict(payload.get("summary_row") or payload)
    row.setdefault("name", report.parent.name)

    flow_summary = _read_optional_json(report.parent / "flow_development_diagnostics_summary.json")
    flow_final = dict(flow_summary.get("final") or {}) if flow_summary else {}
    merged = dict(row)
    for key, value in flow_final.items():
        merged.setdefault(key, value)
    if flow_summary:
        _merge_tail_fields(merged, flow_summary)

    merged.setdefault("source_step", SOURCE_STEP)
    for key, value in source.items():
        if key != "step143_single_probe_allowed":
            merged.setdefault(key, value)
    merged["selected96_claim_allowed"] = False
    merged["validation_claim_allowed"] = False
    return {field: _jsonable(merged.get(field)) for field in COMPARISON_FIELDS}


def _read_optional_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    return _read_json(path)


def _merge_tail_fields(row: Dict[str, Any], flow_summary: Dict[str, Any]) -> None:
    aliases = {
        "collapse_first_x": "collapse_first_x",
        "collapse_first_step": "collapse_first_step",
        "controller_authority_ratio_tail_mean": "controller_authority_ratio_tail_mean",
        "controller_saturation_fraction_tail": "controller_saturation_fraction_tail",
        "controller_drop_guard_activation_fraction_tail": "drop_guard_activation_fraction_tail",
        "drop_guard_activation_fraction_tail": "drop_guard_activation_fraction_tail",
        "mass_neutral_rho_feedback_tail_mean": "mass_neutral_rho_feedback_tail_mean",
        "mass_neutral_mass_error_tail_mean": "mass_neutral_mass_error_tail_mean",
        "mass_neutral_feedback_saturation_fraction_tail": "mass_neutral_feedback_saturation_fraction_tail",
    }
    for source, target in aliases.items():
        if target not in row and source in flow_summary:
            row[target] = flow_summary.get(source)
    if "mass_neutral_mass_error_final" not in row:
        final = dict(flow_summary.get("final") or {})
        if "mass_neutral_mass_error" in final:
            row["mass_neutral_mass_error_final"] = final.get("mass_neutral_mass_error")


def _decision_summary(
    rows: List[Dict[str, Any]],
    phase_root: Path,
    step143_decision: Path,
    step143_comparison: Path,
    source: Dict[str, Any],
) -> Dict[str, Any]:
    row = rows[0] if rows else None
    decision_case = "mass_neutral_design_unstable_long_window"
    step145_allowed = False
    recommendation = "Keep selected96 blocked and diagnose Step144 missing or unstable evidence."

    if row is None or len(rows) != 1 or not source.get("step143_single_probe_allowed"):
        decision_case = "mass_neutral_design_unstable_long_window"
    elif _has_failure_or_collapse(row):
        decision_case = "mass_neutral_design_unstable_long_window"
        recommendation = "Stop parameter progression and revisit the boundary formulation."
    elif not _flow_gate_pass(row):
        decision_case = "mass_neutral_flow_stationarity_long_window_failure"
        recommendation = "Do stationarity/controller-lag diagnosis; do not run selected96."
    elif not _mass_gate_pass(row):
        decision_case = "mass_neutral_mass_long_window_failure"
        recommendation = "Do mass-neutral long-window formulation refinement; do not run selected96."
    elif _claim_flags_blocked(row):
        decision_case = "mass_neutral_final48_probe_passed"
        step145_allowed = True
        recommendation = (
            "Step145 may propose selected-candidate-surface review only; selected96 remains blocked."
        )

    return {
        "artifact": "step144_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "decision_ready",
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step143_decision_path": _display_path(step143_decision),
        "step143_comparison_path": _display_path(step143_comparison),
        **{key: value for key, value in source.items() if key != "step143_single_probe_allowed"},
        "row_count": len(rows),
        "row_name": row.get("name") if row else None,
        "decision_case": decision_case,
        "step145_selected_candidate_surface_review_proposal_allowed": bool(step145_allowed),
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "next_step_recommendation": recommendation,
        "mass_neutral_feedback_saturation_fraction_tail": row.get("mass_neutral_feedback_saturation_fraction_tail") if row else None,
        "mass_neutral_mass_error_final": row.get("mass_neutral_mass_error_final") if row else None,
    }


def _comparison_payload(
    rows: List[Dict[str, Any]],
    phase_root: Path,
    step143_decision: Path,
    step143_comparison: Path,
    decision: Dict[str, Any],
    source: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact": "step144_long_window_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": decision["status"],
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step143_decision_path": _display_path(step143_decision),
        "step143_comparison_path": _display_path(step143_comparison),
        **{key: value for key, value in source.items() if key != "step143_single_probe_allowed"},
        "row_count": len(rows),
        "decision_case": decision["decision_case"],
        "step145_selected_candidate_surface_review_proposal_allowed": bool(
            decision["step145_selected_candidate_surface_review_proposal_allowed"]
        ),
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "rows": rows,
    }


def _write_missing_summary(
    output_dir: Path,
    phase_root: Path,
    step143_decision: Path,
    step143_comparison: Path,
    missing: List[str],
) -> Dict[str, Any]:
    summary = {
        "artifact": "step144_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step143_decision_path": _display_path(step143_decision),
        "step143_comparison_path": _display_path(step143_comparison),
        "row_count": 0,
        "row_name": None,
        "decision_case": "missing_input",
        "step145_selected_candidate_surface_review_proposal_allowed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    }
    comparison = {
        "artifact": "step144_long_window_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step143_decision_path": _display_path(step143_decision),
        "step143_comparison_path": _display_path(step143_comparison),
        "row_count": 0,
        "selected96_execution_allowed": False,
        "validation_claim_allowed": False,
        "rows": [],
    }
    _write_json(output_dir / "step144_long_window_comparison.json", comparison)
    _write_csv(output_dir / "step144_long_window_comparison.csv", [], COMPARISON_FIELDS)
    _write_json(output_dir / "step144_decision_summary.json", summary)
    return summary


def _has_failure_or_collapse(row: Dict[str, Any]) -> bool:
    if int(row.get("steps_completed", 0) or 0) < 500:
        return True
    if row.get("first_failure_step") is not None or row.get("first_failure_reason") is not None:
        return True
    if row.get("collapse_first_x") is not None or row.get("collapse_first_step") is not None:
        return True
    for key in ("finite_pass", "density_gate_pass", "population_gate_pass", "mach_gate_pass", "mass_drift_gate_pass"):
        if row.get(key) is not True:
            return True
    return False


def _mass_gate_pass(row: Dict[str, Any]) -> bool:
    return bool(
        row.get("candidate_mass_acceptance_gate_pass") is True
        and _metric(row.get("candidate_mass_acceptance_observed_abs")) < 0.005
    )


def _flow_gate_pass(row: Dict[str, Any]) -> bool:
    return bool(
        row.get("requested_window_completed") is True
        and row.get("simulation_backed_artifact") is True
        and row.get("flow_development_gate_pass") is True
        and 0.80 <= _metric(row.get("outlet_to_inlet_flux_ratio_tail_mean")) <= 1.20
        and 0.80 <= _metric(row.get("midplane_to_inlet_flux_ratio_tail_mean")) <= 1.20
        and _metric(row.get("flux_imbalance_rel_tail_mean")) < 0.10
        and _metric(row.get("flux_imbalance_rel_tail_max")) < 0.20
        and _metric(row.get("outlet_flux_tail_cv")) < 0.10
        and _metric(row.get("limiter_activation_fraction"), default=math.inf) <= 0.05
    )


def _claim_flags_blocked(row: Dict[str, Any]) -> bool:
    return bool(row.get("selected96_claim_allowed") is False and row.get("validation_claim_allowed") is False)


def _metric(value: Any, default: float = math.inf) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(numeric):
        return default
    return numeric


def _jsonable(value: Any) -> Any:
    if isinstance(value, float):
        return _finite_float(value)
    return value


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase-root", type=Path, default=DEFAULT_PHASE_ROOT)
    parser.add_argument("--step143-decision", type=Path, default=DEFAULT_STEP143_DECISION)
    parser.add_argument("--step143-comparison", type=Path, default=DEFAULT_STEP143_COMPARISON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    run_step144_mass_neutral_final48_audit(
        phase_root=args.phase_root,
        step143_decision=args.step143_decision,
        step143_comparison=args.step143_comparison,
        output_dir=args.output_dir,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
