from __future__ import annotations

import argparse
import math
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from experiments.steps.step116_regularized_lbm_duct_flow_baseline import (  # noqa: E402
    _read_json,
    _write_csv,
    _write_json,
)


STEP = 141
SOURCE_STEP = 140
STEP141_ROLE = "density_feedback_isolation_diagnostic_48"
DEFAULT_PHASE_ROOT = Path("outputs") / "step141_density_feedback_isolation" / "density_feedback_isolation48"
DEFAULT_STEP140_SUMMARY = (
    Path("outputs") / "step140_long_window_drift_forensics" / "step140_failure_mechanism_summary.json"
)
DEFAULT_OUTPUT_DIR = Path("outputs") / "step141_density_feedback_isolation"

COMPARISON_FIELDS = [
    "name",
    "row_role",
    "open_boundary_flux_feedback_gain_rho",
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
    "controller_density_feedback_tail_mean",
    "outlet_flux_drop_guard_activation_fraction_tail",
    "selected96_claim_allowed",
    "validation_claim_allowed",
    "source_step",
    "source_step139_row_name",
    "source_step139_solver_state_hash",
    "source_step139_run_manifest_hash",
    "source_step139_code_commit",
    "source_step140_summary_hash",
    "source_step140_summary_path",
    "source_step140_dominant_failure_mechanism",
    "source_step140_mass_drift_mechanism",
    "solver_state_hash",
    "run_manifest_hash",
]


def run_step141_density_feedback_audit(
    phase_root: Path | str = DEFAULT_PHASE_ROOT,
    step140_summary: Path | str = DEFAULT_STEP140_SUMMARY,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> Dict[str, Any]:
    phase_root = Path(phase_root)
    step140_summary = Path(step140_summary)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    missing = _missing_inputs(phase_root, step140_summary)
    if missing:
        return _write_missing_summary(output_dir, phase_root, step140_summary, missing)

    step140 = _read_json(step140_summary)
    step140_hash = sha256(step140_summary.read_bytes()).hexdigest()
    rows = [_comparison_row(report, step140, step140_hash) for report in _finite_reports(phase_root)]
    rows.sort(key=_sort_key)

    decision = _decision_summary(rows, phase_root, step140_summary, step140, step140_hash)
    comparison = _comparison_payload(rows, phase_root, step140_summary, step140_hash, decision)

    _write_json(output_dir / "step141_density_feedback_comparison.json", comparison)
    _write_csv(output_dir / "step141_density_feedback_comparison.csv", rows, COMPARISON_FIELDS)
    _write_json(output_dir / "step141_decision_summary.json", decision)
    return decision


def _missing_inputs(phase_root: Path, step140_summary: Path) -> List[str]:
    missing: List[str] = []
    if not step140_summary.is_file():
        missing.append(str(step140_summary))
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


def _comparison_row(report: Path, step140: Dict[str, Any], step140_hash: str) -> Dict[str, Any]:
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

    mechanism = dict(step140.get("mechanism_summary") or {})
    merged.setdefault("source_step", SOURCE_STEP)
    merged.setdefault("source_step140_summary_hash", step140_hash)
    merged.setdefault(
        "source_step140_summary_path",
        "outputs/step140_long_window_drift_forensics/step140_failure_mechanism_summary.json",
    )
    merged.setdefault("source_step140_dominant_failure_mechanism", step140.get("dominant_failure_mechanism"))
    merged.setdefault("source_step140_mass_drift_mechanism", mechanism.get("mass_drift_mechanism"))
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
        "density_feedback_tail_mean": "controller_density_feedback_tail_mean",
        "drop_guard_activation_fraction_tail": "outlet_flux_drop_guard_activation_fraction_tail",
    }
    for source, target in aliases.items():
        if target not in row and source in flow_summary:
            row[target] = flow_summary.get(source)


def _sort_key(row: Dict[str, Any]) -> tuple[float, float, float, float, float]:
    ratio = _float_or_none(row.get("outlet_to_inlet_flux_ratio_tail_mean"))
    return (
        _sort_float(row.get("candidate_mass_acceptance_observed_abs")),
        _sort_float(row.get("outlet_flux_tail_cv")),
        _sort_float(row.get("flux_imbalance_rel_tail_mean")),
        abs(float(ratio) - 1.0) if ratio is not None else math.inf,
        _sort_float(row.get("controller_saturation_fraction_tail")),
    )


