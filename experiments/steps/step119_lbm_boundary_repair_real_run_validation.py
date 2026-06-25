from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import taichi as ti

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
    Step118RunSpec,
    _make_lbm_config,
    population_stats_from_record,
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


DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "step119_lbm_boundary_repair_real_run_validation"
STEP119_SCHEMA_VERSION = 1
LIMITER_ACTIVATION_FRACTION_LIMIT = 0.05

REQUIRED_ROW_NAMES = [
    "duct_only_48_legacy_boundary_500step_reference_real",
    "duct_only_48_regularized_boundary_500step_reference_real",
    "duct_only_48_regularized_limited_boundary_500step_real",
    "duct_only_48_convective_outlet_boundary_500step_real",
    "duct_only_96_regularized_limited_boundary_1000step_real",
    "duct_only_96_convective_outlet_boundary_1000step_real",
    "static_two_flap_96_best_boundary_1000step_real",
    "duct_only_96_regularized_limited_physical_nu_report_only_100step_guarded_real",
]

REQUIRED_VALIDATION_ROW_NAMES = [
    "duct_only_48_legacy_boundary_500step_reference_real",
    "duct_only_48_regularized_boundary_500step_reference_real",
    "duct_only_48_regularized_limited_boundary_500step_real",
    "duct_only_48_convective_outlet_boundary_500step_real",
    "duct_only_96_regularized_limited_boundary_1000step_real",
    "duct_only_96_convective_outlet_boundary_1000step_real",
    "static_two_flap_96_best_boundary_1000step_real",
]

FINAL_CLASSIFICATIONS = {
    "boundary_repair_success_go_to_quasi2d",
    "boundary_repair_partial_continue_lbm",
    "boundary_repair_failed_revisit_lbm_solver",
}


@dataclass(frozen=True)
class Step119RunSpec(Step118RunSpec):
    artifact_scope_note: str = "Step119 real non-synthetic LBM boundary repair validation row"
    step119_required_row: bool = True
    synthetic_diagnostic_mode: bool = False
    stop_on_first_failure: bool = True
    checkpoint_every: int = 0
    max_wall_seconds: Optional[float] = None
    limiter_activation_fraction_limit: float = LIMITER_ACTIVATION_FRACTION_LIMIT
    allow_large_real_run_without_flag: bool = False


def step119_real_run_specs(output_interval: int = 5) -> List[Step119RunSpec]:
    return [
        Step119RunSpec(
            name="tiny_step119_real_runner_smoke",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=8,
            requested_n_steps=5,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            artifact_scope_note="committed tiny real non-synthetic smoke row for Step119 runner plumbing",
            step119_required_row=False,
            not_used_for_validation=True,
            allow_large_real_run_without_flag=True,
        ),
        Step119RunSpec(
            name="duct_only_48_legacy_boundary_500step_reference_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            open_boundary_semantics="equilibrium_all_population_reset",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            artifact_scope_note="required real 48^3 legacy 500-step reference; skipped unless large rows are explicitly allowed",
        ),
        Step119RunSpec(
            name="duct_only_48_regularized_boundary_500step_reference_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            artifact_scope_note="required real 48^3 old regularized 500-step reference; skipped unless large rows are explicitly allowed",
        ),
        Step119RunSpec(
            name="duct_only_48_regularized_limited_boundary_500step_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            artifact_scope_note="required real 48^3 limited regularized 500-step repair row; skipped unless large rows are explicitly allowed",
        ),
        Step119RunSpec(
            name="duct_only_48_convective_outlet_boundary_500step_real",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            open_boundary_semantics="convective_pressure_outlet_experimental",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            artifact_scope_note="required real 48^3 convective outlet 500-step repair row; skipped unless large rows are explicitly allowed",
        ),
        Step119RunSpec(
            name="duct_only_96_regularized_limited_boundary_1000step_real",
            nx=96,
            ny=96,
            nz=96,
            n_steps=1000,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=96,
            requested_n_steps=1000,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            artifact_scope_note="required real 96^3 limited regularized 1000-step repair row; only run after 48^3 improvement is established",
        ),
        Step119RunSpec(
            name="duct_only_96_convective_outlet_boundary_1000step_real",
            nx=96,
            ny=96,
            nz=96,
            n_steps=1000,
            output_interval=output_interval,
            open_boundary_semantics="convective_pressure_outlet_experimental",
            geometry_mode="duct_only",
            requested_nx=96,
            requested_n_steps=1000,
            artifact_scope_note="required real 96^3 convective outlet 1000-step repair row; only run after 48^3 improvement is established",
        ),
        Step119RunSpec(
            name="static_two_flap_96_best_boundary_1000step_real",
            nx=96,
            ny=96,
            nz=96,
            n_steps=1000,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="static_two_flap",
            requested_nx=96,
            requested_n_steps=1000,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            artifact_scope_note="required real 96^3 static two-flap best-boundary row; LBM-only and not FSI",
        ),
        Step119RunSpec(
            name="duct_only_96_regularized_limited_physical_nu_report_only_100step_guarded_real",
            nx=96,
            ny=96,
            nz=96,
            n_steps=100,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=96,
            requested_n_steps=100,
            lbm_viscosity_semantics="physical_nu_mapping",
            lbm_tau_stability_policy="strict",
            lbm_dt_phys_override_s=2.0833333333333334e-6,
            target_inlet_velocity_mps=10.0,
            target_reynolds_number=26666.666666666668,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            not_used_for_validation=True,
            artifact_scope_note="strict tau-guarded physical-nu policy row; report-only and not validation",
        ),
    ]


