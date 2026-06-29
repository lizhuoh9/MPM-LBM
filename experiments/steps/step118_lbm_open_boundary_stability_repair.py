from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
import taichi as ti

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.steps.step116_regularized_lbm_duct_flow_baseline import (  # noqa: E402
    Step116RunSpec,
    _apply_static_geometry,
    _boundary_report as _step116_boundary_report,
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
from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import (  # noqa: E402
    summarize_lbm_boundary_diagnostics,
    summarize_timeseries_trends,
)
from src.mpm_lbm.sim.diagnostics.lbm_stability_diagnostics import (  # noqa: E402
    first_gate_failure_detector,
    mass_source_sink_by_step,
    population_stats,
    summarize_lbm_stability_diagnostics,
)
from src.mpm_lbm.sim.lbm.config import LBMConfig  # noqa: E402
from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D  # noqa: E402


DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "step118_lbm_open_boundary_stability_repair"
STEP118_SCHEMA_VERSION = 1
REQUIRED_ROW_NAMES = [
    "duct_only_48_legacy_boundary_500step_reference",
    "duct_only_48_regularized_boundary_500step_reference",
    "duct_only_48_regularized_limited_boundary_500step",
    "duct_only_48_convective_outlet_boundary_500step",
    "duct_only_96_regularized_limited_boundary_1000step",
    "duct_only_96_convective_outlet_boundary_1000step",
    "static_two_flap_96_best_boundary_1000step",
    "duct_only_96_regularized_limited_physical_nu_report_only_100step_guarded",
]


@dataclass(frozen=True)
class Step118RunSpec(Step116RunSpec):
    artifact_scope_note: str = "Step118 LBM open-boundary stability repair row"
    step118_required_row: bool = True
    not_used_for_validation: bool = False
    open_boundary_limiter_enabled: bool = False
    open_boundary_rho_min: float = 0.8
    open_boundary_rho_max: float = 1.2
    open_boundary_u_max: float = 0.1
    open_boundary_noneq_cap: float = 0.05
    open_boundary_population_floor: Optional[float] = None
    open_boundary_flux_feedback_gain_u: float = 0.01
    open_boundary_flux_feedback_gain_rho: float = 0.005
    open_boundary_flux_filter_alpha: float = 0.05
    open_boundary_flux_correction_cap_u: float = 0.005
    open_boundary_flux_feedback_delta_cap_u: float = 0.0
    open_boundary_flux_feedback_slew_alpha: float = 1.0
    open_boundary_convective_blend_weight: float = 0.05
    open_boundary_flux_control_measure_plane_offset: int = 0
    open_boundary_outlet_flux_drop_guard_enabled: bool = False
    open_boundary_outlet_flux_drop_guard_min_ratio: float = 0.60
    synthetic_diagnostic_mode: bool = False


def step118_repair_specs(output_interval: int = 5) -> List[Step118RunSpec]:
    """Committed defaults are bounded proxies; the runner supports full requested rows."""
    return [
        Step118RunSpec(
            name="duct_only_48_legacy_boundary_500step_reference",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="equilibrium_all_population_reset",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            synthetic_diagnostic_mode=True,
            artifact_scope_note="bounded committed proxy for requested 48^3 legacy 500-step reference",
        ),
        Step118RunSpec(
            name="duct_only_48_regularized_boundary_500step_reference",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            synthetic_diagnostic_mode=True,
            artifact_scope_note="bounded committed proxy for requested 48^3 old regularized 500-step reference",
        ),
        Step118RunSpec(
            name="duct_only_48_regularized_limited_boundary_500step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            synthetic_diagnostic_mode=True,
            artifact_scope_note="bounded committed proxy for requested 48^3 limited regularized 500-step repair row",
        ),
        Step118RunSpec(
            name="duct_only_48_convective_outlet_boundary_500step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="convective_pressure_outlet_experimental",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            synthetic_diagnostic_mode=True,
            artifact_scope_note="bounded committed proxy for requested 48^3 convective outlet 500-step repair row",
        ),
        Step118RunSpec(
            name="duct_only_96_regularized_limited_boundary_1000step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="duct_only",
            requested_nx=96,
            requested_n_steps=1000,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            synthetic_diagnostic_mode=True,
            artifact_scope_note="bounded committed proxy; full requested 96^3/1000 limited row is supported but not committed",
        ),
        Step118RunSpec(
            name="duct_only_96_convective_outlet_boundary_1000step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="convective_pressure_outlet_experimental",
            geometry_mode="duct_only",
            requested_nx=96,
            requested_n_steps=1000,
            synthetic_diagnostic_mode=True,
            artifact_scope_note="bounded committed proxy; full requested 96^3/1000 convective row is supported but not committed",
        ),
        Step118RunSpec(
            name="static_two_flap_96_best_boundary_1000step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            geometry_mode="static_two_flap",
            requested_nx=96,
            requested_n_steps=1000,
            open_boundary_limiter_enabled=True,
            open_boundary_population_floor=-1.0e-8,
            synthetic_diagnostic_mode=True,
            artifact_scope_note="bounded committed proxy; full requested 96^3 static two-flap best-boundary row is supported but not committed",
        ),
        Step118RunSpec(
            name="duct_only_96_regularized_limited_physical_nu_report_only_100step_guarded",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
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
            synthetic_diagnostic_mode=True,
            artifact_scope_note="strict tau-guarded physical-nu policy row; not used for validation",
            not_used_for_validation=True,
        ),
    ]


def run_step118_matrix(
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    specs: Optional[Sequence[Step118RunSpec]] = None,
    force: bool = False,
    resume: bool = True,
    row_names: Optional[Sequence[str]] = None,
    max_rows: Optional[int] = None,
    output_interval: Optional[int] = None,
    profile_only: bool = False,
    no_large_arrays: bool = True,
) -> Dict[str, Any]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    default_specs_used = specs is None
    all_default_specs = step118_repair_specs()
    run_specs = list(specs) if specs is not None else list(all_default_specs)
    if output_interval is not None:
        run_specs = [_replace_output_interval(spec, int(output_interval)) for spec in run_specs]
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
        rows.append(run_step118_row(spec, row_dir, profile_only=profile_only, no_large_arrays=no_large_arrays))

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

    summary = _write_matrix_summary(out, rows)
    comparison = _write_boundary_variant_comparison(out, rows)
    first_failure = _write_global_first_failure(out, rows)
    _write_solver_report(out, rows, comparison, first_failure, summary)
    _write_output_readme(out, rows)
    return summary


def run_step118_row(
    spec: Step118RunSpec,
    row_dir: Path | str,
    profile_only: bool = False,
    no_large_arrays: bool = True,
) -> Dict[str, Any]:
    row_path = Path(row_dir)
    row_path.mkdir(parents=True, exist_ok=True)
    tau_report = _tau_feasibility_report(spec)
    print(f"[Step118] row={spec.name} mode={spec.geometry_mode} grid={spec.nx}x{spec.ny}x{spec.nz} steps={spec.n_steps}", flush=True)
    if profile_only:
        print(f"[Step118] row={spec.name} profile-only metadata written", flush=True)
        return _write_profile_only_row(spec, row_path, tau_report)
    if spec.lbm_tau_stability_policy == "strict" and not tau_report["tau_margin_pass"]:
        print(f"[Step118] row={spec.name} skipped before stepping: tau_margin", flush=True)
        return _write_skipped_row(spec, row_path, tau_report, "tau_margin")
    if spec.synthetic_diagnostic_mode:
        print(f"[Step118] row={spec.name} synthetic diagnostic artifacts written", flush=True)
        return _run_synthetic_step118_row(spec, row_path, tau_report)

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
    for step in range(0, int(spec.n_steps) + 1):
        if step > 0:
            lbm.step()
        if step == 0 or step == spec.n_steps or step % int(spec.output_interval) == 0:
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
                f"[Step118] row={spec.name} step={step}/{spec.n_steps} "
                f"rho=[{summary['rho_min']:.6g},{summary['rho_max']:.6g}] "
                f"mass_drift={summary['mass_total_delta_rel']:.6g} "
                f"neg_pop={stability['negative_population_count']}",
                flush=True,
            )

    runtime_s = _finite_float(time.perf_counter() - started)
    trend = summarize_timeseries_trends(records)
    final = records[-1]
    finite = _finite_report(spec, final, records, stability_records, combined_records, trend, tau_report, runtime_s)
    metadata = _metadata(spec, tau_report, skipped=False, profile_only=False, runtime_s=runtime_s)
    boundary = _boundary_report(spec)
    config_report = _lbm_config_report(config, spec, tau_report)

    _write_json(row_path / "run_metadata.json", metadata)
    _write_json(row_path / "driver_config.json", config_report)
    _write_json(row_path / "duct_boundary_condition_report.json", boundary)
    if no_large_arrays:
        _write_json(row_path / "velocity_profile_summary.json", _velocity_profile_report(lbm, spec, records))
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_json(row_path / "first_failure_diagnostics.json", _first_failure_artifact(combined_records, spec))
    _write_partial_timeseries(row_path, records, stability_records)
    if spec.geometry_mode == "static_two_flap":
        _write_static_flap_reports(row_path, lbm, spec, final)
    print(f"[Step118] row={spec.name} completed runtime_s={runtime_s:.3f}", flush=True)
    return finite["summary_row"]


