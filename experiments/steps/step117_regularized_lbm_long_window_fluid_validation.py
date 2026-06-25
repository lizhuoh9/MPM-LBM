from __future__ import annotations

import argparse
import csv
import json
import math
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
    Step116RunSpec,
    _apply_static_geometry,
    _boundary_report,
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
from src.mpm_lbm.sim.lbm.config import LBMConfig  # noqa: E402
from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D  # noqa: E402


DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "step117_regularized_lbm_long_window_fluid_validation"
STEP117_SCHEMA_VERSION = 1
REQUIRED_ROW_NAMES = [
    "duct_only_48_legacy_boundary_500step_full",
    "duct_only_48_regularized_boundary_500step_full",
    "duct_only_96_regularized_boundary_1000step_full",
    "static_two_flap_96_regularized_1000step_full",
    "duct_only_96_regularized_boundary_physical_nu_report_only_100step_guarded",
]
VALID_COMPARISON_RESULTS = {
    "regularized_better_than_legacy_for_long_window",
    "regularized_comparable_but_not_better",
    "regularized_not_acceptable_for_long_window",
    "insufficient_completed_rows",
}


@dataclass(frozen=True)
class Step117RunSpec(Step116RunSpec):
    artifact_scope_note: str = "Step117 LBM-only long-window fluid validation row"
    step117_required_row: bool = True
    not_used_for_validation: bool = False


def step117_long_window_specs(output_interval: int = 50) -> List[Step117RunSpec]:
    return [
        Step117RunSpec(
            name="duct_only_48_legacy_boundary_500step_full",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            open_boundary_semantics="equilibrium_all_population_reset",
            geometry_mode="duct_only",
            artifact_scope_note="required Step117 48^3 legacy 500-step duct-only long-window row",
        ),
        Step117RunSpec(
            name="duct_only_48_regularized_boundary_500step_full",
            nx=48,
            ny=48,
            nz=48,
            n_steps=500,
            output_interval=output_interval,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            artifact_scope_note="required Step117 48^3 regularized 500-step duct-only long-window row",
        ),
        Step117RunSpec(
            name="duct_only_96_regularized_boundary_1000step_full",
            nx=96,
            ny=96,
            nz=96,
            n_steps=1000,
            output_interval=max(output_interval, 100),
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            artifact_scope_note="required Step117 96^3 regularized 1000-step duct-only long-window row",
        ),
        Step117RunSpec(
            name="static_two_flap_96_regularized_1000step_full",
            nx=96,
            ny=96,
            nz=96,
            n_steps=1000,
            output_interval=max(output_interval, 100),
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="static_two_flap",
            artifact_scope_note="required Step117 96^3 regularized 1000-step static two-flap fluid-only row",
        ),
        Step117RunSpec(
            name="duct_only_96_regularized_boundary_physical_nu_report_only_100step_guarded",
            nx=96,
            ny=96,
            nz=96,
            n_steps=100,
            output_interval=max(output_interval, 50),
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            lbm_viscosity_semantics="physical_nu_mapping",
            lbm_tau_stability_policy="strict",
            lbm_dt_phys_override_s=2.0833333333333334e-6,
            target_inlet_velocity_mps=10.0,
            target_reynolds_number=26666.666666666668,
            artifact_scope_note="strict tau-guarded physical-nu policy row; not used for validation",
            not_used_for_validation=True,
        ),
    ]


def run_step117_matrix(
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    specs: Optional[Sequence[Step117RunSpec]] = None,
    force: bool = False,
    resume: bool = True,
    row_names: Optional[Sequence[str]] = None,
    max_rows: Optional[int] = None,
    output_interval: Optional[int] = None,
    profile_only: bool = False,
    no_large_arrays: bool = True,
) -> Dict[str, Any]:
    if not profile_only:
        _ensure_taichi()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    default_specs_used = specs is None
    all_default_specs = step117_long_window_specs()
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
        rows.append(run_step117_row(spec, row_dir, profile_only=profile_only, no_large_arrays=no_large_arrays))

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
    comparison = _write_regularized_vs_legacy_comparison(out, rows)
    _write_reynolds_relaxed_surrogate_report(out)
    _write_solver_report(out, rows, comparison, summary)
    _write_output_readme(out, rows)
    return summary


