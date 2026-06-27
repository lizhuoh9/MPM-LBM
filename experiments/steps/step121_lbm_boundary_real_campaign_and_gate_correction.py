from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
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
    FLOW_REPAIR_CANDIDATE_SEMANTICS,
    PLANE_FLUX_CONTROL_CANDIDATE_SEMANTICS,
    REPAIRED_CANDIDATE_SEMANTICS,
    STEP120_SCHEMA_VERSION,
    REFERENCE_SEMANTICS,
    Step120RunSpec,
    _boundary_slug,
    _metric,
    _replace_spec,
    run_step120_matrix,
    run_manifest_hash_for_spec,
    solver_state_hash_for_spec,
    step120_real_run_specs,
    step120_row_reusable_for_spec,
)


DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "step121_lbm_boundary_real_campaign_and_gate_correction"
DEFAULT_CHECKPOINT_ROOT = REPO_ROOT / "outputs" / "tmp" / "step121_checkpoints"
DEFAULT_RUNTIME_SNAPSHOT_ROOT = REPO_ROOT / "outputs" / "tmp" / "step121_failure_snapshots"
STEP121_SCHEMA_VERSION = 1

CAMPAIGN_AWAITING_48_REFERENCES = "awaiting_48_references"
CAMPAIGN_48_LEGACY_REFERENCE_FAILED = "48_legacy_reference_failed"
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
REQUIRED_REPAIRED_CANDIDATE_SEMANTICS = set(REPAIRED_CANDIDATE_SEMANTICS)
SELECTED_CHAIN_ROLES = {"candidate_48", "repair_candidate_48", "selected_96_duct", "selected_96_static"}
SELECTED_BOUNDARY_PROVENANCE_KEYS = [
    "open_boundary_limiter_enabled",
    "open_boundary_rho_min",
    "open_boundary_rho_max",
    "open_boundary_u_max",
    "open_boundary_noneq_cap",
    "open_boundary_population_floor",
    "inlet_u_lbm",
    "outlet_rho",
    "lbm_niu",
    "lbm_viscosity_semantics",
    "lbm_relaxation_semantics",
    "tau",
    "config_hash",
    "solver_state_hash",
]
SELECTED_96_OUTLET_FLUX_MIN = 1.0e-12
STEP121_CAMPAIGN_MANIFEST = "campaign_manifest.json"
STEP121_CAMPAIGN_MANIFEST_SCHEMA_VERSION = 2
STEP121_CAMPAIGN_BASE_COMMIT = "516b1aaa4c71d5468ce5ea444a21ffa07741c8bc"
FLOW_INLET_FLUX_MIN = 1.0e-6
FLOW_RATIO_MIN = 0.80
FLOW_RATIO_MAX = 1.20
FLOW_IMBALANCE_TAIL_MEAN_MAX = 0.10
FLOW_IMBALANCE_TAIL_MAX_MAX = 0.20
FLOW_OUTLET_TAIL_CV_MAX = 0.10


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


def step121_repair_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    return [
        _replace_spec(spec, output_interval=output_interval)
        for spec in step120_real_run_specs(output_interval=output_interval)
        if spec.row_role == "repair_candidate_48"
    ]


def step121_flow_repair_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    return [
        _replace_spec(spec, output_interval=output_interval)
        for spec in step120_real_run_specs(output_interval=output_interval)
        if spec.row_role == "flow_repair_candidate_48"
        and spec.open_boundary_semantics in FLOW_REPAIR_CANDIDATE_SEMANTICS
    ]


def step121_plane_flux_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    return [
        _replace_spec(spec, output_interval=output_interval)
        for spec in step120_real_run_specs(output_interval=output_interval)
        if spec.row_role == "plane_flux_control_candidate_48"
        and spec.open_boundary_semantics in PLANE_FLUX_CONTROL_CANDIDATE_SEMANTICS
    ]


def _step132_gain_slug(value: float) -> str:
    return f"{float(value):.2f}".replace(".", "p")


def _step132_cap_slug(value: float) -> str:
    return f"{float(value):.3f}".replace(".", "p")


def _step133_param_slug(value: float, decimals: int, *, strip_trailing: bool = True) -> str:
    text = f"{float(value):.{int(decimals)}f}"
    if strip_trailing:
        text = text.rstrip("0").rstrip(".")
    return text.replace(".", "p")


def step121_plane_flux_sweep_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    baseline_by_semantics = {
        spec.open_boundary_semantics: spec for spec in step121_plane_flux_48_specs(output_interval=output_interval)
    }
    sweep_plan = [
        ("regularized_plane_flux_controlled_pressure_outlet", 0.05, 0.002),
        ("regularized_plane_flux_controlled_pressure_outlet", 0.10, 0.002),
        ("regularized_plane_flux_controlled_pressure_outlet", 0.25, 0.002),
        ("regularized_plane_flux_controlled_pressure_outlet", 0.25, 0.005),
        ("convective_plane_flux_controlled_damped_outlet", 0.05, 0.002),
        ("convective_plane_flux_controlled_damped_outlet", 0.10, 0.002),
    ]
    name_slug_by_semantics = {
        "regularized_plane_flux_controlled_pressure_outlet": "regularized_plane_flux_controlled",
        "convective_plane_flux_controlled_damped_outlet": "convective_plane_flux_controlled_damped",
    }
    specs: List[Step120RunSpec] = []
    for semantics, gain_u, cap_u in sweep_plan:
        base = baseline_by_semantics[semantics]
        specs.append(
            _replace_spec(
                base,
                name=(
                    f"duct_only_48_{name_slug_by_semantics[semantics]}"
                    f"_gain{_step132_gain_slug(gain_u)}_cap{_step132_cap_slug(cap_u)}_250step_triage"
                ),
                output_interval=output_interval,
                open_boundary_flux_feedback_gain_u=gain_u,
                open_boundary_flux_feedback_gain_rho=0.0,
                open_boundary_flux_filter_alpha=0.02,
                open_boundary_flux_correction_cap_u=cap_u,
                open_boundary_convective_blend_weight=0.02,
                artifact_scope_note=(
                    "Step132 bounded 48^3 plane-flux controller authority sweep; "
                    "reuses Step131 semantics and is not a selected96 enabling row"
                ),
            )
        )
    return specs


