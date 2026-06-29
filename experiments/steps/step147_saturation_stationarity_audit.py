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


STEP = 147
SOURCE_STEP = 146
STEP147_ROLE = "saturation_stationarity_diagnostic_48"
DEFAULT_PHASE_ROOT = (
    Path("outputs") / "step147_saturation_stationarity_diagnostic" / "saturation_stationarity48"
)
DEFAULT_STEP146_READINESS = (
    Path("outputs")
    / "step146_coupled_saturation_stationarity_design"
    / "step146_design_readiness_report.json"
)
DEFAULT_OUTPUT_DIR = Path("outputs") / "step147_saturation_stationarity_diagnostic"

COMPARISON_FIELDS = [
    "name",
    "mass_neutral_label",
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
    "mass_total_delta_rel_final",
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
    "open_boundary_mass_neutral_mass_error_gain",
    "open_boundary_mass_neutral_mass_error_cap",
    "open_boundary_mass_neutral_correction_blend",
    "open_boundary_flux_feedback_slew_alpha",
    "runtime_s",
    "selected96_claim_allowed",
    "validation_claim_allowed",
    "source_step",
    "source_step146_readiness_hash",
    "source_step146_readiness_path",
    "source_step146_status",
    "source_step146_recommended_design",
    "source_step146_recommended_phase",
    "source_step146_recommended_row_role",
    "source_step145_decision_case",
    "source_step144_decision_case",
    "mass_neutral_activation_hash",
    "solver_state_hash",
    "run_manifest_hash",
]