def run_step117_row(
    spec: Step117RunSpec,
    row_dir: Path | str,
    profile_only: bool = False,
    no_large_arrays: bool = True,
) -> Dict[str, Any]:
    row_path = Path(row_dir)
    row_path.mkdir(parents=True, exist_ok=True)
    tau_report = _tau_feasibility_report(spec)
    print(f"[Step117] row={spec.name} mode={spec.geometry_mode} grid={spec.nx}x{spec.ny}x{spec.nz} steps={spec.n_steps}", flush=True)
    if profile_only:
        print(f"[Step117] row={spec.name} profile-only metadata written", flush=True)
        return _write_profile_only_row(spec, row_path, tau_report)
    if spec.lbm_tau_stability_policy == "strict" and not tau_report["tau_margin_pass"]:
        print(f"[Step117] row={spec.name} skipped before stepping: tau_margin", flush=True)
        return _write_skipped_row(spec, row_path, tau_report, "tau_margin")

    config = LBMConfig(
        nx=spec.nx,
        ny=spec.ny,
        nz=spec.nz,
        niu=float(tau_report["lbm_niu"]),
        relaxation_semantics=str(tau_report["lbm_relaxation_semantics"]),
        open_boundary_semantics=spec.open_boundary_semantics,
        bc_x_left=2,
        bc_x_right=1,
        vel_bc_x_left=(float(spec.inlet_u_lbm), 0.0, 0.0),
        rho_bc_x_right=float(spec.outlet_rho),
    )
    started = time.perf_counter()
    lbm = LBMFluid3D(config)
    _apply_static_geometry(lbm, spec)
    lbm.init_simulation()

    records = []
    mass_initial = None
    for step in range(0, int(spec.n_steps) + 1):
        if step > 0:
            lbm.step()
        if step == 0 or step == spec.n_steps or step % int(spec.output_interval) == 0:
            summary = summarize_lbm_boundary_diagnostics(lbm, step=step, mass_initial=mass_initial)
            if mass_initial is None:
                mass_initial = summary["mass_total"]
                summary = summarize_lbm_boundary_diagnostics(lbm, step=step, mass_initial=mass_initial)
            records.append(summary)
            _write_partial_timeseries(row_path, records)
            print(
                f"[Step117] row={spec.name} step={step}/{spec.n_steps} "
                f"rho=[{summary['rho_min']:.6g},{summary['rho_max']:.6g}] "
                f"mass_drift={summary['mass_total_delta_rel']:.6g} "
                f"outlet_flux={summary['outlet_flux']:.6g}",
                flush=True,
            )

    runtime_s = _finite_float(time.perf_counter() - started)
    trend = summarize_timeseries_trends(records)
    final = records[-1]
    finite = _finite_report(spec, final, records, trend, tau_report, runtime_s)
    metadata = _metadata(spec, tau_report, skipped=False, profile_only=False, runtime_s=runtime_s)
    boundary = _boundary_report(spec)
    config_report = _lbm_config_report(config, spec, tau_report)

    _write_json(row_path / "run_metadata.json", metadata)
    _write_json(row_path / "driver_config.json", config_report)
    _write_json(row_path / "duct_boundary_condition_report.json", boundary)
    if no_large_arrays:
        _write_json(row_path / "velocity_profile_summary.json", _velocity_profile_report(lbm, spec, records))
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_partial_timeseries(row_path, records)
    if spec.geometry_mode == "static_two_flap":
        _write_static_flap_reports(row_path, lbm, spec, final)
    print(f"[Step117] row={spec.name} completed runtime_s={runtime_s:.3f}", flush=True)
    return finite["summary_row"]