def run_step119_matrix(
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    specs: Optional[Sequence[Step119RunSpec]] = None,
    force: bool = False,
    resume: bool = True,
    row_names: Optional[Sequence[str]] = None,
    max_rows: Optional[int] = None,
    output_interval: Optional[int] = None,
    stop_on_first_failure: Optional[bool] = None,
    checkpoint_every: Optional[int] = None,
    max_wall_seconds: Optional[float] = None,
    allow_large_real_rows: bool = False,
) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    default_specs_used = specs is None
    all_default_specs = step119_real_run_specs()
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

    rows = []
    for spec in run_specs:
        row_dir = out / spec.name
        if resume and not force and _row_complete(row_dir):
            row = _read_json(row_dir / "finite_stability_report.json")["summary_row"]
            row["row_source"] = "resumed"
            rows.append(row)
            continue
        rows.append(run_step119_row(spec, row_dir, allow_large_real_rows=allow_large_real_rows))

    if default_specs_used:
        row_names_seen = {row["name"] for row in rows}
        for spec in all_default_specs:
            if spec.name in row_names_seen:
                continue
            row_dir = out / spec.name
            if _row_complete(row_dir):
                row = _read_json(row_dir / "finite_stability_report.json")["summary_row"]
                row["row_source"] = "existing"
                rows.append(row)

    limiter_summary = _write_limiter_activation_summary(out, rows)
    gate = _write_step119_gate_report(out, rows, limiter_summary)
    summary = _write_matrix_summary(out, rows, gate)
    comparison = _write_boundary_variant_comparison(out, rows)
    first_failure = _write_global_first_failure(out, rows)
    _write_solver_report(out, rows, comparison, first_failure, limiter_summary, gate, summary)
    _write_output_readme(out, rows, gate)
    return summary


def run_step119_row(
    spec: Step119RunSpec,
    row_dir: Path | str,
    allow_large_real_rows: bool = False,
) -> Dict[str, Any]:
    row_path = Path(row_dir)
    row_path.mkdir(parents=True, exist_ok=True)
    tau_report = _tau_feasibility_report(spec)
    print(
        f"[Step119] row={spec.name} mode={spec.geometry_mode} "
        f"grid={spec.nx}x{spec.ny}x{spec.nz} steps={spec.n_steps}",
        flush=True,
    )

    if spec.synthetic_diagnostic_mode:
        return _write_nonstepped_row(spec, row_path, tau_report, "synthetic_diagnostic_mode_not_allowed")
    if spec.lbm_tau_stability_policy == "strict" and not tau_report["tau_margin_pass"]:
        print(f"[Step119] row={spec.name} skipped before stepping: tau_margin", flush=True)
        return _write_nonstepped_row(spec, row_path, tau_report, "tau_margin")
    if _large_real_row_requires_allowance(spec) and not (allow_large_real_rows or spec.allow_large_real_run_without_flag):
        print(f"[Step119] row={spec.name} skipped before stepping: large row requires --allow-large-real-rows", flush=True)
        return _write_nonstepped_row(spec, row_path, tau_report, "large_real_row_requires_explicit_allowance")

    _ensure_taichi()
    config = _make_lbm_config(spec, tau_report)
    started = time.perf_counter()
    lbm = LBMFluid3D(config)
    _apply_static_geometry(lbm, spec)
    lbm.init_simulation()

    records: List[Dict[str, Any]] = []
    stability_records: List[Dict[str, Any]] = []
    combined_records: List[Dict[str, Any]] = []
    mass_initial = None
    steps_completed = 0
    stop_reason = None
    for step in range(0, int(spec.n_steps) + 1):
        if step > 0:
            lbm.step()
            steps_completed = step
        should_sample = step == 0 or step == int(spec.n_steps) or step % int(spec.output_interval) == 0
        if should_sample:
            summary = summarize_lbm_boundary_diagnostics(lbm, step=step, mass_initial=mass_initial)
            if mass_initial is None:
                mass_initial = summary["mass_total"]
                summary = summarize_lbm_boundary_diagnostics(lbm, step=step, mass_initial=mass_initial)
            stability = summarize_lbm_stability_diagnostics(lbm, step=step)
            combined = {**summary, **stability}
            records.append(summary)
            stability_records.append(stability)
            combined_records.append(combined)
            _write_partial_timeseries(row_path, records, stability_records)
            print(
                f"[Step119] row={spec.name} step={step}/{spec.n_steps} "
                f"rho=[{summary['rho_min']:.6g},{summary['rho_max']:.6g}] "
                f"mass_drift={summary['mass_total_delta_rel']:.6g} "
                f"neg_pop={stability['negative_population_count']}",
                flush=True,
            )
            first_failure = first_gate_failure_detector(combined_records)
            if spec.stop_on_first_failure and first_failure["first_failure_step"] is not None:
                stop_reason = f"first_failure:{first_failure['first_failure_reason']}"
                break
        if spec.max_wall_seconds is not None and time.perf_counter() - started >= float(spec.max_wall_seconds):
            stop_reason = "max_wall_seconds"
            break

    runtime_s = _finite_float(time.perf_counter() - started)
    finite = _finite_report(spec, steps_completed, records, stability_records, combined_records, tau_report, runtime_s, stop_reason)
    metadata = _metadata(spec, tau_report, skipped=False, runtime_s=runtime_s, stop_reason=stop_reason)
    boundary = _boundary_report(spec)
    config_report = _lbm_config_report(config, spec, tau_report)
    limiter_summary = finite["limiter_activation_summary"]

    _write_json(row_path / "run_metadata.json", metadata)
    _write_json(row_path / "driver_config.json", config_report)
    _write_json(row_path / "duct_boundary_condition_report.json", boundary)
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_json(row_path / "first_failure_diagnostics.json", _first_failure_artifact(combined_records, spec, limiter_summary))
    _write_json(row_path / "limiter_activation_summary.json", limiter_summary)
    _write_json(row_path / "velocity_profile_summary.json", _velocity_profile_report(lbm, spec, records))
    _write_partial_timeseries(row_path, records, stability_records)
    if spec.geometry_mode == "static_two_flap":
        _write_static_flap_reports(row_path, lbm, spec, records[-1])
    print(f"[Step119] row={spec.name} completed runtime_s={runtime_s:.3f}", flush=True)
    return finite["summary_row"]