def run_step147_saturation_stationarity_audit(
    phase_root: Path | str = DEFAULT_PHASE_ROOT,
    step146_readiness: Path | str = DEFAULT_STEP146_READINESS,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> Dict[str, Any]:
    del force
    phase_root = Path(phase_root)
    step146_readiness = Path(step146_readiness)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    missing = _missing_inputs(phase_root, step146_readiness)
    if missing:
        return _write_missing_summary(output_dir, phase_root, step146_readiness, missing)

    readiness = _read_json(step146_readiness)
    source = _source_provenance(step146_readiness, readiness)
    rows = [_comparison_row(report, source) for report in _finite_reports(phase_root)]
    rows.sort(key=_sort_key)

    summary = _decision_summary(rows, phase_root, step146_readiness, source)
    payload = _comparison_payload(rows, phase_root, step146_readiness, summary, source)

    _write_json(output_dir / "step147_saturation_stationarity_comparison.json", payload)
    _write_csv(output_dir / "step147_saturation_stationarity_comparison.csv", rows, COMPARISON_FIELDS)
    _write_json(output_dir / "step147_decision_summary.json", summary)
    return summary


def _missing_inputs(phase_root: Path, step146_readiness: Path) -> List[str]:
    missing: List[str] = []
    if not step146_readiness.is_file():
        missing.append(str(step146_readiness))
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


def _source_provenance(step146_readiness: Path, readiness: Dict[str, Any]) -> Dict[str, Any]:
    readiness_valid = bool(
        readiness.get("status") == "design_ready"
        and readiness.get("step147_250step_diagnostic_proposal_allowed") is True
        and readiness.get("step146_500step_probe_allowed") is False
        and readiness.get("selected96_execution_allowed") is False
        and readiness.get("recommended_step147_phase") == "planeflux_saturation_stationarity48"
        and readiness.get("recommended_step147_row_role") == STEP147_ROLE
    )
    return {
        "source_step146_readiness_hash": sha256(step146_readiness.read_bytes()).hexdigest(),
        "source_step146_readiness_path": _display_path(step146_readiness),
        "source_step146_status": readiness.get("status"),
        "source_step146_recommended_design": readiness.get("recommended_design"),
        "source_step146_recommended_phase": readiness.get("recommended_step147_phase"),
        "source_step146_recommended_row_role": readiness.get("recommended_step147_row_role"),
        "source_step145_decision_case": readiness.get("source_step145_decision_case"),
        "source_step144_decision_case": readiness.get("source_step144_decision_case"),
        "source_step146_readiness_valid": readiness_valid,
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
    merged.setdefault("mass_neutral_label", _infer_label(str(merged.get("name") or "")))
    for key, value in source.items():
        if key != "source_step146_readiness_valid":
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
    step146_readiness: Path,
    source: Dict[str, Any],
) -> Dict[str, Any]:
    baseline = _baseline_row(rows)
    relief_rows = [row for row in rows if row is not baseline]
    analyses = [_relief_analysis(row, baseline) for row in relief_rows if baseline is not None]
    supported = next((item for item in analyses if item["supports_step148"]), None)
    mass_only = next((item for item in analyses if item["mass_improved"] and not item["stationarity_improved"]), None)
    stationarity_only = next(
        (item for item in analyses if item["stationarity_improved"] and not item["mass_improved"]),
        None,
    )

    decision_case = "relief_design_insufficient"
    step148_allowed = False
    best = supported["row"] if supported else (relief_rows[0] if relief_rows else None)
    recommendation = "Keep selected96 and validation blocked; do not propose a 500-step probe yet."

    if not source.get("source_step146_readiness_valid"):
        decision_case = "source_step146_readiness_not_design_ready"
        recommendation = "Regenerate or repair the Step146 readiness artifact before Step147 audit."
        best = None
    elif len(rows) > 4:
        decision_case = "row_count_exceeds_step147_contract"
        recommendation = "Discard extra rows and rerun the bounded four-row Step147 diagnostic."
        best = None
    elif baseline is None or not relief_rows:
        decision_case = "relief_design_insufficient"
    elif any(_has_failure_or_collapse(row) for row in rows):
        decision_case = "relief_design_unstable"
        recommendation = "Stop parameter progression and diagnose the unstable Step147 row."
        best = None
    elif supported is not None:
        decision_case = "saturation_stationarity_relief_supports_step148_500step_probe"
        step148_allowed = True
        recommendation = (
            "Step148 may propose one 48^3 / 500-step probe for the best Step147 relief row only; "
            "selected96 and validation remain blocked."
        )
    elif mass_only is not None:
        decision_case = "mass_relief_without_stationarity"
        best = mass_only["row"]
        recommendation = "Mass relief improved but stationarity/saturation did not; keep 500-step and selected96 blocked."
    elif stationarity_only is not None:
        decision_case = "stationarity_relief_without_mass"
        best = stationarity_only["row"]
        recommendation = "Stationarity improved without mass relief; keep 500-step and selected96 blocked."

    return {
        "artifact": "step147_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "decision_ready",
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step146_readiness_path": _display_path(step146_readiness),
        **{key: value for key, value in source.items() if key != "source_step146_readiness_valid"},
        "row_count": len(rows),
        "baseline_row_name": baseline.get("name") if baseline else None,
        "best_row_name": best.get("name") if best else None,
        "best_mass_neutral_label": best.get("mass_neutral_label") if best else None,
        "decision_case": decision_case,
        "step148_500step_probe_proposal_allowed": bool(step148_allowed),
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "selected_candidate_surface_review_allowed": False,
        "next_step_recommendation": recommendation,
        "best_mass_abs": _metric(best.get("candidate_mass_acceptance_observed_abs")) if best else None,
        "best_outlet_flux_tail_cv": _metric(best.get("outlet_flux_tail_cv")) if best else None,
        "best_flux_imbalance_rel_tail_mean": _metric(best.get("flux_imbalance_rel_tail_mean")) if best else None,
        "best_mass_neutral_feedback_saturation_fraction_tail": (
            _metric(best.get("mass_neutral_feedback_saturation_fraction_tail")) if best else None
        ),
    }


def _comparison_payload(
    rows: List[Dict[str, Any]],
    phase_root: Path,
    step146_readiness: Path,
    decision: Dict[str, Any],
    source: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "artifact": "step147_saturation_stationarity_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": decision["status"],
        "missing_input": False,
        "phase_root": _display_path(phase_root),
        "step146_readiness_path": _display_path(step146_readiness),
        **{key: value for key, value in source.items() if key != "source_step146_readiness_valid"},
        "row_count": len(rows),
        "decision_case": decision["decision_case"],
        "step148_500step_probe_proposal_allowed": bool(decision["step148_500step_probe_proposal_allowed"]),
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
    step146_readiness: Path,
    missing: List[str],
) -> Dict[str, Any]:
    summary = {
        "artifact": "step147_decision_summary",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step146_readiness_path": _display_path(step146_readiness),
        "row_count": 0,
        "baseline_row_name": None,
        "best_row_name": None,
        "decision_case": "missing_input",
        "step148_500step_probe_proposal_allowed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "selected_candidate_surface_review_allowed": False,
    }
    comparison = {
        "artifact": "step147_saturation_stationarity_comparison",
        "step": STEP,
        "source_step": SOURCE_STEP,
        "status": "missing_input",
        "missing_input": True,
        "missing_inputs": missing,
        "phase_root": _display_path(phase_root),
        "step146_readiness_path": _display_path(step146_readiness),
        "row_count": 0,
        "step148_500step_probe_proposal_allowed": False,
        "selected96_execution_allowed": False,
        "validation_claim_allowed": False,
        "rows": [],
    }
    _write_json(output_dir / "step147_saturation_stationarity_comparison.json", comparison)
    _write_csv(output_dir / "step147_saturation_stationarity_comparison.csv", [], COMPARISON_FIELDS)
    _write_json(output_dir / "step147_decision_summary.json", summary)
    return summary


def _baseline_row(rows: Sequence[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for row in rows:
        label = str(row.get("mass_neutral_label") or "")
        name = str(row.get("name") or "")
        if label == "baseline_high_repeat" or "_mnhigh_" in name:
            return row
    return rows[0] if rows else None


def _relief_analysis(row: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    base_mass = _abs_metric(_mass_metric(baseline))
    row_mass = _abs_metric(_mass_metric(row))
    base_cv = _metric(baseline.get("outlet_flux_tail_cv"))
    row_cv = _metric(row.get("outlet_flux_tail_cv"))
    base_imbalance = _metric(baseline.get("flux_imbalance_rel_tail_mean"))
    row_imbalance = _metric(row.get("flux_imbalance_rel_tail_mean"))
    base_saturation = _metric(baseline.get("mass_neutral_feedback_saturation_fraction_tail"))
    row_saturation = _metric(row.get("mass_neutral_feedback_saturation_fraction_tail"))
    mass_improved = row_mass < base_mass
    cv_improved = row_cv < base_cv
    imbalance_improved = row_imbalance < base_imbalance
    saturation_improved = row_saturation < base_saturation and row_saturation < 0.75
    flow_ok = _flow_pass(row)
    return {
        "row": row,
        "mass_improved": mass_improved,
        "stationarity_improved": bool(cv_improved and imbalance_improved and saturation_improved and flow_ok),
        "supports_step148": bool(
            mass_improved and cv_improved and imbalance_improved and saturation_improved and flow_ok
        ),
    }


def _mass_metric(row: Dict[str, Any]) -> Any:
    if row.get("candidate_mass_acceptance_observed_abs") is not None:
        return row.get("candidate_mass_acceptance_observed_abs")
    if row.get("mass_total_delta_rel_final") is not None:
        return row.get("mass_total_delta_rel_final")
    return row.get("mass_neutral_mass_error_final")


def _flow_pass(row: Dict[str, Any]) -> bool:
    return bool(
        row.get("flow_development_gate_pass") is True
        and not _has_failure_or_collapse(row)
        and _metric(row.get("outlet_flux_tail_cv")) <= 0.10
        and _metric(row.get("flux_imbalance_rel_tail_mean")) <= 0.10
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


def _sort_key(row: Dict[str, Any]) -> tuple[int, float, float, float, str]:
    label = str(row.get("mass_neutral_label") or "")
    return (
        1 if label == "baseline_high_repeat" else 0,
        _abs_metric(_mass_metric(row)),
        _metric(row.get("outlet_flux_tail_cv")),
        _metric(row.get("flux_imbalance_rel_tail_mean")),
        str(row.get("name") or ""),
    )


def _infer_label(name: str) -> Optional[str]:
    if "_mnhigh_" in name:
        return "baseline_high_repeat"
    if "_mnrelieflow_" in name:
        return "relief_low_slew025"
    if "_mnreliefmid_" in name:
        return "relief_mid_slew025"
    if "_mncaptest_" in name:
        return "relief_cap_test_slew025"
    return None


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
    parser.add_argument("--step146-readiness", type=Path, default=DEFAULT_STEP146_READINESS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    run_step147_saturation_stationarity_audit(
        phase_root=args.phase_root,
        step146_readiness=args.step146_readiness,
        output_dir=args.output_dir,
        force=args.force,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
