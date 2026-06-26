from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.steps.step116_regularized_lbm_duct_flow_baseline import (  # noqa: E402
    _finite_float,
    _read_json,
    _write_json,
)
from experiments.steps.step119_lbm_boundary_repair_real_run_validation import (  # noqa: E402
    FINAL_CLASSIFICATIONS,
    LIMITER_ACTIVATION_FRACTION_LIMIT,
)
from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (  # noqa: E402
    CANDIDATE_SEMANTICS,
    STEP120_SCHEMA_VERSION,
    REFERENCE_SEMANTICS,
    Step120RunSpec,
    _boundary_slug,
    _metric,
    _replace_spec,
    run_step120_matrix,
    step120_real_run_specs,
)


DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "step121_lbm_boundary_real_campaign_and_gate_correction"
DEFAULT_CHECKPOINT_ROOT = REPO_ROOT / "outputs" / "tmp" / "step121_checkpoints"
DEFAULT_RUNTIME_SNAPSHOT_ROOT = REPO_ROOT / "outputs" / "tmp" / "step121_failure_snapshots"
STEP121_SCHEMA_VERSION = 1

CAMPAIGN_AWAITING_48_REFERENCES = "awaiting_48_references"
CAMPAIGN_AWAITING_48_CANDIDATES = "awaiting_48_candidates"
CAMPAIGN_48_CANDIDATES_FAILED = "48_candidates_failed"
CAMPAIGN_BEST_48_SELECTED = "best_48_selected"
CAMPAIGN_AWAITING_SELECTED_96_DUCT = "awaiting_selected_96_duct"
CAMPAIGN_AWAITING_SELECTED_96_STATIC = "awaiting_selected_96_static"
CAMPAIGN_COMPLETE = "complete"

CLASSIFICATION_PARTIAL = "boundary_repair_partial_continue_lbm"
CLASSIFICATION_FAILED = "boundary_repair_failed_revisit_lbm_solver"
CLASSIFICATION_SUCCESS = "boundary_repair_success_go_to_quasi2d"

REQUIRED_REFERENCE_SEMANTICS = {
    "equilibrium_all_population_reset",
    "regularized_velocity_pressure",
}
REQUIRED_CANDIDATE_SEMANTICS = {
    "regularized_velocity_pressure_limited",
    "convective_pressure_outlet_experimental",
}
SELECTED_CHAIN_ROLES = {"candidate_48", "selected_96_duct", "selected_96_static"}


def step121_smoke_specs() -> List[Step120RunSpec]:
    smoke = step120_real_run_specs(output_interval=1)[0]
    return [
        _replace_spec(
            smoke,
            name="tiny_step121_real_runner_smoke",
            artifact_scope_note="committed tiny real Step121 smoke for campaign-controller plumbing",
            row_role="tiny_smoke",
        )
    ]


def step121_reference_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    return [
        _replace_spec(spec, output_interval=output_interval)
        for spec in step120_real_run_specs(output_interval=output_interval)
        if spec.row_role == "reference_48"
    ]


def step121_candidate_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    return [
        _replace_spec(spec, output_interval=output_interval)
        for spec in step120_real_run_specs(output_interval=output_interval)
        if spec.row_role == "candidate_48"
    ]


