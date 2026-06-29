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


STEP = 143
SOURCE_STEP = 142
STEP143_ROLE = "mass_neutral_design_diagnostic_48"
DEFAULT_PHASE_ROOT = Path("outputs") / "step143_mass_neutral_design_diagnostic" / "mass_neutral_design48"
DEFAULT_STEP142_READINESS = (
    Path("outputs") / "step142_mass_neutral_plane_flux_design" / "step142_design_readiness_report.json"
)
DEFAULT_OUTPUT_DIR = Path("outputs") / "step143_mass_neutral_design_diagnostic"

COMPARISON_FIELDS = [
    "name",
    "row_role",
    "open_boundary_mass_neutral_flux_control_enabled",
    "open_boundary_mass_neutral_flux_control_mode",
    "open_boundary_mass_neutral_mass_error_gain",
    "open_boundary_mass_neutral_mass_error_cap",
    "open_boundary_mass_neutral_correction_blend",
    "open_boundary_mass_neutral_reference_mass_mode",
    "mass_neutral_activation_hash",
    "requested_nx",
    "executed_nx",
    "requested_n_steps",
    "steps_completed",
    "requested_window_completed",
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
    "controller_authority_ratio_tail_mean",
    "controller_saturation_fraction_tail",
    "density_feedback_tail_mean",
    "mass_neutral_rho_feedback_tail_mean",
    "mass_neutral_rho_feedback_abs_tail_mean",
    "mass_neutral_mass_error_tail_mean",
    "mass_neutral_feedback_saturation_fraction_tail",
    "selected96_claim_allowed",
    "validation_claim_allowed",
    "source_step",
    "source_step142_readiness_hash",
    "source_step142_readiness_path",
    "source_step142_status",
    "source_step142_recommended_design",
    "solver_state_hash",
    "run_manifest_hash",
]


def run_step143_mass_neutral_design_audit(
    phase_root: Path | str = DEFAULT_PHASE_ROOT,
    step142_readiness: Path | str = DEFAULT_STEP142_READINESS,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> Dict[str, Any]:
    del force
    phase_root = Path(phase_root)
    step142_readiness = Path(step142_readiness)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    missing = _missing_inputs(phase_root, step142_readiness)
    if missing:
        return _write_missing_summary(output_dir, phase_root, step142_readiness, missing)

    step142 = _read_json(step142_readiness)
    step142_hash = sha256(step142_readiness.read_bytes()).hexdigest()
    rows = [_comparison_row(report, step142, step142_hash) for report in _finite_reports(phase_root)]
    rows.sort(key=_sort_key)

    decision = _decision_summary(rows, phase_root, step142_readiness, step142, step142_hash)
    comparison = _comparison_payload(rows, phase_root, step142_readiness, step142_hash, decision)

    _write_json(output_dir / "step143_mass_neutral_comparison.json", comparison)
    _write_csv(output_dir / "step143_mass_neutral_comparison.csv", rows, COMPARISON_FIELDS)
    _write_json(output_dir / "step143_decision_summary.json", decision)
    return decision


def _missing_inputs(phase_root: Path, step142_readiness: Path) -> List[str]:
    missing: List[str] = []
    if not step142_readiness.is_file():
        missing.append(str(step142_readiness))
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


def _comparison_row(report: Path, step142: Dict[str, Any], step142_hash: str) -> Dict[str, Any]:
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

    design = dict(step142.get("recommended_design") or {})
    merged.setdefault("source_step", SOURCE_STEP)
    merged.setdefault("source_step142_readiness_hash", step142_hash)
    merged.setdefault(
        "source_step142_readiness_path",
        "outputs/step142_mass_neutral_plane_flux_design/step142_design_readiness_report.json",
    )
    merged.setdefault("source_step142_status", step142.get("status"))
    merged.setdefault("source_step142_recommended_design", design.get("primary_mode"))
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
        "density_feedback_tail_mean": "density_feedback_tail_mean",
        "mass_neutral_rho_feedback_tail_mean": "mass_neutral_rho_feedback_tail_mean",
        "mass_neutral_rho_feedback_abs_tail_mean": "mass_neutral_rho_feedback_abs_tail_mean",
        "mass_neutral_mass_error_tail_mean": "mass_neutral_mass_error_tail_mean",
        "mass_neutral_feedback_saturation_fraction_tail": "mass_neutral_feedback_saturation_fraction_tail",
    }
    for source, target in aliases.items():
        if target not in row and source in flow_summary:
            row[target] = flow_summary.get(source)


