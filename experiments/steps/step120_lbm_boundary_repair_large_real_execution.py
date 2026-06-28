from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.steps.step116_regularized_lbm_duct_flow_baseline import (  # noqa: E402
    CS_LBM,
    _apply_static_geometry,
    _ensure_taichi,
    _finite_float,
    _lbm_config_report,
    _read_json,
    _tau_feasibility_report,
    _velocity_profile_report,
    _write_boundary_flux_timeseries,
    _write_csv,
    _write_density_drift_timeseries,
    _write_json,
    _write_static_flap_reports,
    _write_timeseries,
)
from experiments.steps.step118_lbm_open_boundary_stability_repair import (  # noqa: E402
    _make_lbm_config,
    population_stats_from_record,
)
from experiments.steps.step119_lbm_boundary_repair_real_run_validation import (  # noqa: E402
    FINAL_CLASSIFICATIONS,
    LIMITER_ACTIVATION_FRACTION_LIMIT,
    Step119RunSpec,
    _boundary_plane_from_location,
    _empty_first_failure,
    _first_location_record,
    _large_real_row_requires_allowance,
    _spec_value,
    _tail_value,
)
from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import (  # noqa: E402
    summarize_lbm_boundary_diagnostics,
    summarize_timeseries_trends,
)
from src.mpm_lbm.sim.diagnostics.lbm_stability_diagnostics import (  # noqa: E402
    first_gate_failure_detector,
    mass_source_sink_by_step,
    summarize_lbm_stability_diagnostics,
)
from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D  # noqa: E402


DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "step120_lbm_boundary_repair_large_real_execution"
DEFAULT_CHECKPOINT_ROOT = REPO_ROOT / "outputs" / "tmp" / "step120_checkpoints"
DEFAULT_FAILURE_SNAPSHOT_ROOT = REPO_ROOT / "outputs" / "tmp" / "step120_failure_snapshots"
STEP120_SCHEMA_VERSION = 1


def _current_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return "unknown"

ROW_STATUS_COMPLETED = "completed"
ROW_STATUS_EXPECTED_POLICY_SKIP = "expected_policy_skip"
ROW_STATUS_INCOMPLETE_PLACEHOLDER = "incomplete_placeholder"
ROW_STATUS_STOPPED_ON_FAILURE = "stopped_on_failure"
ROW_STATUS_STOPPED_ON_WALLTIME = "stopped_on_walltime"
ROW_STATUS_CHECKPOINT_AVAILABLE = "checkpoint_available"
ROW_STATUS_INTERRUPTED = "interrupted"
ROW_STATUS_MISSING = "missing"

STEP127_CANDIDATE_SEMANTICS = {
    "regularized_velocity_pressure_limited",
    "convective_pressure_outlet_experimental",
}
REPAIRED_CANDIDATE_SEMANTICS = {
    "regularized_mass_balanced_pressure_outlet",
    "convective_mass_balanced_pressure_outlet",
}
FLOW_REPAIR_CANDIDATE_SEMANTICS = {
    "regularized_flux_matched_pressure_outlet",
    "convective_flux_matched_damped_outlet",
}
PLANE_FLUX_CONTROL_CANDIDATE_SEMANTICS = {
    "regularized_plane_flux_controlled_pressure_outlet",
    "convective_plane_flux_controlled_damped_outlet",
}
CANDIDATE_SEMANTICS = STEP127_CANDIDATE_SEMANTICS | REPAIRED_CANDIDATE_SEMANTICS
REFERENCE_SEMANTICS = {
    "equilibrium_all_population_reset",
    "regularized_velocity_pressure",
}
CANDIDATE_MASS_ACCEPTANCE_ABS_MAX = 0.005
HARD_STOP_MASS_DRIFT_ABS_MAX = 0.05

SOLVER_STATE_HASH_FIELDS = {
    "nx",
    "ny",
    "nz",
    "row_role",
    "open_boundary_semantics",
    "geometry_mode",
    "inlet_u_lbm",
    "outlet_rho",
    "niu",
    "lbm_viscosity_semantics",
    "lbm_tau_stability_policy",
    "lbm_min_tau_margin",
    "fluid_kinematic_viscosity_m2_s",
    "physical_duct_length_m",
    "lbm_dt_phys_override_s",
    "target_inlet_velocity_mps",
    "target_reynolds_number",
    "requested_nx",
    "open_boundary_limiter_enabled",
    "open_boundary_rho_min",
    "open_boundary_rho_max",
    "open_boundary_u_max",
    "open_boundary_noneq_cap",
    "open_boundary_population_floor",
    "open_boundary_flux_feedback_gain_u",
    "open_boundary_flux_feedback_gain_rho",
    "open_boundary_flux_filter_alpha",
    "open_boundary_flux_correction_cap_u",
    "open_boundary_flux_feedback_delta_cap_u",
    "open_boundary_flux_feedback_slew_alpha",
    "open_boundary_convective_blend_weight",
    "open_boundary_flux_control_measure_plane_offset",
    "open_boundary_flux_control_target_scale",
    "open_boundary_outlet_flux_drop_guard_enabled",
    "open_boundary_outlet_flux_drop_guard_min_ratio",
    "open_boundary_inlet_ramp_steps",
    "open_boundary_inlet_ramp_profile",
}


@dataclass(frozen=True)
class Step120RunSpec(Step119RunSpec):
    artifact_scope_note: str = "Step120 recoverable large-real LBM boundary repair execution row"
    step120_required_row: bool = True
    synthetic_diagnostic_mode: bool = False
    failure_check_interval: int = 5
    full_population_snapshot_interval: int = 0
    snapshot_on_failure: bool = True
    snapshot_on_final: bool = True
    row_role: str = "candidate_or_reference"
    selected_source_row_name: Optional[str] = None
    selected_source_config_hash: Optional[str] = None
    selected_source_tau: Optional[float] = None
    selected_source_lbm_relaxation_semantics: Optional[str] = None
    source_step: Optional[int] = None
    source_row_name: Optional[str] = None
    source_solver_state_hash: Optional[str] = None
    source_run_manifest_hash: Optional[str] = None
    source_code_commit: Optional[str] = None
    source_step139_row_name: Optional[str] = None
    source_step139_solver_state_hash: Optional[str] = None
    source_step139_run_manifest_hash: Optional[str] = None
    source_step139_code_commit: Optional[str] = None
    source_step140_summary_hash: Optional[str] = None
    source_step140_summary_path: Optional[str] = None
    source_step140_dominant_failure_mechanism: Optional[str] = None
    source_step140_mass_drift_mechanism: Optional[str] = None
    open_boundary_inlet_ramp_steps: int = 0
    open_boundary_inlet_ramp_profile: str = "linear"
    open_boundary_flux_control_target_scale: float = 1.0


def step120_real_run_specs(output_interval: int = 25) -> List[Step120RunSpec]:
    return [
        Step120RunSpec(
            name="tiny_step120_real_runner_smoke",
            nx=5,
            ny=4,
            nz=4,
            n_steps=3,
            output_interval=1,
            failure_check_interval=1,
            checkpoint_every=1,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=5,
            requested_n_steps=3,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            artifact_scope_note="committed tiny real Step120 smoke for runner, checkpoint, and counter plumbing",
            step120_required_row=False,
            step119_required_row=False,
            not_used_for_validation=True,
            allow_large_real_run_without_flag=True,
            row_role="tiny_smoke",
        ),
        Step120RunSpec(
            name="duct_only_48_legacy_boundary_500step_reference_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=100,
            open_boundary_semantics="equilibrium_all_population_reset",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            row_role="reference_48",
        ),
        Step120RunSpec(
            name="duct_only_48_regularized_boundary_500step_reference_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=100,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            row_role="reference_48",
        ),
        Step120RunSpec(
            name="duct_only_48_regularized_limited_boundary_500step_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=100,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            row_role="candidate_48",
        ),
        Step120RunSpec(
            name="duct_only_48_convective_outlet_boundary_500step_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=100,
            open_boundary_semantics="convective_pressure_outlet_experimental",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            row_role="candidate_48",
        ),
        Step120RunSpec(
            name="duct_only_48_regularized_mass_balanced_pressure_outlet_500step_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=100,
            open_boundary_semantics="regularized_mass_balanced_pressure_outlet",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            row_role="repair_candidate_48",
        ),
        Step120RunSpec(
            name="duct_only_48_convective_mass_balanced_pressure_outlet_500step_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=100,
            open_boundary_semantics="convective_mass_balanced_pressure_outlet",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            row_role="repair_candidate_48",
        ),
        Step120RunSpec(
            name="duct_only_48_regularized_flux_matched_pressure_outlet_250step_triage",
            nx=48,
            ny=48,
            nz=48,
            n_steps=250,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=50,
            open_boundary_semantics="regularized_flux_matched_pressure_outlet",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=250,
            row_role="flow_repair_candidate_48",
            open_boundary_flux_feedback_gain_u=0.01,
            open_boundary_flux_feedback_gain_rho=0.005,
            open_boundary_flux_filter_alpha=0.05,
            open_boundary_flux_correction_cap_u=0.005,
            open_boundary_convective_blend_weight=0.05,
            artifact_scope_note="Step130 bounded 48^3 flow-development triage; not a selected96 enabling row",
        ),
        Step120RunSpec(
            name="duct_only_48_convective_flux_matched_damped_outlet_250step_triage",
            nx=48,
            ny=48,
            nz=48,
            n_steps=250,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=50,
            open_boundary_semantics="convective_flux_matched_damped_outlet",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=250,
            row_role="flow_repair_candidate_48",
            open_boundary_flux_feedback_gain_u=0.01,
            open_boundary_flux_feedback_gain_rho=0.005,
            open_boundary_flux_filter_alpha=0.05,
            open_boundary_flux_correction_cap_u=0.005,
            open_boundary_convective_blend_weight=0.05,
            artifact_scope_note="Step130 bounded 48^3 convective damped flow-development triage; not a selected96 enabling row",
        ),
        Step120RunSpec(
            name="duct_only_48_regularized_plane_flux_controlled_pressure_outlet_250step_triage",
            nx=48,
            ny=48,
            nz=48,
            n_steps=250,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=50,
            open_boundary_semantics="regularized_plane_flux_controlled_pressure_outlet",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=250,
            row_role="plane_flux_control_candidate_48",
            open_boundary_flux_feedback_gain_u=0.0025,
            open_boundary_flux_feedback_gain_rho=0.0,
            open_boundary_flux_filter_alpha=0.02,
            open_boundary_flux_correction_cap_u=0.002,
            open_boundary_convective_blend_weight=0.02,
            artifact_scope_note="Step131 bounded 48^3 plane-flux-control triage; not a selected96 enabling row",
        ),
        Step120RunSpec(
            name="duct_only_48_convective_plane_flux_controlled_damped_outlet_250step_triage",
            nx=48,
            ny=48,
            nz=48,
            n_steps=250,
            output_interval=output_interval,
            failure_check_interval=5,
            checkpoint_every=50,
            open_boundary_semantics="convective_plane_flux_controlled_damped_outlet",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=250,
            row_role="plane_flux_control_candidate_48",
            open_boundary_flux_feedback_gain_u=0.0025,
            open_boundary_flux_feedback_gain_rho=0.0,
            open_boundary_flux_filter_alpha=0.02,
            open_boundary_flux_correction_cap_u=0.002,
            open_boundary_convective_blend_weight=0.02,
            artifact_scope_note="Step131 bounded 48^3 convective plane-flux-control triage; not a selected96 enabling row",
        ),
        Step120RunSpec(
            name="duct_only_96_regularized_limited_physical_nu_report_only_100step_guarded_real",
            nx=96,
            ny=96,
            nz=96,
            n_steps=100,
            output_interval=100,
            failure_check_interval=5,
            checkpoint_every=100,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            lbm_viscosity_semantics="physical_nu_mapping",
            lbm_tau_stability_policy="strict",
            lbm_min_tau_margin=1.0e-4,
            lbm_dt_phys_override_s=2.0833333333333334e-6,
            physical_duct_length_m=0.1,
            target_inlet_velocity_mps=10.0,
            target_reynolds_number=26666.666666666668,
            requested_nx=96,
            requested_n_steps=100,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            row_role="policy_guard",
        ),
    ]


def run_step120_matrix(
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    specs: Optional[Sequence[Step120RunSpec]] = None,
    force: bool = False,
    resume: bool = True,
    row_names: Optional[Sequence[str]] = None,
    max_rows: Optional[int] = None,
    output_interval: Optional[int] = None,
    stop_on_first_failure: Optional[bool] = None,
    checkpoint_every: Optional[int] = None,
    max_wall_seconds: Optional[float] = None,
    allow_large_real_rows: bool = False,
    checkpoint_root: Path | str = DEFAULT_CHECKPOINT_ROOT,
) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    default_specs_used = specs is None
    all_default_specs = step120_real_run_specs()
    run_specs = list(specs) if specs is not None else list(all_default_specs)
    if output_interval is not None:
        run_specs = [_replace_spec(spec, output_interval=int(output_interval)) for spec in run_specs]
    if stop_on_first_failure is not None:
        run_specs = [_replace_spec(spec, stop_on_first_failure=bool(stop_on_first_failure)) for spec in run_specs]
    if checkpoint_every is not None:
        run_specs = [_replace_spec(spec, checkpoint_every=int(checkpoint_every)) for spec in run_specs]
    if max_wall_seconds is not None:
        run_specs = [_replace_spec(spec, max_wall_seconds=float(max_wall_seconds)) for spec in run_specs]
    if row_names:
        requested = set(row_names)
        run_specs = [spec for spec in run_specs if spec.name in requested]
    if max_rows is not None:
        run_specs = run_specs[: int(max_rows)]

    rows: List[Dict[str, Any]] = []
    for spec in run_specs:
        row_dir = out / spec.name
        if resume and not force and step120_row_complete_for_resume(row_dir) and step120_row_reusable_for_spec(row_dir, spec):
            row = _read_json(row_dir / "finite_stability_report.json")["summary_row"]
            row["row_source"] = "resumed"
            rows.append(row)
            continue
        rows.append(
            run_step120_row(
                spec,
                row_dir,
                allow_large_real_rows=allow_large_real_rows,
                checkpoint_root=checkpoint_root,
                resume_from_checkpoint=bool(resume and not force),
            )
        )

    if default_specs_used:
        seen = {row["name"] for row in rows}
        for spec in all_default_specs:
            row_dir = out / spec.name
            if spec.name not in seen and step120_row_complete_for_resume(row_dir) and step120_row_reusable_for_spec(row_dir, spec):
                row = _read_json(row_dir / "finite_stability_report.json")["summary_row"]
                row["row_source"] = "existing"
                rows.append(row)

    limiter_summary = _write_limiter_actual_activation_summary(out, rows)
    row_status = _write_row_status_summary(out, rows)
    comparison_48 = _write_boundary_variant_48_comparison(out, rows)
    best_selection = _write_best_boundary_selection(out, rows)
    validation_96 = _write_boundary_variant_96_validation(out, rows, best_selection)
    first_failure = _write_global_first_failure(out, rows)
    gate = _write_step120_gate_report(out, rows, limiter_summary, best_selection)
    summary = _write_matrix_summary(out, rows, gate, row_status)
    _write_solver_report(out, rows, comparison_48, best_selection, validation_96, first_failure, limiter_summary, gate, summary)
    _write_output_readme(out, rows, gate, best_selection)
    return summary


def _step120_inlet_ramp_factor(spec: Step120RunSpec, step: int) -> float:
    ramp_steps = int(spec.open_boundary_inlet_ramp_steps or 0)
    if ramp_steps < 0:
        raise ValueError("open_boundary_inlet_ramp_steps must be >= 0")
    if ramp_steps == 0:
        return 1.0
    profile = str(spec.open_boundary_inlet_ramp_profile or "linear").lower()
    if profile != "linear":
        raise ValueError("open_boundary_inlet_ramp_profile must be 'linear'")
    return _finite_float(min(1.0, max(0.0, float(step) / float(ramp_steps))))


def _apply_step120_inlet_ramp(lbm: Any, spec: Step120RunSpec, step: int) -> float:
    factor = _step120_inlet_ramp_factor(spec, step)
    target = _finite_float(float(spec.inlet_u_lbm) * factor)
    velocity = [target, 0.0, 0.0]
    if hasattr(lbm, "set_bc_vel_x0"):
        lbm.set_bc_vel_x0(velocity)
    else:
        lbm.vx_bcxl, lbm.vy_bcxl, lbm.vz_bcxl = velocity
        if hasattr(lbm, "bc_vel_x_left"):
            lbm.bc_vel_x_left = velocity
    return factor