def _finite_report(
    spec: Step117RunSpec,
    final: Dict[str, Any],
    records: Sequence[Dict[str, Any]],
    trend: Dict[str, Any],
    tau_report: Dict[str, Any],
    runtime_s: float,
) -> Dict[str, Any]:
    finite_pass = bool(all(record["all_finite"] for record in records))
    density_range_gate_pass = bool(0.85 < trend["rho_min_global"] <= trend["rho_max_global"] < 1.15)
    density_gate_pass = density_range_gate_pass
    mass_drift_gate_pass = bool(abs(trend["mass_drift_final"]) < 0.05)
    requested_window_completed = bool(spec.n_steps == spec.requested_steps() and spec.nx == spec.requested_grid())
    flux_development_gate_pass = bool(
        abs(trend["outlet_flux_tail_mean"]) > 1.0e-10 or abs(trend["midplane_mean_ux_tail_mean"]) > 1.0e-8
    )
    outlet_reflection_proxy_gate_pass = bool(
        trend["negative_ux_fraction_tail_mean"] <= 0.5 and trend["rho_std_outlet_tail_mean"] < 0.2
    )
    long_window_gates = {
        "requested_window_completed": requested_window_completed,
        "density_range_gate_pass": density_range_gate_pass,
        "mass_drift_gate_pass": mass_drift_gate_pass,
        "flux_development_gate_pass": flux_development_gate_pass,
        "flux_imbalance_trend_reported": True,
        "outlet_reflection_proxy_gate_pass": outlet_reflection_proxy_gate_pass,
        "regularized_vs_legacy_comparison_reported": False,
    }
    step117_gate_pass = bool(
        requested_window_completed
        and finite_pass
        and density_gate_pass
        and mass_drift_gate_pass
        and flux_development_gate_pass
        and outlet_reflection_proxy_gate_pass
        and tau_report["tau_margin_pass"] is not False
    )
    summary_row = _summary_row(
        spec,
        steps_completed=spec.n_steps,
        requested_window_completed=requested_window_completed,
        finite_pass=finite_pass,
        density_gate_pass=density_gate_pass,
        mass_drift_gate_pass=mass_drift_gate_pass,
        flux_imbalance_rel_final=final["flux_imbalance_rel"],
        mass_total_delta_rel_final=final["mass_total_delta_rel"],
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=False,
        profile_only=False,
        row_source="computed",
        step117_validation_claimed=step117_gate_pass,
        runtime_s=runtime_s,
    )
    return {
        **summary_row,
        "skipped_reason": None,
        "step117_gate_pass": step117_gate_pass,
        "long_window_gates": long_window_gates,
        "timeseries_trend_summary": trend,
        "final_diagnostics": final,
        "tau_feasibility_report": tau_report,
        "physical_reynolds_direct_simulation_feasible_with_current_lbm": bool(
            tau_report.get("physical_reynolds_direct_simulation_feasible_with_current_lbm") or False
        ),
        "not_used_for_validation": bool(spec.not_used_for_validation or tau_report["tau_margin_pass"] is False),
        "summary_row": summary_row,
    }


def _write_profile_only_row(spec: Step117RunSpec, row_path: Path, tau_report: Dict[str, Any]) -> Dict[str, Any]:
    summary_row = _summary_row(
        spec,
        steps_completed=0,
        requested_window_completed=False,
        finite_pass=False,
        density_gate_pass=False,
        mass_drift_gate_pass=False,
        flux_imbalance_rel_final=None,
        mass_total_delta_rel_final=None,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=False,
        profile_only=True,
        row_source="profile_only",
        step117_validation_claimed=False,
        runtime_s=0.0,
    )
    finite = {
        **summary_row,
        "skipped_reason": "profile_only",
        "step117_gate_pass": False,
        "long_window_gates": _empty_long_window_gates(),
        "timeseries_trend_summary": _empty_trend_summary(),
        "tau_feasibility_report": tau_report,
        "physical_reynolds_direct_simulation_feasible_with_current_lbm": bool(
            tau_report.get("physical_reynolds_direct_simulation_feasible_with_current_lbm") or False
        ),
        "not_used_for_validation": True,
        "summary_row": summary_row,
    }
    _write_common_nonstepped_artifacts(spec, row_path, tau_report, finite, skipped=False, profile_only=True)
    return summary_row


def _write_skipped_row(spec: Step117RunSpec, row_path: Path, tau_report: Dict[str, Any], reason: str) -> Dict[str, Any]:
    summary_row = _summary_row(
        spec,
        steps_completed=0,
        requested_window_completed=False,
        finite_pass=False,
        density_gate_pass=False,
        mass_drift_gate_pass=False,
        flux_imbalance_rel_final=None,
        mass_total_delta_rel_final=None,
        tau_margin_pass=tau_report["tau_margin_pass"],
        skipped_due_to_tau_margin=reason == "tau_margin",
        profile_only=False,
        row_source="skipped",
        step117_validation_claimed=False,
        runtime_s=0.0,
    )
    finite = {
        **summary_row,
        "skipped_reason": reason,
        "step117_gate_pass": False,
        "long_window_gates": _empty_long_window_gates(),
        "timeseries_trend_summary": _empty_trend_summary(),
        "tau_feasibility_report": tau_report,
        "physical_reynolds_direct_simulation_feasible_with_current_lbm": False,
        "not_used_for_validation": True,
        "summary_row": summary_row,
    }
    _write_common_nonstepped_artifacts(spec, row_path, tau_report, finite, skipped=True, profile_only=False)
    return summary_row