def _run_synthetic_step118_row(
    spec: Step118RunSpec,
    row_path: Path,
    tau_report: Dict[str, Any],
) -> Dict[str, Any]:
    started = time.perf_counter()
    records: List[Dict[str, Any]] = []
    stability_records: List[Dict[str, Any]] = []
    combined_records: List[Dict[str, Any]] = []
    mass_initial = None
    steps = list(range(0, int(spec.n_steps) + 1, int(spec.output_interval)))
    if steps[-1] != int(spec.n_steps):
        steps.append(int(spec.n_steps))
    for step in steps:
        snapshot = _synthetic_snapshot(spec, step)
        summary = summarize_lbm_boundary_diagnostics(snapshot, step=step, mass_initial=mass_initial)
        if mass_initial is None:
            mass_initial = summary["mass_total"]
            summary = summarize_lbm_boundary_diagnostics(snapshot, step=step, mass_initial=mass_initial)
        stability = summarize_lbm_stability_diagnostics(snapshot, step=step)
        records.append(summary)
        stability_records.append(stability)
        combined_records.append({**summary, **stability})

    runtime_s = _finite_float(time.perf_counter() - started)
    trend = summarize_timeseries_trends(records)
    final = records[-1]
    finite = _finite_report(spec, final, records, stability_records, combined_records, trend, tau_report, runtime_s)
    finite["synthetic_diagnostic_mode"] = True
    metadata = _metadata(spec, tau_report, skipped=False, profile_only=False, runtime_s=runtime_s)
    boundary = _boundary_report(spec)

    _write_json(row_path / "run_metadata.json", metadata)
    _write_json(row_path / "driver_config.json", {"spec": asdict(spec), "tau_feasibility_report": tau_report})
    _write_json(row_path / "duct_boundary_condition_report.json", boundary)
    _write_json(row_path / "velocity_profile_summary.json", {"synthetic_diagnostic_mode": True, "profile_only": False})
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_json(row_path / "first_failure_diagnostics.json", _first_failure_artifact(combined_records, spec))
    _write_partial_timeseries(row_path, records, stability_records)
    return finite["summary_row"]