def step121_plane_flux_mass_damped_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    sweep_specs = step121_plane_flux_sweep_48_specs(output_interval=output_interval)
    regularized_base = next(
        spec
        for spec in sweep_specs
        if spec.open_boundary_semantics == "regularized_plane_flux_controlled_pressure_outlet"
        and math.isclose(float(spec.open_boundary_flux_feedback_gain_u), 0.25, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(spec.open_boundary_flux_correction_cap_u), 0.005, rel_tol=0.0, abs_tol=1.0e-12)
    )
    convective_base = next(
        spec
        for spec in sweep_specs
        if spec.open_boundary_semantics == "convective_plane_flux_controlled_damped_outlet"
        and math.isclose(float(spec.open_boundary_flux_feedback_gain_u), 0.10, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(spec.open_boundary_flux_correction_cap_u), 0.002, rel_tol=0.0, abs_tol=1.0e-12)
    )
    mass_damped_plan = [
        (regularized_base, 0.25, 0.005, 0.0005, 0.02, 0.0005, 0.50),
        (regularized_base, 0.25, 0.005, 0.0010, 0.02, 0.0005, 0.50),
        (regularized_base, 0.25, 0.005, 0.0020, 0.02, 0.0005, 0.50),
        (regularized_base, 0.25, 0.005, 0.0010, 0.01, 0.00025, 0.50),
        (regularized_base, 0.25, 0.005, 0.0010, 0.005, 0.00025, 0.25),
        (convective_base, 0.10, 0.002, 0.0010, 0.02, 0.0005, 0.50),
    ]
    name_slug_by_semantics = {
        "regularized_plane_flux_controlled_pressure_outlet": "regularized_plane_flux_controlled",
        "convective_plane_flux_controlled_damped_outlet": "convective_plane_flux_controlled_damped",
    }
    specs: List[Step120RunSpec] = []
    for base, gain_u, cap_u, gain_rho, alpha, delta_cap_u, slew_alpha in mass_damped_plan:
        semantics = base.open_boundary_semantics
        specs.append(
            _replace_spec(
                base,
                name=(
                    f"duct_only_48_{name_slug_by_semantics[semantics]}"
                    f"_gain{_step132_gain_slug(gain_u)}"
                    f"_cap{_step132_cap_slug(cap_u)}"
                    f"_rho{_step133_param_slug(gain_rho, 4)}"
                    f"_alpha{_step133_param_slug(alpha, 3)}"
                    f"_du{_step133_param_slug(delta_cap_u, 5)}"
                    f"_slew{_step133_param_slug(slew_alpha, 2, strip_trailing=False)}"
                    "_250step_triage"
                ),
                output_interval=output_interval,
                open_boundary_flux_feedback_gain_u=gain_u,
                open_boundary_flux_feedback_gain_rho=gain_rho,
                open_boundary_flux_filter_alpha=alpha,
                open_boundary_flux_correction_cap_u=cap_u,
                open_boundary_flux_feedback_delta_cap_u=delta_cap_u,
                open_boundary_flux_feedback_slew_alpha=slew_alpha,
                open_boundary_convective_blend_weight=0.02,
                artifact_scope_note=(
                    "Step133 bounded 48^3 mass-damped plane-flux triage; "
                    "adds slow density feedback and outlet stationarity damping; "
                    "not a selected96 enabling row"
                ),
            )
        )
    return specs