def summarize_limiter_activation(records: Sequence[Dict[str, Any]], spec: Step119RunSpec | Dict[str, Any]) -> Dict[str, Any]:
    limiter_enabled = bool(_spec_value(spec, "open_boundary_limiter_enabled", False))
    population_floor = _spec_value(spec, "open_boundary_population_floor", None)
    noneq_cap = _spec_value(spec, "open_boundary_noneq_cap", None)
    nx = int(_spec_value(spec, "nx", 1) or 1)
    ny = int(_spec_value(spec, "ny", 1) or 1)
    nz = int(_spec_value(spec, "nz", 1) or 1)
    rho_clip_count = sum(int(row.get("rho_below_low_count", 0) or 0) + int(row.get("rho_above_high_count", 0) or 0) for row in records)
    velocity_clip_count = sum(int(row.get("velocity_outlier_count", 0) or 0) for row in records)
    negative_population_count = sum(int(row.get("negative_population_count", 0) or 0) for row in records)
    noneq_clip_count = negative_population_count if limiter_enabled and noneq_cap is not None else 0
    population_floor_count = negative_population_count if limiter_enabled and population_floor is not None else 0
    denominator = sum(int(row.get("population_entry_count", 0) or 0) for row in records)
    if denominator <= 0:
        denominator = max(1, len(records) * nx * ny * nz * 19)
    activation_count = int(rho_clip_count + velocity_clip_count + noneq_clip_count + population_floor_count)
    activation_fraction = _finite_float(activation_count / denominator if denominator else 0.0)
    fraction_limit = float(_spec_value(spec, "limiter_activation_fraction_limit", LIMITER_ACTIVATION_FRACTION_LIMIT))
    blocked = bool(activation_fraction > fraction_limit)
    return {
        "step": 119,
        "open_boundary_limiter_enabled": limiter_enabled,
        "rho_clip_used": bool(limiter_enabled),
        "velocity_clip_used": bool(limiter_enabled),
        "noneq_limiter_used": bool(limiter_enabled and noneq_cap is not None),
        "population_floor_used": bool(limiter_enabled and population_floor is not None),
        "rho_clip_count": int(rho_clip_count),
        "velocity_clip_count": int(velocity_clip_count),
        "noneq_clip_count": int(noneq_clip_count),
        "population_floor_count": int(population_floor_count),
        "limiter_activation_count": activation_count,
        "limiter_activation_denominator": int(denominator),
        "limiter_activation_fraction": activation_fraction,
        "limiter_activation_fraction_limit": fraction_limit,
        "validation_blocked_by_limiter_activation": blocked,
        "validation_claim_allowed": False,
    }


def build_step119_gate_report(rows: Sequence[Dict[str, Any]], limiter_summary: Dict[str, Any]) -> Dict[str, Any]:
    rows_by_name = {row["name"]: row for row in rows}
    incomplete = [
        name
        for name in REQUIRED_VALIDATION_ROW_NAMES
        if rows_by_name.get(name, {}).get("requested_window_completed") is not True
        or rows_by_name.get(name, {}).get("step119_validation_claimed") is not True
    ]
    limiter_gate_pass = not bool(limiter_summary.get("validation_blocked_by_limiter_activation", False))
    all_required_pass = bool(not incomplete)
    quasi2d_allowed = bool(all_required_pass and limiter_gate_pass)
    any_real_progress = any(int(row.get("steps_completed", 0) or 0) > 0 for row in rows) or bool(rows)
    if quasi2d_allowed:
        classification = "boundary_repair_success_go_to_quasi2d"
    elif any_real_progress:
        classification = "boundary_repair_partial_continue_lbm"
    else:
        classification = "boundary_repair_failed_revisit_lbm_solver"
    return {
        "step": 119,
        "step119_schema_version": STEP119_SCHEMA_VERSION,
        "quasi2d_allowed": quasi2d_allowed,
        "step120_quasi2d_allowed": quasi2d_allowed,
        "validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "full_fsi_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "required_validation_rows": list(REQUIRED_VALIDATION_ROW_NAMES),
        "incomplete_required_rows": incomplete,
        "all_required_real_rows_pass": all_required_pass,
        "limiter_activation_gate_pass": limiter_gate_pass,
        "final_classification": classification,
        "no_fluent_claim": True,
        "no_fsi_claim": True,
    }