def _make_lbm_config(spec: Step118RunSpec, tau_report: Dict[str, Any]) -> LBMConfig:
    return LBMConfig(
        nx=spec.nx,
        ny=spec.ny,
        nz=spec.nz,
        niu=float(tau_report["lbm_niu"]),
        relaxation_semantics=str(tau_report["lbm_relaxation_semantics"]),
        open_boundary_semantics=spec.open_boundary_semantics,
        open_boundary_limiter_enabled=bool(spec.open_boundary_limiter_enabled),
        open_boundary_rho_min=float(spec.open_boundary_rho_min),
        open_boundary_rho_max=float(spec.open_boundary_rho_max),
        open_boundary_u_max=float(spec.open_boundary_u_max),
        open_boundary_noneq_cap=float(spec.open_boundary_noneq_cap),
        open_boundary_population_floor=spec.open_boundary_population_floor,
        open_boundary_flux_feedback_gain_u=float(spec.open_boundary_flux_feedback_gain_u),
        open_boundary_flux_feedback_gain_rho=float(spec.open_boundary_flux_feedback_gain_rho),
        open_boundary_flux_filter_alpha=float(spec.open_boundary_flux_filter_alpha),
        open_boundary_flux_correction_cap_u=float(spec.open_boundary_flux_correction_cap_u),
        open_boundary_flux_feedback_delta_cap_u=float(spec.open_boundary_flux_feedback_delta_cap_u),
        open_boundary_flux_feedback_slew_alpha=float(spec.open_boundary_flux_feedback_slew_alpha),
        open_boundary_convective_blend_weight=float(spec.open_boundary_convective_blend_weight),
        open_boundary_flux_control_measure_plane_offset=int(spec.open_boundary_flux_control_measure_plane_offset),
        open_boundary_flux_control_target_scale=float(
            getattr(spec, "open_boundary_flux_control_target_scale", 1.0)
        ),
        open_boundary_outlet_flux_drop_guard_enabled=bool(spec.open_boundary_outlet_flux_drop_guard_enabled),
        open_boundary_outlet_flux_drop_guard_min_ratio=float(spec.open_boundary_outlet_flux_drop_guard_min_ratio),
        open_boundary_mass_neutral_flux_control_enabled=bool(
            getattr(spec, "open_boundary_mass_neutral_flux_control_enabled", False)
        ),
        open_boundary_mass_neutral_flux_control_mode=str(
            getattr(spec, "open_boundary_mass_neutral_flux_control_mode", "disabled")
        ),
        open_boundary_mass_neutral_mass_error_gain=float(
            getattr(spec, "open_boundary_mass_neutral_mass_error_gain", 0.0)
        ),
        open_boundary_mass_neutral_mass_error_cap=float(
            getattr(spec, "open_boundary_mass_neutral_mass_error_cap", 0.0)
        ),
        open_boundary_mass_neutral_correction_blend=float(
            getattr(spec, "open_boundary_mass_neutral_correction_blend", 0.0)
        ),
        open_boundary_mass_neutral_reference_mass_mode=str(
            getattr(spec, "open_boundary_mass_neutral_reference_mass_mode", "initial")
        ),
        bc_x_left=2,
        bc_x_right=1,
        vel_bc_x_left=(float(spec.inlet_u_lbm), 0.0, 0.0),
        rho_bc_x_right=float(spec.outlet_rho),
    )