def step121_plane_flux_stationarity_48_specs(output_interval: int = 100) -> List[Step120RunSpec]:
    mass_damped_specs = step121_plane_flux_mass_damped_48_specs(output_interval=output_interval)
    regularized_base = next(
        spec
        for spec in mass_damped_specs
        if spec.open_boundary_semantics == "regularized_plane_flux_controlled_pressure_outlet"
        and math.isclose(float(spec.open_boundary_flux_feedback_gain_u), 0.25, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(spec.open_boundary_flux_correction_cap_u), 0.005, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(spec.open_boundary_flux_feedback_gain_rho), 0.001, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(spec.open_boundary_flux_filter_alpha), 0.02, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(spec.open_boundary_flux_feedback_delta_cap_u), 0.0005, rel_tol=0.0, abs_tol=1.0e-12)
        and math.isclose(float(spec.open_boundary_flux_feedback_slew_alpha), 0.50, rel_tol=0.0, abs_tol=1.0e-12)
    )
    convective_base = next(
        spec
        for spec in mass_damped_specs
        if spec.open_boundary_semantics == "convective_plane_flux_controlled_damped_outlet"
    )
    stationarity_plan = [
        (regularized_base, 0.25, 0.005, 0.0010, 0.02, 0.0005, 0.50, 1, False, 0.60),
        (regularized_base, 0.25, 0.005, 0.0010, 0.02, 0.0005, 0.50, 1, True, 0.50),
        (regularized_base, 0.25, 0.005, 0.0010, 0.02, 0.0005, 0.50, 1, True, 0.70),
        (regularized_base, 0.25, 0.005, 0.0010, 0.01, 0.0005, 0.50, 1, True, 0.70),
        (regularized_base, 0.25, 0.005, 0.0010, 0.02, 0.0005, 0.50, 2, True, 0.70),
        (convective_base, 0.10, 0.002, 0.0010, 0.02, 0.0005, 0.50, 1, True, 0.70),
    ]
    name_slug_by_semantics = {
        "regularized_plane_flux_controlled_pressure_outlet": "regularized_plane_flux_controlled",
        "convective_plane_flux_controlled_damped_outlet": "convective_plane_flux_controlled_damped",
    }
    specs: List[Step120RunSpec] = []
    for (
        base,
        gain_u,
        cap_u,
        gain_rho,
        alpha,
        delta_cap_u,
        slew_alpha,
        measure_offset,
        drop_guard_enabled,
        drop_guard_min_ratio,
    ) in stationarity_plan:
        semantics = base.open_boundary_semantics
        guard_slug = "on" if drop_guard_enabled else "off"
        specs.append(
            _replace_spec(
                base,
                name=(
                    f"duct_only_48_{name_slug_by_semantics[semantics]}"
                    f"_gain{_step132_gain_slug(gain_u)}"
                    f"_cap{_step132_cap_slug(cap_u)}"
                    f"_rho{_step133_param_slug(gain_rho, 4)}"
                    f"_alpha{_step133_param_slug(alpha, 3)}"
                    f"_du{_step133_param_slug(delta_cap_u, 5)}"
                    f"_slew{_step133_param_slug(slew_alpha, 2, strip_trailing=False)}"
                    f"_offset{int(measure_offset)}"
                    f"_guard_{guard_slug}"
                    f"_min{_step133_param_slug(drop_guard_min_ratio, 2, strip_trailing=False)}"
                    "_250step_triage"
                ),
                output_interval=output_interval,
                open_boundary_flux_feedback_gain_u=gain_u,
                open_boundary_flux_feedback_gain_rho=gain_rho,
                open_boundary_flux_filter_alpha=alpha,
                open_boundary_flux_correction_cap_u=cap_u,
                open_boundary_flux_feedback_delta_cap_u=delta_cap_u,
                open_boundary_flux_feedback_slew_alpha=slew_alpha,
                open_boundary_convective_blend_weight=0.02,
                open_boundary_flux_control_measure_plane_offset=measure_offset,
                open_boundary_outlet_flux_drop_guard_enabled=drop_guard_enabled,
                open_boundary_outlet_flux_drop_guard_min_ratio=drop_guard_min_ratio,
                artifact_scope_note=(
                    "Step134 bounded 48^3 outlet tail-collapse diagnosis and near-outlet control-plane repair; "
                    "does not enable selected96 or 500-step promotion"
                ),
            )
        )
    return specs


def _provenance_float(provenance: Dict[str, Any], key: str, default: float) -> float:
    value = provenance.get(key, default)
    if value is None:
        return float(default)
    return float(value)


def _selected_boundary_provenance(row: Dict[str, Any]) -> Dict[str, Any]:
    provenance: Dict[str, Any] = {}
    for key in SELECTED_BOUNDARY_PROVENANCE_KEYS:
        if key in row:
            provenance[key] = row.get(key)
    if "open_boundary_limiter_enabled" not in provenance:
        provenance["open_boundary_limiter_enabled"] = bool(row.get("open_boundary_limiter_enabled", False))
    return provenance


def _require_selected_96_duct_pass(output_dir: Path, duct_spec: Step120RunSpec) -> Dict[str, Any]:
    report_path = output_dir / duct_spec.name / "finite_stability_report.json"
    if not report_path.is_file():
        raise ValueError(f"selected 96 duct row must complete before selected-static: missing {duct_spec.name}")
    payload = _read_json(report_path)
    row = dict(payload.get("summary_row") or payload)
    row.setdefault("name", duct_spec.name)
    failures = []
    if not step120_row_reusable_for_spec(report_path.parent, duct_spec):
        failures.append("spec_provenance_mismatch")
    if row.get("requested_window_completed") is not True:
        failures.append("requested_window_completed")
    if row.get("step120_validation_claimed") is not True:
        failures.append("step120_validation_claimed")
    if row.get("first_failure_step") is not None or row.get("first_failure_reason") is not None:
        failures.append("first_failure")
    flow_gate = _selected_96_flow_development_gate(row)
    if not flow_gate["pass"]:
        failures.extend(flow_gate["reasons"])
    if not _row_validation_pass(row):
        failures.append("row_validation_pass")
    if failures:
        reasons = ",".join(sorted(set(failures)))
        raise ValueError(f"selected 96 duct row must pass before selected-static: {duct_spec.name} failed {reasons}")
    return row