def _finite_report(
    spec: Step119RunSpec,
    steps_completed: int,
    records: Sequence[Dict[str, Any]],
    stability_records: Sequence[Dict[str, Any]],
    combined_records: Sequence[Dict[str, Any]],
    tau_report: Dict[str, Any],
    runtime_s: float,
    stop_reason: Optional[str],
) -> Dict[str, Any]:
    trend = summarize_timeseries_trends(records) if records else {}
    final = records[-1] if records else {}
    first_failure = first_gate_failure_detector(combined_records)
    limiter_summary = summarize_limiter_activation(stability_records, spec)
    finite_pass = bool(records and all(record["all_finite"] for record in records) and all(row["stability_all_finite"] for row in stability_records))
    density_gate_pass = bool(0.85 < float(trend.get("rho_min_global", 0.0)) <= float(trend.get("rho_max_global", 1.0e9)) < 1.15)
    mass_drift_gate_pass = bool(abs(float(trend.get("mass_drift_final", 1.0e9))) < 0.05)
    population_gate_pass = bool((stability_records[-1].get("negative_population_fraction", 1.0) if stability_records else 1.0) < 1.0e-3)
    mach_gate_pass = bool(float(trend.get("mach_proxy_observed_max", 1.0e9)) < 0.35)
    no_first_failure = first_failure["first_failure_reason"] is None
    requested_window_completed = bool(
        int(steps_completed) == int(spec.requested_steps()) and int(spec.nx) == int(spec.requested_grid())
    )
    step119_gate_pass = bool(
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
    summary_row = _summary_row(
        spec,
        steps_completed=steps_completed,
        requested_window_completed=requested_window_completed,
        finite_pass=finite_pass,
        density_gate_pass=density_gate_pass,
        mass_drift_gate_pass=mass_drift_gate_pass,
        population_gate_pass=population_gate_pass,
        mach_gate_pass=mach_gate_pass,
        first_failure_step=first_failure["first_failure_step"],
        first_failure_reason=first_failure["first_failure_reason"] or stop_reason,
        flux_imbalance_rel_final=final.get("flux_imbalance_rel"),
        flux_imbalance_rel_tail_mean=trend.get("flux_imbalance_rel_tail_mean"),
        mass_total_delta_rel_final=final.get("mass_total_delta_rel"),
        mach_proxy_observed_max=trend.get("mach_proxy_observed_max"),
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=False,
        row_source="computed",
        step119_validation_claimed=step119_gate_pass,
        runtime_s=runtime_s,
        limiter_summary=limiter_summary,
        simulation_backed_artifact=True,
    )
    return {
        **summary_row,
        "skipped_reason": stop_reason,
        "step119_gate_pass": step119_gate_pass,
        "step119_validation_claimed": step119_gate_pass,
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
        "summary_row": summary_row,
    }


def _write_nonstepped_row(spec: Step119RunSpec, row_path: Path, tau_report: Dict[str, Any], reason: str) -> Dict[str, Any]:
    limiter_summary = summarize_limiter_activation([], spec)
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
        mass_total_delta_rel_final=None,
        mach_proxy_observed_max=None,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=reason == "tau_margin",
        row_source="skipped",
        step119_validation_claimed=False,
        runtime_s=0.0,
        limiter_summary=limiter_summary,
        simulation_backed_artifact=False,
    )
    first_failure = _empty_first_failure(reason)
    finite = {
        **summary_row,
        "skipped_reason": reason,
        "step119_gate_pass": False,
        "step119_validation_claimed": False,
        "stability_repair_gates": {},
        "timeseries_trend_summary": {},
        "stability_timeseries_trend_summary": {},
        "population_stats_final": {},
        "first_failure_detector": first_failure,
        "limiter_activation_summary": limiter_summary,
        "mass_source_sink_by_step": {"record_count": 0},
        "tau_feasibility_report": tau_report,
        "not_used_for_validation": True,
        "validation_claim_allowed": False,
        "summary_row": summary_row,
    }
    _write_json(row_path / "run_metadata.json", _metadata(spec, tau_report, skipped=True, runtime_s=0.0, stop_reason=reason))
    _write_json(row_path / "driver_config.json", {"spec": asdict(spec), "tau_feasibility_report": tau_report})
    _write_json(row_path / "duct_boundary_condition_report.json", _boundary_report(spec))
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_json(row_path / "first_failure_diagnostics.json", _first_failure_artifact([], spec, limiter_summary, reason=reason))
    _write_json(row_path / "limiter_activation_summary.json", limiter_summary)
    _write_json(row_path / "velocity_profile_summary.json", {"skipped": True, "reason": reason, "synthetic_diagnostic_mode": False})
    _write_partial_timeseries(row_path, [], [])
    if spec.geometry_mode == "static_two_flap":
        _write_static_placeholder_reports(row_path, reason)
    return summary_row