def _write_common_nonstepped_artifacts(
    spec: Step117RunSpec,
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
    _write_partial_timeseries(row_path, [])


def _metadata(
    spec: Step117RunSpec,
    tau_report: Dict[str, Any],
    skipped: bool,
    profile_only: bool,
    runtime_s: float = 0.0,
) -> Dict[str, Any]:
    return {
        "step": 117,
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_shape": [int(spec.nx), int(spec.ny), int(spec.nz)],
        "requested_n_steps": spec.requested_steps(),
        "steps_configured": int(spec.n_steps),
        "output_interval": int(spec.output_interval),
        "artifact_scope_note": spec.artifact_scope_note,
        "long_window_schema_version": STEP117_SCHEMA_VERSION,
        "simulation_backed_artifact": bool(not skipped and not profile_only),
        "profile_only": bool(profile_only),
        "fluid_only": True,
        "full_fsi_rerun_done": False,
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "official_mesh_or_case_used": False,
        "no_large_arrays": True,
        "runtime_s": _finite_float(runtime_s),
        "tau_feasibility_report": tau_report,
    }


def _summary_row(
    spec: Step117RunSpec,
    steps_completed: int,
    requested_window_completed: bool,
    finite_pass: bool,
    density_gate_pass: bool,
    mass_drift_gate_pass: bool,
    flux_imbalance_rel_final: Optional[float],
    mass_total_delta_rel_final: Optional[float],
    tau_margin_pass: Optional[bool],
    skipped_due_to_tau_margin: bool,
    profile_only: bool,
    row_source: str,
    step117_validation_claimed: bool,
    runtime_s: float,
) -> Dict[str, Any]:
    return {
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_nx": int(spec.nx),
        "requested_n_steps": spec.requested_steps(),
        "steps_completed": int(steps_completed),
        "requested_window_completed": bool(requested_window_completed),
        "finite_pass": bool(finite_pass),
        "density_gate_pass": bool(density_gate_pass),
        "mass_drift_gate_pass": bool(mass_drift_gate_pass),
        "flux_balance_reported": not (skipped_due_to_tau_margin or profile_only),
        "flux_imbalance_rel_final": flux_imbalance_rel_final,
        "mass_total_delta_rel_final": mass_total_delta_rel_final,
        "skipped_due_to_tau_margin": bool(skipped_due_to_tau_margin),
        "tau_margin_pass": tau_margin_pass,
        "profile_only": bool(profile_only),
        "row_source": row_source,
        "long_window_schema_version": STEP117_SCHEMA_VERSION,
        "step117_validation_claimed": bool(step117_validation_claimed),
        "not_used_for_validation": bool(spec.not_used_for_validation or skipped_due_to_tau_margin or profile_only),
        "runtime_s": _finite_float(runtime_s),
    }


def _write_partial_timeseries(row_path: Path, records: Sequence[Dict[str, Any]]) -> None:
    _write_timeseries(row_path / "fluid_diagnostics_timeseries.csv", records)
    _write_boundary_flux_timeseries(row_path / "boundary_flux_timeseries.csv", records)
    _write_density_drift_timeseries(row_path / "density_drift_timeseries.csv", records)


def _write_matrix_summary(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    rows_by_name = {row["name"]: row for row in rows}
    incomplete = [
        name
        for name in REQUIRED_ROW_NAMES
        if name not in rows_by_name or rows_by_name[name].get("requested_window_completed") is not True
    ]
    validation_ready_rows = [
        "duct_only_48_regularized_boundary_500step_full",
        "duct_only_96_regularized_boundary_1000step_full",
        "static_two_flap_96_regularized_1000step_full",
    ]
    step118_quasi2d_allowed = bool(
        not incomplete
        and all(rows_by_name.get(name, {}).get("step117_validation_claimed") is True for name in validation_ready_rows)
    )
    summary = {
        "step": 117,
        "long_window_schema_version": STEP117_SCHEMA_VERSION,
        "simulation_backed_artifacts": any(
            not row.get("skipped_due_to_tau_margin", False) and not row.get("profile_only", False) for row in rows
        ),
        "fluent_validation_claim_allowed": False,
        "full_fsi_rerun_done": False,
        "required_rows": list(REQUIRED_ROW_NAMES),
        "incomplete_required_rows": incomplete,
        "step118_quasi2d_allowed": step118_quasi2d_allowed,
        "runs": list(rows),
    }
    _write_json(out / "run_matrix_summary.json", summary)
    _write_csv(out / "run_matrix_summary.csv", list(rows), _RUN_SUMMARY_FIELDS)
    return summary


def _write_regularized_vs_legacy_comparison(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    by_name = {row["name"]: row for row in rows}
    legacy = by_name.get("duct_only_48_legacy_boundary_500step_full")
    regularized = by_name.get("duct_only_48_regularized_boundary_500step_full")
    if not legacy or not regularized or not legacy.get("requested_window_completed") or not regularized.get("requested_window_completed"):
        result = "insufficient_completed_rows"
    elif not regularized.get("finite_pass") or not regularized.get("density_gate_pass") or not regularized.get("mass_drift_gate_pass"):
        result = "regularized_not_acceptable_for_long_window"
    else:
        reg_drift = abs(float(regularized.get("mass_total_delta_rel_final") or 0.0))
        leg_drift = abs(float(legacy.get("mass_total_delta_rel_final") or 0.0))
        if reg_drift < leg_drift * 0.9:
            result = "regularized_better_than_legacy_for_long_window"
        elif reg_drift <= max(leg_drift * 1.25, leg_drift + 1.0e-12):
            result = "regularized_comparable_but_not_better"
        else:
            result = "regularized_not_acceptable_for_long_window"
    comparison = {
        "step": 117,
        "comparison_result": result,
        "valid_results": sorted(VALID_COMPARISON_RESULTS),
        "legacy_row": legacy,
        "regularized_row": regularized,
        "regularized_vs_legacy_comparison_reported": True,
        "step118_quasi2d_allowed_by_comparison": result in (
            "regularized_better_than_legacy_for_long_window",
            "regularized_comparable_but_not_better",
        ),
    }
    _write_json(out / "regularized_vs_legacy_comparison.json", comparison)
    return comparison


def _write_reynolds_relaxed_surrogate_report(out: Path) -> Dict[str, Any]:
    target_re = 26666.67
    min_tau_margin = 1.0e-4
    min_safe_nu_lbm = min_tau_margin / 3.0
    report = {
        "step": 117,
        "target_reynolds_number": target_re,
        "lbm_min_tau_margin": min_tau_margin,
        "minimum_safe_nu_lbm_from_tau_margin": min_safe_nu_lbm,
        "physical_reynolds_direct_simulation_feasible_with_current_lbm": False,
        "official_like_physical_nu_not_used_for_validation": True,
        "reason": "official-like physical viscosity mapping remains too close to tau=0.5 under the current LBM policy",
        "options": [
            "increase grid resolution and revisit dt mapping",
            "change physical time-step mapping",
            "introduce a turbulence or model-form strategy",
            "accept an explicitly labeled surrogate Reynolds comparison",
        ],
    }
    _write_json(out / "reynolds_relaxed_surrogate_report.json", report)
    return report


def _write_solver_report(
    out: Path,
    rows: Sequence[Dict[str, Any]],
    comparison: Dict[str, Any],
    summary: Dict[str, Any],
) -> None:
    rows_by_name = {row["name"]: row for row in rows}
    _write_json(
        out / "solver_report.json",
        {
            "step": 117,
            "step_name": "regularized LBM long-window fluid validation",
            "long_window_schema_version": STEP117_SCHEMA_VERSION,
            "simulation_backed_artifacts": summary["simulation_backed_artifacts"],
            "fluent_validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
            "full_fsi_rerun_done": False,
            "official_mesh_or_case_used": False,
            "step118_quasi2d_allowed": bool(
                summary["step118_quasi2d_allowed"]
                and comparison["step118_quasi2d_allowed_by_comparison"]
                and not summary["incomplete_required_rows"]
            ),
            "incomplete_required_rows": summary["incomplete_required_rows"],
            "answers": {
                "duct_only_48_legacy_completed_500": _row_completed(rows_by_name, "duct_only_48_legacy_boundary_500step_full"),
                "duct_only_48_regularized_completed_500": _row_completed(
                    rows_by_name, "duct_only_48_regularized_boundary_500step_full"
                ),
                "duct_only_96_regularized_completed_1000": _row_completed(
                    rows_by_name, "duct_only_96_regularized_boundary_1000step_full"
                ),
                "static_two_flap_96_regularized_completed_1000": _row_completed(
                    rows_by_name, "static_two_flap_96_regularized_1000step_full"
                ),
                "regularized_better_than_legacy": comparison["comparison_result"],
                "physical_nu_official_like_blocked_by_tau": any(
                    row.get("tau_margin_pass") is False for row in rows if "physical_nu" in row["name"]
                ),
                "step118_quasi2d_allowed": False,
            },
            "remaining_gaps": _remaining_gaps(summary, comparison),
        },
    )


def _remaining_gaps(summary: Dict[str, Any], comparison: Dict[str, Any]) -> List[str]:
    gaps = []
    if summary["incomplete_required_rows"]:
        gaps.append("one or more required Step117 long-window rows are incomplete")
    if comparison["comparison_result"] != "regularized_better_than_legacy_for_long_window":
        gaps.append("regularized boundary is not proven better than legacy")
    gaps.extend(
        [
            "no quasi-2D or periodic-z semantics implemented",
            "no conservative interface traction transfer",
            "no small-strain solid model",
            "no full FSI rerun",
        ]
    )
    return gaps


def _write_output_readme(out: Path, rows: Sequence[Dict[str, Any]]) -> None:
    lines = [
        "# Step117 Regularized LBM Long-Window Fluid Validation Artifacts",
        "",
        "This directory is generated by `experiments/steps/step117_regularized_lbm_long_window_fluid_validation.py`.",
        "It is LBM-only evidence and does not claim Fluent validation or full FSI readiness.",
        "",
        "Rows:",
    ]
    for row in rows:
        lines.append(
            f"- `{row['name']}`: steps_completed={row['steps_completed']}, "
            f"requested_window_completed={row['requested_window_completed']}, "
            f"profile_only={row.get('profile_only', False)}, tau_margin_pass={row.get('tau_margin_pass')}"
        )
    lines.append("")
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _row_completed(rows_by_name: Dict[str, Dict[str, Any]], name: str) -> bool:
    return bool(rows_by_name.get(name, {}).get("requested_window_completed") is True)


def _row_complete(row_dir: Path) -> bool:
    return (row_dir / "finite_stability_report.json").is_file()


def _replace_output_interval(spec: Step117RunSpec, output_interval: int) -> Step117RunSpec:
    data = asdict(spec)
    data["output_interval"] = int(output_interval)
    return Step117RunSpec(**data)


def _empty_long_window_gates() -> Dict[str, bool]:
    return {
        "requested_window_completed": False,
        "density_range_gate_pass": False,
        "mass_drift_gate_pass": False,
        "flux_development_gate_pass": False,
        "flux_imbalance_trend_reported": False,
        "outlet_reflection_proxy_gate_pass": False,
        "regularized_vs_legacy_comparison_reported": False,
    }


def _empty_trend_summary() -> Dict[str, Any]:
    return {
        "record_count": 0,
        "tail_record_count": 0,
        "rho_min_global": None,
        "rho_max_global": None,
        "mass_drift_final": None,
        "mass_drift_abs_max": None,
        "flux_imbalance_rel_final": None,
        "flux_imbalance_rel_tail_mean": None,
        "outlet_flux_final": None,
        "outlet_flux_tail_mean": None,
        "midplane_mean_ux_tail_mean": None,
        "max_v_global": None,
        "mach_proxy_observed_max": None,
        "negative_ux_fraction_tail_mean": None,
        "rho_std_outlet_tail_mean": None,
    }


_RUN_SUMMARY_FIELDS = [
    "name",
    "geometry_mode",
    "lbm_open_boundary_semantics",
    "requested_nx",
    "executed_nx",
    "requested_n_steps",
    "steps_completed",
    "requested_window_completed",
    "finite_pass",
    "density_gate_pass",
    "mass_drift_gate_pass",
    "flux_balance_reported",
    "flux_imbalance_rel_final",
    "mass_total_delta_rel_final",
    "skipped_due_to_tau_margin",
    "tau_margin_pass",
    "profile_only",
    "row_source",
    "long_window_schema_version",
    "step117_validation_claimed",
    "not_used_for_validation",
    "runtime_s",
]


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Step117 LBM-only long-window fluid validation.")
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
    run_step117_matrix(
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


if __name__ == "__main__":
    raise SystemExit(main())