def make_selected_96_specs(
    best_selection: Dict[str, Any],
    output_interval: int = 100,
    *,
    allow_legacy_provenance_defaults: Optional[bool] = None,
) -> List[Step120RunSpec]:
    if not bool(best_selection.get("best_boundary_selected", False)):
        raise ValueError("selected 96^3 specs require best_boundary_selected=true")
    semantics = str(best_selection.get("selected_boundary_semantics") or "")
    if semantics not in REQUIRED_CANDIDATE_SEMANTICS | REQUIRED_REPAIRED_CANDIDATE_SEMANTICS:
        raise ValueError(f"unsupported selected boundary semantics: {semantics!r}")
    slug = str(best_selection.get("selected_boundary_slug") or _boundary_slug(semantics))
    limited = semantics == "regularized_velocity_pressure_limited"
    provenance = dict(best_selection.get("selected_boundary_provenance") or {})
    allow_legacy = bool(
        best_selection.get("allow_legacy_provenance_defaults", False)
        if allow_legacy_provenance_defaults is None
        else allow_legacy_provenance_defaults
    )
    missing_provenance = [key for key in SELECTED_BOUNDARY_PROVENANCE_KEYS if key not in provenance]
    if missing_provenance and not allow_legacy:
        raise ValueError(
            "selected_boundary_provenance missing required formal keys: "
            + ",".join(sorted(missing_provenance))
        )
    limiter_parameters = dict(best_selection.get("selected_limiter_parameters") or {})
    limiter_enabled = bool(
        provenance.get(
            "open_boundary_limiter_enabled",
            limiter_parameters.get("open_boundary_limiter_enabled", limited),
        )
    )
    population_floor = provenance.get("open_boundary_population_floor")
    if population_floor is None:
        population_floor = -1.0e-8 if limiter_enabled else None
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
        "open_boundary_limiter_enabled": limiter_enabled,
        "open_boundary_rho_min": _provenance_float(provenance, "open_boundary_rho_min", 0.8),
        "open_boundary_rho_max": _provenance_float(provenance, "open_boundary_rho_max", 1.2),
        "open_boundary_u_max": _provenance_float(provenance, "open_boundary_u_max", 0.1),
        "open_boundary_noneq_cap": _provenance_float(provenance, "open_boundary_noneq_cap", 0.05),
        "open_boundary_population_floor": population_floor,
        "inlet_u_lbm": _provenance_float(provenance, "inlet_u_lbm", 0.02),
        "outlet_rho": _provenance_float(provenance, "outlet_rho", 1.0),
        "niu": _provenance_float(provenance, "lbm_niu", 0.1),
        "lbm_viscosity_semantics": str(provenance.get("lbm_viscosity_semantics") or "legacy_external"),
        "selected_source_row_name": best_selection.get("selected_row_name"),
        "selected_source_config_hash": provenance.get("solver_state_hash") or provenance.get("config_hash"),
        "selected_source_tau": provenance.get("tau"),
        "selected_source_lbm_relaxation_semantics": provenance.get("lbm_relaxation_semantics"),
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
    output_dir: Optional[Path | str] = None,
) -> List[Step120RunSpec]:
    if phase == "smoke":
        return step121_smoke_specs()
    if phase == "references48":
        return step121_reference_48_specs(output_interval=output_interval)
    if phase == "candidates48":
        return step121_candidate_48_specs(output_interval=output_interval)
    if phase == "repair48":
        return step121_repair_48_specs(output_interval=output_interval)
    if phase == "flowrepair48":
        return step121_flow_repair_48_specs(output_interval=output_interval)
    if phase == "planeflux48":
        return step121_plane_flux_48_specs(output_interval=output_interval)
    if phase == "planeflux_sweep48":
        return step121_plane_flux_sweep_48_specs(output_interval=output_interval)
    if phase == "planeflux_mass_damped48":
        return step121_plane_flux_mass_damped_48_specs(output_interval=output_interval)
    if phase == "planeflux_stationarity48":
        return step121_plane_flux_stationarity_48_specs(output_interval=output_interval)
    if phase in {"selected96", "selected-static"}:
        if best_selection_path is None:
            raise ValueError(f"{phase} phase requires --best-selection-path")
        selection = _read_json(Path(best_selection_path))
        specs = make_selected_96_specs(selection, output_interval=output_interval)
        if phase == "selected-static":
            _require_selected_96_duct_pass(Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR, specs[0])
        return [specs[0]] if phase == "selected96" else [specs[1]]
    if phase == "all48":
        return step121_reference_48_specs(output_interval=output_interval) + step121_candidate_48_specs(
            output_interval=output_interval
        )
    raise ValueError(f"unknown Step121 phase: {phase}")


def write_step121_campaign_manifest(
    output_dir: Path | str,
    specs: Sequence[Step120RunSpec],
    *,
    phase: str,
    campaign_id: Optional[str] = None,
    git_commit: Optional[str] = None,
    campaign_base_commit: Optional[str] = None,
) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / STEP121_CAMPAIGN_MANIFEST
    existing: Dict[str, Any] = {}
    if path.is_file():
        try:
            existing = _read_json(path)
        except Exception:
            existing = {}
    expected_rows = dict(existing.get("expected_rows") or {})
    for spec in specs:
        expected_rows[spec.name] = _manifest_row_for_spec(spec)
    phase_history = list(existing.get("phase_history") or [])
    if phase not in phase_history:
        phase_history.append(phase)
    current_code_commit = git_commit or _current_git_commit()
    base_commit = (
        campaign_base_commit
        or existing.get("campaign_base_commit")
        or existing.get("base_commit")
        or existing.get("git_commit")
        or STEP121_CAMPAIGN_BASE_COMMIT
    )
    phase_commit_history = _updated_phase_commit_history(existing, phase, current_code_commit)
    manifest = {
        "step121_campaign_manifest_schema_version": STEP121_CAMPAIGN_MANIFEST_SCHEMA_VERSION,
        "campaign_id": campaign_id or existing.get("campaign_id") or _default_campaign_id(str(base_commit)),
        "campaign_base_commit": str(base_commit),
        "current_code_commit": current_code_commit,
        "git_commit": current_code_commit,
        "artifact_root": str(out),
        "phase_history": phase_history,
        "phase_commit_history": phase_commit_history,
        "expected_rows": expected_rows,
        "gate_thresholds": _flow_gate_thresholds(),
        "run_commands": _manifest_run_commands(),
    }
    _write_json(path, manifest)
    return manifest