def _summary_row(
    spec: Step119RunSpec,
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
    mass_total_delta_rel_final: Optional[float],
    mach_proxy_observed_max: Optional[float],
    tau_margin_pass: Optional[bool],
    skipped_due_to_tau_margin: bool,
    row_source: str,
    step119_validation_claimed: bool,
    runtime_s: float,
    limiter_summary: Dict[str, Any],
    simulation_backed_artifact: bool,
) -> Dict[str, Any]:
    return {
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "open_boundary_limiter_enabled": bool(spec.open_boundary_limiter_enabled),
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
        "first_failure_step": first_failure_step,
        "first_failure_reason": first_failure_reason,
        "flux_balance_reported": not bool(skipped_due_to_tau_margin),
        "flux_imbalance_rel_final": flux_imbalance_rel_final,
        "flux_imbalance_rel_tail_mean": flux_imbalance_rel_tail_mean,
        "mass_total_delta_rel_final": mass_total_delta_rel_final,
        "mach_proxy_observed_max": mach_proxy_observed_max,
        "skipped_due_to_tau_margin": bool(skipped_due_to_tau_margin),
        "tau_margin_pass": tau_margin_pass,
        "synthetic_diagnostic_mode": False,
        "simulation_backed_artifact": bool(simulation_backed_artifact),
        "row_source": row_source,
        "step119_schema_version": STEP119_SCHEMA_VERSION,
        "step119_validation_claimed": bool(step119_validation_claimed),
        "validation_claim_allowed": False,
        "not_used_for_validation": bool(spec.not_used_for_validation or skipped_due_to_tau_margin or not step119_validation_claimed),
        "limiter_activation_count": int(limiter_summary.get("limiter_activation_count", 0)),
        "limiter_activation_fraction": _finite_float(limiter_summary.get("limiter_activation_fraction", 0.0)),
        "limiter_activation_gate_pass": not bool(limiter_summary.get("validation_blocked_by_limiter_activation", False)),
        "runtime_s": _finite_float(runtime_s),
    }


def _metadata(
    spec: Step119RunSpec,
    tau_report: Dict[str, Any],
    skipped: bool,
    runtime_s: float,
    stop_reason: Optional[str],
) -> Dict[str, Any]:
    return {
        "step": 119,
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_shape": [int(spec.nx), int(spec.ny), int(spec.nz)],
        "requested_n_steps": spec.requested_steps(),
        "steps_configured": int(spec.n_steps),
        "output_interval": int(spec.output_interval),
        "artifact_scope_note": spec.artifact_scope_note,
        "step119_schema_version": STEP119_SCHEMA_VERSION,
        "synthetic_diagnostic_mode": False,
        "fluid_only": True,
        "full_fsi_rerun_done": False,
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "official_mesh_or_case_used": False,
        "validation_claim_allowed": False,
        "step120_quasi2d_allowed": False,
        "simulation_backed_artifact": bool(not skipped),
        "runtime_s": _finite_float(runtime_s),
        "stop_reason": stop_reason,
        "checkpoint_every": int(spec.checkpoint_every),
        "stop_on_first_failure": bool(spec.stop_on_first_failure),
        "max_wall_seconds": spec.max_wall_seconds,
        "tau_feasibility_report": tau_report,
    }


def _boundary_report(spec: Step119RunSpec) -> Dict[str, Any]:
    return {
        "step": 119,
        "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "regularized_limited_boundary_used": spec.open_boundary_semantics == "regularized_velocity_pressure_limited",
        "convective_outlet_used": spec.open_boundary_semantics == "convective_pressure_outlet_experimental",
        "all_population_equilibrium_reset_used": spec.open_boundary_semantics == "equilibrium_all_population_reset",
        "open_boundary_limiter_enabled": bool(spec.open_boundary_limiter_enabled),
        "open_boundary_rho_min": float(spec.open_boundary_rho_min),
        "open_boundary_rho_max": float(spec.open_boundary_rho_max),
        "open_boundary_u_max": float(spec.open_boundary_u_max),
        "open_boundary_noneq_cap": float(spec.open_boundary_noneq_cap),
        "open_boundary_population_floor": spec.open_boundary_population_floor,
        "implemented_axis": "x",
        "pressure_outlet_density": float(spec.outlet_rho),
        "velocity_inlet_target": [float(spec.inlet_u_lbm), 0.0, 0.0],
        "boundary_condition_equivalence_claim_allowed": False,
        "validation_claim_allowed": False,
    }