def run_step120_row(
    spec: Step120RunSpec,
    row_dir: Path | str,
    allow_large_real_rows: bool = False,
    checkpoint_root: Path | str = DEFAULT_CHECKPOINT_ROOT,
    resume_from_checkpoint: bool = False,
    stop_after_steps: Optional[int] = None,
) -> Dict[str, Any]:
    row_path = Path(row_dir)
    row_path.mkdir(parents=True, exist_ok=True)
    tau_report = _tau_feasibility_report(spec)
    print(
        f"[Step120] row={spec.name} role={spec.row_role} mode={spec.geometry_mode} "
        f"grid={spec.nx}x{spec.ny}x{spec.nz} steps={spec.n_steps}",
        flush=True,
    )

    if spec.synthetic_diagnostic_mode:
        return _write_nonstepped_row(spec, row_path, tau_report, "synthetic_diagnostic_mode_not_allowed")
    if spec.lbm_tau_stability_policy == "strict" and not tau_report["tau_margin_pass"]:
        return _write_nonstepped_row(spec, row_path, tau_report, "tau_margin")
    if _large_real_row_requires_allowance(spec) and not (allow_large_real_rows or spec.allow_large_real_run_without_flag):
        return _write_nonstepped_row(spec, row_path, tau_report, "large_real_row_requires_explicit_allowance")

    started = time.perf_counter()
    lbm, tau_report = create_step120_lbm(spec, tau_report=tau_report)
    checkpoint_root_path = Path(checkpoint_root)
    start_step = 0
    mass_initial = None
    restored_checkpoint = None
    checkpoint_records: List[Dict[str, Any]] = []
    checkpoint_stability_records: List[Dict[str, Any]] = []
    lbm.clear_open_boundary_limiter_run_counters()
    if resume_from_checkpoint:
        restored = restore_latest_step120_checkpoint_with_history(lbm, spec, checkpoint_root_path)
        if restored is not None:
            (
                start_step,
                mass_initial,
                restored_checkpoint,
                checkpoint_records,
                checkpoint_stability_records,
            ) = restored

    csv_records, csv_stability_records = _load_step120_timeseries_history(row_path) if restored_checkpoint else ([], [])
    records = _merge_step120_record_sets(checkpoint_records, csv_records)
    stability_records = _merge_step120_record_sets(checkpoint_stability_records, csv_stability_records)
    combined_records: List[Dict[str, Any]] = _combine_step120_records(records, stability_records)
    if mass_initial is None:
        mass_initial = _first_mass_total(records, stability_records)
    steps_completed = int(start_step)
    stop_reason = None

    for step in range(int(start_step), int(spec.n_steps) + 1):
        _apply_step120_inlet_ramp(lbm, spec, step)
        if step > int(start_step):
            lbm.step()
            steps_completed = step
        should_full_sample = _should_full_sample(spec, step)
        should_failure_check = _should_failure_check(spec, step)
        stability = None
        if should_failure_check or should_full_sample:
            stability = summarize_step120_lightweight_stability(lbm, step)
            if "mass_total" in stability:
                if mass_initial is None:
                    mass_initial = _finite_float(stability["mass_total"])
                _annotate_lightweight_mass_drift(stability, mass_initial)
            stability_records.append(stability)
        if should_failure_check and stability is not None and spec.stop_on_first_failure:
            lightweight_failure = _step120_lightweight_failure_detector(stability, mass_initial=mass_initial)
            if lightweight_failure["first_failure_step"] is not None:
                stop_reason = f"lightweight_failure:{lightweight_failure['first_failure_reason']}"
                combined_records.append({**stability, **lightweight_failure})
                if spec.snapshot_on_failure:
                    _write_full_population_snapshot(row_path, lbm, step, "lightweight_failure")
                write_step120_checkpoint(lbm, spec, checkpoint_root_path, step, mass_initial, records, stability_records)
                break
        if should_full_sample:
            summary = summarize_lbm_boundary_diagnostics(lbm, step=step, mass_initial=mass_initial)
            if mass_initial is None:
                mass_initial = summary["mass_total"]
                summary = summarize_lbm_boundary_diagnostics(lbm, step=step, mass_initial=mass_initial)
            summary.update(_flow_development_diagnostic_record(summary, spec, lbm.get_open_boundary_limiter_stats()))
            if stability is None:
                stability = summarize_step120_lightweight_stability(lbm, step)
                if "mass_total" in stability:
                    _annotate_lightweight_mass_drift(stability, mass_initial)
                stability_records.append(stability)
            combined = {**summary, **stability}
            records.append(summary)
            combined_records.append(combined)
            _write_partial_timeseries(row_path, records, stability_records)
            print(
                f"[Step120] row={spec.name} step={step}/{spec.n_steps} "
                f"rho=[{summary['rho_min']:.6g},{summary['rho_max']:.6g}] "
                f"mass_drift={summary['mass_total_delta_rel']:.6g} "
                f"neg_pop={stability['negative_population_count']}",
                flush=True,
            )
            first_failure = first_gate_failure_detector(combined_records)
            if spec.stop_on_first_failure and first_failure["first_failure_step"] is not None:
                stop_reason = f"first_failure:{first_failure['first_failure_reason']}"
                if spec.snapshot_on_failure:
                    _write_full_population_snapshot(row_path, lbm, step, "first_failure")
                write_step120_checkpoint(lbm, spec, checkpoint_root_path, step, mass_initial, records, stability_records)
                break
        if spec.checkpoint_every > 0 and step > 0 and step % int(spec.checkpoint_every) == 0:
            write_step120_checkpoint(lbm, spec, checkpoint_root_path, step, mass_initial, records, stability_records)
        if stop_after_steps is not None and step >= int(stop_after_steps) and step < int(spec.n_steps):
            stop_reason = "interrupted"
            write_step120_checkpoint(lbm, spec, checkpoint_root_path, step, mass_initial, records, stability_records)
            break
        if spec.max_wall_seconds is not None and time.perf_counter() - started >= float(spec.max_wall_seconds):
            stop_reason = "max_wall_seconds"
            write_step120_checkpoint(lbm, spec, checkpoint_root_path, step, mass_initial, records, stability_records)
            break

    if spec.snapshot_on_final and int(steps_completed) == int(spec.n_steps):
        _write_full_population_snapshot(row_path, lbm, int(steps_completed), "final")

    records = _dedupe_step120_records(records)
    stability_records = _dedupe_step120_records(stability_records)
    combined_records = _combine_step120_records(records, stability_records)
    runtime_s = _finite_float(time.perf_counter() - started)
    limiter_summary = summarize_step120_limiter_activation(lbm, spec)
    finite = _finite_report(
        spec,
        steps_completed,
        records,
        stability_records,
        combined_records,
        tau_report,
        runtime_s,
        stop_reason,
        limiter_summary,
        checkpoint_root_path,
        restored_checkpoint,
    )
    metadata = _metadata(spec, tau_report, skipped=False, runtime_s=runtime_s, stop_reason=stop_reason, restored_checkpoint=restored_checkpoint)
    config_report = _lbm_config_report(lbm.config, spec, tau_report)
    _write_json(row_path / "run_metadata.json", metadata)
    _write_json(row_path / "driver_config.json", config_report)
    _write_json(row_path / "duct_boundary_condition_report.json", _boundary_report(spec))
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_json(row_path / "first_failure_diagnostics.json", _first_failure_artifact(combined_records, spec, limiter_summary, reason=stop_reason))
    _write_json(row_path / "limiter_activation_summary.json", limiter_summary)
    _write_json(row_path / "velocity_profile_summary.json", _velocity_profile_report(lbm, spec, records))
    _write_partial_timeseries(row_path, records, stability_records)
    if spec.geometry_mode == "static_two_flap" and records:
        _write_static_flap_reports(row_path, lbm, spec, records[-1])
    print(f"[Step120] row={spec.name} completed runtime_s={runtime_s:.3f}", flush=True)
    return finite["summary_row"]


def create_step120_lbm(spec: Step120RunSpec, tau_report: Optional[Dict[str, Any]] = None) -> Tuple[LBMFluid3D, Dict[str, Any]]:
    _ensure_taichi()
    tau = tau_report if tau_report is not None else _tau_feasibility_report(spec)
    config = _make_lbm_config(spec, tau)
    lbm = LBMFluid3D(config)
    _apply_static_geometry(lbm, spec)
    lbm.init_simulation()
    return lbm, tau


def summarize_step120_lightweight_stability(lbm: Any, step: int) -> Dict[str, Any]:
    if hasattr(lbm, "get_lightweight_stability_stats"):
        stats = lbm.get_lightweight_stability_stats()
        all_finite = bool(
            math.isfinite(stats["rho_min"])
            and math.isfinite(stats["rho_max"])
            and math.isfinite(stats["max_v"])
            and math.isfinite(stats["f_min"])
            and math.isfinite(stats["f_max"])
            and math.isfinite(stats["F_min"])
            and math.isfinite(stats["F_max"])
            and math.isfinite(float(stats.get("mass_total", 0.0)))
        )
        return {
            "step": int(step),
            "diagnostic_mode": "lightweight_reduction",
            "f_all_finite": bool(math.isfinite(stats["f_min"]) and math.isfinite(stats["f_max"])),
            "F_all_finite": bool(math.isfinite(stats["F_min"]) and math.isfinite(stats["F_max"])),
            "all_finite": all_finite,
            "rho_min": _finite_float(stats["rho_min"]),
            "rho_max": _finite_float(stats["rho_max"]),
            "max_v": _finite_float(stats["max_v"]),
            "f_min": _finite_float(stats["f_min"]),
            "f_max": _finite_float(stats["f_max"]),
            "F_min": _finite_float(stats["F_min"]),
            "F_max": _finite_float(stats["F_max"]),
            "negative_population_count": int(stats["negative_population_count"]),
            "negative_population_fraction": _finite_float(stats["negative_population_fraction"]),
            "f_negative_population_count": None,
            "F_negative_population_count": None,
            "population_entry_count": int(stats["population_entry_count"]),
            "fluid_cell_count": int(stats.get("fluid_cell_count", 0) or 0),
            "mass_total": _finite_float(stats.get("mass_total", 0.0)),
            "mass_total_delta_rel": _finite_float(stats.get("mass_total_delta_rel", 0.0)),
            "rho_below_low_count": int(stats["rho_min"] < 0.0),
            "rho_above_high_count": int(stats["rho_max"] > 1.2),
            "first_negative_density_location": None,
            "first_high_density_location": None,
            "velocity_outlier_count": int(stats["max_v"] > 0.2),
            "first_velocity_outlier_location": None,
            "boundary_x_min_negative_population_count": int(stats["boundary_x_min_negative_population_count"]),
            "boundary_x_max_negative_population_count": int(stats["boundary_x_max_negative_population_count"]),
            "first_failure_location": None,
            "first_failure_cell": None,
            "stability_all_finite": all_finite,
        }
    result = summarize_lbm_stability_diagnostics(lbm, step)
    result["diagnostic_mode"] = "full_numpy_fallback"
    return result


def _annotate_lightweight_mass_drift(stability: Dict[str, Any], mass_initial: Optional[float]) -> None:
    if mass_initial is None:
        return
    mass_total = _finite_float(stability.get("mass_total", math.nan))
    initial = _finite_float(mass_initial)
    if not math.isfinite(mass_total) or not math.isfinite(initial) or initial == 0.0:
        stability["mass_total_delta_rel"] = math.nan
        return
    stability["mass_total_delta_rel"] = _finite_float((mass_total - initial) / initial)


def _step120_lightweight_failure_detector(
    stability: Dict[str, Any],
    *,
    mass_initial: Optional[float] = None,
    mass_drift_abs: float = HARD_STOP_MASS_DRIFT_ABS_MAX,
) -> Dict[str, Any]:
    reasons: List[str] = []
    rho_min = _finite_float(stability.get("rho_min", math.nan))
    rho_max = _finite_float(stability.get("rho_max", math.nan))
    max_v = _finite_float(stability.get("max_v", math.nan))
    negative_fraction = _finite_float(stability.get("negative_population_fraction", 0.0))
    mass_total_delta_rel = stability.get("mass_total_delta_rel")
    if mass_total_delta_rel is None and mass_initial is not None and "mass_total" in stability:
        _annotate_lightweight_mass_drift(stability, mass_initial)
        mass_total_delta_rel = stability.get("mass_total_delta_rel")
    if not bool(stability.get("stability_all_finite", stability.get("all_finite", True))):
        reasons.append("nonfinite_field")
    if not math.isfinite(rho_min) or not math.isfinite(rho_max) or rho_min <= 0.85 or rho_max >= 1.15:
        reasons.append("rho_range")
    if not math.isfinite(max_v) or max_v >= 0.35:
        reasons.append("max_v")
    for key in ("f_min", "f_max", "F_min", "F_max"):
        value = _finite_float(stability.get(key, 0.0))
        if not math.isfinite(value):
            reasons.append(f"nonfinite_{key}")
    drift = math.nan
    if mass_total_delta_rel is not None:
        try:
            drift = float(mass_total_delta_rel)
        except (TypeError, ValueError):
            drift = math.nan
        if not math.isfinite(drift) or abs(drift) > float(mass_drift_abs):
            reasons.append("mass_drift")
    if negative_fraction > 1.0e-3:
        reasons.append("negative_population_fraction")
    hard_stop_reason = reasons[0] if reasons else None
    hard_stop_step = int(stability.get("step", 0) or 0) if reasons else None
    return {
        "first_failure_step": hard_stop_step,
        "first_failure_reason": hard_stop_reason,
        "lightweight_failure_reasons": sorted(set(reasons)),
        "lightweight_failure_detector": "step120_failure_check_interval",
        "mass_total_delta_rel": _finite_float(mass_total_delta_rel if mass_total_delta_rel is not None else 0.0),
        "hard_stop_failure_reason": hard_stop_reason,
        "hard_stop_failure_step": hard_stop_step,
        "hard_stop_mass_drift_abs_max": _finite_float(mass_drift_abs),
        "hard_stop_mass_drift_observed_abs": _finite_float(abs(drift) if math.isfinite(drift) else math.nan),
        "hard_stop_mass_drift_gate_pass": "mass_drift" not in reasons,
    }


def summarize_step120_limiter_activation(stats_or_lbm: Any, spec: Step120RunSpec | Dict[str, Any]) -> Dict[str, Any]:
    stats = stats_or_lbm
    if hasattr(stats_or_lbm, "get_open_boundary_limiter_stats"):
        stats = stats_or_lbm.get_open_boundary_limiter_stats()
    stats = dict(stats or {})
    limiter_enabled = bool(_spec_value(spec, "open_boundary_limiter_enabled", False))
    activation_count = int(stats.get("limiter_activation_count", 0) or 0)
    denominator = int(stats.get("limiter_activation_denominator", 0) or 0)
    activation_fraction = _finite_float(activation_count / denominator if denominator else 0.0)
    fraction_limit = float(_spec_value(spec, "limiter_activation_fraction_limit", LIMITER_ACTIVATION_FRACTION_LIMIT))
    return {
        "step": 120,
        "limiter_counter_source": "actual_open_boundary_kernel_counters",
        "open_boundary_limiter_enabled": limiter_enabled,
        "rho_clip_used": limiter_enabled,
        "velocity_clip_used": limiter_enabled,
        "noneq_limiter_used": limiter_enabled,
        "population_floor_used": bool(limiter_enabled and _spec_value(spec, "open_boundary_population_floor", None) is not None),
        "rho_clip_count": int(stats.get("rho_clip_count_run", stats.get("rho_clip_count_step", 0)) or 0),
        "velocity_clip_count": int(stats.get("velocity_clip_count_run", stats.get("velocity_clip_count_step", 0)) or 0),
        "noneq_clip_count": int(stats.get("noneq_clip_count_run", stats.get("noneq_clip_count_step", 0)) or 0),
        "population_floor_count": int(stats.get("population_floor_count_run", stats.get("population_floor_count_step", 0)) or 0),
        "reconstructed_population_count": int(stats.get("reconstructed_population_count_run", 0) or 0),
        "limiter_activation_count": activation_count,
        "limiter_activation_denominator": denominator,
        "limiter_activation_fraction": activation_fraction,
        "limiter_activation_fraction_limit": fraction_limit,
        "mass_balance_correction_count": int(stats.get("mass_balance_correction_count_run", 0) or 0),
        "mass_balance_correction_count_step": int(stats.get("mass_balance_correction_count_step", 0) or 0),
        "mass_balance_correction_abs_sum": _finite_float(stats.get("mass_balance_correction_abs_sum_run", 0.0) or 0.0),
        "mass_balance_correction_abs_sum_step": _finite_float(stats.get("mass_balance_correction_abs_sum_step", 0.0) or 0.0),
        "unknown_population_delta_abs_sum": _finite_float(stats.get("unknown_population_delta_abs_sum_run", 0.0) or 0.0),
        "unknown_population_delta_abs_sum_step": _finite_float(stats.get("unknown_population_delta_abs_sum_step", 0.0) or 0.0),
        "flow_correction_delta_abs_sum": _finite_float(stats.get("flow_correction_delta_abs_sum_run", 0.0) or 0.0),
        "flow_correction_delta_abs_sum_step": _finite_float(stats.get("flow_correction_delta_abs_sum_step", 0.0) or 0.0),
        "flow_outlet_flux_error_filtered": _finite_float(stats.get("flow_outlet_flux_error_filtered_run", 0.0) or 0.0),
        "flow_correction_gain_effective": _finite_float(stats.get("flow_correction_gain_effective_step", 0.0) or 0.0),
        "open_boundary_flux_control_measure_plane_offset": int(
            _spec_value(spec, "open_boundary_flux_control_measure_plane_offset", 0)
        ),
        "open_boundary_outlet_flux_drop_guard_enabled": bool(
            _spec_value(spec, "open_boundary_outlet_flux_drop_guard_enabled", False)
        ),
        "open_boundary_outlet_flux_drop_guard_min_ratio": _finite_float(
            _spec_value(spec, "open_boundary_outlet_flux_drop_guard_min_ratio", 0.60)
        ),
        "near_outlet_flux_xminus1": _finite_float(stats.get("near_outlet_flux_xminus1", 0.0) or 0.0),
        "near_outlet_flux_xminus2": _finite_float(stats.get("near_outlet_flux_xminus2", 0.0) or 0.0),
        "near_outlet_flux_xminus3": _finite_float(stats.get("near_outlet_flux_xminus3", 0.0) or 0.0),
        "controller_true_outlet_flux_for_guard": _finite_float(stats.get("controller_true_outlet_flux_for_guard", 0.0) or 0.0),
        "controller_measure_plane_offset": int(stats.get("controller_measure_plane_offset", 0) or 0),
        "controller_drop_guard_active_step": int(stats.get("controller_drop_guard_active_step", 0) or 0),
        "controller_drop_guard_activation_count_run": int(
            stats.get("controller_drop_guard_activation_count_run", 0) or 0
        ),
        "controller_drop_guard_reference_flux": _finite_float(stats.get("controller_drop_guard_reference_flux", 0.0) or 0.0),
        "controller_target_scale": _finite_float(
            stats.get(
                "controller_target_scale",
                _spec_value(spec, "open_boundary_flux_control_target_scale", 1.0),
            )
            or 1.0
        ),
        "controller_drop_guard_min_ratio": _finite_float(stats.get("controller_drop_guard_min_ratio", 0.60) or 0.60),
        "controller_drop_guard_activation_fraction_run": _finite_float(
            stats.get("controller_drop_guard_activation_fraction_run", 0.0) or 0.0
        ),
        "validation_blocked_by_limiter_activation": bool(activation_fraction > fraction_limit),
        "validation_claim_allowed": False,
    }