def make_selected_96_specs(best_selection: Dict[str, Any], output_interval: int = 100) -> List[Step120RunSpec]:
    if not bool(best_selection.get("best_boundary_selected", False)):
        raise ValueError("selected 96^3 specs require best_boundary_selected=true")
    semantics = str(best_selection.get("selected_boundary_semantics") or "")
    if semantics not in REQUIRED_CANDIDATE_SEMANTICS:
        raise ValueError(f"unsupported selected boundary semantics: {semantics!r}")
    slug = str(best_selection.get("selected_boundary_slug") or _boundary_slug(semantics))
    limited = semantics == "regularized_velocity_pressure_limited"
    common = {
        "nx": 96,
        "ny": 96,
        "nz": 96,
        "n_steps": 1000,
        "output_interval": int(output_interval),
        "failure_check_interval": 5,
        "checkpoint_every": 100,
        "open_boundary_semantics": semantics,
        "requested_nx": 96,
        "requested_n_steps": 1000,
        "open_boundary_limiter_enabled": bool(limited),
        "open_boundary_population_floor": -1.0e-8 if limited else None,
        "step120_required_row": False,
        "step119_required_row": False,
        "not_used_for_validation": False,
        "artifact_scope_note": "Step121 selected 96^3 large-real LBM-only boundary gate",
    }
    static_common = dict(common)
    static_common["artifact_scope_note"] = "Step121 selected 96^3 static two-flap LBM-only boundary gate; not FSI"
    return [
        Step120RunSpec(
            **common,
            name=f"duct_only_96_{slug}_1000step_real",
            geometry_mode="duct_only",
            row_role="selected_96_duct",
        ),
        Step120RunSpec(
            **static_common,
            name=f"static_two_flap_96_{slug}_1000step_real",
            geometry_mode="static_two_flap",
            row_role="selected_96_static",
        ),
    ]


def resolve_step121_phase_specs(
    phase: str,
    *,
    best_selection_path: Optional[Path | str] = None,
    output_interval: int = 100,
) -> List[Step120RunSpec]:
    if phase == "smoke":
        return step121_smoke_specs()
    if phase == "references48":
        return step121_reference_48_specs(output_interval=output_interval)
    if phase == "candidates48":
        return step121_candidate_48_specs(output_interval=output_interval)
    if phase in {"selected96", "selected-static"}:
        if best_selection_path is None:
            raise ValueError(f"{phase} phase requires --best-selection-path")
        selection = _read_json(Path(best_selection_path))
        specs = make_selected_96_specs(selection, output_interval=output_interval)
        return [specs[0]] if phase == "selected96" else [specs[1]]
    if phase == "all48":
        return step121_reference_48_specs(output_interval=output_interval) + step121_candidate_48_specs(
            output_interval=output_interval
        )
    raise ValueError(f"unknown Step121 phase: {phase}")


def collect_step121_rows(output_dir: Path | str) -> List[Dict[str, Any]]:
    out = Path(output_dir)
    rows: List[Dict[str, Any]] = []
    if not out.is_dir():
        return rows
    for report in sorted(out.glob("*/finite_stability_report.json")):
        try:
            payload = _read_json(report)
        except Exception:
            continue
        row = dict(payload.get("summary_row") or payload)
        row.setdefault("name", report.parent.name)
        rows.append(row)
    return rows