def _first_failure_artifact(
    records: Sequence[Dict[str, Any]],
    spec: Step119RunSpec,
    limiter_summary: Dict[str, Any],
    reason: Optional[str] = None,
) -> Dict[str, Any]:
    detector = first_gate_failure_detector(records)
    if reason is not None and detector["first_failure_reason"] is None:
        detector["first_failure_reason"] = reason
    location_row = _first_location_record(records, detector.get("first_failure_step"))
    location = location_row.get("first_failure_location") if location_row else None
    cell = location_row.get("first_failure_cell") if location_row else None
    plane = _boundary_plane_from_location(location)
    return {
        "step": 119,
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


def _write_partial_timeseries(
    row_path: Path,
    records: Sequence[Dict[str, Any]],
    stability_records: Sequence[Dict[str, Any]],
) -> None:
    _write_timeseries(row_path / "fluid_diagnostics_timeseries.csv", records)
    _write_boundary_flux_timeseries(row_path / "boundary_flux_timeseries.csv", records)
    _write_density_drift_timeseries(row_path / "density_drift_timeseries.csv", records)
    _write_csv(row_path / "stability_diagnostics_timeseries.csv", list(stability_records), _STABILITY_TIMESERIES_FIELDS)


def _write_matrix_summary(out: Path, rows: Sequence[Dict[str, Any]], gate: Dict[str, Any]) -> Dict[str, Any]:
    rows_by_name = {row["name"]: row for row in rows}
    incomplete = [
        name
        for name in REQUIRED_ROW_NAMES
        if name not in rows_by_name or rows_by_name[name].get("requested_window_completed") is not True
    ]
    summary = {
        "step": 119,
        "step119_schema_version": STEP119_SCHEMA_VERSION,
        "simulation_backed_artifacts": any(row.get("simulation_backed_artifact", False) for row in rows),
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "full_fsi_rerun_done": False,
        "validation_claim_allowed": False,
        "required_rows": list(REQUIRED_ROW_NAMES),
        "required_validation_rows": list(REQUIRED_VALIDATION_ROW_NAMES),
        "incomplete_required_rows": incomplete,
        "step120_quasi2d_allowed": bool(gate["step120_quasi2d_allowed"]),
        "final_classification": gate["final_classification"],
        "runs": list(rows),
    }
    _write_json(out / "run_matrix_summary.json", summary)
    _write_csv(out / "run_matrix_summary.csv", list(rows), _RUN_SUMMARY_FIELDS)
    return summary


def _write_boundary_variant_comparison(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = [row for row in rows if row.get("steps_completed", 0) > 0]
    ranked = sorted(
        candidates,
        key=lambda row: (
            0 if row.get("finite_pass") else 1,
            abs(float(row.get("mass_total_delta_rel_final") or 1.0e9)),
            float(row.get("flux_imbalance_rel_tail_mean") or row.get("flux_imbalance_rel_final") or 1.0e9),
        ),
    )
    best = ranked[0] if ranked else None
    new_variants = [
        row
        for row in rows
        if row.get("lbm_open_boundary_semantics")
        in {"regularized_velocity_pressure_limited", "convective_pressure_outlet_experimental"}
        and row.get("requested_window_completed") is True
    ]
    improved_48 = any(
        row.get("requested_nx") == 48
        and row.get("step119_validation_claimed") is True
        and float(row.get("flux_imbalance_rel_tail_mean") or 1.0e9) < 0.1
        and abs(float(row.get("mass_total_delta_rel_final") or 1.0e9)) < 0.005
        for row in new_variants
    )
    comparison = {
        "step": 119,
        "comparison_scope": "real non-synthetic Step119 LBM boundary repair validation",
        "best_boundary_semantics": None if best is None else best["lbm_open_boundary_semantics"],
        "best_row_name": None if best is None else best["name"],
        "candidate_rows": list(rows),
        "legacy_reference_present": any(row["lbm_open_boundary_semantics"] == "equilibrium_all_population_reset" for row in rows),
        "regularized_reference_present": any(row["lbm_open_boundary_semantics"] == "regularized_velocity_pressure" for row in rows),
        "limited_variant_present": any(row["lbm_open_boundary_semantics"] == "regularized_velocity_pressure_limited" for row in rows),
        "convective_variant_present": any(row["lbm_open_boundary_semantics"] == "convective_pressure_outlet_experimental" for row in rows),
        "limited_or_convective_variant_improved_48": improved_48,
        "validation_claim_allowed": False,
    }
    _write_json(out / "boundary_variant_real_run_comparison.json", comparison)
    return comparison


def _write_limiter_activation_summary(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    row_summaries = [
        {
            "name": row["name"],
            "lbm_open_boundary_semantics": row["lbm_open_boundary_semantics"],
            "open_boundary_limiter_enabled": bool(row.get("open_boundary_limiter_enabled", False)),
            "limiter_activation_count": int(row.get("limiter_activation_count", 0) or 0),
            "limiter_activation_fraction": _finite_float(row.get("limiter_activation_fraction", 0.0) or 0.0),
            "limiter_activation_gate_pass": bool(row.get("limiter_activation_gate_pass", True)),
        }
        for row in rows
    ]
    total_count = sum(item["limiter_activation_count"] for item in row_summaries)
    max_fraction = max([item["limiter_activation_fraction"] for item in row_summaries] or [0.0])
    blocked = bool(max_fraction > LIMITER_ACTIVATION_FRACTION_LIMIT)
    summary = {
        "step": 119,
        "row_summaries": row_summaries,
        "total_limiter_activation_count": int(total_count),
        "max_limiter_activation_fraction": _finite_float(max_fraction),
        "limiter_activation_fraction_limit": LIMITER_ACTIVATION_FRACTION_LIMIT,
        "validation_blocked_by_limiter_activation": blocked,
        "validation_claim_allowed": False,
    }
    _write_json(out / "limiter_activation_summary.json", summary)
    return summary


def _write_step119_gate_report(out: Path, rows: Sequence[Dict[str, Any]], limiter_summary: Dict[str, Any]) -> Dict[str, Any]:
    gate = build_step119_gate_report(rows, limiter_summary)
    _write_json(out / "step119_gate_report.json", gate)
    return gate


def _write_global_first_failure(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    failures = [
        {
            "name": row["name"],
            "first_failure_step": row.get("first_failure_step"),
            "first_failure_reason": row.get("first_failure_reason"),
            "lbm_open_boundary_semantics": row["lbm_open_boundary_semantics"],
        }
        for row in rows
    ]
    finite_failures = [item for item in failures if item["first_failure_step"] is not None]
    first_step = None
    first_reason = None
    if finite_failures:
        finite_failures.sort(key=lambda item: int(item["first_failure_step"]))
        first_step = finite_failures[0]["first_failure_step"]
        first_reason = finite_failures[0]["first_failure_reason"]
    report = {
        "step": 119,
        "row_first_failures": failures,
        "first_failure_detector": {
            "record_count": len(failures),
            "first_failure_step": first_step,
            "first_failure_reason": first_reason,
        },
        "validation_claim_allowed": False,
    }
    _write_json(out / "first_failure_global_summary.json", report)
    return report


def _write_solver_report(
    out: Path,
    rows: Sequence[Dict[str, Any]],
    comparison: Dict[str, Any],
    first_failure: Dict[str, Any],
    limiter_summary: Dict[str, Any],
    gate: Dict[str, Any],
    summary: Dict[str, Any],
) -> None:
    _write_json(
        out / "solver_report.json",
        {
            "step": 119,
            "step_name": "LBM boundary repair real-run validation",
            "step119_schema_version": STEP119_SCHEMA_VERSION,
            "simulation_backed_artifacts": summary["simulation_backed_artifacts"],
            "fluent_validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
            "full_fsi_rerun_done": False,
            "official_mesh_or_case_used": False,
            "validation_claim_allowed": False,
            "step120_quasi2d_allowed": bool(gate["step120_quasi2d_allowed"]),
            "final_classification": gate["final_classification"],
            "incomplete_required_rows": gate["incomplete_required_rows"],
            "boundary_variant_real_run_comparison": comparison,
            "first_failure_global_summary": first_failure,
            "limiter_activation_summary": limiter_summary,
            "step119_gate_report": gate,
            "answers": {
                "step117_instability_location_identified_on_real_rows": first_failure["first_failure_detector"]["first_failure_step"] is not None,
                "limited_or_convective_variant_improved_48": comparison["limited_or_convective_variant_improved_48"],
                "best_boundary_completed_96_duct_only": _row_claimed(rows, "duct_only_96_regularized_limited_boundary_1000step_real")
                or _row_claimed(rows, "duct_only_96_convective_outlet_boundary_1000step_real"),
                "best_boundary_completed_96_static_two_flap": _row_claimed(rows, "static_two_flap_96_best_boundary_1000step_real"),
                "step120_quasi2d_allowed": bool(gate["step120_quasi2d_allowed"]),
            },
            "remaining_gaps": _remaining_gaps(gate),
        },
    )


def _write_output_readme(out: Path, rows: Sequence[Dict[str, Any]], gate: Dict[str, Any]) -> None:
    lines = [
        "# Step119 LBM Boundary Repair Real-Run Validation Artifacts",
        "",
        "Generated by `experiments/steps/step119_lbm_boundary_repair_real_run_validation.py`.",
        "Rows are recorded with `synthetic_diagnostic_mode=false`; large rows that were not executed are explicit incomplete real-run targets.",
        "These artifacts do not claim Fluent validation, Figure 29.3 parity, quasi-2D readiness, or full FSI validation.",
        "",
        f"Final classification: `{gate['final_classification']}`",
        f"Step120 quasi-2D allowed: `{gate['step120_quasi2d_allowed']}`",
        "",
        "Rows:",
    ]
    for row in rows:
        lines.append(
            f"- `{row['name']}`: semantics={row['lbm_open_boundary_semantics']}, "
            f"steps_completed={row['steps_completed']}, requested_window_completed={row['requested_window_completed']}, "
            f"synthetic={row['synthetic_diagnostic_mode']}, first_failure={row.get('first_failure_reason')}"
        )
    lines.append("")
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _large_real_row_requires_allowance(spec: Step119RunSpec) -> bool:
    return bool(spec.requested_grid() >= 48 or spec.requested_steps() >= 100)


def _empty_first_failure(reason: Optional[str]) -> Dict[str, Any]:
    return {
        "record_count": 0,
        "all_records_finite": True,
        "first_nonfinite_step": None,
        "first_negative_density_step": None,
        "first_high_density_step": None,
        "first_mass_drift_step": None,
        "first_max_v_step": None,
        "first_failure_step": None,
        "first_failure_reason": reason,
    }


def _first_location_record(records: Sequence[Dict[str, Any]], first_failure_step: Optional[int]) -> Optional[Dict[str, Any]]:
    if not records:
        return None
    if first_failure_step is not None:
        for record in records:
            if int(record.get("step", -1)) == int(first_failure_step):
                return record
    for record in records:
        if record.get("first_failure_location") is not None:
            return record
    return records[-1]


def _boundary_plane_from_location(location: Optional[str]) -> Optional[str]:
    if location is None:
        return None
    if location == "inlet":
        return "x_min"
    if location == "outlet":
        return "x_max"
    if location == "wall_or_open_boundary_corner":
        return "wall_open_boundary_corner"
    return str(location)


def _tail_value(records: Sequence[Dict[str, Any]], key: str, default: Any) -> Any:
    if not records:
        return default
    return records[-1].get(key, default)


def _row_claimed(rows: Sequence[Dict[str, Any]], name: str) -> bool:
    for row in rows:
        if row["name"] == name:
            return bool(row.get("step119_validation_claimed") is True)
    return False


def _remaining_gaps(gate: Dict[str, Any]) -> List[str]:
    gaps = []
    if gate["incomplete_required_rows"]:
        gaps.append("Required Step119 real long-window rows remain incomplete")
    if not gate["step120_quasi2d_allowed"]:
        gaps.append("Step119 quasi-2D remains blocked until real 48^3/96^3 duct-only and static two-flap gates pass")
    gaps.extend(
        [
            "No Fluent validation is claimed",
            "No full FSI validation is claimed",
            "No official mesh/case reproduction is claimed",
        ]
    )
    return gaps


def _write_static_placeholder_reports(row_path: Path, reason: str) -> None:
    payload = {
        "static_flap_fluid_only": True,
        "full_fsi_rerun_done": False,
        "skipped": True,
        "skipped_reason": reason,
        "validation_claim_allowed": False,
    }
    _write_json(row_path / "flap_region_flow_summary.json", payload)
    _write_json(row_path / "throat_speed_summary.json", payload)
    _write_json(row_path / "recirculation_proxy_summary.json", payload)


def _row_complete(row_dir: Path) -> bool:
    return (row_dir / "finite_stability_report.json").is_file()


def _replace_spec(spec: Step119RunSpec, **updates: Any) -> Step119RunSpec:
    data = asdict(spec)
    data.update(updates)
    return Step119RunSpec(**data)


def _spec_value(spec: Step119RunSpec | Dict[str, Any], key: str, default: Any) -> Any:
    if isinstance(spec, dict):
        return spec.get(key, default)
    return getattr(spec, key, default)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Step119 real LBM boundary repair validation rows.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--row", action="append", dest="rows", help="Run only the named row; repeatable.")
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--output-interval", type=int, default=None)
    parser.add_argument("--stop-on-first-failure", action="store_true", default=None)
    parser.add_argument("--no-stop-on-first-failure", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=None)
    parser.add_argument("--max-wall-seconds", type=float, default=None)
    parser.add_argument("--allow-large-real-rows", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    stop_on_first_failure = args.stop_on_first_failure
    if args.no_stop_on_first_failure:
        stop_on_first_failure = False
    run_step119_matrix(
        args.output_dir,
        force=args.force,
        resume=bool(args.resume and not args.no_resume),
        row_names=args.rows,
        max_rows=args.max_rows,
        output_interval=args.output_interval,
        stop_on_first_failure=stop_on_first_failure,
        checkpoint_every=args.checkpoint_every,
        max_wall_seconds=args.max_wall_seconds,
        allow_large_real_rows=args.allow_large_real_rows,
    )
    return 0


_STABILITY_TIMESERIES_FIELDS = [
    "step",
    "f_min",
    "f_max",
    "F_min",
    "F_max",
    "negative_population_count",
    "negative_population_fraction",
    "boundary_x_min_negative_population_count",
    "boundary_x_max_negative_population_count",
    "rho_below_low_count",
    "rho_above_high_count",
    "velocity_outlier_count",
    "first_failure_location",
    "stability_all_finite",
]

_RUN_SUMMARY_FIELDS = [
    "name",
    "geometry_mode",
    "lbm_open_boundary_semantics",
    "open_boundary_limiter_enabled",
    "requested_nx",
    "executed_nx",
    "requested_n_steps",
    "steps_completed",
    "requested_window_completed",
    "finite_pass",
    "density_gate_pass",
    "mass_drift_gate_pass",
    "population_gate_pass",
    "mach_gate_pass",
    "first_failure_step",
    "first_failure_reason",
    "flux_balance_reported",
    "flux_imbalance_rel_final",
    "flux_imbalance_rel_tail_mean",
    "mass_total_delta_rel_final",
    "mach_proxy_observed_max",
    "skipped_due_to_tau_margin",
    "tau_margin_pass",
    "synthetic_diagnostic_mode",
    "simulation_backed_artifact",
    "row_source",
    "step119_schema_version",
    "step119_validation_claimed",
    "not_used_for_validation",
    "limiter_activation_count",
    "limiter_activation_fraction",
    "limiter_activation_gate_pass",
    "runtime_s",
]


if __name__ == "__main__":
    raise SystemExit(main())