def _updated_phase_commit_history(existing: Dict[str, Any], phase: str, current_code_commit: str) -> List[Dict[str, str]]:
    history: List[Dict[str, str]] = []
    for item in existing.get("phase_commit_history") or []:
        if not isinstance(item, dict):
            continue
        existing_phase = item.get("phase")
        code_commit = item.get("code_commit")
        if existing_phase is None or code_commit is None:
            continue
        record = {"phase": str(existing_phase), "code_commit": str(code_commit)}
        if record not in history:
            history.append(record)
    if not history:
        legacy_commit = existing.get("current_code_commit") or existing.get("git_commit")
        if legacy_commit is not None:
            for legacy_phase in existing.get("phase_history") or []:
                record = {"phase": str(legacy_phase), "code_commit": str(legacy_commit)}
                if record not in history:
                    history.append(record)
    record = {"phase": str(phase), "code_commit": str(current_code_commit)}
    if record not in history:
        history.append(record)
    return history


def load_step121_campaign_manifest(output_dir: Path | str) -> Optional[Dict[str, Any]]:
    path = Path(output_dir) / STEP121_CAMPAIGN_MANIFEST
    if not path.is_file():
        return None
    return _read_json(path)


def collect_step121_rows(output_dir: Path | str, *, return_ignored: bool = False) -> Any:
    out = Path(output_dir)
    rows: List[Dict[str, Any]] = []
    ignored: List[Dict[str, Any]] = []
    manifest = load_step121_campaign_manifest(out)
    expected_rows = dict((manifest or {}).get("expected_rows") or {})
    if not out.is_dir():
        return {"rows": rows, "ignored_rows": ignored, "manifest": manifest} if return_ignored else rows
    for report in sorted(out.glob("*/finite_stability_report.json")):
        try:
            payload = _read_json(report)
        except Exception:
            continue
        row = dict(payload.get("summary_row") or payload)
        row.setdefault("name", report.parent.name)
        reasons = _manifest_rejection_reasons(row, expected_rows.get(str(row.get("name"))), manifest)
        if reasons:
            ignored.append(
                {
                    "name": row.get("name"),
                    "path": str(report),
                    "ignored_reasons": reasons,
                    "ignored_by_campaign_gate": True,
                }
            )
            continue
        if manifest is not None:
            row["campaign_id"] = manifest.get("campaign_id")
            row["campaign_manifest_path"] = str(out / STEP121_CAMPAIGN_MANIFEST)
        rows.append(row)
    if return_ignored:
        return {"rows": rows, "ignored_rows": ignored, "manifest": manifest}
    return rows


def _manifest_row_for_spec(spec: Step120RunSpec) -> Dict[str, Any]:
    return {
        "row_role": spec.row_role,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "geometry_mode": spec.geometry_mode,
        "solver_state_hash": solver_state_hash_for_spec(spec),
        "run_manifest_hash": run_manifest_hash_for_spec(spec),
        "selected_source_row_name": spec.selected_source_row_name,
        "selected_source_config_hash": spec.selected_source_config_hash,
        "selected_source_tau": spec.selected_source_tau,
        "selected_source_lbm_relaxation_semantics": spec.selected_source_lbm_relaxation_semantics,
    }


def _manifest_rejection_reasons(
    row: Dict[str, Any],
    expected: Optional[Dict[str, Any]],
    manifest: Optional[Dict[str, Any]],
) -> List[str]:
    if manifest is None:
        return []
    if expected is None:
        return ["stale_artifact"]
    checks = {
        "solver_state_hash": row.get("solver_state_hash") or row.get("config_hash"),
        "row_role": row.get("row_role"),
        "lbm_open_boundary_semantics": row.get("lbm_open_boundary_semantics"),
        "selected_source_row_name": row.get("selected_source_row_name"),
        "selected_source_config_hash": row.get("selected_source_config_hash"),
        "selected_source_lbm_relaxation_semantics": row.get("selected_source_lbm_relaxation_semantics"),
    }
    reasons: List[str] = []
    for key, actual in checks.items():
        expected_value = expected.get(key)
        if expected_value is not None and actual != expected_value:
            reasons.append(f"{key}_mismatch")
    expected_tau = expected.get("selected_source_tau")
    if expected_tau is not None:
        actual_tau = row.get("selected_source_tau")
        if actual_tau is None or not math.isclose(float(actual_tau), float(expected_tau), rel_tol=1.0e-9, abs_tol=1.0e-12):
            reasons.append("selected_source_tau_mismatch")
    return sorted(set(reasons))