def classify_step120_row_status(row_dir: Path | str) -> Dict[str, Any]:
    row_path = Path(row_dir)
    report_path = row_path / "finite_stability_report.json"
    if not report_path.is_file():
        return {"status": ROW_STATUS_MISSING, "row_dir": str(row_path), "validation_pass": False}
    finite = _read_json(report_path)
    row = finite.get("summary_row", finite)
    skipped_reason = finite.get("skipped_reason") or row.get("first_failure_reason")
    checkpoint_available = bool(row.get("checkpoint_available") or finite.get("checkpoint_available"))
    validation_pass = bool(row.get("step120_validation_claimed") or finite.get("step120_validation_claimed"))
    if row.get("requested_window_completed") is True:
        status = ROW_STATUS_COMPLETED
    elif skipped_reason == "tau_margin" or row.get("skipped_due_to_tau_margin") is True:
        status = ROW_STATUS_EXPECTED_POLICY_SKIP
    elif skipped_reason == "large_real_row_requires_explicit_allowance":
        status = ROW_STATUS_INCOMPLETE_PLACEHOLDER
    elif _row_stopped_on_physical_failure(row, skipped_reason):
        status = ROW_STATUS_STOPPED_ON_FAILURE
    elif skipped_reason == "max_wall_seconds":
        status = ROW_STATUS_STOPPED_ON_WALLTIME
    elif checkpoint_available:
        status = ROW_STATUS_CHECKPOINT_AVAILABLE
    else:
        status = ROW_STATUS_INTERRUPTED
    return {
        "status": status,
        "row_dir": str(row_path),
        "row_name": row.get("name", row_path.name),
        "skipped_reason": skipped_reason,
        "checkpoint_available": checkpoint_available,
        "validation_pass": validation_pass,
        "requested_window_completed": bool(row.get("requested_window_completed", False)),
        "steps_completed": int(row.get("steps_completed", 0) or 0),
    }


def step120_row_complete_for_resume(row_dir: Path | str) -> bool:
    status = classify_step120_row_status(row_dir)["status"]
    return status in {ROW_STATUS_COMPLETED, ROW_STATUS_EXPECTED_POLICY_SKIP, ROW_STATUS_STOPPED_ON_FAILURE}


def step120_row_reusable_for_spec(row_dir: Path | str, spec: Step120RunSpec) -> bool:
    row_path = Path(row_dir)
    report_path = row_path / "finite_stability_report.json"
    if not report_path.is_file():
        return False
    try:
        finite = _read_json(report_path)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    row = finite.get("summary_row", finite)
    if not isinstance(row, dict):
        return False
    if str(row.get("name", row_path.name)) != str(spec.name):
        return False
    if str(row.get("lbm_open_boundary_semantics", "")) != str(spec.open_boundary_semantics):
        return False
    if str(row.get("geometry_mode", "")) != str(spec.geometry_mode):
        return False
    if int(row.get("requested_nx", -1) or -1) != int(spec.requested_grid()):
        return False
    if int(row.get("requested_n_steps", -1) or -1) != int(spec.requested_steps()):
        return False
    actual_solver_hash = row.get("solver_state_hash") or row.get("config_hash")
    if actual_solver_hash != solver_state_hash_for_spec(spec):
        return False
    if not _selected_source_fields_match(row, spec):
        return False
    return True


def _selected_source_fields_match(row: Dict[str, Any], spec: Step120RunSpec) -> bool:
    checks = {
        "selected_source_row_name": spec.selected_source_row_name,
        "selected_source_config_hash": spec.selected_source_config_hash,
        "selected_source_lbm_relaxation_semantics": spec.selected_source_lbm_relaxation_semantics,
    }
    for key, expected in checks.items():
        if expected is not None and row.get(key) != expected:
            return False
    if spec.selected_source_tau is not None:
        actual = row.get("selected_source_tau")
        if actual is None or not math.isclose(float(actual), float(spec.selected_source_tau), rel_tol=1.0e-9, abs_tol=1.0e-12):
            return False
    return True


def _row_stopped_on_physical_failure(row: Dict[str, Any], skipped_reason: Any) -> bool:
    reason = str(skipped_reason or "")
    if not bool(row.get("simulation_backed_artifact", False)):
        return False
    if reason in {"max_wall_seconds", "interrupted", "large_real_row_requires_explicit_allowance", "tau_margin"}:
        return False
    if reason.startswith("first_failure") or reason.startswith("lightweight_failure"):
        return True
    return bool(row.get("first_failure_step") is not None or row.get("first_failure_reason") is not None)