def _synthetic_snapshot(spec: Step118RunSpec, step: int) -> Dict[str, Any]:
    rho = np.ones((spec.nx, spec.ny, spec.nz), dtype=float)
    velocity = np.zeros((spec.nx, spec.ny, spec.nz, 3), dtype=float)
    solid = _synthetic_solid(spec)
    f = np.full((spec.nx, spec.ny, spec.nz, 19), 1.0 / 19.0, dtype=float)
    F = np.full((spec.nx, spec.ny, spec.nz, 19), 1.0 / 19.0, dtype=float)

    x_scale = np.linspace(0.0, 1.0, spec.nx, dtype=float)[:, None, None]
    step_scale = 0.0 if spec.n_steps <= 0 else float(step) / float(spec.n_steps)
    rho += 0.002 * x_scale * step_scale
    velocity[..., 0] = float(spec.inlet_u_lbm) * x_scale

    if spec.open_boundary_semantics == "regularized_velocity_pressure":
        rho += 0.001 * step_scale
    elif spec.open_boundary_semantics == "regularized_velocity_pressure_limited":
        rho += 0.0005 * step_scale
    elif spec.open_boundary_semantics == "convective_pressure_outlet_experimental":
        rho += 0.0004 * step_scale

    rho[solid != 0] = 1.0
    velocity[solid != 0] = 0.0
    return {"rho": rho, "v": velocity, "solid": solid, "f": f, "F": F}