def _flow_gate_thresholds() -> Dict[str, Any]:
    return {
        "inlet_flux_min": FLOW_INLET_FLUX_MIN,
        "ratio_min": FLOW_RATIO_MIN,
        "ratio_max": FLOW_RATIO_MAX,
        "flux_imbalance_rel_tail_mean_max": FLOW_IMBALANCE_TAIL_MEAN_MAX,
        "flux_imbalance_rel_tail_max_max": FLOW_IMBALANCE_TAIL_MAX_MAX,
        "outlet_flux_tail_cv_max": FLOW_OUTLET_TAIL_CV_MAX,
        "candidate_mass_acceptance_max": 0.005,
        "selected96_mass_acceptance_max": 0.01,
        "hard_stop_mass_drift_max": 0.05,
        "hard_stop_rho_min": 0.85,
        "hard_stop_rho_max": 1.15,
        "hard_stop_mach_max": 0.35,
        "hard_stop_negative_population_fraction_max": 1.0e-3,
    }


def _manifest_run_commands() -> List[str]:
    return [
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase references48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase candidates48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase repair48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase flowrepair48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux_sweep48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux_mass_damped48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase planeflux_stationarity48 --allow-large-real-rows --output-interval 25",
        "D:\\working\\taichi\\env\\python.exe -m experiments.steps.step121_lbm_boundary_real_campaign_and_gate_correction --phase summary",
    ]


def _current_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"


def _default_campaign_id(git_commit: Optional[str]) -> str:
    commit = git_commit or _current_git_commit()
    return f"step124_lbm_boundary_{commit[:8]}"


def select_step121_best_boundary(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    refs = _reference_status(rows)
    candidates = _candidate_rows(rows)
    evaluated = [_evaluate_candidate(row, rows) for row in candidates]
    candidate_summaries = [_candidate_summary(item) for item in evaluated]

    if not refs["reference_comparison_ready"]:
        if refs.get("legacy_reference_failed"):
            return _selection_payload(
                refs,
                candidate_summaries,
                campaign_state=CAMPAIGN_48_LEGACY_REFERENCE_FAILED,
                final_classification=CLASSIFICATION_FAILED,
                reason="48_legacy_reference_physical_failure",
            )
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
        if _real_terminal_evidence(row) and row.get("lbm_open_boundary_semantics") in REQUIRED_CANDIDATE_SEMANTICS
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
            "selected_boundary_provenance": _selected_boundary_provenance(selected),
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
    selected_96_flow_gate = _empty_selected_96_flow_gate()
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
        selected_96_flow_gate = _selected_96_chain_flow_development_gate(duct, static)
        if duct is None:
            missing_selected_rows.append(required_selected_rows[0])
            campaign_state = CAMPAIGN_AWAITING_SELECTED_96_DUCT
        elif not _row_validation_pass(duct) or not _selected_row_provenance_matches(duct, best_selection):
            failed_selected_rows.append(required_selected_rows[0])
            campaign_state = CAMPAIGN_AWAITING_SELECTED_96_DUCT
        elif static is None:
            missing_selected_rows.append(required_selected_rows[1])
            campaign_state = CAMPAIGN_AWAITING_SELECTED_96_STATIC
        elif not _row_validation_pass(static) or not _selected_row_provenance_matches(static, best_selection):
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
        "selected_96_flow_development_gate": selected_96_flow_gate,
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
        output_dir=out,
    )
    if selected_specs:
        write_step121_campaign_manifest(out, selected_specs, phase=phase)
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
    collected = collect_step121_rows(out, return_ignored=True)
    return write_step121_artifacts(
        out,
        collected["rows"],
        phase=phase,
        ignored_rows=collected["ignored_rows"],
        campaign_manifest=collected["manifest"],
    )