def select_step120_best_boundary(rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    refs = {row.get("lbm_open_boundary_semantics"): row for row in rows if row.get("requested_nx") == 48}
    regularized = refs.get("regularized_velocity_pressure")
    legacy = refs.get("equilibrium_all_population_reset")
    candidates = [
        row
        for row in rows
        if row.get("requested_nx") == 48
        and row.get("lbm_open_boundary_semantics") in CANDIDATE_SEMANTICS
        and not bool(row.get("not_used_for_validation", False))
    ]
    evaluated = []
    for row in candidates:
        reasons = []
        flux = _metric(row, "flux_imbalance_rel_tail_mean")
        mass = abs(_metric(row, "mass_total_delta_rel_final"))
        limiter = _metric(row, "limiter_activation_fraction")
        if row.get("requested_window_completed") is not True:
            reasons.append("requested_window_not_completed")
        for key in ("finite_pass", "density_gate_pass", "mass_drift_gate_pass", "population_gate_pass", "mach_gate_pass"):
            if row.get(key) is not True:
                reasons.append(key)
        if row.get("first_failure_step") is not None:
            reasons.append("first_failure")
        if flux >= 0.1:
            reasons.append("flux_imbalance_gate")
        if mass >= 0.005:
            reasons.append("mass_drift_gate")
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
        evaluated.append(
            {
                "row": row,
                "rejection_reasons": reasons,
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
        )
    passing = [item for item in evaluated if item["candidate_pass"]]
    passing.sort(key=lambda item: item["sort_key"])
    candidate_summaries = [
        {
            "name": item["row"].get("name"),
            "semantics": item["row"].get("lbm_open_boundary_semantics"),
            "candidate_pass": item["candidate_pass"],
            "rejection_reasons": item["rejection_reasons"],
            "flux_imbalance_rel_tail_mean": item["row"].get("flux_imbalance_rel_tail_mean"),
            "mass_total_delta_rel_final": item["row"].get("mass_total_delta_rel_final"),
            "limiter_activation_fraction": item["row"].get("limiter_activation_fraction"),
        }
        for item in evaluated
    ]
    if not passing:
        return {
            "step": 120,
            "best_boundary_selected": False,
            "campaign_should_stop_at_48": True,
            "failure_classification": "boundary_repair_failed_revisit_lbm_solver",
            "candidate_summaries": candidate_summaries,
            "selection_reason": "no_48_candidate_passed_comparison_gate",
            "validation_claim_allowed": False,
        }
    selected = passing[0]["row"]
    return {
        "step": 120,
        "best_boundary_selected": True,
        "campaign_should_stop_at_48": False,
        "selected_row_name": selected.get("name"),
        "selected_boundary_semantics": selected.get("lbm_open_boundary_semantics"),
        "selected_boundary_slug": _boundary_slug(selected.get("lbm_open_boundary_semantics")),
        "selected_limiter_parameters": _limiter_parameters(selected),
        "selected_48_metrics": {
            "flux_imbalance_rel_tail_mean": selected.get("flux_imbalance_rel_tail_mean"),
            "mass_total_delta_rel_final": selected.get("mass_total_delta_rel_final"),
            "limiter_activation_fraction": selected.get("limiter_activation_fraction"),
            "runtime_s": selected.get("runtime_s"),
        },
        "candidate_summaries": candidate_summaries,
        "selection_reason": "lowest_ranked_48_candidate_that_passed_comparison_gate",
        "validation_claim_allowed": False,
    }


def build_step120_gate_report(
    rows: Sequence[Dict[str, Any]],
    limiter_summary: Dict[str, Any],
    best_boundary_selection: Dict[str, Any],
) -> Dict[str, Any]:
    rows_by_name = {row.get("name"): row for row in rows}
    limiter_gate_pass = not bool(limiter_summary.get("validation_blocked_by_limiter_activation", False))
    selected = bool(best_boundary_selection.get("best_boundary_selected", False))
    missing_selected_rows: List[str] = []
    failed_selected_rows: List[str] = []
    required_selected_rows: List[str] = []
    if selected:
        slug = best_boundary_selection.get("selected_boundary_slug") or _boundary_slug(
            best_boundary_selection.get("selected_boundary_semantics")
        )
        required_selected_rows = [
            f"duct_only_96_{slug}_1000step_real",
            f"static_two_flap_96_{slug}_1000step_real",
        ]
        for name in required_selected_rows:
            row = rows_by_name.get(name)
            if row is None:
                missing_selected_rows.append(name)
            elif row.get("requested_window_completed") is not True or row.get("step120_validation_claimed") is not True:
                failed_selected_rows.append(name)
    if not selected and best_boundary_selection.get("campaign_should_stop_at_48"):
        classification = "boundary_repair_failed_revisit_lbm_solver"
    elif selected and not missing_selected_rows and not failed_selected_rows and limiter_gate_pass:
        classification = "boundary_repair_success_go_to_quasi2d"
    else:
        classification = "boundary_repair_partial_continue_lbm"
    quasi2d_allowed = bool(classification == "boundary_repair_success_go_to_quasi2d")
    return {
        "step": 120,
        "step120_schema_version": STEP120_SCHEMA_VERSION,
        "quasi2d_allowed": quasi2d_allowed,
        "step121_quasi2d_allowed": quasi2d_allowed,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "full_fsi_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "best_boundary_selected": selected,
        "selected_boundary_semantics": best_boundary_selection.get("selected_boundary_semantics"),
        "required_selected_rows": required_selected_rows,
        "missing_selected_rows": missing_selected_rows,
        "failed_selected_rows": failed_selected_rows,
        "limiter_activation_gate_pass": limiter_gate_pass,
        "final_classification": classification,
        "allowed_final_classifications": sorted(FINAL_CLASSIFICATIONS),
        "no_fluent_claim": True,
        "no_fsi_claim": True,
    }


def _checkpoint_limiter_counters(lbm: LBMFluid3D) -> Dict[str, Any]:
    stats = lbm.get_open_boundary_limiter_stats()
    return {
        "rho_clip_count": int(stats.get("rho_clip_count_run", 0) or 0),
        "velocity_clip_count": int(stats.get("velocity_clip_count_run", 0) or 0),
        "noneq_clip_count": int(stats.get("noneq_clip_count_run", 0) or 0),
        "population_floor_count": int(stats.get("population_floor_count_run", 0) or 0),
        "reconstructed_population_count": int(stats.get("reconstructed_population_count_run", 0) or 0),
        "mass_balance_correction_count": int(stats.get("mass_balance_correction_count_run", 0) or 0),
        "mass_balance_correction_abs_sum": _finite_float(
            stats.get("mass_balance_correction_abs_sum_run", 0.0) or 0.0
        ),
        "unknown_population_delta_abs_sum": _finite_float(
            stats.get("unknown_population_delta_abs_sum_run", 0.0) or 0.0
        ),
    }


def write_step120_checkpoint(
    lbm: LBMFluid3D,
    spec: Step120RunSpec,
    checkpoint_root: Path | str,
    step: int,
    mass_initial: Optional[float],
    records: Optional[Sequence[Dict[str, Any]]] = None,
    stability_records: Optional[Sequence[Dict[str, Any]]] = None,
) -> Path:
    root = Path(checkpoint_root) / spec.name
    root.mkdir(parents=True, exist_ok=True)
    history = {
        "records": list(records or []),
        "stability_records": list(stability_records or []),
    }
    metadata = {
        "step": int(step),
        "schema_version": STEP120_SCHEMA_VERSION,
        "config_hash": _config_hash(spec),
        "solver_state_hash": solver_state_hash_for_spec(spec),
        "run_manifest_hash": run_manifest_hash_for_spec(spec),
        "shape": [int(spec.nx), int(spec.ny), int(spec.nz)],
        "boundary_semantics": spec.open_boundary_semantics,
        "relaxation_semantics": _relaxation_semantics_for_spec(spec),
        "mass_initial": mass_initial,
        "limiter_counter_source": "actual_open_boundary_kernel_counters",
        "limiter_counters": _checkpoint_limiter_counters(lbm),
        "history_record_count": int(len(history["records"])),
        "history_stability_record_count": int(len(history["stability_records"])),
    }
    path = root / f"checkpoint_step_{int(step):06d}.npz"
    tmp = path.with_suffix(".npz.tmp")
    with tmp.open("wb") as handle:
        np.savez_compressed(
            handle,
            f=lbm.f.to_numpy(),
            F=lbm.F.to_numpy(),
            rho=lbm.rho.to_numpy(),
            v=lbm.v.to_numpy(),
            solid=lbm.solid.to_numpy(),
            static_solid=lbm.static_solid.to_numpy(),
            metadata_json=np.array(json.dumps(metadata)),
            history_json=np.array(json.dumps(history)),
        )
    with np.load(tmp, allow_pickle=False) as data:
        json.loads(str(data["metadata_json"]))
    os.replace(tmp, path)
    json_path = path.with_suffix(".json")
    json_tmp = json_path.with_suffix(".json.tmp")
    json_tmp.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    json.loads(json_tmp.read_text(encoding="utf-8"))
    os.replace(json_tmp, json_path)
    _prune_step120_checkpoints(root, keep_last=3)
    return path


def restore_latest_step120_checkpoint(
    lbm: LBMFluid3D,
    spec: Step120RunSpec,
    checkpoint_root: Path | str,
) -> Optional[Tuple[int, Optional[float], str]]:
    restored = restore_latest_step120_checkpoint_with_history(lbm, spec, checkpoint_root)
    if restored is None:
        return None
    step, mass_initial, checkpoint_path, _records, _stability_records = restored
    return step, mass_initial, checkpoint_path


def restore_latest_step120_checkpoint_with_history(
    lbm: LBMFluid3D,
    spec: Step120RunSpec,
    checkpoint_root: Path | str,
) -> Optional[Tuple[int, Optional[float], str, List[Dict[str, Any]], List[Dict[str, Any]]]]:
    for latest in _checkpoint_paths(spec, Path(checkpoint_root), reverse=True):
        try:
            with np.load(latest, allow_pickle=False) as data:
                metadata = json.loads(str(data["metadata_json"]))
                history = _checkpoint_history_from_npz(data)
                _validate_checkpoint_metadata(spec, metadata)
                lbm.f.from_numpy(data["f"].astype(np.float32))
                lbm.F.from_numpy(data["F"].astype(np.float32))
                lbm.rho.from_numpy(data["rho"].astype(np.float32))
                lbm.v.from_numpy(data["v"].astype(np.float32))
                lbm.solid.from_numpy(data["solid"].astype(np.int8))
                lbm.static_solid.from_numpy(data["static_solid"].astype(np.int8))
        except Exception:
            continue
        counters = metadata.get("limiter_counters") or {}
        if hasattr(lbm, "set_open_boundary_limiter_run_counters"):
            lbm.set_open_boundary_limiter_run_counters(
                int(counters.get("rho_clip_count", 0) or 0),
                int(counters.get("velocity_clip_count", 0) or 0),
                int(counters.get("noneq_clip_count", 0) or 0),
                int(counters.get("population_floor_count", 0) or 0),
                int(counters.get("reconstructed_population_count", 0) or 0),
            )
        if hasattr(lbm, "set_open_boundary_repair_run_counters"):
            lbm.set_open_boundary_repair_run_counters(
                int(counters.get("mass_balance_correction_count", 0) or 0),
                _finite_float(counters.get("mass_balance_correction_abs_sum", 0.0) or 0.0),
                _finite_float(counters.get("unknown_population_delta_abs_sum", 0.0) or 0.0),
            )
        return (
            int(metadata["step"]),
            metadata.get("mass_initial"),
            str(latest),
            _dedupe_step120_records(history.get("records", [])),
            _dedupe_step120_records(history.get("stability_records", [])),
        )
    return None


def _hard_stop_reason_from(
    stop_reason: Optional[str],
    first_failure_reason: Optional[str],
) -> Optional[str]:
    reason = str(stop_reason or first_failure_reason or "")
    if reason.startswith("lightweight_failure:"):
        return reason.split(":", 1)[1] or None
    return reason or None


def _hard_stop_mass_fields(
    *,
    stop_reason: Optional[str],
    first_failure_reason: Optional[str],
    first_failure_step: Optional[int],
    mass_drift_abs_max_observed: Optional[float],
) -> Dict[str, Any]:
    reason = _hard_stop_reason_from(stop_reason, first_failure_reason)
    observed = _finite_float(mass_drift_abs_max_observed if mass_drift_abs_max_observed is not None else math.nan)
    observed_finite = math.isfinite(observed)
    mass_drift_failed = bool(reason == "mass_drift" or (observed_finite and observed > HARD_STOP_MASS_DRIFT_ABS_MAX))
    return {
        "hard_stop_failure_reason": reason,
        "hard_stop_failure_step": first_failure_step if reason is not None else None,
        "hard_stop_mass_drift_abs_max": _finite_float(HARD_STOP_MASS_DRIFT_ABS_MAX),
        "hard_stop_mass_drift_observed_abs": observed,
        "hard_stop_mass_drift_gate_pass": not mass_drift_failed,
    }


def _candidate_mass_acceptance_fields(mass_total_delta_rel_final: Optional[float]) -> Dict[str, Any]:
    observed = _finite_float(abs(float(mass_total_delta_rel_final)) if mass_total_delta_rel_final is not None else math.nan)
    return {
        "candidate_mass_acceptance_abs_max": _finite_float(CANDIDATE_MASS_ACCEPTANCE_ABS_MAX),
        "candidate_mass_acceptance_observed_abs": observed,
        "candidate_mass_acceptance_gate_pass": bool(
            math.isfinite(observed) and observed < CANDIDATE_MASS_ACCEPTANCE_ABS_MAX
        ),
    }


def _checkpoint_history_from_npz(data: Any) -> Dict[str, List[Dict[str, Any]]]:
    if "history_json" not in data.files:
        return {"records": [], "stability_records": []}
    raw = data["history_json"]
    if hasattr(raw, "item"):
        raw = raw.item()
    try:
        history = json.loads(str(raw))
    except (TypeError, ValueError):
        return {"records": [], "stability_records": []}
    return {
        "records": list(history.get("records") or []),
        "stability_records": list(history.get("stability_records") or []),
    }


def _finite_report(
    spec: Step120RunSpec,
    steps_completed: int,
    records: Sequence[Dict[str, Any]],
    stability_records: Sequence[Dict[str, Any]],
    combined_records: Sequence[Dict[str, Any]],
    tau_report: Dict[str, Any],
    runtime_s: float,
    stop_reason: Optional[str],
    limiter_summary: Dict[str, Any],
    checkpoint_root: Path,
    restored_checkpoint: Optional[str],
) -> Dict[str, Any]:
    trend = summarize_timeseries_trends(records) if records else {}
    final = records[-1] if records else {}
    first_failure = first_gate_failure_detector(combined_records)
    first_failure_step = first_failure["first_failure_step"]
    first_failure_reason = first_failure["first_failure_reason"]
    if first_failure_step is None and stop_reason is not None:
        first_failure_step = int(steps_completed)
        first_failure_reason = stop_reason
    mass_total_delta_rel_final = final.get("mass_total_delta_rel")
    hard_stop_fields = _hard_stop_mass_fields(
        stop_reason=stop_reason,
        first_failure_reason=first_failure_reason,
        first_failure_step=first_failure_step,
        mass_drift_abs_max_observed=trend.get("mass_drift_abs_max"),
    )
    candidate_mass_fields = _candidate_mass_acceptance_fields(mass_total_delta_rel_final)
    finite_pass = bool(
        records
        and all(record.get("all_finite", True) is not False for record in records)
        and all(row.get("stability_all_finite", row.get("all_finite", True)) is not False for row in stability_records)
    )
    density_gate_pass = bool(records and 0.85 < float(trend.get("rho_min_global", 0.0)) <= float(trend.get("rho_max_global", 1.0e9)) < 1.15)
    mass_drift_gate_pass = bool(records and abs(float(trend.get("mass_drift_final", 1.0e9))) < 0.05)
    population_gate_pass = bool(stability_records and (stability_records[-1].get("negative_population_fraction", 1.0) or 0.0) < 1.0e-3)
    mach_gate_pass = bool(records and float(trend.get("mach_proxy_observed_max", 1.0e9)) < 0.35)
    no_first_failure = first_failure_reason is None and stop_reason is None
    requested_window_completed = bool(
        int(steps_completed) == int(spec.requested_steps()) and int(spec.nx) == int(spec.requested_grid())
    )
    gate_pass = bool(
        requested_window_completed
        and finite_pass
        and density_gate_pass
        and mass_drift_gate_pass
        and population_gate_pass
        and mach_gate_pass
        and no_first_failure
        and tau_report["tau_margin_pass"] is not False
        and not limiter_summary["validation_blocked_by_limiter_activation"]
        and not spec.not_used_for_validation
    )
    checkpoint_available = _latest_checkpoint_path(spec, checkpoint_root) is not None
    outlet_flux_tail_mean = trend.get("outlet_flux_tail_mean")
    inlet_flux_tail_mean = trend.get("inlet_flux_tail_mean")
    outlet_to_inlet_flux_ratio_tail_mean = trend.get("outlet_to_inlet_flux_ratio_tail_mean")
    midplane_to_inlet_flux_ratio_tail_mean = trend.get("midplane_to_inlet_flux_ratio_tail_mean")
    flux_imbalance_rel_tail_max = trend.get("flux_imbalance_rel_tail_max")
    outlet_flux_tail_cv = trend.get("outlet_flux_tail_cv")
    flow_development_gate_pass = _flow_development_gate_pass(
        flux_balance_reported=bool(records),
        inlet_flux_tail_mean=inlet_flux_tail_mean,
        outlet_flux_tail_mean=outlet_flux_tail_mean,
        outlet_to_inlet_flux_ratio_tail_mean=outlet_to_inlet_flux_ratio_tail_mean,
        midplane_to_inlet_flux_ratio_tail_mean=midplane_to_inlet_flux_ratio_tail_mean,
        flux_imbalance_rel_tail_mean=trend.get("flux_imbalance_rel_tail_mean"),
        flux_imbalance_rel_tail_max=flux_imbalance_rel_tail_max,
        outlet_flux_tail_cv=outlet_flux_tail_cv,
    )
    summary_row = _summary_row(
        spec,
        steps_completed=steps_completed,
        requested_window_completed=requested_window_completed,
        finite_pass=finite_pass,
        density_gate_pass=density_gate_pass,
        mass_drift_gate_pass=mass_drift_gate_pass,
        population_gate_pass=population_gate_pass,
        mach_gate_pass=mach_gate_pass,
        first_failure_step=first_failure_step,
        first_failure_reason=first_failure_reason,
        flux_imbalance_rel_final=final.get("flux_imbalance_rel"),
        flux_imbalance_rel_tail_mean=trend.get("flux_imbalance_rel_tail_mean"),
        flux_imbalance_rel_tail_max=flux_imbalance_rel_tail_max,
        inlet_flux_tail_mean=inlet_flux_tail_mean,
        outlet_flux_tail_mean=outlet_flux_tail_mean,
        outlet_flux_tail_cv=outlet_flux_tail_cv,
        outlet_to_inlet_flux_ratio_tail_mean=outlet_to_inlet_flux_ratio_tail_mean,
        midplane_to_inlet_flux_ratio_tail_mean=midplane_to_inlet_flux_ratio_tail_mean,
        flow_development_gate_pass=flow_development_gate_pass,
        mass_total_delta_rel_final=mass_total_delta_rel_final,
        mach_proxy_observed_max=trend.get("mach_proxy_observed_max"),
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=False,
        stop_reason=stop_reason,
        row_source="computed_from_checkpoint" if restored_checkpoint else "computed",
        step120_validation_claimed=gate_pass,
        runtime_s=runtime_s,
        limiter_summary=limiter_summary,
        simulation_backed_artifact=True,
        flux_balance_reported=bool(records),
        checkpoint_available=checkpoint_available,
        hard_stop_fields=hard_stop_fields,
        candidate_mass_fields=candidate_mass_fields,
    )
    return {
        **summary_row,
        "skipped_reason": stop_reason,
        "step120_gate_pass": gate_pass,
        "step120_validation_claimed": gate_pass,
        "stability_repair_gates": {
            "requested_window_completed": requested_window_completed,
            "finite_pass": finite_pass,
            "density_range_gate_pass": density_gate_pass,
            "mass_drift_gate_pass": mass_drift_gate_pass,
            "population_gate_pass": population_gate_pass,
            "mach_gate_pass": mach_gate_pass,
            "no_first_failure": no_first_failure,
            "tau_margin_pass": tau_report["tau_margin_pass"],
            "limiter_activation_gate_pass": not limiter_summary["validation_blocked_by_limiter_activation"],
        },
        "timeseries_trend_summary": trend,
        "stability_timeseries_trend_summary": {
            "record_count": int(len(stability_records)),
            "diagnostic_mode": "lightweight_reduction",
            "negative_population_count_final": int(stability_records[-1].get("negative_population_count", 0)) if stability_records else 0,
            "negative_population_fraction_final": _finite_float(stability_records[-1].get("negative_population_fraction", 0.0)) if stability_records else 0.0,
            "boundary_x_min_negative_population_count_final": int(stability_records[-1].get("boundary_x_min_negative_population_count", 0)) if stability_records else 0,
            "boundary_x_max_negative_population_count_final": int(stability_records[-1].get("boundary_x_max_negative_population_count", 0)) if stability_records else 0,
        },
        "population_stats_final": population_stats_from_record(stability_records[-1] if stability_records else {}),
        "first_failure_detector": first_failure,
        "limiter_activation_summary": limiter_summary,
        "mass_source_sink_by_step": mass_source_sink_by_step(combined_records),
        "final_diagnostics": final,
        "tau_feasibility_report": tau_report,
        "not_used_for_validation": bool(spec.not_used_for_validation),
        "validation_claim_allowed": False,
        "checkpoint_available": checkpoint_available,
        "restored_checkpoint": restored_checkpoint,
        "summary_row": summary_row,
    }


def _write_nonstepped_row(spec: Step120RunSpec, row_path: Path, tau_report: Dict[str, Any], reason: str) -> Dict[str, Any]:
    limiter_summary = summarize_step120_limiter_activation({}, spec)
    summary_row = _summary_row(
        spec,
        steps_completed=0,
        requested_window_completed=False,
        finite_pass=False,
        density_gate_pass=False,
        mass_drift_gate_pass=False,
        population_gate_pass=False,
        mach_gate_pass=False,
        first_failure_step=None,
        first_failure_reason=reason,
        flux_imbalance_rel_final=None,
        flux_imbalance_rel_tail_mean=None,
        flux_imbalance_rel_tail_max=None,
        inlet_flux_tail_mean=None,
        outlet_flux_tail_mean=None,
        outlet_flux_tail_cv=None,
        outlet_to_inlet_flux_ratio_tail_mean=None,
        midplane_to_inlet_flux_ratio_tail_mean=None,
        flow_development_gate_pass=False,
        mass_total_delta_rel_final=None,
        mach_proxy_observed_max=None,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=reason == "tau_margin",
        stop_reason=reason,
        row_source="skipped",
        step120_validation_claimed=False,
        runtime_s=0.0,
        limiter_summary=limiter_summary,
        simulation_backed_artifact=False,
        flux_balance_reported=False,
        checkpoint_available=False,
        hard_stop_fields=_hard_stop_mass_fields(
            stop_reason=reason,
            first_failure_reason=reason,
            first_failure_step=None,
            mass_drift_abs_max_observed=None,
        ),
        candidate_mass_fields=_candidate_mass_acceptance_fields(None),
    )
    finite = {
        **summary_row,
        "skipped_reason": reason,
        "step120_gate_pass": False,
        "step120_validation_claimed": False,
        "stability_repair_gates": {},
        "timeseries_trend_summary": {},
        "stability_timeseries_trend_summary": {},
        "population_stats_final": {},
        "first_failure_detector": _empty_first_failure(reason),
        "limiter_activation_summary": limiter_summary,
        "mass_source_sink_by_step": {"record_count": 0},
        "tau_feasibility_report": tau_report,
        "not_used_for_validation": True,
        "validation_claim_allowed": False,
        "checkpoint_available": False,
        "summary_row": summary_row,
    }
    _write_json(row_path / "run_metadata.json", _metadata(spec, tau_report, skipped=True, runtime_s=0.0, stop_reason=reason, restored_checkpoint=None))
    _write_json(row_path / "driver_config.json", {"spec": asdict(spec), "tau_feasibility_report": tau_report})
    _write_json(row_path / "duct_boundary_condition_report.json", _boundary_report(spec))
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_json(row_path / "first_failure_diagnostics.json", _first_failure_artifact([], spec, limiter_summary, reason=reason))
    _write_json(row_path / "limiter_activation_summary.json", limiter_summary)
    _write_json(row_path / "velocity_profile_summary.json", {"skipped": True, "reason": reason, "synthetic_diagnostic_mode": False})
    _write_partial_timeseries(row_path, [], [])
    return summary_row


def _summary_row(
    spec: Step120RunSpec,
    steps_completed: int,
    requested_window_completed: bool,
    finite_pass: bool,
    density_gate_pass: bool,
    mass_drift_gate_pass: bool,
    population_gate_pass: bool,
    mach_gate_pass: bool,
    first_failure_step: Optional[int],
    first_failure_reason: Optional[str],
    flux_imbalance_rel_final: Optional[float],
    flux_imbalance_rel_tail_mean: Optional[float],
    flux_imbalance_rel_tail_max: Optional[float],
    inlet_flux_tail_mean: Optional[float],
    outlet_flux_tail_mean: Optional[float],
    outlet_flux_tail_cv: Optional[float],
    outlet_to_inlet_flux_ratio_tail_mean: Optional[float],
    midplane_to_inlet_flux_ratio_tail_mean: Optional[float],
    flow_development_gate_pass: bool,
    mass_total_delta_rel_final: Optional[float],
    mach_proxy_observed_max: Optional[float],
    tau_margin_pass: Optional[bool],
    skipped_due_to_tau_margin: bool,
    stop_reason: Optional[str],
    row_source: str,
    step120_validation_claimed: bool,
    runtime_s: float,
    limiter_summary: Dict[str, Any],
    simulation_backed_artifact: bool,
    flux_balance_reported: bool,
    checkpoint_available: bool,
    hard_stop_fields: Dict[str, Any],
    candidate_mass_fields: Dict[str, Any],
) -> Dict[str, Any]:
    tau_report = _tau_feasibility_report(spec)
    return {
        "name": spec.name,
        "row_role": spec.row_role,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "open_boundary_limiter_enabled": bool(spec.open_boundary_limiter_enabled),
        "open_boundary_rho_min": float(spec.open_boundary_rho_min),
        "open_boundary_rho_max": float(spec.open_boundary_rho_max),
        "open_boundary_u_max": float(spec.open_boundary_u_max),
        "open_boundary_noneq_cap": float(spec.open_boundary_noneq_cap),
        "open_boundary_population_floor": spec.open_boundary_population_floor,
        "open_boundary_flux_feedback_gain_u": float(spec.open_boundary_flux_feedback_gain_u),
        "open_boundary_flux_feedback_gain_rho": float(spec.open_boundary_flux_feedback_gain_rho),
        "open_boundary_flux_filter_alpha": float(spec.open_boundary_flux_filter_alpha),
        "open_boundary_flux_correction_cap_u": float(spec.open_boundary_flux_correction_cap_u),
        "open_boundary_flux_feedback_delta_cap_u": float(spec.open_boundary_flux_feedback_delta_cap_u),
        "open_boundary_flux_feedback_slew_alpha": float(spec.open_boundary_flux_feedback_slew_alpha),
        "open_boundary_convective_blend_weight": float(spec.open_boundary_convective_blend_weight),
        "open_boundary_flux_control_measure_plane_offset": int(spec.open_boundary_flux_control_measure_plane_offset),
        "open_boundary_flux_control_target_scale": float(spec.open_boundary_flux_control_target_scale),
        "open_boundary_outlet_flux_drop_guard_enabled": bool(spec.open_boundary_outlet_flux_drop_guard_enabled),
        "open_boundary_outlet_flux_drop_guard_min_ratio": float(spec.open_boundary_outlet_flux_drop_guard_min_ratio),
        "open_boundary_inlet_ramp_steps": int(spec.open_boundary_inlet_ramp_steps or 0),
        "open_boundary_inlet_ramp_profile": str(spec.open_boundary_inlet_ramp_profile or "linear"),
        "inlet_u_lbm": float(spec.inlet_u_lbm),
        "outlet_rho": float(spec.outlet_rho),
        "lbm_niu": float(tau_report["lbm_niu"]),
        "lbm_viscosity_semantics": str(spec.lbm_viscosity_semantics),
        "lbm_relaxation_semantics": str(tau_report["lbm_relaxation_semantics"]),
        "tau": _finite_float(tau_report["tau"]),
        "config_hash": _config_hash(spec),
        "solver_state_hash": solver_state_hash_for_spec(spec),
        "run_manifest_hash": run_manifest_hash_for_spec(spec),
        "code_commit_at_run": _current_git_commit(),
        "selected_source_row_name": spec.selected_source_row_name,
        "selected_source_config_hash": spec.selected_source_config_hash,
        "selected_source_tau": spec.selected_source_tau,
        "selected_source_lbm_relaxation_semantics": spec.selected_source_lbm_relaxation_semantics,
        "source_step": spec.source_step,
        "source_row_name": spec.source_row_name,
        "source_solver_state_hash": spec.source_solver_state_hash,
        "source_run_manifest_hash": spec.source_run_manifest_hash,
        "source_code_commit": spec.source_code_commit,
        "source_step139_row_name": spec.source_step139_row_name,
        "source_step139_solver_state_hash": spec.source_step139_solver_state_hash,
        "source_step139_run_manifest_hash": spec.source_step139_run_manifest_hash,
        "source_step139_code_commit": spec.source_step139_code_commit,
        "source_step140_summary_hash": spec.source_step140_summary_hash,
        "source_step140_summary_path": spec.source_step140_summary_path,
        "source_step140_dominant_failure_mechanism": spec.source_step140_dominant_failure_mechanism,
        "source_step140_mass_drift_mechanism": spec.source_step140_mass_drift_mechanism,
        "requested_nx": spec.requested_grid(),
        "executed_nx": int(spec.nx),
        "requested_n_steps": spec.requested_steps(),
        "steps_completed": int(steps_completed),
        "requested_window_completed": bool(requested_window_completed),
        "finite_pass": bool(finite_pass),
        "density_gate_pass": bool(density_gate_pass),
        "mass_drift_gate_pass": bool(mass_drift_gate_pass),
        "population_gate_pass": bool(population_gate_pass),
        "mach_gate_pass": bool(mach_gate_pass),
        "stability_diagnostics_reported": True,
        "stability_diagnostic_mode": "lightweight_reduction",
        "first_failure_step": first_failure_step,
        "first_failure_reason": first_failure_reason,
        "stop_reason": stop_reason,
        "hard_stop_failure_reason": hard_stop_fields.get("hard_stop_failure_reason"),
        "hard_stop_failure_step": hard_stop_fields.get("hard_stop_failure_step"),
        "hard_stop_mass_drift_abs_max": hard_stop_fields.get("hard_stop_mass_drift_abs_max"),
        "hard_stop_mass_drift_observed_abs": hard_stop_fields.get("hard_stop_mass_drift_observed_abs"),
        "hard_stop_mass_drift_gate_pass": bool(hard_stop_fields.get("hard_stop_mass_drift_gate_pass", True)),
        "candidate_mass_acceptance_abs_max": candidate_mass_fields.get("candidate_mass_acceptance_abs_max"),
        "candidate_mass_acceptance_observed_abs": candidate_mass_fields.get("candidate_mass_acceptance_observed_abs"),
        "candidate_mass_acceptance_gate_pass": bool(candidate_mass_fields.get("candidate_mass_acceptance_gate_pass", False)),
        "flux_balance_reported": bool(flux_balance_reported),
        "flux_imbalance_rel_final": flux_imbalance_rel_final,
        "flux_imbalance_rel_tail_mean": flux_imbalance_rel_tail_mean,
        "flux_imbalance_rel_tail_max": flux_imbalance_rel_tail_max,
        "inlet_flux_tail_mean": inlet_flux_tail_mean,
        "outlet_flux_tail_mean": outlet_flux_tail_mean,
        "outlet_flux_tail_cv": outlet_flux_tail_cv,
        "outlet_to_inlet_flux_ratio_tail_mean": outlet_to_inlet_flux_ratio_tail_mean,
        "midplane_to_inlet_flux_ratio_tail_mean": midplane_to_inlet_flux_ratio_tail_mean,
        "flow_development_gate_pass": bool(flow_development_gate_pass),
        "step130_flow_repair_triage": bool(spec.row_role == "flow_repair_candidate_48" and spec.requested_steps() < 500),
        "step135_interior_reflection_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step135" in str(spec.artifact_scope_note)
        ),
        "step136_ramped_throughput_calibration_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step136" in str(spec.artifact_scope_note)
        ),
        "step137_ramp_target_refinement_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step137" in str(spec.artifact_scope_note)
        ),
        "step138_high_authority_outlet_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step138" in str(spec.artifact_scope_note)
        ),
        "step139_planeflux_final48_candidate": bool(
            spec.row_role == "final_evidence_candidate_48" and "Step139" in str(spec.artifact_scope_note)
        ),
        "step141_density_feedback_isolation_candidate": bool(
            spec.row_role == "density_feedback_isolation_diagnostic_48" and "Step141" in str(spec.artifact_scope_note)
        ),
        "selected96_claim_allowed": False,
        "mass_total_delta_rel_final": mass_total_delta_rel_final,
        "mach_proxy_observed_max": mach_proxy_observed_max,
        "skipped_due_to_tau_margin": bool(skipped_due_to_tau_margin),
        "tau_margin_pass": tau_margin_pass,
        "synthetic_diagnostic_mode": False,
        "simulation_backed_artifact": bool(simulation_backed_artifact),
        "row_source": row_source,
        "step120_schema_version": STEP120_SCHEMA_VERSION,
        "step120_validation_claimed": bool(step120_validation_claimed),
        "validation_claim_allowed": False,
        "not_used_for_validation": bool(spec.not_used_for_validation or skipped_due_to_tau_margin or not step120_validation_claimed),
        "limiter_counter_source": limiter_summary.get("limiter_counter_source"),
        "limiter_activation_count": int(limiter_summary.get("limiter_activation_count", 0)),
        "limiter_activation_denominator": int(limiter_summary.get("limiter_activation_denominator", 0)),
        "limiter_activation_fraction": _finite_float(limiter_summary.get("limiter_activation_fraction", 0.0)),
        "limiter_activation_gate_pass": not bool(limiter_summary.get("validation_blocked_by_limiter_activation", False)),
        "mass_balance_correction_count": int(limiter_summary.get("mass_balance_correction_count", 0)),
        "mass_balance_correction_abs_sum": _finite_float(limiter_summary.get("mass_balance_correction_abs_sum", 0.0)),
        "unknown_population_delta_abs_sum": _finite_float(limiter_summary.get("unknown_population_delta_abs_sum", 0.0)),
        "flow_correction_delta_abs_sum": _finite_float(limiter_summary.get("flow_correction_delta_abs_sum", 0.0)),
        "flow_outlet_flux_error_filtered": _finite_float(limiter_summary.get("flow_outlet_flux_error_filtered", 0.0)),
        "outlet_flux_drop_guard_activation_fraction_tail": _finite_float(
            limiter_summary.get("controller_drop_guard_activation_fraction_run", 0.0)
        ),
        "checkpoint_available": bool(checkpoint_available),
        "runtime_s": _finite_float(runtime_s),
    }