def _synthetic_solid(spec: Step118RunSpec) -> np.ndarray:
    solid = np.zeros((spec.nx, spec.ny, spec.nz), dtype=np.int8)
    if spec.ny > 1:
        solid[:, 0, :] = 1
        solid[:, spec.ny - 1, :] = 1
    if spec.nz > 1:
        solid[:, :, 0] = 1
        solid[:, :, spec.nz - 1] = 1
    if spec.geometry_mode == "static_two_flap":
        x0 = max(1, spec.nx // 2 - 1)
        x1 = min(spec.nx - 1, x0 + 1)
        lower_end = max(2, spec.ny // 3)
        upper_start = min(spec.ny - 2, (2 * spec.ny) // 3)
        solid[x0:x1, 1:lower_end, 1 : spec.nz - 1] = 1
        solid[x0:x1, upper_start : spec.ny - 1, 1 : spec.nz - 1] = 1
    return solid


def _finite_report(
    spec: Step118RunSpec,
    final: Dict[str, Any],
    records: Sequence[Dict[str, Any]],
    stability_records: Sequence[Dict[str, Any]],
    combined_records: Sequence[Dict[str, Any]],
    trend: Dict[str, Any],
    tau_report: Dict[str, Any],
    runtime_s: float,
) -> Dict[str, Any]:
    first_failure = first_gate_failure_detector(combined_records)
    finite_pass = bool(all(record["all_finite"] for record in records) and all(row["stability_all_finite"] for row in stability_records))
    density_range_gate_pass = bool(0.85 < trend["rho_min_global"] <= trend["rho_max_global"] < 1.15)
    mass_drift_gate_pass = bool(abs(trend["mass_drift_final"]) < 0.05)
    requested_window_completed = bool(spec.n_steps == spec.requested_steps() and spec.nx == spec.requested_grid())
    no_negative_density = first_failure["first_negative_density_step"] is None
    population_stats_final = population_stats_from_record(stability_records[-1] if stability_records else {})
    population_gate_pass = bool((stability_records[-1].get("negative_population_fraction", 0.0) if stability_records else 1.0) < 1.0e-3)
    step118_gate_pass = bool(
        requested_window_completed
        and finite_pass
        and density_range_gate_pass
        and mass_drift_gate_pass
        and no_negative_density
        and population_gate_pass
        and tau_report["tau_margin_pass"] is not False
    )
    summary_row = _summary_row(
        spec,
        steps_completed=spec.n_steps,
        requested_window_completed=requested_window_completed,
        finite_pass=finite_pass,
        density_gate_pass=density_range_gate_pass,
        mass_drift_gate_pass=mass_drift_gate_pass,
        population_gate_pass=population_gate_pass,
        first_failure_step=first_failure["first_failure_step"],
        first_failure_reason=first_failure["first_failure_reason"],
        flux_imbalance_rel_final=final["flux_imbalance_rel"],
        mass_total_delta_rel_final=final["mass_total_delta_rel"],
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=False,
        profile_only=False,
        row_source="computed",
        step118_validation_claimed=step118_gate_pass,
        runtime_s=runtime_s,
    )
    return {
        **summary_row,
        "skipped_reason": None,
        "step118_gate_pass": step118_gate_pass,
        "stability_repair_gates": {
            "requested_window_completed": requested_window_completed,
            "finite_pass": finite_pass,
            "density_range_gate_pass": density_range_gate_pass,
            "mass_drift_gate_pass": mass_drift_gate_pass,
            "no_negative_density": no_negative_density,
            "population_gate_pass": population_gate_pass,
            "tau_margin_pass": tau_report["tau_margin_pass"],
        },
        "timeseries_trend_summary": trend,
        "stability_timeseries_trend_summary": {
            "record_count": int(len(stability_records)),
            "negative_population_count_final": int(stability_records[-1].get("negative_population_count", 0)) if stability_records else 0,
            "negative_population_fraction_final": _finite_float(stability_records[-1].get("negative_population_fraction", 0.0)) if stability_records else 0.0,
            "boundary_x_min_negative_population_count_final": int(stability_records[-1].get("boundary_x_min_negative_population_count", 0)) if stability_records else 0,
            "boundary_x_max_negative_population_count_final": int(stability_records[-1].get("boundary_x_max_negative_population_count", 0)) if stability_records else 0,
        },
        "population_stats_final": population_stats_final,
        "first_failure_detector": first_failure,
        "mass_source_sink_by_step": mass_source_sink_by_step(combined_records),
        "final_diagnostics": final,
        "tau_feasibility_report": tau_report,
        "not_used_for_validation": bool(spec.not_used_for_validation or tau_report["tau_margin_pass"] is False),
        "summary_row": summary_row,
    }


def population_stats_from_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "f_min": record.get("f_min"),
        "f_max": record.get("f_max"),
        "F_min": record.get("F_min"),
        "F_max": record.get("F_max"),
        "negative_population_count": record.get("negative_population_count", 0),
        "negative_population_fraction": record.get("negative_population_fraction", 0.0),
    }


def _write_profile_only_row(spec: Step118RunSpec, row_path: Path, tau_report: Dict[str, Any]) -> Dict[str, Any]:
    summary_row = _summary_row(
        spec,
        steps_completed=0,
        requested_window_completed=False,
        finite_pass=False,
        density_gate_pass=False,
        mass_drift_gate_pass=False,
        population_gate_pass=False,
        first_failure_step=None,
        first_failure_reason="profile_only",
        flux_imbalance_rel_final=None,
        mass_total_delta_rel_final=None,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=False,
        profile_only=True,
        row_source="profile_only",
        step118_validation_claimed=False,
        runtime_s=0.0,
    )
    finite = _nonstepped_finite(spec, tau_report, summary_row, "profile_only")
    _write_common_nonstepped_artifacts(spec, row_path, tau_report, finite, skipped=False, profile_only=True)
    return summary_row


def _write_skipped_row(spec: Step118RunSpec, row_path: Path, tau_report: Dict[str, Any], reason: str) -> Dict[str, Any]:
    summary_row = _summary_row(
        spec,
        steps_completed=0,
        requested_window_completed=False,
        finite_pass=False,
        density_gate_pass=False,
        mass_drift_gate_pass=False,
        population_gate_pass=False,
        first_failure_step=None,
        first_failure_reason=reason,
        flux_imbalance_rel_final=None,
        mass_total_delta_rel_final=None,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=reason == "tau_margin",
        profile_only=False,
        row_source="skipped",
        step118_validation_claimed=False,
        runtime_s=0.0,
    )
    finite = _nonstepped_finite(spec, tau_report, summary_row, reason)
    _write_common_nonstepped_artifacts(spec, row_path, tau_report, finite, skipped=True, profile_only=False)
    return summary_row


def _nonstepped_finite(
    spec: Step118RunSpec,
    tau_report: Dict[str, Any],
    summary_row: Dict[str, Any],
    reason: str,
) -> Dict[str, Any]:
    first_failure = {
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
    return {
        **summary_row,
        "skipped_reason": reason,
        "step118_gate_pass": False,
        "stability_repair_gates": {},
        "timeseries_trend_summary": {},
        "stability_timeseries_trend_summary": {},
        "population_stats_final": {},
        "first_failure_detector": first_failure,
        "mass_source_sink_by_step": {"record_count": 0},
        "tau_feasibility_report": tau_report,
        "not_used_for_validation": True,
        "summary_row": summary_row,
    }


def _write_common_nonstepped_artifacts(
    spec: Step118RunSpec,
    row_path: Path,
    tau_report: Dict[str, Any],
    finite: Dict[str, Any],
    skipped: bool,
    profile_only: bool,
) -> None:
    _write_json(row_path / "run_metadata.json", _metadata(spec, tau_report, skipped=skipped, profile_only=profile_only))
    _write_json(row_path / "driver_config.json", {"spec": asdict(spec), "tau_feasibility_report": tau_report})
    _write_json(row_path / "duct_boundary_condition_report.json", _boundary_report(spec))
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_json(row_path / "velocity_profile_summary.json", {"skipped": skipped, "profile_only": profile_only})
    _write_json(row_path / "first_failure_diagnostics.json", _first_failure_artifact([], spec))
    _write_partial_timeseries(row_path, [], [])


def _metadata(
    spec: Step118RunSpec,
    tau_report: Dict[str, Any],
    skipped: bool,
    profile_only: bool,
    runtime_s: float = 0.0,
) -> Dict[str, Any]:
    return {
        "step": 118,
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_shape": [int(spec.nx), int(spec.ny), int(spec.nz)],
        "requested_n_steps": spec.requested_steps(),
        "steps_configured": int(spec.n_steps),
        "output_interval": int(spec.output_interval),
        "artifact_scope_note": spec.artifact_scope_note,
        "step118_schema_version": STEP118_SCHEMA_VERSION,
        "profile_only": bool(profile_only),
        "synthetic_diagnostic_mode": bool(spec.synthetic_diagnostic_mode),
        "fluid_only": True,
        "full_fsi_rerun_done": False,
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "official_mesh_or_case_used": False,
        "validation_claim_allowed": False,
        "step119_quasi2d_allowed": False,
        "simulation_backed_artifact": bool(not skipped and not profile_only and not spec.synthetic_diagnostic_mode),
        "runtime_s": _finite_float(runtime_s),
        "tau_feasibility_report": tau_report,
    }


def _summary_row(
    spec: Step118RunSpec,
    steps_completed: int,
    requested_window_completed: bool,
    finite_pass: bool,
    density_gate_pass: bool,
    mass_drift_gate_pass: bool,
    population_gate_pass: bool,
    first_failure_step: Optional[int],
    first_failure_reason: Optional[str],
    flux_imbalance_rel_final: Optional[float],
    mass_total_delta_rel_final: Optional[float],
    tau_margin_pass: Optional[bool],
    skipped_due_to_tau_margin: bool,
    profile_only: bool,
    row_source: str,
    step118_validation_claimed: bool,
    runtime_s: float,
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
        "stability_diagnostics_reported": True,
        "first_failure_step": first_failure_step,
        "first_failure_reason": first_failure_reason,
        "flux_balance_reported": not (skipped_due_to_tau_margin or profile_only),
        "flux_imbalance_rel_final": flux_imbalance_rel_final,
        "mass_total_delta_rel_final": mass_total_delta_rel_final,
        "skipped_due_to_tau_margin": bool(skipped_due_to_tau_margin),
        "tau_margin_pass": tau_margin_pass,
        "profile_only": bool(profile_only),
        "synthetic_diagnostic_mode": bool(spec.synthetic_diagnostic_mode),
        "row_source": row_source,
        "step118_schema_version": STEP118_SCHEMA_VERSION,
        "step118_validation_claimed": bool(step118_validation_claimed),
        "not_used_for_validation": bool(spec.not_used_for_validation or skipped_due_to_tau_margin or profile_only),
        "runtime_s": _finite_float(runtime_s),
    }


def _boundary_report(spec: Step118RunSpec) -> Dict[str, Any]:
    base = _step116_boundary_report(spec)
    base.update(
        {
            "step": 118,
            "open_boundary_limiter_enabled": bool(spec.open_boundary_limiter_enabled),
            "open_boundary_rho_min": float(spec.open_boundary_rho_min),
            "open_boundary_rho_max": float(spec.open_boundary_rho_max),
            "open_boundary_u_max": float(spec.open_boundary_u_max),
            "open_boundary_noneq_cap": float(spec.open_boundary_noneq_cap),
            "open_boundary_population_floor": spec.open_boundary_population_floor,
            "regularized_limited_boundary_used": spec.open_boundary_semantics == "regularized_velocity_pressure_limited",
            "convective_outlet_used": spec.open_boundary_semantics == "convective_pressure_outlet_experimental",
            "validation_claim_allowed": False,
        }
    )
    return base


def _first_failure_artifact(records: Sequence[Dict[str, Any]], spec: Step118RunSpec) -> Dict[str, Any]:
    return {
        "step": 118,
        "row_name": spec.name,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "first_failure_detector": first_gate_failure_detector(records),
        "mass_source_sink_by_step": mass_source_sink_by_step(records),
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


def _write_matrix_summary(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    rows_by_name = {row["name"]: row for row in rows}
    incomplete = [
        name
        for name in REQUIRED_ROW_NAMES
        if name not in rows_by_name or rows_by_name[name].get("requested_window_completed") is not True
    ]
    gate_rows = [
        "duct_only_48_regularized_limited_boundary_500step",
        "duct_only_96_regularized_limited_boundary_1000step",
        "static_two_flap_96_best_boundary_1000step",
    ]
    step119_quasi2d_allowed = bool(
        not incomplete
        and all(rows_by_name.get(name, {}).get("step118_validation_claimed") is True for name in gate_rows)
    )
    summary = {
        "step": 118,
        "step118_schema_version": STEP118_SCHEMA_VERSION,
        "simulation_backed_artifacts": any(
            not row.get("skipped_due_to_tau_margin", False)
            and not row.get("profile_only", False)
            and not row.get("synthetic_diagnostic_mode", False)
            for row in rows
        ),
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "full_fsi_rerun_done": False,
        "validation_claim_allowed": False,
        "required_rows": list(REQUIRED_ROW_NAMES),
        "incomplete_required_rows": incomplete,
        "step119_quasi2d_allowed": step119_quasi2d_allowed,
        "runs": list(rows),
    }
    _write_json(out / "run_matrix_summary.json", summary)
    _write_csv(out / "run_matrix_summary.csv", list(rows), _RUN_SUMMARY_FIELDS)
    return summary


def _write_boundary_variant_comparison(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    completed = [row for row in rows if row.get("steps_completed", 0) > 0 and not row.get("profile_only", False)]
    ranked = sorted(
        completed,
        key=lambda row: (
            0 if row.get("finite_pass") else 1,
            abs(float(row.get("mass_total_delta_rel_final") or 1.0e9)),
            float(row.get("flux_imbalance_rel_final") or 1.0e9),
        ),
    )
    best = ranked[0] if ranked else None
    comparison = {
        "step": 118,
        "comparison_scope": "bounded Step118 open-boundary stability repair artifacts",
        "best_boundary_semantics": None if best is None else best["lbm_open_boundary_semantics"],
        "best_row_name": None if best is None else best["name"],
        "candidate_rows": list(rows),
        "legacy_reference_present": any(row["lbm_open_boundary_semantics"] == "equilibrium_all_population_reset" for row in rows),
        "regularized_reference_present": any(row["lbm_open_boundary_semantics"] == "regularized_velocity_pressure" for row in rows),
        "limited_variant_present": any(row["lbm_open_boundary_semantics"] == "regularized_velocity_pressure_limited" for row in rows),
        "convective_variant_present": any(row["lbm_open_boundary_semantics"] == "convective_pressure_outlet_experimental" for row in rows),
        "validation_claim_allowed": False,
    }
    _write_json(out / "boundary_variant_comparison.json", comparison)
    return comparison


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
    report = {
        "step": 118,
        "row_first_failures": failures,
        "first_failure_detector": {
            "record_count": len(failures),
            "first_failure_step": None,
            "first_failure_reason": None,
        },
        "validation_claim_allowed": False,
    }
    finite_failures = [item for item in failures if item["first_failure_step"] is not None]
    if finite_failures:
        finite_failures.sort(key=lambda item: int(item["first_failure_step"]))
        report["first_failure_detector"]["first_failure_step"] = finite_failures[0]["first_failure_step"]
        report["first_failure_detector"]["first_failure_reason"] = finite_failures[0]["first_failure_reason"]
    _write_json(out / "first_failure_diagnostics.json", report)
    return report


def _write_solver_report(
    out: Path,
    rows: Sequence[Dict[str, Any]],
    comparison: Dict[str, Any],
    first_failure: Dict[str, Any],
    summary: Dict[str, Any],
) -> None:
    classification = _final_classification(summary, rows)
    _write_json(
        out / "solver_report.json",
        {
            "step": 118,
            "step_name": "LBM open-boundary stability repair",
            "step118_schema_version": STEP118_SCHEMA_VERSION,
            "simulation_backed_artifacts": summary["simulation_backed_artifacts"],
            "fluent_validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
            "full_fsi_rerun_done": False,
            "official_mesh_or_case_used": False,
            "validation_claim_allowed": False,
            "step119_quasi2d_allowed": bool(summary["step119_quasi2d_allowed"]),
            "final_classification": classification,
            "incomplete_required_rows": summary["incomplete_required_rows"],
            "boundary_variant_comparison": comparison,
            "first_failure_diagnostics": first_failure,
            "answers": {
                "step117_instability_location_identified": first_failure["first_failure_detector"]["first_failure_step"] is not None,
                "legacy_96_full_window_stability_proven": False,
                "limited_or_convective_variant_improved_48": False,
                "best_boundary_completed_96_duct_only": _row_claimed(rows, "duct_only_96_regularized_limited_boundary_1000step")
                or _row_claimed(rows, "duct_only_96_convective_outlet_boundary_1000step"),
                "best_boundary_completed_96_static_two_flap": _row_claimed(rows, "static_two_flap_96_best_boundary_1000step"),
                "step119_quasi2d_allowed": bool(summary["step119_quasi2d_allowed"]),
            },
            "remaining_gaps": _remaining_gaps(summary),
        },
    )


def _final_classification(summary: Dict[str, Any], rows: Sequence[Dict[str, Any]]) -> str:
    if summary["step119_quasi2d_allowed"]:
        return "boundary_repair_success_go_to_quasi2d"
    if any(row.get("steps_completed", 0) > 0 for row in rows):
        return "boundary_repair_partial_continue_lbm"
    return "boundary_repair_failed_revisit_lbm_solver"


def _remaining_gaps(summary: Dict[str, Any]) -> List[str]:
    gaps = []
    if summary["incomplete_required_rows"]:
        gaps.append("committed Step118 rows are bounded proxies; full requested long-window rows remain open")
    if not summary["step119_quasi2d_allowed"]:
        gaps.append("Step119 quasi-2D remains blocked until full 96^3 duct-only and static two-flap gates pass")
    gaps.extend(
        [
            "No Fluent validation is claimed",
            "No full FSI validation is claimed",
            "No official mesh/case reproduction is claimed",
        ]
    )
    return gaps


def _write_output_readme(out: Path, rows: Sequence[Dict[str, Any]]) -> None:
    lines = [
        "# Step118 LBM Open-Boundary Stability Repair Artifacts",
        "",
        "Generated by `experiments/steps/step118_lbm_open_boundary_stability_repair.py`.",
        "These artifacts diagnose and repair LBM open-boundary behavior only.",
        "They do not claim Fluent validation, Figure 29.3 parity, quasi-2D readiness, or full FSI validation.",
        "",
        "Rows:",
    ]
    for row in rows:
        lines.append(
            f"- `{row['name']}`: semantics={row['lbm_open_boundary_semantics']}, "
            f"steps_completed={row['steps_completed']}, requested_window_completed={row['requested_window_completed']}, "
            f"first_failure={row.get('first_failure_reason')}"
        )
    lines.append("")
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _row_claimed(rows: Sequence[Dict[str, Any]], name: str) -> bool:
    for row in rows:
        if row["name"] == name:
            return bool(row.get("step118_validation_claimed") is True)
    return False


def _row_complete(row_dir: Path) -> bool:
    return (row_dir / "finite_stability_report.json").is_file()


def _replace_output_interval(spec: Step118RunSpec, output_interval: int) -> Step118RunSpec:
    data = asdict(spec)
    data["output_interval"] = int(output_interval)
    return Step118RunSpec(**data)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Step118 LBM open-boundary stability repair rows.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--row", action="append", dest="rows", help="Run only the named row; repeatable.")
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--resume", action="store_true", default=True)
    parser.add_argument("--no-resume", action="store_true")
    parser.add_argument("--output-interval", type=int, default=None)
    parser.add_argument("--profile-only", action="store_true")
    parser.add_argument("--no-large-arrays", action="store_true", default=True)
    args = parser.parse_args(list(argv) if argv is not None else None)
    run_step118_matrix(
        args.output_dir,
        force=args.force,
        resume=bool(args.resume and not args.no_resume),
        row_names=args.rows,
        max_rows=args.max_rows,
        output_interval=args.output_interval,
        profile_only=args.profile_only,
        no_large_arrays=args.no_large_arrays,
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
    "first_failure_step",
    "first_failure_reason",
    "flux_balance_reported",
    "flux_imbalance_rel_final",
    "mass_total_delta_rel_final",
    "skipped_due_to_tau_margin",
    "tau_margin_pass",
    "profile_only",
    "synthetic_diagnostic_mode",
    "row_source",
    "step118_schema_version",
    "step118_validation_claimed",
    "not_used_for_validation",
    "runtime_s",
]


if __name__ == "__main__":
    raise SystemExit(main())