def write_step121_artifacts(
    output_dir: Path | str,
    rows: Sequence[Dict[str, Any]],
    *,
    phase: str,
    ignored_rows: Optional[Sequence[Dict[str, Any]]] = None,
    campaign_manifest: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ignored_list = list(ignored_rows or [])
    selection = select_step121_best_boundary(rows)
    gate = build_step121_gate_report(rows, selection)
    summary = {
        "step": 121,
        "step121_schema_version": STEP121_SCHEMA_VERSION,
        "phase": phase,
        "row_count": int(len(rows)),
        "ignored_row_count": int(len(ignored_list)),
        "campaign_state": gate["campaign_state"],
        "final_classification": gate["final_classification"],
        "quasi2d_allowed": gate["quasi2d_allowed"],
        "validation_claim_allowed": False,
        "campaign_manifest_id": (campaign_manifest or {}).get("campaign_id"),
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
            "ignored_rows": ignored_list,
            "campaign_manifest": campaign_manifest,
            "fluid_only": True,
            "full_fsi_rerun_done": False,
            "fluent_validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
            "static_two_flap_rows_are_lbm_only": True,
        },
    )
    _write_output_readme(out, summary)
    return {
        "summary": summary,
        "selection": selection,
        "gate": gate,
        "runs": list(rows),
        "ignored_rows": ignored_list,
        "campaign_manifest": campaign_manifest,
    }


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
    incomplete: List[str] = []
    failed: List[str] = []
    for semantics, row in refs.items():
        if semantics not in REQUIRED_REFERENCE_SEMANTICS or _real_completed(row):
            continue
        if _real_terminal_evidence(row):
            failed.append(semantics)
            if semantics == "equilibrium_all_population_reset":
                continue
            if semantics == "regularized_velocity_pressure":
                continue
        incomplete.append(semantics)
    legacy_failed = "equilibrium_all_population_reset" in failed
    return {
        "reference_comparison_ready": not missing and not incomplete and not legacy_failed,
        "legacy_reference_failed": legacy_failed,
        "reference_rows": {
            semantics: {
                "name": row.get("name"),
                "requested_window_completed": bool(row.get("requested_window_completed", False)),
                "simulation_backed_artifact": bool(row.get("simulation_backed_artifact", False)),
                "terminal_real_evidence": _real_terminal_evidence(row),
                "first_failure_reason": row.get("first_failure_reason"),
            }
            for semantics, row in refs.items()
            if semantics in REQUIRED_REFERENCE_SEMANTICS
        },
        "missing_reference_semantics": missing,
        "incomplete_reference_semantics": sorted(incomplete),
        "failed_reference_semantics": sorted(failed),
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
    flow_gate = _flow_development_gate(row)
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
    if not flow_gate["pass"]:
        reasons.extend(flow_gate["reasons"])
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
    throughput_penalty = abs(1.0 - float(flow_gate.get("outlet_to_inlet_flux_ratio_tail_mean") or 0.0))
    throughput_penalty += abs(1.0 - float(flow_gate.get("midplane_to_inlet_flux_ratio_tail_mean") or 0.0))
    throughput_penalty += float(flow_gate.get("outlet_flux_tail_cv") or 0.0)
    throughput_penalty += flux
    return {
        "row": row,
        "rejection_reasons": sorted(set(reasons)),
        "flow_development_gate": flow_gate,
        "candidate_pass": not reasons,
        "sort_key": (
            0 if not reasons else 1,
            throughput_penalty,
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
        "terminal_real_evidence": _real_terminal_evidence(row),
        "simulation_backed_artifact": bool(row.get("simulation_backed_artifact", False)),
        "candidate_pass": item["candidate_pass"],
        "rejection_reasons": item["rejection_reasons"],
        "flow_development_gate_pass": item["flow_development_gate"]["pass"],
        "flow_development_rejection_reasons": item["flow_development_gate"]["reasons"],
        "flux_imbalance_rel_tail_mean": row.get("flux_imbalance_rel_tail_mean"),
        "flux_imbalance_rel_tail_max": row.get("flux_imbalance_rel_tail_max"),
        "inlet_flux_tail_mean": row.get("inlet_flux_tail_mean"),
        "outlet_flux_tail_mean": row.get("outlet_flux_tail_mean"),
        "outlet_to_inlet_flux_ratio_tail_mean": row.get("outlet_to_inlet_flux_ratio_tail_mean"),
        "midplane_to_inlet_flux_ratio_tail_mean": row.get("midplane_to_inlet_flux_ratio_tail_mean"),
        "outlet_flux_tail_cv": row.get("outlet_flux_tail_cv"),
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
        "campaign_should_stop_at_48": campaign_state
        in {CAMPAIGN_48_LEGACY_REFERENCE_FAILED, CAMPAIGN_48_CANDIDATES_FAILED},
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
    base_pass = bool(_real_completed(row) and row.get("step120_validation_claimed") is True and row.get("first_failure_step") is None)
    if row.get("row_role") in {"selected_96_duct", "selected_96_static"}:
        return bool(base_pass and _selected_96_flow_development_gate(row)["pass"])
    return base_pass


def _real_completed(row: Dict[str, Any]) -> bool:
    return bool(row.get("requested_window_completed") is True and row.get("simulation_backed_artifact") is True)


def _real_terminal_evidence(row: Dict[str, Any]) -> bool:
    if _real_completed(row):
        return True
    if row.get("simulation_backed_artifact") is not True:
        return False
    reason = str(row.get("stop_reason") or row.get("skipped_reason") or row.get("first_failure_reason") or "")
    if reason in {"max_wall_seconds", "interrupted", "large_real_row_requires_explicit_allowance", "tau_margin"}:
        return False
    if reason.startswith("max_wall_seconds") or reason.startswith("interrupted"):
        return False
    return bool(row.get("first_failure_step") is not None or row.get("first_failure_reason") is not None)


def _flow_development_gate(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if row is None:
        return _empty_flow_development_gate(["missing_row"])
    reasons: List[str] = []
    inlet_flux = _optional_float(row.get("inlet_flux_tail_mean"))
    outlet_flux = _optional_float(row.get("outlet_flux_tail_mean"))
    outlet_ratio = _optional_float(row.get("outlet_to_inlet_flux_ratio_tail_mean"))
    midplane_ratio = _optional_float(row.get("midplane_to_inlet_flux_ratio_tail_mean"))
    flux_mean = _optional_float(row.get("flux_imbalance_rel_tail_mean"))
    flux_max = _optional_float(row.get("flux_imbalance_rel_tail_max"))
    outlet_cv = _optional_float(row.get("outlet_flux_tail_cv"))
    if row.get("flux_balance_reported") is not True:
        reasons.append("flux_balance_not_reported")
    if inlet_flux is None or abs(inlet_flux) <= FLOW_INLET_FLUX_MIN:
        reasons.append("inlet_flux_tail_mean")
    if outlet_flux is None:
        reasons.append("outlet_flux_tail_mean")
    elif inlet_flux is not None and abs(inlet_flux) > FLOW_INLET_FLUX_MIN and inlet_flux * outlet_flux <= 0.0:
        reasons.append("flux_direction_consistent")
    if outlet_ratio is None or not (FLOW_RATIO_MIN <= abs(outlet_ratio) <= FLOW_RATIO_MAX):
        reasons.append("outlet_to_inlet_flux_ratio_tail_mean")
    if midplane_ratio is None or not (FLOW_RATIO_MIN <= abs(midplane_ratio) <= FLOW_RATIO_MAX):
        reasons.append("midplane_to_inlet_flux_ratio_tail_mean")
    if flux_mean is None or flux_mean >= FLOW_IMBALANCE_TAIL_MEAN_MAX:
        reasons.append("flux_imbalance_rel_tail_mean")
    if flux_max is None or flux_max >= FLOW_IMBALANCE_TAIL_MAX_MAX:
        reasons.append("flux_imbalance_rel_tail_max")
    if outlet_cv is None or outlet_cv >= FLOW_OUTLET_TAIL_CV_MAX:
        reasons.append("outlet_flux_tail_cv")
    return {
        "pass": not reasons,
        "reasons": sorted(set(reasons)),
        "inlet_flux_tail_mean": inlet_flux,
        "outlet_flux_tail_mean": outlet_flux,
        "outlet_to_inlet_flux_ratio_tail_mean": outlet_ratio,
        "midplane_to_inlet_flux_ratio_tail_mean": midplane_ratio,
        "flux_imbalance_rel_tail_mean": flux_mean,
        "flux_imbalance_rel_tail_max": flux_max,
        "outlet_flux_tail_cv": outlet_cv,
        "inlet_flux_min": FLOW_INLET_FLUX_MIN,
        "ratio_min": FLOW_RATIO_MIN,
        "ratio_max": FLOW_RATIO_MAX,
    }


def _empty_flow_development_gate(reasons: Sequence[str]) -> Dict[str, Any]:
    return {
        "pass": False,
        "reasons": sorted(set(reasons)),
        "inlet_flux_tail_mean": None,
        "outlet_flux_tail_mean": None,
        "outlet_to_inlet_flux_ratio_tail_mean": None,
        "midplane_to_inlet_flux_ratio_tail_mean": None,
        "flux_imbalance_rel_tail_mean": None,
        "flux_imbalance_rel_tail_max": None,
        "outlet_flux_tail_cv": None,
        "inlet_flux_min": FLOW_INLET_FLUX_MIN,
        "ratio_min": FLOW_RATIO_MIN,
        "ratio_max": FLOW_RATIO_MAX,
    }


def _optional_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(result):
        return None
    return result


def _selected_96_flow_development_gate(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    gate = _flow_development_gate(row)
    return {**gate, "outlet_flux_min": SELECTED_96_OUTLET_FLUX_MIN}


def _selected_96_chain_flow_development_gate(
    duct: Optional[Dict[str, Any]],
    static: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    duct_gate = _selected_96_flow_development_gate(duct)
    static_gate = _selected_96_flow_development_gate(static)
    return {
        "duct_pass": duct_gate["pass"],
        "static_pass": static_gate["pass"],
        "duct_reasons": duct_gate["reasons"],
        "static_reasons": static_gate["reasons"],
        "outlet_flux_tail_mean": duct_gate["outlet_flux_tail_mean"],
        "outlet_to_inlet_flux_ratio_tail_mean": duct_gate["outlet_to_inlet_flux_ratio_tail_mean"],
        "midplane_to_inlet_flux_ratio_tail_mean": duct_gate["midplane_to_inlet_flux_ratio_tail_mean"],
        "outlet_flux_tail_cv": duct_gate["outlet_flux_tail_cv"],
        "flux_imbalance_rel_tail_max": duct_gate["flux_imbalance_rel_tail_max"],
        "outlet_flux_min": SELECTED_96_OUTLET_FLUX_MIN,
    }


def _empty_selected_96_flow_gate() -> Dict[str, Any]:
    return {
        "duct_pass": False,
        "static_pass": False,
        "duct_reasons": ["not_selected"],
        "static_reasons": ["not_selected"],
        "outlet_flux_tail_mean": None,
        "outlet_to_inlet_flux_ratio_tail_mean": None,
        "midplane_to_inlet_flux_ratio_tail_mean": None,
        "outlet_flux_tail_cv": None,
        "flux_imbalance_rel_tail_max": None,
        "outlet_flux_min": SELECTED_96_OUTLET_FLUX_MIN,
    }


def _selected_row_provenance_matches(row: Dict[str, Any], selection: Dict[str, Any]) -> bool:
    provenance = dict(selection.get("selected_boundary_provenance") or {})
    expected_hash = provenance.get("solver_state_hash") or provenance.get("config_hash")
    checks = {
        "selected_source_row_name": selection.get("selected_row_name"),
        "selected_source_config_hash": expected_hash,
        "selected_source_lbm_relaxation_semantics": provenance.get("lbm_relaxation_semantics"),
    }
    for key, expected in checks.items():
        if expected is not None and row.get(key) != expected:
            return False
    expected_tau = provenance.get("tau")
    if expected_tau is not None:
        actual_tau = row.get("selected_source_tau")
        if actual_tau is None or not math.isclose(float(actual_tau), float(expected_tau), rel_tol=1.0e-9, abs_tol=1.0e-12):
            return False
    return True


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
        choices=[
            "smoke",
            "references48",
            "candidates48",
            "repair48",
            "flowrepair48",
            "planeflux48",
            "planeflux_sweep48",
            "planeflux_mass_damped48",
            "planeflux_stationarity48",
            "all48",
            "selected96",
            "selected-static",
            "summary",
        ],
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
        collected = collect_step121_rows(args.output_dir, return_ignored=True)
        write_step121_artifacts(
            args.output_dir,
            collected["rows"],
            phase=args.phase,
            ignored_rows=collected["ignored_rows"],
            campaign_manifest=collected["manifest"],
        )
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