def _metadata(
    spec: Step120RunSpec,
    tau_report: Dict[str, Any],
    skipped: bool,
    runtime_s: float,
    stop_reason: Optional[str],
    restored_checkpoint: Optional[str],
) -> Dict[str, Any]:
    return {
        "step": 120,
        "name": spec.name,
        "row_role": spec.row_role,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_shape": [int(spec.nx), int(spec.ny), int(spec.nz)],
        "requested_n_steps": spec.requested_steps(),
        "steps_configured": int(spec.n_steps),
        "output_interval": int(spec.output_interval),
        "failure_check_interval": int(spec.failure_check_interval),
        "full_population_snapshot_interval": int(spec.full_population_snapshot_interval),
        "artifact_scope_note": spec.artifact_scope_note,
        "open_boundary_flux_feedback_gain_u": float(spec.open_boundary_flux_feedback_gain_u),
        "open_boundary_flux_feedback_gain_rho": float(spec.open_boundary_flux_feedback_gain_rho),
        "open_boundary_flux_filter_alpha": float(spec.open_boundary_flux_filter_alpha),
        "open_boundary_flux_correction_cap_u": float(spec.open_boundary_flux_correction_cap_u),
        "open_boundary_flux_feedback_delta_cap_u": float(spec.open_boundary_flux_feedback_delta_cap_u),
        "open_boundary_flux_feedback_slew_alpha": float(spec.open_boundary_flux_feedback_slew_alpha),
        "open_boundary_convective_blend_weight": float(spec.open_boundary_convective_blend_weight),
        "open_boundary_flux_control_measure_plane_offset": int(spec.open_boundary_flux_control_measure_plane_offset),
        "open_boundary_flux_control_target_scale": float(spec.open_boundary_flux_control_target_scale),
        "open_boundary_outlet_flux_drop_guard_enabled": bool(spec.open_boundary_outlet_flux_drop_guard_enabled),
        "open_boundary_outlet_flux_drop_guard_min_ratio": float(spec.open_boundary_outlet_flux_drop_guard_min_ratio),
        "open_boundary_inlet_ramp_steps": int(spec.open_boundary_inlet_ramp_steps or 0),
        "open_boundary_inlet_ramp_profile": str(spec.open_boundary_inlet_ramp_profile or "linear"),
        "step130_flow_repair_triage": bool(spec.row_role == "flow_repair_candidate_48"),
        "step135_interior_reflection_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step135" in str(spec.artifact_scope_note)
        ),
        "step136_ramped_throughput_calibration_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step136" in str(spec.artifact_scope_note)
        ),
        "step137_ramp_target_refinement_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step137" in str(spec.artifact_scope_note)
        ),
        "step138_high_authority_outlet_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step138" in str(spec.artifact_scope_note)
        ),
        "step139_planeflux_final48_candidate": bool(
            spec.row_role == "final_evidence_candidate_48" and "Step139" in str(spec.artifact_scope_note)
        ),
        "step120_schema_version": STEP120_SCHEMA_VERSION,
        "synthetic_diagnostic_mode": False,
        "fluid_only": True,
        "static_lbm_only": spec.geometry_mode == "static_two_flap",
        "full_fsi_rerun_done": False,
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "validation_claim_allowed": False,
        "step121_quasi2d_allowed": False,
        "simulation_backed_artifact": bool(not skipped),
        "runtime_s": _finite_float(runtime_s),
        "stop_reason": stop_reason,
        "checkpoint_every": int(spec.checkpoint_every),
        "config_hash": _config_hash(spec),
        "solver_state_hash": solver_state_hash_for_spec(spec),
        "run_manifest_hash": run_manifest_hash_for_spec(spec),
        "code_commit_at_run": _current_git_commit(),
        "source_step": spec.source_step,
        "source_row_name": spec.source_row_name,
        "source_solver_state_hash": spec.source_solver_state_hash,
        "source_run_manifest_hash": spec.source_run_manifest_hash,
        "source_code_commit": spec.source_code_commit,
        "source_step139_row_name": spec.source_step139_row_name,
        "source_step139_solver_state_hash": spec.source_step139_solver_state_hash,
        "source_step139_run_manifest_hash": spec.source_step139_run_manifest_hash,
        "source_step139_code_commit": spec.source_step139_code_commit,
        "source_step140_summary_hash": spec.source_step140_summary_hash,
        "source_step140_summary_path": spec.source_step140_summary_path,
        "source_step140_dominant_failure_mechanism": spec.source_step140_dominant_failure_mechanism,
        "source_step140_mass_drift_mechanism": spec.source_step140_mass_drift_mechanism,
        "checkpoint_runtime_artifact_committed": False,
        "restored_checkpoint": restored_checkpoint,
        "stop_on_first_failure": bool(spec.stop_on_first_failure),
        "max_wall_seconds": spec.max_wall_seconds,
        "tau_feasibility_report": tau_report,
    }


def _boundary_report(spec: Step120RunSpec) -> Dict[str, Any]:
    return {
        "step": 120,
        "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "regularized_limited_boundary_used": spec.open_boundary_semantics == "regularized_velocity_pressure_limited",
        "convective_outlet_used": spec.open_boundary_semantics == "convective_pressure_outlet_experimental",
        "regularized_mass_balanced_pressure_outlet_used": spec.open_boundary_semantics == "regularized_mass_balanced_pressure_outlet",
        "convective_mass_balanced_pressure_outlet_used": spec.open_boundary_semantics == "convective_mass_balanced_pressure_outlet",
        "regularized_flux_matched_pressure_outlet_used": spec.open_boundary_semantics == "regularized_flux_matched_pressure_outlet",
        "convective_flux_matched_damped_outlet_used": spec.open_boundary_semantics == "convective_flux_matched_damped_outlet",
        "regularized_plane_flux_controlled_pressure_outlet_used": spec.open_boundary_semantics
        == "regularized_plane_flux_controlled_pressure_outlet",
        "convective_plane_flux_controlled_damped_outlet_used": spec.open_boundary_semantics
        == "convective_plane_flux_controlled_damped_outlet",
        "step130_flow_repair_candidate": spec.row_role == "flow_repair_candidate_48",
        "step131_plane_flux_control_candidate": spec.row_role == "plane_flux_control_candidate_48",
        "step135_interior_reflection_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step135" in str(spec.artifact_scope_note)
        ),
        "step136_ramped_throughput_calibration_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step136" in str(spec.artifact_scope_note)
        ),
        "step137_ramp_target_refinement_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step137" in str(spec.artifact_scope_note)
        ),
        "step138_high_authority_outlet_candidate": bool(
            spec.row_role == "interior_reflection_diagnostic_48" and "Step138" in str(spec.artifact_scope_note)
        ),
        "step139_planeflux_final48_candidate": bool(
            spec.row_role == "final_evidence_candidate_48" and "Step139" in str(spec.artifact_scope_note)
        ),
        "step141_density_feedback_isolation_candidate": bool(
            spec.row_role == "density_feedback_isolation_diagnostic_48" and "Step141" in str(spec.artifact_scope_note)
        ),
        "source_step": spec.source_step,
        "source_row_name": spec.source_row_name,
        "source_solver_state_hash": spec.source_solver_state_hash,
        "source_run_manifest_hash": spec.source_run_manifest_hash,
        "source_code_commit": spec.source_code_commit,
        "source_step139_row_name": spec.source_step139_row_name,
        "source_step139_solver_state_hash": spec.source_step139_solver_state_hash,
        "source_step139_run_manifest_hash": spec.source_step139_run_manifest_hash,
        "source_step139_code_commit": spec.source_step139_code_commit,
        "source_step140_summary_hash": spec.source_step140_summary_hash,
        "source_step140_summary_path": spec.source_step140_summary_path,
        "source_step140_dominant_failure_mechanism": spec.source_step140_dominant_failure_mechanism,
        "source_step140_mass_drift_mechanism": spec.source_step140_mass_drift_mechanism,
        "all_population_equilibrium_reset_used": spec.open_boundary_semantics == "equilibrium_all_population_reset",
        "open_boundary_limiter_enabled": bool(spec.open_boundary_limiter_enabled),
        "open_boundary_rho_min": float(spec.open_boundary_rho_min),
        "open_boundary_rho_max": float(spec.open_boundary_rho_max),
        "open_boundary_u_max": float(spec.open_boundary_u_max),
        "open_boundary_noneq_cap": float(spec.open_boundary_noneq_cap),
        "open_boundary_population_floor": spec.open_boundary_population_floor,
        "open_boundary_flux_feedback_gain_u": float(spec.open_boundary_flux_feedback_gain_u),
        "open_boundary_flux_feedback_gain_rho": float(spec.open_boundary_flux_feedback_gain_rho),
        "open_boundary_flux_filter_alpha": float(spec.open_boundary_flux_filter_alpha),
        "open_boundary_flux_correction_cap_u": float(spec.open_boundary_flux_correction_cap_u),
        "open_boundary_flux_feedback_delta_cap_u": float(spec.open_boundary_flux_feedback_delta_cap_u),
        "open_boundary_flux_feedback_slew_alpha": float(spec.open_boundary_flux_feedback_slew_alpha),
        "open_boundary_convective_blend_weight": float(spec.open_boundary_convective_blend_weight),
        "open_boundary_flux_control_measure_plane_offset": int(spec.open_boundary_flux_control_measure_plane_offset),
        "open_boundary_flux_control_target_scale": float(spec.open_boundary_flux_control_target_scale),
        "open_boundary_outlet_flux_drop_guard_enabled": bool(spec.open_boundary_outlet_flux_drop_guard_enabled),
        "open_boundary_outlet_flux_drop_guard_min_ratio": float(spec.open_boundary_outlet_flux_drop_guard_min_ratio),
        "open_boundary_inlet_ramp_steps": int(spec.open_boundary_inlet_ramp_steps or 0),
        "open_boundary_inlet_ramp_profile": str(spec.open_boundary_inlet_ramp_profile or "linear"),
        "actual_limiter_counter_required": True,
        "implemented_axis": "x",
        "pressure_outlet_density": float(spec.outlet_rho),
        "velocity_inlet_target": [float(spec.inlet_u_lbm), 0.0, 0.0],
        "boundary_condition_equivalence_claim_allowed": False,
        "validation_claim_allowed": False,
    }