def _decision_summary(
    rows: List[Dict[str, Any]],
    phase_root: Path,
    step140_summary: Path,
    step140: Dict[str, Any],
    step140_hash: str,
) -> Dict[str, Any]:
    best = rows[0] if rows else None
    baseline = _baseline_row(rows)
    decision_case = "density_feedback_isolation_inconclusive"
    step142_allowed = False
    next_step_recommendation = "Step142 should stay diagnostic; selected96 remains blocked."

    if any(_has_collapse_or_failure(row) for row in rows):
        decision_case = "long_window_drift_workaround_unstable"
        next_step_recommendation = "Stop parameter progression and return to solver/boundary formulation diagnosis."
    elif best is not None and baseline is not None:
        best_mass = _abs_metric(best.get("candidate_mass_acceptance_observed_abs"))
        baseline_mass = _abs_metric(baseline.get("candidate_mass_acceptance_observed_abs"))
        best_rho = _sort_float(best.get("open_boundary_flux_feedback_gain_rho"))
        baseline_rho = _sort_float(baseline.get("open_boundary_flux_feedback_gain_rho"))
        if best_mass < baseline_mass and best_rho < baseline_rho and best_mass < 0.005 and _flow_pass(best):
            decision_case = "density_feedback_contributes_to_mass_stationarity_drift"
            step142_allowed = True
            next_step_recommendation = (
                "Step142 may propose one 48^3 / 500-step final-evidence row for the best rho setting; "
                "selected96 remains blocked."
            )
        elif best_mass < baseline_mass and not _flow_pass(best):
            decision_case = "density_feedback_trades_mass_against_throughput"
            next_step_recommendation = (
                "Step142 should diagnose the controller formulation only; no selected96 and no validation claim."
            )
        elif best_mass >= baseline_mass or _all_variants_reproduce_failure(rows):
            decision_case = "density_feedback_isolation_insufficient"
            next_step_recommendation = (
                "Step142 should be a mass-neutral plane-flux controller design proposal, not a 500-step run."
            )

    mechanism = dict(step140.get("mechanism_summary") or {})
    return {
        "artifact": "step141_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "decision_ready",
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step140_summary_path": _display_path(step140_summary),
        "source_step140_summary_hash": step140_hash,
        "source_step140_dominant_failure_mechanism": step140.get("dominant_failure_mechanism"),
        "source_step140_mass_drift_mechanism": mechanism.get("mass_drift_mechanism"),
        "step140_mechanism_interpretation": "post_250_mass_excursion_with_tail_acceptance_failure",
        "row_count": len(rows),
        "best_row_name": best.get("name") if best else None,
        "best_gain_rho": best.get("open_boundary_flux_feedback_gain_rho") if best else None,
        "decision_case": decision_case,
        "step142_single_500step_final_evidence_proposal_allowed": bool(step142_allowed),
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
    step140_summary: Path,
    step140_hash: str,
    decision: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact": "step141_density_feedback_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": decision["status"],
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step140_summary_path": _display_path(step140_summary),
        "source_step140_summary_hash": step140_hash,
        "row_count": len(rows),
        "sort_order": [
            "candidate_mass_acceptance_observed_abs",
            "outlet_flux_tail_cv",
            "flux_imbalance_rel_tail_mean",
            "abs(outlet_to_inlet_flux_ratio_tail_mean - 1.0)",
            "controller_saturation_fraction_tail",
        ],
        "decision_case": decision["decision_case"],
        "selected96_execution_allowed": False,
        "validation_claim_allowed": False,
        "rows": rows,
    }


def _write_missing_summary(
    output_dir: Path,
    phase_root: Path,
    step140_summary: Path,
    missing: List[str],
) -> Dict[str, Any]:
    summary = {
        "artifact": "step141_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step140_summary_path": _display_path(step140_summary),
        "row_count": 0,
        "best_row_name": None,
        "decision_case": "missing_input",
        "step142_single_500step_final_evidence_proposal_allowed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    }
    comparison = {
        "artifact": "step141_density_feedback_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step140_summary_path": _display_path(step140_summary),
        "row_count": 0,
        "selected96_execution_allowed": False,
        "validation_claim_allowed": False,
        "rows": [],
    }
    _write_json(output_dir / "step141_density_feedback_comparison.json", comparison)
    _write_csv(output_dir / "step141_density_feedback_comparison.csv", [], COMPARISON_FIELDS)
    _write_json(output_dir / "step141_decision_summary.json", summary)
    return summary


def _baseline_row(rows: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for row in rows:
        rho = _float_or_none(row.get("open_boundary_flux_feedback_gain_rho"))
        if rho is not None and math.isclose(rho, 0.001, rel_tol=0.0, abs_tol=1.0e-12):
            return row
    for row in rows:
        if "rho0p001" in str(row.get("name") or "") or "rho_base" in str(row.get("name") or ""):
            return row
    return None


def _has_collapse_or_failure(row: Dict[str, Any]) -> bool:
    return row.get("first_failure_step") is not None or row.get("collapse_first_x") is not None


def _flow_pass(row: Dict[str, Any]) -> bool:
    return bool(row.get("flow_development_gate_pass") is True)


def _all_variants_reproduce_failure(rows: Sequence[Dict[str, Any]]) -> bool:
    if not rows:
        return False
    for row in rows:
        mass = _abs_metric(row.get("candidate_mass_acceptance_observed_abs"))
        outlet_cv = _sort_float(row.get("outlet_flux_tail_cv"))
        flux_mean = _sort_float(row.get("flux_imbalance_rel_tail_mean"))
        if mass < 0.005 and outlet_cv < 0.10 and flux_mean < 0.10 and _flow_pass(row):
            return False
    return True


def _abs_metric(value: Any) -> float:
    numeric = _float_or_none(value)
    return abs(float(numeric)) if numeric is not None else math.inf


def _sort_float(value: Any) -> float:
    numeric = _float_or_none(value)
    return float(numeric) if numeric is not None else math.inf


def _float_or_none(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(numeric):
        return None
    return numeric


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return value
    if math.isfinite(numeric):
        return numeric
    return None


def _display_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Step141 density-feedback isolation rows.")
    parser.add_argument("--phase-root", type=Path, default=DEFAULT_PHASE_ROOT)
    parser.add_argument("--step140-summary", type=Path, default=DEFAULT_STEP140_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    run_step141_density_feedback_audit(
        phase_root=args.phase_root,
        step140_summary=args.step140_summary,
        output_dir=args.output_dir,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