def _decision_summary(
    rows: List[Dict[str, Any]],
    phase_root: Path,
    step142_readiness: Path,
    step142: Dict[str, Any],
    step142_hash: str,
) -> Dict[str, Any]:
    baseline = _baseline_row(rows)
    enabled_rows = [row for row in rows if _enabled(row)]
    best = enabled_rows[0] if enabled_rows else None
    decision_case = "mass_neutral_design_insufficient"
    step144_allowed = False
    next_step_recommendation = "Keep selected96 and validation blocked; do not propose Step144 yet."

    if any(_has_failure_or_collapse(row) for row in rows):
        decision_case = "mass_neutral_design_unstable"
        next_step_recommendation = "Stop mass-neutral progression and return to solver/boundary diagnosis."
    elif baseline is not None and best is not None:
        baseline_mass = _abs_metric(baseline.get("candidate_mass_acceptance_observed_abs"))
        best_mass = _abs_metric(best.get("candidate_mass_acceptance_observed_abs"))
        baseline_cv = _metric(baseline.get("outlet_flux_tail_cv"))
        best_cv = _metric(best.get("outlet_flux_tail_cv"))
        mass_improved = best_mass < baseline_mass
        flow_ok = _flow_pass(best)
        cv_improved = best_cv < baseline_cv
        if mass_improved and flow_ok and cv_improved:
            decision_case = "mass_neutral_design_supports_step144_single_500step_probe"
            step144_allowed = True
            next_step_recommendation = (
                "Step144 may propose one 48^3 / 500-step final-evidence probe for the best Step143 setting only; "
                "selected96 remains blocked."
            )
        elif mass_improved and (not flow_ok or not cv_improved):
            decision_case = "mass_neutral_reduces_mass_but_damages_flow"
            next_step_recommendation = "Mass-neutral feedback is not ready for Step144 because flow/CV regressed."

    design = dict(step142.get("recommended_design") or {})
    return {
        "artifact": "step143_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "decision_ready",
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step142_readiness_path": _display_path(step142_readiness),
        "source_step142_readiness_hash": step142_hash,
        "source_step142_status": step142.get("status"),
        "source_step142_recommended_design": design.get("primary_mode"),
        "row_count": len(rows),
        "enabled_row_count": len(enabled_rows),
        "baseline_row_name": baseline.get("name") if baseline else None,
        "best_row_name": best.get("name") if best else None,
        "best_mass_neutral_gain": best.get("open_boundary_mass_neutral_mass_error_gain") if best else None,
        "decision_case": decision_case,
        "step144_single_500step_probe_proposal_allowed": bool(step144_allowed),
        "step144_selected96_execution_allowed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "next_step_recommendation": next_step_recommendation,
    }


def _comparison_payload(
    rows: List[Dict[str, Any]],
    phase_root: Path,
    step142_readiness: Path,
    step142_hash: str,
    decision: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact": "step143_mass_neutral_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": decision["status"],
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step142_readiness_path": _display_path(step142_readiness),
        "source_step142_readiness_hash": step142_hash,
        "row_count": len(rows),
        "sort_order": [
            "enabled rows before disabled baseline",
            "candidate_mass_acceptance_observed_abs",
            "outlet_flux_tail_cv",
            "flux_imbalance_rel_tail_mean",
        ],
        "decision_case": decision["decision_case"],
        "step144_single_500step_probe_proposal_allowed": bool(
            decision["step144_single_500step_probe_proposal_allowed"]
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
    step142_readiness: Path,
    missing: List[str],
) -> Dict[str, Any]:
    summary = {
        "artifact": "step143_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step142_readiness_path": _display_path(step142_readiness),
        "row_count": 0,
        "best_row_name": None,
        "decision_case": "missing_input",
        "step144_single_500step_probe_proposal_allowed": False,
        "step144_selected96_execution_allowed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    }
    comparison = {
        "artifact": "step143_mass_neutral_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step142_readiness_path": _display_path(step142_readiness),
        "row_count": 0,
        "selected96_execution_allowed": False,
        "validation_claim_allowed": False,
        "rows": [],
    }
    _write_json(output_dir / "step143_mass_neutral_comparison.json", comparison)
    _write_csv(output_dir / "step143_mass_neutral_comparison.csv", [], COMPARISON_FIELDS)
    _write_json(output_dir / "step143_decision_summary.json", summary)
    return summary


def _baseline_row(rows: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for row in rows:
        if not _enabled(row) or row.get("open_boundary_mass_neutral_flux_control_mode") == "disabled":
            return row
    return None


def _enabled(row: Dict[str, Any]) -> bool:
    return bool(row.get("open_boundary_mass_neutral_flux_control_enabled", False))


def _sort_key(row: Dict[str, Any]) -> tuple[int, float, float, float]:
    return (
        0 if _enabled(row) else 1,
        _sort_float(row.get("candidate_mass_acceptance_observed_abs")),
        _sort_float(row.get("outlet_flux_tail_cv")),
        _sort_float(row.get("flux_imbalance_rel_tail_mean")),
    )


def _flow_pass(row: Dict[str, Any]) -> bool:
    return bool(
        row.get("flow_development_gate_pass") is True
        and not _has_failure_or_collapse(row)
        and _sort_float(row.get("outlet_flux_tail_cv")) <= 0.10
        and _sort_float(row.get("flux_imbalance_rel_tail_mean")) <= 0.10
    )


def _has_failure_or_collapse(row: Dict[str, Any]) -> bool:
    if row.get("first_failure_step") is not None or row.get("first_failure_reason") is not None:
        return True
    if row.get("collapse_first_x") is not None or row.get("collapse_first_step") is not None:
        return True
    for key in ("finite_pass", "density_gate_pass", "population_gate_pass", "mach_gate_pass"):
        if row.get(key) is False:
            return True
    return False


def _abs_metric(value: Any, default: float = math.inf) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(numeric):
        return default
    return abs(numeric)


def _metric(value: Any, default: float = math.inf) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(numeric):
        return default
    return numeric


def _sort_float(value: Any) -> float:
    return _metric(value)


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
    parser.add_argument("--step142-readiness", type=Path, default=DEFAULT_STEP142_READINESS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    run_step143_mass_neutral_design_audit(
        phase_root=args.phase_root,
        step142_readiness=args.step142_readiness,
        output_dir=args.output_dir,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