def _first_failure_artifact(
    records: Sequence[Dict[str, Any]],
    spec: Step120RunSpec,
    limiter_summary: Dict[str, Any],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    detector = first_gate_failure_detector(records)
    if reason is not None and detector["first_failure_reason"] is None:
        detector["first_failure_reason"] = reason
        detector["first_failure_step"] = _tail_value(records, "step", None)
    location_row = _first_location_record(records, detector.get("first_failure_step"))
    location = location_row.get("first_failure_location") if location_row else None
    cell = location_row.get("first_failure_cell") if location_row else None
    plane = _boundary_plane_from_location(location)
    return {
        "step": 120,
        "row_name": spec.name,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "first_failure_step": detector.get("first_failure_step"),
        "first_failure_reason": detector.get("first_failure_reason"),
        "first_failure_location": location,
        "first_failure_cell": cell,
        "boundary_plane_where_failure_started": plane,
        "first_negative_density_step": detector.get("first_negative_density_step"),
        "first_high_density_step": detector.get("first_high_density_step"),
        "first_mass_drift_step": detector.get("first_mass_drift_step"),
        "first_max_v_step": detector.get("first_max_v_step"),
        "boundary_x_min_negative_population_count_tail": _tail_value(records, "boundary_x_min_negative_population_count", 0),
        "boundary_x_max_negative_population_count_tail": _tail_value(records, "boundary_x_max_negative_population_count", 0),
        "f_min": _tail_value(records, "f_min", None),
        "F_min": _tail_value(records, "F_min", None),
        "f_max": _tail_value(records, "f_max", None),
        "F_max": _tail_value(records, "F_max", None),
        "first_failure_detector": detector,
        "mass_source_sink_by_step": mass_source_sink_by_step(records),
        "limiter_activation_summary": limiter_summary,
        "validation_claim_allowed": False,
    }


def _load_step120_timeseries_history(row_path: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    records = _read_csv_records(row_path / "fluid_diagnostics_timeseries.csv")
    stability_records = _read_csv_records(row_path / "stability_diagnostics_timeseries.csv")
    return _dedupe_step120_records(records), _dedupe_step120_records(stability_records)


def _merge_step120_record_sets(*record_sets: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for records in record_sets:
        merged.extend(dict(row) for row in records)
    return _dedupe_step120_records(merged)


def _first_mass_total(*record_sets: Sequence[Dict[str, Any]]) -> Optional[float]:
    for records in record_sets:
        for row in records:
            if row.get("mass_total") is not None:
                return _finite_float(row["mass_total"])
    return None


def _read_csv_records(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{key: _coerce_csv_value(value) for key, value in row.items()} for row in reader]


def _coerce_csv_value(value: Any) -> Any:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float, bool)):
        return value
    text = str(value)
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False
    try:
        if "." not in text and "e" not in text.lower():
            return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return value


def _dedupe_step120_records(records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_step: Dict[int, Dict[str, Any]] = {}
    for row in records:
        if "step" not in row or row.get("step") is None:
            continue
        by_step[int(row["step"])] = dict(row)
    return [by_step[step] for step in sorted(by_step)]


def _combine_step120_records(
    records: Sequence[Dict[str, Any]],
    stability_records: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    stability_by_step = {int(row["step"]): row for row in stability_records if row.get("step") is not None}
    combined: List[Dict[str, Any]] = []
    for row in records:
        step = row.get("step")
        if step is None:
            continue
        combined.append({**row, **stability_by_step.get(int(step), {})})
    extra_stability = [
        row for row in stability_records if row.get("step") is not None and int(row["step"]) not in {int(item["step"]) for item in records if item.get("step") is not None}
    ]
    combined.extend(extra_stability)
    return _dedupe_step120_records(combined)


def _flow_development_diagnostic_record(
    record: Dict[str, Any],
    spec: Step120RunSpec,
    stats: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    stats = stats or {}
    target_scale = _finite_float(getattr(spec, "open_boundary_flux_control_target_scale", 1.0))
    target_outlet_flux = _finite_float(record.get("inlet_flux", 0.0)) * target_scale
    outlet_flux_after_correction = _finite_float(record.get("outlet_flux", 0.0))
    outlet_flux_error = _finite_float(target_outlet_flux - outlet_flux_after_correction)
    controller_target = _finite_float(stats.get("controller_target_outlet_flux", target_outlet_flux))
    controller_measured = _finite_float(stats.get("controller_measured_outlet_flux", outlet_flux_after_correction))
    controller_raw_error = _finite_float(stats.get("controller_raw_flux_error", controller_target - controller_measured))
    controller_filtered_error = _finite_float(stats.get("controller_filtered_flux_error", controller_raw_error))
    controller_u_feedback = _finite_float(stats.get("controller_u_feedback", 0.0))
    controller_density_feedback = _finite_float(stats.get("controller_density_feedback", 0.0))
    controller_cap_u = _finite_float(stats.get("flow_correction_cap_u", spec.open_boundary_flux_correction_cap_u))
    controller_authority_ratio = _finite_float(
        stats.get(
            "controller_authority_ratio",
            abs(controller_u_feedback) / abs(controller_cap_u) if abs(controller_cap_u) > 0.0 else 0.0,
        )
    )
    step133_mass_damped_candidate = bool(
        spec.row_role == "plane_flux_control_candidate_48" and "Step133" in str(spec.artifact_scope_note)
    )
    step134_outlet_stationarity_candidate = bool(
        spec.row_role == "plane_flux_control_candidate_48" and "Step134" in str(spec.artifact_scope_note)
    )
    step135_interior_reflection_candidate = bool(
        spec.row_role == "interior_reflection_diagnostic_48" and "Step135" in str(spec.artifact_scope_note)
    )
    step136_ramped_throughput_calibration_candidate = bool(
        spec.row_role == "interior_reflection_diagnostic_48" and "Step136" in str(spec.artifact_scope_note)
    )
    step137_ramp_target_refinement_candidate = bool(
        spec.row_role == "interior_reflection_diagnostic_48" and "Step137" in str(spec.artifact_scope_note)
    )
    step138_high_authority_outlet_candidate = bool(
        spec.row_role == "interior_reflection_diagnostic_48" and "Step138" in str(spec.artifact_scope_note)
    )
    step139_planeflux_final48_candidate = bool(
        spec.row_role == "final_evidence_candidate_48" and "Step139" in str(spec.artifact_scope_note)
    )
    step141_density_feedback_isolation_candidate = bool(
        spec.row_role == "density_feedback_isolation_diagnostic_48" and "Step141" in str(spec.artifact_scope_note)
    )
    step132_authority_sweep_candidate = bool(
        spec.row_role == "plane_flux_control_candidate_48" and "Step132" in str(spec.artifact_scope_note)
    )
    sample_step = int(record.get("step", 0) or 0)
    return {
        "step": sample_step,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "row_role": spec.row_role,
        "step135_interior_reflection_candidate": step135_interior_reflection_candidate,
        "step136_ramped_throughput_calibration_candidate": step136_ramped_throughput_calibration_candidate,
        "step137_ramp_target_refinement_candidate": step137_ramp_target_refinement_candidate,
        "step138_high_authority_outlet_candidate": step138_high_authority_outlet_candidate,
        "step139_planeflux_final48_candidate": step139_planeflux_final48_candidate,
        "step141_density_feedback_isolation_candidate": step141_density_feedback_isolation_candidate,
        "step134_outlet_stationarity_candidate": step134_outlet_stationarity_candidate,
        "step133_mass_damped_candidate": step133_mass_damped_candidate,
        "step132_authority_sweep_candidate": step132_authority_sweep_candidate,
        "open_boundary_flux_control_measure_plane_offset": int(spec.open_boundary_flux_control_measure_plane_offset),
        "open_boundary_outlet_flux_drop_guard_enabled": bool(spec.open_boundary_outlet_flux_drop_guard_enabled),
        "open_boundary_outlet_flux_drop_guard_min_ratio": _finite_float(
            spec.open_boundary_outlet_flux_drop_guard_min_ratio
        ),
        "open_boundary_inlet_ramp_steps": int(spec.open_boundary_inlet_ramp_steps or 0),
        "open_boundary_inlet_ramp_profile": str(spec.open_boundary_inlet_ramp_profile or "linear"),
        "open_boundary_inlet_ramp_factor": _step120_inlet_ramp_factor(spec, sample_step),
        "open_boundary_flux_control_target_scale": target_scale,
        "target_outlet_flux": target_outlet_flux,
        "outlet_flux_raw_before_correction": _finite_float(stats.get("flow_outlet_flux_raw_before_correction_step", outlet_flux_after_correction)),
        "outlet_flux_after_correction": outlet_flux_after_correction,
        "outlet_flux_error": outlet_flux_error,
        "outlet_flux_error_filtered": _finite_float(stats.get("flow_outlet_flux_error_filtered_run", outlet_flux_error)),
        "correction_gain_effective": _finite_float(stats.get("flow_correction_gain_effective_step", spec.open_boundary_flux_feedback_gain_u)),
        "flow_correction_cap_u": controller_cap_u,
        "correction_delta_abs_sum": _finite_float(stats.get("flow_correction_delta_abs_sum_step", 0.0)),
        "correction_delta_abs_sum_run": _finite_float(stats.get("flow_correction_delta_abs_sum_run", 0.0)),
        "controller_target_outlet_flux": controller_target,
        "controller_measured_outlet_flux": controller_measured,
        "controller_raw_flux_error": controller_raw_error,
        "controller_filtered_flux_error": controller_filtered_error,
        "controller_u_feedback": controller_u_feedback,
        "controller_u_feedback_abs": _finite_float(stats.get("controller_u_feedback_abs", abs(controller_u_feedback))),
        "controller_density_feedback": controller_density_feedback,
        "controller_density_feedback_abs": _finite_float(
            stats.get("controller_density_feedback_abs", abs(controller_density_feedback))
        ),
        "controller_delta_cap_u": _finite_float(
            stats.get("controller_delta_cap_u", spec.open_boundary_flux_feedback_delta_cap_u)
        ),
        "controller_slew_alpha": _finite_float(
            stats.get("controller_slew_alpha", spec.open_boundary_flux_feedback_slew_alpha)
        ),
        "controller_authority_ratio": controller_authority_ratio,
        "controller_saturation_count_step": int(stats.get("controller_saturation_count_step", 0) or 0),
        "controller_saturation_count_run": int(stats.get("controller_saturation_count_run", 0) or 0),
        "controller_saturation_fraction_run": _finite_float(stats.get("controller_saturation_fraction_run", 0.0)),
        "controller_measure_plane_offset": int(
            stats.get("controller_measure_plane_offset", spec.open_boundary_flux_control_measure_plane_offset) or 0
        ),
        "controller_target_scale": _finite_float(stats.get("controller_target_scale", target_scale)),
        "controller_drop_guard_active_step": int(stats.get("controller_drop_guard_active_step", 0) or 0),
        "controller_drop_guard_activation_count_run": int(
            stats.get("controller_drop_guard_activation_count_run", 0) or 0
        ),
        "controller_drop_guard_activation_fraction_run": _finite_float(
            stats.get("controller_drop_guard_activation_fraction_run", 0.0)
        ),
        "controller_drop_guard_reference_flux": _finite_float(stats.get("controller_drop_guard_reference_flux", 0.0)),
        "controller_true_outlet_flux_for_guard": _finite_float(
            stats.get("controller_true_outlet_flux_for_guard", outlet_flux_after_correction)
        ),
        "outlet_plane_ux_min": _finite_float(record.get("outlet_plane_ux_min", 0.0)),
        "outlet_plane_ux_max": _finite_float(record.get("outlet_plane_ux_max", 0.0)),
        "outlet_plane_ux_mean": _finite_float(record.get("outlet_plane_ux_mean", 0.0)),
        "outlet_plane_negative_ux_fraction": _finite_float(record.get("outlet_plane_negative_ux_fraction", 0.0)),
        "outlet_plane_rho_mean": _finite_float(record.get("outlet_plane_rho_mean", 0.0)),
        "outlet_plane_rho_std": _finite_float(record.get("outlet_plane_rho_std", 0.0)),
        "midplane_flux": _finite_float(record.get("midplane_flux", 0.0)),
        "near_outlet_flux_xminus1": _finite_float(
            record.get("near_outlet_flux_xminus1", stats.get("near_outlet_flux_xminus1", 0.0))
        ),
        "near_outlet_flux_xminus2": _finite_float(
            record.get("near_outlet_flux_xminus2", stats.get("near_outlet_flux_xminus2", 0.0))
        ),
        "near_outlet_flux_xminus3": _finite_float(
            record.get("near_outlet_flux_xminus3", stats.get("near_outlet_flux_xminus3", 0.0))
        ),
        "near_outlet_to_outlet_flux_ratio": _finite_float(record.get("near_outlet_to_outlet_flux_ratio", 0.0)),
        "x_profile_flux_samples": _compact_diagnostic_mapping(
            record.get("x_profile_flux_samples") or record.get("sampled_x_profile_flux")
        ),
        "x_profile_ux_mean_samples": _compact_diagnostic_mapping(record.get("x_profile_ux_mean_samples")),
        "x_profile_rho_mean_samples": _compact_diagnostic_mapping(record.get("x_profile_rho_mean_samples")),
        "sampled_x_profile_flux": str(record.get("sampled_x_profile_flux") or ""),
        "source_step": spec.source_step,
        "source_row_name": spec.source_row_name,
        "source_solver_state_hash": spec.source_solver_state_hash,
        "source_run_manifest_hash": spec.source_run_manifest_hash,
        "source_code_commit": spec.source_code_commit,
        "source_step139_row_name": spec.source_step139_row_name,
        "source_step139_solver_state_hash": spec.source_step139_solver_state_hash,
        "source_step139_run_manifest_hash": spec.source_step139_run_manifest_hash,
        "source_step139_code_commit": spec.source_step139_code_commit,
        "source_step140_summary_hash": spec.source_step140_summary_hash,
        "source_step140_summary_path": spec.source_step140_summary_path,
        "source_step140_dominant_failure_mechanism": spec.source_step140_dominant_failure_mechanism,
        "source_step140_mass_drift_mechanism": spec.source_step140_mass_drift_mechanism,
        "mass_total_delta_rel": _finite_float(record.get("mass_total_delta_rel", 0.0)),
        "validation_claim_allowed": False,
        "selected96_claim_allowed": False,
    }


def _write_flow_development_diagnostics(row_path: Path, records: Sequence[Dict[str, Any]]) -> None:
    diagnostics = [_flow_development_diagnostic_row_from_record(row) for row in records]
    step_number = _flow_development_diagnostic_step_number(diagnostics)
    _write_csv(row_path / "flow_development_diagnostics.csv", diagnostics, FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS)
    tail_summary = _flow_development_tail_summary(diagnostics)
    _write_json(
        row_path / "flow_development_diagnostics_summary.json",
        {
            "step": step_number,
            "artifact": "flow_development_diagnostics",
            "row_count": int(len(diagnostics)),
            "bounded_size_artifact": True,
            "validation_claim_allowed": False,
            "selected96_claim_allowed": False,
            "final": diagnostics[-1] if diagnostics else None,
            **tail_summary,
        },
    )


def _flow_development_diagnostic_step_number(diagnostics: Sequence[Dict[str, Any]]) -> int:
    if any(row.get("step141_density_feedback_isolation_candidate") is True for row in diagnostics):
        return 141
    if any(row.get("step139_planeflux_final48_candidate") is True for row in diagnostics):
        return 139
    if any(row.get("step138_high_authority_outlet_candidate") is True for row in diagnostics):
        return 138
    if any(row.get("step137_ramp_target_refinement_candidate") is True for row in diagnostics):
        return 137
    if any(row.get("step136_ramped_throughput_calibration_candidate") is True for row in diagnostics):
        return 136
    if any(row.get("step135_interior_reflection_candidate") is True for row in diagnostics):
        return 135
    if any(row.get("step134_outlet_stationarity_candidate") is True for row in diagnostics):
        return 134
    if any(row.get("step133_mass_damped_candidate") is True for row in diagnostics):
        return 133
    if any(row.get("step132_authority_sweep_candidate") is True for row in diagnostics):
        return 132
    if any(row.get("row_role") == "plane_flux_control_candidate_48" for row in diagnostics):
        return 131
    return 130


def _diagnostic_tail_records(diagnostics: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not diagnostics:
        return []
    tail_count = max(1, int(math.ceil(len(diagnostics) * 0.2)))
    if len(diagnostics) > 1:
        tail_count = max(2, tail_count)
    if len(diagnostics) > 2:
        tail_count = max(3, tail_count)
    return list(diagnostics[-tail_count:])


def _diagnostic_numeric_values(records: Sequence[Dict[str, Any]], key: str) -> List[float]:
    values: List[float] = []
    for row in records:
        value = row.get(key)
        if value is None or value == "":
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if math.isfinite(numeric):
            values.append(numeric)
    return values


def _diagnostic_mean(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return _finite_float(sum(values) / len(values))


def _diagnostic_std(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    mean = sum(values) / len(values)
    return _finite_float(math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)))


def _diagnostic_abs_max(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return _finite_float(max(abs(value) for value in values))


def _diagnostic_max(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return _finite_float(max(values))


def _diagnostic_slope(values: Sequence[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    return _finite_float(values[-1] - values[0])


def _diagnostic_sum(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return _finite_float(sum(values))


def _diagnostic_ratio(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None or abs(float(denominator)) < 1.0e-12:
        return None
    return _finite_float(float(numerator) / float(denominator))


def _diagnostic_last_to_mean(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return _diagnostic_ratio(values[-1], _diagnostic_mean(values))


def _diagnostic_mapping(value: Any) -> Dict[str, float]:
    if value is None:
        return {}
    if isinstance(value, dict):
        out: Dict[str, float] = {}
        for key, item in value.items():
            try:
                out[str(key)] = _finite_float(item)
            except Exception:
                continue
        return dict(sorted(out.items(), key=lambda item: _numeric_profile_key(item[0])))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return {}
        try:
            parsed = json.loads(text)
        except Exception:
            parsed = None
        if isinstance(parsed, dict):
            return _diagnostic_mapping(parsed)
        out: Dict[str, float] = {}
        for token in text.split(";"):
            if ":" not in token:
                continue
            key, raw = token.split(":", 1)
            try:
                out[str(key)] = _finite_float(raw)
            except Exception:
                continue
        return dict(sorted(out.items(), key=lambda item: _numeric_profile_key(item[0])))
    return {}


def _compact_diagnostic_mapping(value: Any) -> str:
    mapping = _diagnostic_mapping(value)
    return json.dumps(mapping, sort_keys=True, separators=(",", ":"))


def _numeric_profile_key(value: str) -> Tuple[int, str]:
    try:
        return (int(value), str(value))
    except Exception:
        return (10**9, str(value))


def _diagnostic_cv(values: Sequence[float]) -> Optional[float]:
    mean = _diagnostic_mean(values)
    std = _diagnostic_std(values)
    if mean is None or std is None or abs(float(mean)) < 1.0e-12:
        return None
    return _finite_float(abs(float(std) / float(mean)))


def _flow_development_x_profile_tail_summary(tail: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    values_by_x: Dict[str, List[float]] = {}
    steps_by_x: Dict[str, List[int]] = {}
    for row in tail:
        profile = _diagnostic_mapping(row.get("x_profile_flux_samples") or row.get("sampled_x_profile_flux"))
        step = int(row.get("step", 0) or 0)
        for key, value in profile.items():
            values_by_x.setdefault(str(key), []).append(_finite_float(value))
            steps_by_x.setdefault(str(key), []).append(step)

    ordered_keys = sorted(values_by_x, key=_numeric_profile_key)
    tail_values = {key: values_by_x[key] for key in ordered_keys}
    tail_slope = {key: _diagnostic_slope(values_by_x[key]) for key in ordered_keys}
    tail_cv = {key: _diagnostic_cv(values_by_x[key]) for key in ordered_keys}
    last_to_mean = {key: _diagnostic_last_to_mean(values_by_x[key]) for key in ordered_keys}

    collapsed: List[Tuple[int, int, str]] = []
    for key in ordered_keys:
        values = values_by_x[key]
        mean_abs = _diagnostic_mean([abs(value) for value in values])
        if mean_abs is None or abs(float(mean_abs)) < 1.0e-12:
            continue
        threshold = 0.70 * abs(float(mean_abs))
        for step, value in zip(steps_by_x.get(key, []), values):
            if abs(float(value)) < threshold:
                collapsed.append((int(step), _numeric_profile_key(key)[0], key))
                break

    collapsed.sort()
    collapse_first_x: Any = None
    collapse_first_step: Optional[int] = None
    if collapsed:
        collapse_first_step = collapsed[0][0]
        first_key = collapsed[0][2]
        try:
            collapse_first_x = int(first_key)
        except Exception:
            collapse_first_x = first_key

    return {
        "x_profile_flux_tail_values_by_x": tail_values,
        "x_profile_flux_tail_slope_by_x": tail_slope,
        "x_profile_flux_tail_cv_by_x": tail_cv,
        "x_profile_flux_last_to_mean_ratio_by_x": last_to_mean,
        "x_profile_flux_phase_lag_proxy": {
            "collapse_station_count": int(len(collapsed)),
            "collapsed_x": [item[2] for item in collapsed],
            "earliest_collapse_step": collapse_first_step,
            "latest_collapse_step": max((item[0] for item in collapsed), default=None),
        },
        "collapse_first_x": collapse_first_x,
        "collapse_first_step": collapse_first_step,
    }


def _diagnostic_sign_change_count(values: Sequence[float]) -> int:
    signs: List[int] = []
    for value in values:
        if value > 0.0:
            signs.append(1)
        elif value < 0.0:
            signs.append(-1)
    if len(signs) < 2:
        return 0
    return sum(1 for left, right in zip(signs, signs[1:]) if left != right)


def _flow_development_tail_summary(diagnostics: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    tail = _diagnostic_tail_records(diagnostics)
    feedback = _diagnostic_numeric_values(tail, "controller_u_feedback")
    density_feedback = _diagnostic_numeric_values(tail, "controller_density_feedback")
    saturation = _diagnostic_numeric_values(tail, "controller_saturation_fraction_run")
    raw_error = _diagnostic_numeric_values(tail, "controller_raw_flux_error")
    filtered_error = _diagnostic_numeric_values(tail, "controller_filtered_flux_error")
    target_flux = _diagnostic_numeric_values(tail, "controller_target_outlet_flux")
    measured_flux = _diagnostic_numeric_values(tail, "controller_measured_outlet_flux")
    authority = _diagnostic_numeric_values(tail, "controller_authority_ratio")
    mass_drift = _diagnostic_numeric_values(tail, "mass_total_delta_rel")
    outlet_rho = _diagnostic_numeric_values(tail, "outlet_plane_rho_mean")
    outlet_ux_min = _diagnostic_numeric_values(tail, "outlet_plane_ux_min")
    outlet_ux_negative_fraction = _diagnostic_numeric_values(tail, "outlet_plane_negative_ux_fraction")
    inlet_flux = _diagnostic_numeric_values(tail, "target_outlet_flux")
    outlet_flux = _diagnostic_numeric_values(tail, "outlet_flux_after_correction")
    midplane_flux = _diagnostic_numeric_values(tail, "midplane_flux")
    near_outlet_flux_xminus1 = _diagnostic_numeric_values(tail, "near_outlet_flux_xminus1")
    near_outlet_flux_xminus2 = _diagnostic_numeric_values(tail, "near_outlet_flux_xminus2")
    near_outlet_flux_xminus3 = _diagnostic_numeric_values(tail, "near_outlet_flux_xminus3")
    near_outlet_to_outlet = _diagnostic_numeric_values(tail, "near_outlet_to_outlet_flux_ratio")
    drop_guard_active = _diagnostic_numeric_values(tail, "controller_drop_guard_active_step")
    drop_guard_fraction = _diagnostic_numeric_values(tail, "controller_drop_guard_activation_fraction_run")
    x_profile_summary = _flow_development_x_profile_tail_summary(tail)
    return {
        "controller_tail_record_count": int(len(tail)),
        "tail_inlet_flux_values": inlet_flux,
        "tail_outlet_flux_values": outlet_flux,
        "tail_midplane_flux_values": midplane_flux,
        "mass_drift_tail_mean": _diagnostic_mean(mass_drift),
        "mass_drift_tail_slope": _diagnostic_slope(mass_drift),
        "density_feedback_tail_mean": _diagnostic_mean(density_feedback),
        "density_feedback_tail_abs_max": _diagnostic_abs_max(density_feedback),
        "density_feedback_last_to_tail_mean": _diagnostic_last_to_mean(density_feedback),
        "outlet_rho_last": outlet_rho[-1] if outlet_rho else None,
        "outlet_rho_tail_mean": _diagnostic_mean(outlet_rho),
        "rho_outlet_tail_mean": _diagnostic_mean(outlet_rho),
        "rho_outlet_tail_std": _diagnostic_std(outlet_rho),
        "outlet_ux_min_last": outlet_ux_min[-1] if outlet_ux_min else None,
        "outlet_ux_negative_fraction_last": outlet_ux_negative_fraction[-1]
        if outlet_ux_negative_fraction
        else None,
        "controller_u_feedback_tail_mean": _diagnostic_mean(feedback),
        "controller_u_feedback_tail_abs_max": _diagnostic_abs_max(feedback),
        "controller_u_feedback_tail_std": _diagnostic_std(feedback),
        "controller_feedback_last_to_tail_mean": _diagnostic_last_to_mean(feedback),
        "controller_feedback_sign_change_count_tail": _diagnostic_sign_change_count(feedback),
        "controller_saturation_fraction_tail": _diagnostic_mean(saturation),
        "drop_guard_activation_count_tail": int(_diagnostic_sum(drop_guard_active) or 0),
        "drop_guard_activation_fraction_tail": _diagnostic_mean(drop_guard_fraction),
        "controller_raw_flux_error_tail_mean": _diagnostic_mean(raw_error),
        "controller_filtered_flux_error_tail_mean": _diagnostic_mean(filtered_error),
        "controller_target_outlet_flux_tail_mean": _diagnostic_mean(target_flux),
        "controller_measured_outlet_flux_tail_mean": _diagnostic_mean(measured_flux),
        "controller_authority_ratio_tail_mean": _diagnostic_mean(authority),
        "controller_authority_ratio_tail_max": _diagnostic_max(authority),
        "near_outlet_flux_xminus1_tail_mean": _diagnostic_mean(near_outlet_flux_xminus1),
        "near_outlet_flux_xminus2_tail_mean": _diagnostic_mean(near_outlet_flux_xminus2),
        "near_outlet_flux_xminus3_tail_mean": _diagnostic_mean(near_outlet_flux_xminus3),
        "near_outlet_to_outlet_flux_ratio_tail_mean": _diagnostic_mean(near_outlet_to_outlet),
        "outlet_flux_tail_slope": _diagnostic_slope(outlet_flux),
        "outlet_flux_tail_drop_ratio": _diagnostic_ratio(
            outlet_flux[-1] if outlet_flux else None,
            outlet_flux[0] if outlet_flux else None,
        ),
        "outlet_flux_tail_last_to_mean_ratio": _diagnostic_last_to_mean(outlet_flux),
        **x_profile_summary,
    }


def _flow_development_diagnostic_row_from_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {field: record.get(field) for field in FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS}


def _snapshot_anomaly_cell(rho: np.ndarray, v: np.ndarray) -> Tuple[int, int, int]:
    rho_score = np.abs(np.asarray(rho, dtype=float) - 1.0)
    if v.size:
        score = rho_score + np.linalg.norm(np.asarray(v, dtype=float), axis=-1)
    else:
        score = rho_score
    return tuple(int(index) for index in np.unravel_index(int(np.nanargmax(score)), score.shape))


def _snapshot_local_window_stats(
    rho: np.ndarray,
    v: np.ndarray,
    cell: Tuple[int, int, int],
    radius: int = 1,
) -> Dict[str, Any]:
    slices = tuple(
        slice(max(0, index - radius), min(shape, index + radius + 1))
        for index, shape in zip(cell, rho.shape)
    )
    rho_window = rho[slices]
    v_window = v[slices] if v.size else np.zeros((*rho_window.shape, 3), dtype=np.float32)
    return {
        "bounds": [[sl.start, sl.stop] for sl in slices],
        "rho_min": round(_finite_float(np.nanmin(rho_window)), 7),
        "rho_max": round(_finite_float(np.nanmax(rho_window)), 7),
        "max_v": round(_finite_float(np.nanmax(np.linalg.norm(v_window, axis=-1))), 7) if v_window.size else 0.0,
    }


def _write_partial_timeseries(
    row_path: Path,
    records: Sequence[Dict[str, Any]],
    stability_records: Sequence[Dict[str, Any]],
) -> None:
    records = _dedupe_step120_records(records)
    stability_records = _dedupe_step120_records(stability_records)
    _write_timeseries(row_path / "fluid_diagnostics_timeseries.csv", records)
    _write_boundary_flux_timeseries(row_path / "boundary_flux_timeseries.csv", records)
    _write_density_drift_timeseries(row_path / "density_drift_timeseries.csv", records)
    _write_csv(row_path / "stability_diagnostics_timeseries.csv", list(stability_records), _STABILITY_TIMESERIES_FIELDS)
    _write_flow_development_diagnostics(row_path, records)


def _write_full_population_snapshot(row_path: Path, lbm: LBMFluid3D, step: int, reason: str) -> None:
    rho = lbm.rho.to_numpy()
    v = lbm.v.to_numpy()
    f = lbm.f.to_numpy()
    F = lbm.F.to_numpy()
    snapshot_dir = row_path / "population_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = DEFAULT_FAILURE_SNAPSHOT_ROOT / row_path.name
    runtime_dir.mkdir(parents=True, exist_ok=True)
    safe_reason = str(reason).replace(":", "_").replace("/", "_").replace("\\", "_")
    raw_path = runtime_dir / f"snapshot_step_{int(step):06d}_{safe_reason}.npz"
    np.savez_compressed(raw_path, rho=rho, v=v, f=f, F=F)
    anomaly_cell = _snapshot_anomaly_cell(rho, v)
    _write_json(
        snapshot_dir / f"snapshot_step_{int(step):06d}_{reason}.json",
        {
            "step": int(step),
            "reason": reason,
            "snapshot_payload_omitted_from_git": True,
            "runtime_npz_path": str(raw_path),
            "raw_arrays_committed_to_git": False,
            "rho_shape": [int(lbm.nx), int(lbm.ny), int(lbm.nz)],
            "f_shape": [int(lbm.nx), int(lbm.ny), int(lbm.nz), 19],
            "anomaly_cell": list(anomaly_cell),
            "field_stats": {
                "rho_min": _finite_float(np.nanmin(rho)),
                "rho_max": _finite_float(np.nanmax(rho)),
                "max_v": _finite_float(np.nanmax(np.linalg.norm(v, axis=-1))) if v.size else 0.0,
                "f_min": _finite_float(np.nanmin(f)),
                "F_min": _finite_float(np.nanmin(F)),
            },
            "local_window": _snapshot_local_window_stats(rho, v, anomaly_cell),
        },
    )


def _write_matrix_summary(
    out: Path,
    rows: Sequence[Dict[str, Any]],
    gate: Dict[str, Any],
    row_status: Dict[str, Any],
) -> Dict[str, Any]:
    summary = {
        "step": 120,
        "step120_schema_version": STEP120_SCHEMA_VERSION,
        "simulation_backed_artifacts": any(row.get("simulation_backed_artifact", False) for row in rows),
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "full_fsi_rerun_done": False,
        "validation_claim_allowed": False,
        "row_status_summary": row_status,
        "step121_quasi2d_allowed": bool(gate["step121_quasi2d_allowed"]),
        "final_classification": gate["final_classification"],
        "runs": list(rows),
    }
    _write_json(out / "run_matrix_summary.json", summary)
    _write_csv(out / "run_matrix_summary.csv", list(rows), _RUN_SUMMARY_FIELDS)
    return summary


def _write_row_status_summary(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    statuses = []
    for row in rows:
        row_dir = out / row["name"]
        statuses.append(classify_step120_row_status(row_dir))
    counts: Dict[str, int] = {}
    for status in statuses:
        counts[status["status"]] = counts.get(status["status"], 0) + 1
    summary = {
        "step": 120,
        "row_statuses": statuses,
        "status_counts": counts,
        "validation_claim_allowed": False,
    }
    _write_json(out / "row_status_summary.json", summary)
    return summary


def _write_limiter_actual_activation_summary(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    row_summaries = [
        {
            "name": row["name"],
            "lbm_open_boundary_semantics": row["lbm_open_boundary_semantics"],
            "open_boundary_limiter_enabled": bool(row.get("open_boundary_limiter_enabled", False)),
            "limiter_counter_source": row.get("limiter_counter_source"),
            "limiter_activation_count": int(row.get("limiter_activation_count", 0) or 0),
            "limiter_activation_denominator": int(row.get("limiter_activation_denominator", 0) or 0),
            "limiter_activation_fraction": _finite_float(row.get("limiter_activation_fraction", 0.0) or 0.0),
            "limiter_activation_gate_pass": bool(row.get("limiter_activation_gate_pass", True)),
        }
        for row in rows
    ]
    total_count = sum(item["limiter_activation_count"] for item in row_summaries)
    total_denominator = sum(item["limiter_activation_denominator"] for item in row_summaries)
    max_fraction = max([item["limiter_activation_fraction"] for item in row_summaries] or [0.0])
    summary = {
        "step": 120,
        "counter_source": "actual_open_boundary_kernel_counters",
        "row_summaries": row_summaries,
        "total_limiter_activation_count": int(total_count),
        "total_limiter_activation_denominator": int(total_denominator),
        "total_limiter_activation_fraction": _finite_float(total_count / total_denominator if total_denominator else 0.0),
        "max_limiter_activation_fraction": _finite_float(max_fraction),
        "limiter_activation_fraction_limit": LIMITER_ACTIVATION_FRACTION_LIMIT,
        "validation_blocked_by_limiter_activation": bool(max_fraction > LIMITER_ACTIVATION_FRACTION_LIMIT),
        "validation_claim_allowed": False,
    }
    _write_json(out / "limiter_actual_activation_summary.json", summary)
    return summary


def _write_boundary_variant_48_comparison(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    selection = select_step120_best_boundary(rows)
    comparison = {
        "step": 120,
        "comparison_scope": "48^3 real LBM boundary candidate ranking",
        "reference_rows": [row for row in rows if row.get("requested_nx") == 48 and row.get("lbm_open_boundary_semantics") in REFERENCE_SEMANTICS],
        "candidate_summaries": selection.get("candidate_summaries", []),
        "best_boundary_selected": selection.get("best_boundary_selected", False),
        "selected_boundary_semantics": selection.get("selected_boundary_semantics"),
        "selected_row_name": selection.get("selected_row_name"),
        "validation_claim_allowed": False,
    }
    _write_json(out / "boundary_variant_48_comparison.json", comparison)
    return comparison


def _write_best_boundary_selection(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    selection = select_step120_best_boundary(rows)
    _write_json(out / "best_boundary_selection.json", selection)
    return selection


def _write_boundary_variant_96_validation(
    out: Path,
    rows: Sequence[Dict[str, Any]],
    best_selection: Dict[str, Any],
) -> Dict[str, Any]:
    slug = best_selection.get("selected_boundary_slug")
    selected_rows = []
    if slug:
        selected_names = {f"duct_only_96_{slug}_1000step_real", f"static_two_flap_96_{slug}_1000step_real"}
        selected_rows = [row for row in rows if row.get("name") in selected_names]
    validation = {
        "step": 120,
        "best_boundary_selected": bool(best_selection.get("best_boundary_selected", False)),
        "selected_boundary_semantics": best_selection.get("selected_boundary_semantics"),
        "selected_boundary_slug": slug,
        "selected_96_rows": selected_rows,
        "validation_claim_allowed": False,
    }
    _write_json(out / "boundary_variant_96_validation.json", validation)
    return validation


def _write_global_first_failure(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    failures = [
        {
            "name": row["name"],
            "first_failure_step": row.get("first_failure_step"),
            "first_failure_reason": row.get("first_failure_reason"),
        }
        for row in rows
        if row.get("first_failure_reason") is not None
    ]
    summary = {
        "step": 120,
        "failure_rows": failures,
        "first_failure_row": failures[0] if failures else None,
        "validation_claim_allowed": False,
    }
    _write_json(out / "first_failure_global_summary.json", summary)
    return summary


def _write_step120_gate_report(
    out: Path,
    rows: Sequence[Dict[str, Any]],
    limiter_summary: Dict[str, Any],
    best_selection: Dict[str, Any],
) -> Dict[str, Any]:
    gate = build_step120_gate_report(rows, limiter_summary, best_selection)
    _write_json(out / "step120_gate_report.json", gate)
    return gate


def _write_solver_report(
    out: Path,
    rows: Sequence[Dict[str, Any]],
    comparison_48: Dict[str, Any],
    best_selection: Dict[str, Any],
    validation_96: Dict[str, Any],
    first_failure: Dict[str, Any],
    limiter_summary: Dict[str, Any],
    gate: Dict[str, Any],
    matrix_summary: Dict[str, Any],
) -> None:
    _write_json(
        out / "solver_report.json",
        {
            "step": 120,
            "step120_schema_version": STEP120_SCHEMA_VERSION,
            "goal_file": "STEP120_LBM_BOUNDARY_REPAIR_LARGE_REAL_EXECUTION_GOAL.md",
            "runner_file": "experiments/steps/step120_lbm_boundary_repair_large_real_execution.py",
            "fluid_only": True,
            "full_fsi_rerun_done": False,
            "fluent_validation_claim_allowed": False,
            "quasi2d_allowed": gate["quasi2d_allowed"],
            "final_classification": gate["final_classification"],
            "row_count": int(len(rows)),
            "comparison_48": comparison_48,
            "best_boundary_selection": best_selection,
            "validation_96": validation_96,
            "first_failure_global_summary": first_failure,
            "limiter_actual_activation_summary": limiter_summary,
            "matrix_summary": matrix_summary,
        },
    )


def _write_output_readme(out: Path, rows: Sequence[Dict[str, Any]], gate: Dict[str, Any], best_selection: Dict[str, Any]) -> None:
    text = [
        "# Step120 LBM Boundary Repair Large Real Execution",
        "",
        "This directory contains Step120 LBM-only runner repair artifacts.",
        "",
        f"- Final classification: `{gate['final_classification']}`",
        f"- Quasi-2D allowed: `{str(gate['quasi2d_allowed']).lower()}`",
        f"- Best boundary selected: `{str(best_selection.get('best_boundary_selected', False)).lower()}`",
        f"- Rows recorded: `{len(rows)}`",
        "",
        "No Fluent parity, full FSI, or dynamic flap claim is made by this step.",
        "Runtime checkpoints are intentionally kept under `outputs/tmp/step120_checkpoints` and are not committed.",
        "",
    ]
    (out / "README.md").write_text("\n".join(text), encoding="utf-8")


def _replace_spec(spec: Step120RunSpec, **updates: Any) -> Step120RunSpec:
    data = asdict(spec)
    data.update(updates)
    return Step120RunSpec(**data)


def _metric(row: Dict[str, Any], key: str, default: float = 1.0e9) -> float:
    value = row.get(key, default)
    if value is None:
        return float(default)
    return float(value)


def _boundary_slug(semantics: Optional[str]) -> str:
    if semantics == "regularized_velocity_pressure_limited":
        return "limited"
    if semantics == "convective_pressure_outlet_experimental":
        return "convective"
    if semantics == "regularized_mass_balanced_pressure_outlet":
        return "regularized_mass_balanced"
    if semantics == "convective_mass_balanced_pressure_outlet":
        return "convective_mass_balanced"
    if semantics == "regularized_flux_matched_pressure_outlet":
        return "regularized_flux_matched"
    if semantics == "convective_flux_matched_damped_outlet":
        return "convective_flux_matched_damped"
    if semantics == "equilibrium_all_population_reset":
        return "legacy"
    if semantics == "regularized_velocity_pressure":
        return "regularized"
    return "unknown"


def _limiter_parameters(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "open_boundary_limiter_enabled": bool(row.get("open_boundary_limiter_enabled", False)),
        "limiter_activation_fraction": row.get("limiter_activation_fraction"),
    }


def _should_failure_check(spec: Step120RunSpec, step: int) -> bool:
    interval = max(1, int(spec.failure_check_interval))
    return step == 0 or step == int(spec.n_steps) or step % interval == 0


def _should_full_sample(spec: Step120RunSpec, step: int) -> bool:
    interval = max(1, int(spec.output_interval))
    if step == 0 or step == int(spec.n_steps) or step % interval == 0:
        return True
    snapshot_interval = int(spec.full_population_snapshot_interval)
    return bool(snapshot_interval > 0 and step % snapshot_interval == 0)


def solver_state_hash_for_spec(spec: Step120RunSpec) -> str:
    data = asdict(spec)
    relevant = {
        key: data.get(key)
        for key in sorted(SOLVER_STATE_HASH_FIELDS)
        if key in data
    }
    tau = _tau_feasibility_report(spec)
    relevant["requested_nx"] = spec.requested_grid()
    relevant["relaxation_semantics"] = tau["lbm_relaxation_semantics"]
    relevant["tau"] = _finite_float(tau["tau"])
    return _hash_spec_mapping(relevant)


def run_manifest_hash_for_spec(spec: Step120RunSpec) -> str:
    data = asdict(spec)
    for key in [
        "source_step",
        "source_row_name",
        "source_solver_state_hash",
        "source_run_manifest_hash",
        "source_code_commit",
        "source_step139_row_name",
        "source_step139_solver_state_hash",
        "source_step139_run_manifest_hash",
        "source_step139_code_commit",
        "source_step140_summary_hash",
        "source_step140_summary_path",
        "source_step140_dominant_failure_mechanism",
        "source_step140_mass_drift_mechanism",
    ]:
        if data.get(key) is None:
            data.pop(key, None)
    return _hash_spec_mapping(data)


def _config_hash(spec: Step120RunSpec) -> str:
    return solver_state_hash_for_spec(spec)


def _legacy_config_hash(spec: Step120RunSpec) -> str:
    data = asdict(spec)
    relevant = {
        key: data[key]
        for key in sorted(data)
        if key
        not in {
            "max_wall_seconds",
            "artifact_scope_note",
            "stop_on_first_failure",
        }
    }
    return _hash_spec_mapping(relevant)


def _hash_spec_mapping(mapping: Dict[str, Any]) -> str:
    return sha256(json.dumps(mapping, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _flow_development_gate_pass(
    *,
    flux_balance_reported: bool,
    inlet_flux_tail_mean: Optional[float],
    outlet_flux_tail_mean: Optional[float],
    outlet_to_inlet_flux_ratio_tail_mean: Optional[float],
    midplane_to_inlet_flux_ratio_tail_mean: Optional[float],
    flux_imbalance_rel_tail_mean: Optional[float],
    flux_imbalance_rel_tail_max: Optional[float],
    outlet_flux_tail_cv: Optional[float],
) -> bool:
    if (
        not flux_balance_reported
        or inlet_flux_tail_mean is None
        or outlet_flux_tail_mean is None
        or outlet_to_inlet_flux_ratio_tail_mean is None
        or midplane_to_inlet_flux_ratio_tail_mean is None
        or flux_imbalance_rel_tail_mean is None
        or flux_imbalance_rel_tail_max is None
        or outlet_flux_tail_cv is None
    ):
        return False
    if abs(float(inlet_flux_tail_mean)) <= 1.0e-6:
        return False
    outlet_ratio = abs(float(outlet_to_inlet_flux_ratio_tail_mean))
    midplane_ratio = abs(float(midplane_to_inlet_flux_ratio_tail_mean))
    return bool(
        float(inlet_flux_tail_mean) * float(outlet_flux_tail_mean) > 0.0
        and 0.80 <= outlet_ratio <= 1.20
        and 0.80 <= midplane_ratio <= 1.20
        and float(flux_imbalance_rel_tail_mean) < 0.10
        and float(flux_imbalance_rel_tail_max) < 0.20
        and float(outlet_flux_tail_cv) < 0.10
    )


def _latest_checkpoint_path(spec: Step120RunSpec, checkpoint_root: Path) -> Optional[Path]:
    paths = _checkpoint_paths(spec, checkpoint_root)
    return paths[-1] if paths else None


def _checkpoint_paths(spec: Step120RunSpec, checkpoint_root: Path, reverse: bool = False) -> List[Path]:
    root = checkpoint_root / spec.name
    if not root.is_dir():
        return []
    paths = sorted(root.glob("checkpoint_step_*.npz"))
    return list(reversed(paths)) if reverse else paths


def _prune_step120_checkpoints(root: Path, *, keep_last: int) -> None:
    npz_paths = sorted(root.glob("checkpoint_step_*.npz"))
    for old in npz_paths[: max(0, len(npz_paths) - int(keep_last))]:
        json_sidecar = old.with_suffix(".json")
        try:
            old.unlink()
        except OSError:
            pass
        try:
            json_sidecar.unlink()
        except OSError:
            pass


def _validate_checkpoint_metadata(spec: Step120RunSpec, metadata: Dict[str, Any]) -> None:
    if int(metadata.get("schema_version", -1)) != STEP120_SCHEMA_VERSION:
        raise ValueError("checkpoint schema version mismatch")
    checkpoint_solver_hash = metadata.get("solver_state_hash")
    if checkpoint_solver_hash is None and metadata.get("config_hash") == _legacy_config_hash(spec):
        checkpoint_solver_hash = solver_state_hash_for_spec(spec)
    if checkpoint_solver_hash != solver_state_hash_for_spec(spec):
        raise ValueError("checkpoint solver state hash mismatch")
    if list(metadata.get("shape", [])) != [int(spec.nx), int(spec.ny), int(spec.nz)]:
        raise ValueError("checkpoint shape mismatch")
    if metadata.get("boundary_semantics") != spec.open_boundary_semantics:
        raise ValueError("checkpoint boundary semantics mismatch")
    if metadata.get("relaxation_semantics") != _relaxation_semantics_for_spec(spec):
        raise ValueError("checkpoint relaxation semantics mismatch")


def _relaxation_semantics_for_spec(spec: Step120RunSpec) -> str:
    return str(_tau_feasibility_report(spec)["lbm_relaxation_semantics"])


_RUN_SUMMARY_FIELDS = [
    "name",
    "row_role",
    "lbm_open_boundary_semantics",
    "requested_nx",
    "requested_n_steps",
    "steps_completed",
    "requested_window_completed",
    "row_source",
    "simulation_backed_artifact",
    "solver_state_hash",
    "run_manifest_hash",
    "stop_reason",
    "flux_balance_reported",
    "flux_imbalance_rel_tail_mean",
    "flux_imbalance_rel_tail_max",
    "outlet_flux_tail_mean",
    "outlet_flux_tail_cv",
    "outlet_to_inlet_flux_ratio_tail_mean",
    "midplane_to_inlet_flux_ratio_tail_mean",
    "flow_development_gate_pass",
    "mass_total_delta_rel_final",
    "limiter_activation_count",
    "limiter_activation_fraction",
    "checkpoint_available",
    "step120_validation_claimed",
]

FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS = [
    "step",
    "lbm_open_boundary_semantics",
    "row_role",
    "step135_interior_reflection_candidate",
    "step136_ramped_throughput_calibration_candidate",
    "step137_ramp_target_refinement_candidate",
    "step138_high_authority_outlet_candidate",
    "step139_planeflux_final48_candidate",
    "step141_density_feedback_isolation_candidate",
    "step134_outlet_stationarity_candidate",
    "step133_mass_damped_candidate",
    "step132_authority_sweep_candidate",
    "open_boundary_flux_control_measure_plane_offset",
    "open_boundary_outlet_flux_drop_guard_enabled",
    "open_boundary_outlet_flux_drop_guard_min_ratio",
    "open_boundary_inlet_ramp_steps",
    "open_boundary_inlet_ramp_profile",
    "open_boundary_inlet_ramp_factor",
    "open_boundary_flux_control_target_scale",
    "target_outlet_flux",
    "outlet_flux_raw_before_correction",
    "outlet_flux_after_correction",
    "outlet_flux_error",
    "outlet_flux_error_filtered",
    "correction_gain_effective",
    "flow_correction_cap_u",
    "correction_delta_abs_sum",
    "correction_delta_abs_sum_run",
    "controller_target_outlet_flux",
    "controller_measured_outlet_flux",
    "controller_raw_flux_error",
    "controller_filtered_flux_error",
    "controller_u_feedback",
    "controller_u_feedback_abs",
    "controller_density_feedback",
    "controller_density_feedback_abs",
    "controller_delta_cap_u",
    "controller_slew_alpha",
    "controller_authority_ratio",
    "controller_saturation_count_step",
    "controller_saturation_count_run",
    "controller_saturation_fraction_run",
    "controller_measure_plane_offset",
    "controller_target_scale",
    "controller_drop_guard_active_step",
    "controller_drop_guard_activation_count_run",
    "controller_drop_guard_activation_fraction_run",
    "controller_drop_guard_reference_flux",
    "controller_true_outlet_flux_for_guard",
    "outlet_plane_ux_min",
    "outlet_plane_ux_max",
    "outlet_plane_ux_mean",
    "outlet_plane_negative_ux_fraction",
    "outlet_plane_rho_mean",
    "outlet_plane_rho_std",
    "midplane_flux",
    "near_outlet_flux_xminus1",
    "near_outlet_flux_xminus2",
    "near_outlet_flux_xminus3",
    "near_outlet_to_outlet_flux_ratio",
    "x_profile_flux_samples",
    "x_profile_ux_mean_samples",
    "x_profile_rho_mean_samples",
    "sampled_x_profile_flux",
    "source_step",
    "source_row_name",
    "source_solver_state_hash",
    "source_run_manifest_hash",
    "source_code_commit",
    "source_step139_row_name",
    "source_step139_solver_state_hash",
    "source_step139_run_manifest_hash",
    "source_step139_code_commit",
    "source_step140_summary_hash",
    "source_step140_summary_path",
    "source_step140_dominant_failure_mechanism",
    "source_step140_mass_drift_mechanism",
    "mass_total_delta_rel",
    "validation_claim_allowed",
    "selected96_claim_allowed",
]

_STABILITY_TIMESERIES_FIELDS = [
    "step",
    "diagnostic_mode",
    "rho_min",
    "rho_max",
    "max_v",
    "f_min",
    "f_max",
    "F_min",
    "F_max",
    "negative_population_count",
    "negative_population_fraction",
    "population_entry_count",
    "fluid_cell_count",
    "mass_total",
    "mass_total_delta_rel",
    "boundary_x_min_negative_population_count",
    "boundary_x_max_negative_population_count",
    "stability_all_finite",
]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--row", action="append", dest="rows", default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--output-interval", type=int, default=None)
    parser.add_argument("--checkpoint-every", type=int, default=None)
    parser.add_argument("--max-wall-seconds", type=float, default=None)
    parser.add_argument("--allow-large-real-rows", action="store_true")
    args = parser.parse_args(argv)
    run_step120_matrix(
        output_dir=args.output_dir,
        force=args.force,
        resume=not args.no_resume,
        row_names=args.rows,
        max_rows=args.max_rows,
        output_interval=args.output_interval,
        checkpoint_every=args.checkpoint_every,
        max_wall_seconds=args.max_wall_seconds,
        allow_large_real_rows=args.allow_large_real_rows,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