def select_step121_best_boundary(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    refs = _reference_status(rows)
    candidates = _candidate_rows(rows)
    evaluated = [_evaluate_candidate(row, rows) for row in candidates]
    candidate_summaries = [_candidate_summary(item) for item in evaluated]

    if not refs["reference_comparison_ready"]:
        return _selection_payload(
            refs,
            candidate_summaries,
            campaign_state=CAMPAIGN_AWAITING_48_REFERENCES,
            final_classification=CLASSIFICATION_PARTIAL,
            reason="48_reference_rows_not_complete",
        )

    completed_semantics = {
        row.get("lbm_open_boundary_semantics")
        for row in candidates
        if _real_completed(row) and row.get("lbm_open_boundary_semantics") in REQUIRED_CANDIDATE_SEMANTICS
    }
    if completed_semantics != REQUIRED_CANDIDATE_SEMANTICS:
        return _selection_payload(
            refs,
            candidate_summaries,
            campaign_state=CAMPAIGN_AWAITING_48_CANDIDATES,
            final_classification=CLASSIFICATION_PARTIAL,
            reason="48_candidate_rows_not_complete",
        )

    passing = [item for item in evaluated if item["candidate_pass"]]
    if not passing:
        return _selection_payload(
            refs,
            candidate_summaries,
            campaign_state=CAMPAIGN_48_CANDIDATES_FAILED,
            final_classification=CLASSIFICATION_FAILED,
            reason="both_real_48_candidates_failed_hard_gates",
        )

    passing.sort(key=lambda item: item["sort_key"])
    selected = passing[0]["row"]
    payload = _selection_payload(
        refs,
        candidate_summaries,
        campaign_state=CAMPAIGN_BEST_48_SELECTED,
        final_classification=CLASSIFICATION_PARTIAL,
        reason="lowest_ranked_48_candidate_that_passed_step121_gate",
    )
    payload.update(
        {
            "best_boundary_selected": True,
            "campaign_should_stop_at_48": False,
            "selected_row_name": selected.get("name"),
            "selected_boundary_semantics": selected.get("lbm_open_boundary_semantics"),
            "selected_boundary_slug": _boundary_slug(selected.get("lbm_open_boundary_semantics")),
            "selected_limiter_parameters": {
                "open_boundary_limiter_enabled": bool(selected.get("open_boundary_limiter_enabled", False)),
                "limiter_activation_fraction": selected.get("limiter_activation_fraction"),
            },
            "selected_48_metrics": {
                "flux_imbalance_rel_tail_mean": selected.get("flux_imbalance_rel_tail_mean"),
                "mass_total_delta_rel_final": selected.get("mass_total_delta_rel_final"),
                "limiter_activation_fraction": selected.get("limiter_activation_fraction"),
                "runtime_s": selected.get("runtime_s"),
            },
        }
    )
    return payload


def build_step121_gate_report(rows: Sequence[Dict[str, Any]], best_selection: Dict[str, Any]) -> Dict[str, Any]:
    rows_by_name = {str(row.get("name")): row for row in rows if row.get("name") is not None}
    selected = bool(best_selection.get("best_boundary_selected", False))
    selected_chain = _selected_chain_rows(rows, best_selection)
    selected_limiter = _selected_chain_limiter_summary(selected_chain)
    global_limiter_blocked = any(
        _metric(row, "limiter_activation_fraction", 0.0) > LIMITER_ACTIVATION_FRACTION_LIMIT for row in rows
    )
    required_selected_rows: List[str] = []
    missing_selected_rows: List[str] = []
    failed_selected_rows: List[str] = []
    campaign_state = str(best_selection.get("campaign_state") or CAMPAIGN_AWAITING_48_REFERENCES)
    classification = str(best_selection.get("final_classification") or CLASSIFICATION_PARTIAL)

    if selected:
        slug = str(best_selection.get("selected_boundary_slug") or _boundary_slug(best_selection.get("selected_boundary_semantics")))
        selected_48_name = str(best_selection.get("selected_row_name") or "")
        required_selected_rows = [
            f"duct_only_96_{slug}_1000step_real",
            f"static_two_flap_96_{slug}_1000step_real",
        ]
        duct = rows_by_name.get(required_selected_rows[0])
        static = rows_by_name.get(required_selected_rows[1])
        if duct is None:
            missing_selected_rows.append(required_selected_rows[0])
            campaign_state = CAMPAIGN_AWAITING_SELECTED_96_DUCT
        elif not _row_validation_pass(duct):
            failed_selected_rows.append(required_selected_rows[0])
            campaign_state = CAMPAIGN_AWAITING_SELECTED_96_DUCT
        elif static is None:
            missing_selected_rows.append(required_selected_rows[1])
            campaign_state = CAMPAIGN_AWAITING_SELECTED_96_STATIC
        elif not _row_validation_pass(static):
            failed_selected_rows.append(required_selected_rows[1])
            campaign_state = CAMPAIGN_AWAITING_SELECTED_96_STATIC
        elif selected_48_name and selected_limiter["selected_chain_limiter_gate_pass"]:
            campaign_state = CAMPAIGN_COMPLETE
            classification = CLASSIFICATION_SUCCESS
        else:
            classification = CLASSIFICATION_PARTIAL
        if campaign_state != CAMPAIGN_COMPLETE:
            classification = CLASSIFICATION_PARTIAL

    quasi2d_allowed = bool(classification == CLASSIFICATION_SUCCESS)
    return {
        "step": 121,
        "step121_schema_version": STEP121_SCHEMA_VERSION,
        "source_step120_schema_version": STEP120_SCHEMA_VERSION,
        "campaign_state": campaign_state,
        "final_classification": classification,
        "allowed_final_classifications": sorted(FINAL_CLASSIFICATIONS),
        "quasi2d_allowed": quasi2d_allowed,
        "step121_quasi2d_allowed": quasi2d_allowed,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "full_fsi_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "best_boundary_selected": selected,
        "selected_boundary_semantics": best_selection.get("selected_boundary_semantics"),
        "selected_boundary_slug": best_selection.get("selected_boundary_slug"),
        "required_selected_rows": required_selected_rows,
        "missing_selected_rows": missing_selected_rows,
        "failed_selected_rows": failed_selected_rows,
        "selected_chain_row_names": [row.get("name") for row in selected_chain],
        "selected_chain_limiter_gate_pass": selected_limiter["selected_chain_limiter_gate_pass"],
        "selected_chain_limiter_summary": selected_limiter,
        "global_limiter_gate_not_used_for_final_classification": True,
        "global_limiter_gate_would_block_if_used": bool(global_limiter_blocked),
        "no_fluent_claim": True,
        "no_fsi_claim": True,
        "static_two_flap_rows_are_lbm_only": True,
    }


def detect_step121_lightweight_failure(
    stability: Dict[str, Any],
    mass_state: Optional[Dict[str, Any]] = None,
    *,
    rho_min_limit: float = 0.85,
    rho_max_limit: float = 1.15,
    max_v_limit: float = 0.35,
    negative_population_fraction_limit: float = 1.0e-3,
    mass_drift_limit: float = 0.05,
) -> Dict[str, Any]:
    reasons: List[str] = []
    rho_min = _finite_float(stability.get("rho_min", math.nan))
    rho_max = _finite_float(stability.get("rho_max", math.nan))
    max_v = _finite_float(stability.get("max_v", math.nan))
    neg_frac = _finite_float(stability.get("negative_population_fraction", 0.0))
    if not bool(stability.get("stability_all_finite", True)):
        reasons.append("nonfinite_field")
    if not math.isfinite(rho_min) or not math.isfinite(rho_max) or rho_min <= rho_min_limit or rho_max >= rho_max_limit:
        reasons.append("rho_range")
    if not math.isfinite(max_v) or max_v >= max_v_limit:
        reasons.append("max_v")
    for key in ("f_min", "f_max", "F_min", "F_max"):
        value = _finite_float(stability.get(key, 0.0))
        if not math.isfinite(value):
            reasons.append(f"nonfinite_{key}")
    if neg_frac > negative_population_fraction_limit:
        reasons.append("negative_population_fraction")
    mass_drift = None
    if mass_state:
        mass_total = mass_state.get("mass_total")
        mass_initial = mass_state.get("mass_initial")
        if mass_total is not None and mass_initial not in (None, 0):
            mass_drift = _finite_float((float(mass_total) - float(mass_initial)) / float(mass_initial))
            if not math.isfinite(mass_drift) or abs(mass_drift) > mass_drift_limit:
                reasons.append("mass_drift")
    return {
        "failure_detected": bool(reasons),
        "first_failure_step": int(stability.get("step", 0) or 0) if reasons else None,
        "first_failure_reason": reasons[0] if reasons else None,
        "failure_reasons": reasons,
        "rho_min": rho_min,
        "rho_max": rho_max,
        "max_v": max_v,
        "negative_population_fraction": neg_frac,
        "mass_total_delta_rel": mass_drift,
        "detector": "step121_lightweight_failure_detector",
    }


def merge_step121_history(
    previous: Sequence[Dict[str, Any]],
    current: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: Dict[int, Dict[str, Any]] = {}
    order: List[int] = []
    for row in list(previous) + list(current):
        if "step" not in row:
            continue
        step = int(row["step"])
        if step not in merged:
            order.append(step)
        merged[step] = dict(row)
    return [merged[step] for step in sorted(order)]


def write_step121_checkpoint_payload(
    checkpoint_root: Path | str,
    row_name: str,
    step: int,
    metadata: Dict[str, Any],
    history: Dict[str, Any],
    *,
    keep_last: int = 3,
) -> Path:
    root = Path(checkpoint_root) / row_name
    root.mkdir(parents=True, exist_ok=True)
    payload = {
        "step": int(step),
        "step121_schema_version": STEP121_SCHEMA_VERSION,
        "metadata": {**metadata, "step": int(step)},
        "history": history,
    }
    path = root / f"checkpoint_step_{int(step):06d}.json"
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    json.loads(tmp.read_text(encoding="utf-8"))
    os.replace(tmp, path)
    _prune_old_checkpoints(root, keep_last=keep_last)
    return path


def load_latest_step121_checkpoint_payload(checkpoint_root: Path | str, row_name: str) -> Optional[Dict[str, Any]]:
    root = Path(checkpoint_root) / row_name
    if not root.is_dir():
        return None
    for path in sorted(root.glob("checkpoint_step_*.json"), reverse=True):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if int(payload.get("step", -1)) != int(payload.get("metadata", {}).get("step", -2)):
            continue
        return payload
    return None


def write_step121_failure_snapshot_arrays(
    row_dir: Path | str,
    runtime_root: Path | str,
    row_name: str,
    *,
    step: int,
    reason: str,
    rho: np.ndarray,
    v: np.ndarray,
    f: np.ndarray,
    F: np.ndarray,
) -> Path:
    row_path = Path(row_dir)
    row_path.mkdir(parents=True, exist_ok=True)
    runtime_dir = Path(runtime_root) / row_name
    runtime_dir.mkdir(parents=True, exist_ok=True)
    safe_reason = str(reason).replace(":", "_").replace("/", "_").replace("\\", "_")
    raw_path = runtime_dir / f"failure_snapshot_step_{int(step):06d}_{safe_reason}.npz"
    np.savez_compressed(raw_path, rho=rho, v=v, f=f, F=F)
    anomaly_cell = _anomaly_cell(rho, v)
    local = _local_window_stats(rho, v, anomaly_cell)
    stats = {
        "step": int(step),
        "row_name": row_name,
        "reason": reason,
        "runtime_npz_path": str(raw_path),
        "raw_arrays_committed_to_git": False,
        "rho_shape": list(rho.shape),
        "v_shape": list(v.shape),
        "f_shape": list(f.shape),
        "F_shape": list(F.shape),
        "field_stats": {
            "rho_min": _finite_float(np.nanmin(rho)),
            "rho_max": _finite_float(np.nanmax(rho)),
            "max_v": _finite_float(np.nanmax(np.linalg.norm(v, axis=-1))) if v.size else 0.0,
            "f_min": _finite_float(np.nanmin(f)),
            "F_min": _finite_float(np.nanmin(F)),
        },
        "anomaly_cell": list(anomaly_cell),
        "local_window": local,
        "validation_claim_allowed": False,
    }
    stats_path = row_path / f"failure_snapshot_step_{int(step):06d}_{safe_reason}_stats.json"
    stats_path.write_text(json.dumps(stats, indent=2, sort_keys=True), encoding="utf-8")
    return stats_path


def run_step121_matrix(
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    *,
    phase: str = "smoke",
    specs: Optional[Sequence[Step120RunSpec]] = None,
    best_selection_path: Optional[Path | str] = None,
    force: bool = False,
    resume: bool = True,
    allow_large_real_rows: bool = False,
    output_interval: int = 100,
    checkpoint_root: Path | str = DEFAULT_CHECKPOINT_ROOT,
    max_rows: Optional[int] = None,
    max_wall_seconds: Optional[float] = None,
) -> Dict[str, Any]:
    out = Path(output_dir)
    selected_specs = list(specs) if specs is not None else resolve_step121_phase_specs(
        phase,
        best_selection_path=best_selection_path,
        output_interval=output_interval,
    )
    if selected_specs:
        run_step120_matrix(
            out,
            specs=selected_specs,
            force=force,
            resume=resume,
            max_rows=max_rows,
            max_wall_seconds=max_wall_seconds,
            allow_large_real_rows=allow_large_real_rows,
            checkpoint_root=checkpoint_root,
        )
        _remove_step120_aggregate_artifacts(out)
    rows = collect_step121_rows(out)
    return write_step121_artifacts(out, rows, phase=phase)


def write_step121_artifacts(output_dir: Path | str, rows: Sequence[Dict[str, Any]], *, phase: str) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    selection = select_step121_best_boundary(rows)
    gate = build_step121_gate_report(rows, selection)
    summary = {
        "step": 121,
        "step121_schema_version": STEP121_SCHEMA_VERSION,
        "phase": phase,
        "row_count": int(len(rows)),
        "campaign_state": gate["campaign_state"],
        "final_classification": gate["final_classification"],
        "quasi2d_allowed": gate["quasi2d_allowed"],
        "validation_claim_allowed": False,
    }
    _write_json(out / "step121_best_boundary_selection.json", selection)
    _write_json(out / "step121_gate_report.json", gate)
    _write_json(out / "step121_summary.json", summary)
    _write_json(
        out / "solver_report.json",
        {
            **summary,
            "goal_file": "STEP121_LBM_BOUNDARY_REAL_CAMPAIGN_AND_GATE_CORRECTION_GOAL.md",
            "runner_file": "experiments/steps/step121_lbm_boundary_real_campaign_and_gate_correction.py",
            "best_boundary_selection": selection,
            "gate_report": gate,
            "fluid_only": True,
            "full_fsi_rerun_done": False,
            "fluent_validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
            "static_two_flap_rows_are_lbm_only": True,
        },
    )
    _write_output_readme(out, summary)
    return {"summary": summary, "selection": selection, "gate": gate, "runs": list(rows)}


def _remove_step120_aggregate_artifacts(out: Path) -> None:
    legacy_names = [
        "best_boundary_selection.json",
        "boundary_variant_48_comparison.json",
        "boundary_variant_96_validation.json",
        "first_failure_global_summary.json",
        "limiter_actual_activation_summary.json",
        "row_status_summary.json",
        "run_matrix_summary.csv",
        "run_matrix_summary.json",
        "step120_gate_report.json",
    ]
    for name in legacy_names:
        path = out / name
        if path.is_file():
            path.unlink()


def _reference_status(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    refs: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        semantics = row.get("lbm_open_boundary_semantics")
        if row.get("requested_nx") == 48 and semantics in REFERENCE_SEMANTICS:
            refs[str(semantics)] = row
    missing = sorted(REQUIRED_REFERENCE_SEMANTICS - set(refs))
    incomplete = [
        semantics
        for semantics, row in refs.items()
        if semantics in REQUIRED_REFERENCE_SEMANTICS and not _real_completed(row)
    ]
    return {
        "reference_comparison_ready": not missing and not incomplete,
        "reference_rows": {
            semantics: {
                "name": row.get("name"),
                "requested_window_completed": bool(row.get("requested_window_completed", False)),
                "simulation_backed_artifact": bool(row.get("simulation_backed_artifact", False)),
            }
            for semantics, row in refs.items()
            if semantics in REQUIRED_REFERENCE_SEMANTICS
        },
        "missing_reference_semantics": missing,
        "incomplete_reference_semantics": sorted(incomplete),
    }


def _candidate_rows(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    result = []
    for row in rows:
        semantics = row.get("lbm_open_boundary_semantics")
        if row.get("row_role") == "candidate_48" or (
            row.get("requested_nx") == 48 and semantics in CANDIDATE_SEMANTICS
        ):
            result.append(row)
    return result


def _evaluate_candidate(row: Dict[str, Any], rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    reasons: List[str] = []
    flux = _metric(row, "flux_imbalance_rel_tail_mean")
    mass = abs(_metric(row, "mass_total_delta_rel_final"))
    limiter = _metric(row, "limiter_activation_fraction")
    if not _real_completed(row):
        reasons.append("requested_window_not_completed")
    if not bool(row.get("step120_validation_claimed", False)):
        reasons.append("validation_not_claimed")
    for key in ("finite_pass", "density_gate_pass", "mass_drift_gate_pass", "population_gate_pass", "mach_gate_pass"):
        if row.get(key) is not True:
            reasons.append(key)
    if row.get("first_failure_step") is not None or row.get("first_failure_reason") is not None:
        reasons.append("first_failure")
    if bool(row.get("not_used_for_validation", False)):
        reasons.append("not_used_for_validation")
    if flux >= 0.1:
        reasons.append("flux_imbalance_gate")
    if mass >= 0.005:
        reasons.append("mass_drift_gate")
    regularized = _row_by_semantics(rows, "regularized_velocity_pressure")
    legacy = _row_by_semantics(rows, "equilibrium_all_population_reset")
    if regularized is not None and flux >= _metric(regularized, "flux_imbalance_rel_tail_mean"):
        reasons.append("not_improved_over_regularized")
    if legacy is not None:
        legacy_mass = abs(_metric(legacy, "mass_total_delta_rel_final"))
        legacy_flux = _metric(legacy, "flux_imbalance_rel_tail_mean")
        if mass > max(legacy_mass * 2.0, 0.005):
            reasons.append("mass_worse_than_legacy")
        if flux > max(legacy_flux * 2.0, 0.1):
            reasons.append("flux_worse_than_legacy")
    if limiter > LIMITER_ACTIVATION_FRACTION_LIMIT:
        reasons.append("limiter_activation_gate")
    return {
        "row": row,
        "rejection_reasons": sorted(set(reasons)),
        "candidate_pass": not reasons,
        "sort_key": (
            0 if not reasons else 1,
            flux,
            mass,
            limiter,
            _metric(row, "mach_proxy_observed_max"),
            _metric(row, "runtime_s"),
        ),
    }


def _candidate_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    row = item["row"]
    return {
        "name": row.get("name"),
        "semantics": row.get("lbm_open_boundary_semantics"),
        "completed_real_row": _real_completed(row),
        "simulation_backed_artifact": bool(row.get("simulation_backed_artifact", False)),
        "candidate_pass": item["candidate_pass"],
        "rejection_reasons": item["rejection_reasons"],
        "flux_imbalance_rel_tail_mean": row.get("flux_imbalance_rel_tail_mean"),
        "mass_total_delta_rel_final": row.get("mass_total_delta_rel_final"),
        "limiter_activation_fraction": row.get("limiter_activation_fraction"),
        "not_used_for_validation": bool(row.get("not_used_for_validation", False)),
    }


def _selection_payload(
    refs: Dict[str, Any],
    candidate_summaries: Sequence[Dict[str, Any]],
    *,
    campaign_state: str,
    final_classification: str,
    reason: str,
) -> Dict[str, Any]:
    return {
        "step": 121,
        "step121_schema_version": STEP121_SCHEMA_VERSION,
        "best_boundary_selected": False,
        "campaign_should_stop_at_48": campaign_state == CAMPAIGN_48_CANDIDATES_FAILED,
        "campaign_state": campaign_state,
        "final_classification": final_classification,
        "reference_comparison_ready": refs["reference_comparison_ready"],
        "reference_status": refs,
        "candidate_summaries": list(candidate_summaries),
        "selection_reason": reason,
        "validation_claim_allowed": False,
    }


def _selected_chain_rows(rows: Sequence[Dict[str, Any]], selection: Dict[str, Any]) -> List[Dict[str, Any]]:
    names = {
        selection.get("selected_row_name"),
        f"duct_only_96_{selection.get('selected_boundary_slug')}_1000step_real",
        f"static_two_flap_96_{selection.get('selected_boundary_slug')}_1000step_real",
    }
    return [
        row
        for row in rows
        if row.get("name") in names
        or (row.get("row_role") in SELECTED_CHAIN_ROLES and row.get("lbm_open_boundary_semantics") == selection.get("selected_boundary_semantics"))
    ]


def _selected_chain_limiter_summary(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    max_fraction = max([_metric(row, "limiter_activation_fraction", 0.0) for row in rows] or [0.0])
    blocked_rows = [
        row.get("name")
        for row in rows
        if _metric(row, "limiter_activation_fraction", 0.0) > LIMITER_ACTIVATION_FRACTION_LIMIT
    ]
    return {
        "row_count": int(len(rows)),
        "selected_chain_limiter_gate_pass": not blocked_rows,
        "max_limiter_activation_fraction": _finite_float(max_fraction),
        "limiter_activation_fraction_limit": LIMITER_ACTIVATION_FRACTION_LIMIT,
        "blocked_row_names": blocked_rows,
    }


def _row_validation_pass(row: Dict[str, Any]) -> bool:
    return bool(_real_completed(row) and row.get("step120_validation_claimed") is True and row.get("first_failure_step") is None)


def _real_completed(row: Dict[str, Any]) -> bool:
    return bool(row.get("requested_window_completed") is True and row.get("simulation_backed_artifact") is True)


def _row_by_semantics(rows: Sequence[Dict[str, Any]], semantics: str) -> Optional[Dict[str, Any]]:
    for row in rows:
        if row.get("requested_nx") == 48 and row.get("lbm_open_boundary_semantics") == semantics:
            return row
    return None


def _prune_old_checkpoints(root: Path, *, keep_last: int) -> None:
    paths = sorted(root.glob("checkpoint_step_*.json"))
    for old in paths[: max(0, len(paths) - int(keep_last))]:
        try:
            old.unlink()
        except OSError:
            pass


def _anomaly_cell(rho: np.ndarray, v: np.ndarray) -> tuple[int, int, int]:
    rho_score = np.abs(np.asarray(rho, dtype=float) - 1.0)
    if v.size:
        vmag = np.linalg.norm(np.asarray(v, dtype=float), axis=-1)
        score = rho_score + vmag
    else:
        score = rho_score
    return tuple(int(i) for i in np.unravel_index(int(np.nanargmax(score)), score.shape))


def _local_window_stats(rho: np.ndarray, v: np.ndarray, cell: tuple[int, int, int], radius: int = 1) -> Dict[str, Any]:
    x, y, z = cell
    slices = tuple(slice(max(0, idx - radius), min(shape, idx + radius + 1)) for idx, shape in zip((x, y, z), rho.shape))
    rho_window = rho[slices]
    v_window = v[slices] if v.size else np.zeros((*rho_window.shape, 3), dtype=np.float32)
    return {
        "bounds": [[sl.start, sl.stop] for sl in slices],
        "rho_min": _stable_json_float(np.nanmin(rho_window)),
        "rho_max": _stable_json_float(np.nanmax(rho_window)),
        "max_v": _stable_json_float(np.nanmax(np.linalg.norm(v_window, axis=-1))) if v_window.size else 0.0,
    }


def _stable_json_float(value: Any) -> float:
    return round(_finite_float(value), 7)


def _write_output_readme(out: Path, summary: Dict[str, Any]) -> None:
    text = [
        "# Step121 LBM Boundary Real Campaign And Gate Correction",
        "",
        "This directory contains Step121 LBM-only campaign-controller artifacts.",
        "",
        f"- Campaign state: `{summary['campaign_state']}`",
        f"- Final classification: `{summary['final_classification']}`",
        f"- Quasi-2D allowed: `{str(summary['quasi2d_allowed']).lower()}`",
        f"- Rows recorded: `{summary['row_count']}`",
        "",
        "No Fluent parity, full FSI, or dynamic flap claim is made by this step.",
        "Bulky checkpoints and failure snapshots stay under `outputs/tmp` and are not committed.",
        "",
    ]
    (out / "README.md").write_text("\n".join(text), encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--phase",
        choices=["smoke", "references48", "candidates48", "all48", "selected96", "selected-static", "summary"],
        default="smoke",
    )
    parser.add_argument("--best-selection-path", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--allow-large-real-rows", action="store_true")
    parser.add_argument("--output-interval", type=int, default=100)
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--max-wall-seconds", type=float, default=None)
    args = parser.parse_args(argv)

    if args.phase == "summary":
        rows = collect_step121_rows(args.output_dir)
        write_step121_artifacts(args.output_dir, rows, phase=args.phase)
        return 0

    run_step121_matrix(
        args.output_dir,
        phase=args.phase,
        best_selection_path=args.best_selection_path,
        force=args.force,
        resume=not args.no_resume,
        allow_large_real_rows=args.allow_large_real_rows,
        output_interval=args.output_interval,
        checkpoint_root=DEFAULT_CHECKPOINT_ROOT,
        max_rows=args.max_rows,
        max_wall_seconds=args.max_wall_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
