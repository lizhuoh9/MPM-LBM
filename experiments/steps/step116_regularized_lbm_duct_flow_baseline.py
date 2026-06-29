from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
import taichi as ti

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import (
    centerline_profile_x,
    fluid_mask,
    outlet_reflection_proxy,
    summarize_lbm_boundary_diagnostics,
)
from src.mpm_lbm.sim.lbm.config import LBMConfig
from src.mpm_lbm.sim.lbm.fluid import UNKNOWN_X_MAX_POPULATIONS, UNKNOWN_X_MIN_POPULATIONS, LBMFluid3D
from src.mpm_lbm.sim.lbm.relaxation_semantics import (
    LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
    STANDARD_LATTICE_KINEMATIC_VISCOSITY,
    tau_from_lattice_kinematic_viscosity,
    tau_from_legacy_external_solver_parameter,
)


DEFAULT_OUTPUT_DIR = REPO_ROOT / "outputs" / "step116_regularized_lbm_duct_flow_baseline"
CS_LBM = math.sqrt(1.0 / 3.0)


@dataclass(frozen=True)
class Step116RunSpec:
    name: str
    nx: int
    ny: int
    nz: int
    n_steps: int
    output_interval: int
    open_boundary_semantics: str
    geometry_mode: str
    inlet_u_lbm: float = 0.02
    outlet_rho: float = 1.0
    niu: float = 0.1
    lbm_viscosity_semantics: str = "legacy_external"
    lbm_tau_stability_policy: str = "report_only"
    lbm_min_tau_margin: float = 1.0e-4
    fluid_kinematic_viscosity_m2_s: float = 1.5e-5
    physical_duct_length_m: float = 0.1
    lbm_dt_phys_override_s: Optional[float] = None
    target_inlet_velocity_mps: Optional[float] = None
    target_reynolds_number: Optional[float] = None
    requested_nx: Optional[int] = None
    requested_n_steps: Optional[int] = None
    artifact_scope_note: str = "simulation-backed Step116 LBM-only baseline"

    def requested_grid(self) -> int:
        return int(self.requested_nx if self.requested_nx is not None else self.nx)

    def requested_steps(self) -> int:
        return int(self.requested_n_steps if self.requested_n_steps is not None else self.n_steps)


def default_committed_specs() -> List[Step116RunSpec]:
    return [
        Step116RunSpec(
            name="duct_only_48_legacy_boundary_500step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=5,
            open_boundary_semantics="equilibrium_all_population_reset",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            artifact_scope_note="bounded committed proxy for requested 48^3 legacy 500-step window",
        ),
        Step116RunSpec(
            name="duct_only_48_regularized_boundary_500step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=5,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            requested_nx=48,
            requested_n_steps=500,
            artifact_scope_note="bounded committed proxy for requested 48^3 regularized 500-step window",
        ),
        Step116RunSpec(
            name="duct_only_96_regularized_boundary_1000step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=5,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            requested_nx=96,
            requested_n_steps=1000,
            artifact_scope_note="bounded committed proxy; full requested 96^3/1000 row is supported but not committed",
        ),
        Step116RunSpec(
            name="duct_only_96_regularized_boundary_physical_nu_report_only_100step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=5,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="duct_only",
            lbm_viscosity_semantics="physical_nu_mapping",
            lbm_tau_stability_policy="report_only",
            lbm_dt_phys_override_s=2.0833333333333334e-6,
            target_inlet_velocity_mps=10.0,
            target_reynolds_number=26666.666666666668,
            requested_nx=96,
            requested_n_steps=100,
            artifact_scope_note="report-only physical-nu risk row; reduced committed grid avoids large 96^3 payload",
        ),
        Step116RunSpec(
            name="static_two_flap_96_regularized_1000step",
            nx=8,
            ny=6,
            nz=6,
            n_steps=5,
            output_interval=5,
            open_boundary_semantics="regularized_velocity_pressure",
            geometry_mode="static_two_flap",
            requested_nx=96,
            requested_n_steps=1000,
            artifact_scope_note="bounded static-flap fluid-only row; not FSI and not Figure 29.3 parity",
        ),
    ]


def run_step116_matrix(
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    specs: Optional[Sequence[Step116RunSpec]] = None,
    force: bool = False,
    resume: bool = True,
) -> Dict[str, Any]:
    _ensure_taichi()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    run_specs = list(specs) if specs is not None else default_committed_specs()
    rows = []
    for index, spec in enumerate(run_specs):
        row_dir = out / spec.name
        if resume and not force and _row_complete(row_dir):
            rows.append(_read_json(row_dir / "finite_stability_report.json")["summary_row"])
        else:
            rows.append(run_step116_row(spec, row_dir))
        if index + 1 < len(run_specs):
            ti.reset()
            _ensure_taichi()
    summary = _write_matrix_summary(out, rows)
    _write_solver_report(out, rows)
    return summary


def run_step116_row(spec: Step116RunSpec, row_dir: Path | str) -> Dict[str, Any]:
    row_path = Path(row_dir)
    row_path.mkdir(parents=True, exist_ok=True)
    tau_report = _tau_feasibility_report(spec)
    if spec.lbm_tau_stability_policy == "strict" and not tau_report["tau_margin_pass"]:
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

    final = records[-1]
    finite = _finite_report(spec, final, records, tau_report)
    metadata = _metadata(spec, tau_report, skipped=False)
    boundary = _boundary_report(spec)
    config_report = _lbm_config_report(config, spec, tau_report)

    _write_json(row_path / "run_metadata.json", metadata)
    _write_json(row_path / "driver_config.json", config_report)
    _write_json(row_path / "duct_boundary_condition_report.json", boundary)
    _write_json(row_path / "velocity_profile_summary.json", _velocity_profile_report(lbm, spec, records))
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_timeseries(row_path / "fluid_diagnostics_timeseries.csv", records)
    _write_boundary_flux_timeseries(row_path / "boundary_flux_timeseries.csv", records)
    _write_density_drift_timeseries(row_path / "density_drift_timeseries.csv", records)
    if spec.geometry_mode == "static_two_flap":
        _write_static_flap_reports(row_path, lbm, spec, final)
    return finite["summary_row"]


def _apply_static_geometry(lbm: LBMFluid3D, spec: Step116RunSpec) -> None:
    solid = np.zeros((spec.nx, spec.ny, spec.nz), dtype=np.int8)
    solid[:, 0, :] = 1
    solid[:, spec.ny - 1, :] = 1
    solid[:, :, 0] = 1
    solid[:, :, spec.nz - 1] = 1
    if spec.geometry_mode == "static_two_flap":
        x0 = max(1, spec.nx // 2 - max(1, spec.nx // 48))
        x1 = min(spec.nx - 1, x0 + max(1, spec.nx // 32))
        lower_end = max(2, spec.ny // 3)
        upper_start = min(spec.ny - 2, (2 * spec.ny) // 3)
        solid[x0:x1, 1:lower_end, 1 : spec.nz - 1] = 1
        solid[x0:x1, upper_start : spec.ny - 1, 1 : spec.nz - 1] = 1
    if spec.geometry_mode not in ("duct_only", "static_two_flap"):
        raise ValueError(f"unsupported Step116 geometry_mode: {spec.geometry_mode}")
    lbm.solid.from_numpy(solid)
    lbm.copy_solid_to_static()


def _tau_feasibility_report(spec: Step116RunSpec) -> Dict[str, Any]:
    if spec.lbm_viscosity_semantics == "legacy_external":
        tau = tau_from_legacy_external_solver_parameter(spec.niu)
        tau_minus_half = float(tau) - 0.5
        return {
            "lbm_viscosity_semantics": spec.lbm_viscosity_semantics,
            "lbm_relaxation_semantics": LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER,
            "lbm_niu": float(spec.niu),
            "tau": float(tau),
            "tau_minus_half": tau_minus_half,
            "lbm_min_tau_margin": float(spec.lbm_min_tau_margin),
            "lbm_tau_stability_policy": spec.lbm_tau_stability_policy,
            "tau_margin_pass": bool(tau_minus_half >= float(spec.lbm_min_tau_margin)),
            "mach_proxy": abs(float(spec.inlet_u_lbm)) / CS_LBM,
            "reynolds_from_config": None,
            "target_reynolds_number": None,
            "target_reynolds_match": None,
            "physical_reynolds_direct_simulation_feasible_with_current_lbm": None,
        }
    if spec.lbm_viscosity_semantics != "physical_nu_mapping":
        raise ValueError(f"unsupported lbm_viscosity_semantics: {spec.lbm_viscosity_semantics}")
    dt = float(spec.lbm_dt_phys_override_s if spec.lbm_dt_phys_override_s is not None else 1.0)
    dx = float(spec.physical_duct_length_m) / float(spec.requested_grid())
    nu_lbm = float(spec.fluid_kinematic_viscosity_m2_s) * dt / (dx * dx)
    tau = tau_from_lattice_kinematic_viscosity(nu_lbm)
    tau_minus_half = float(tau) - 0.5
    reynolds = None
    if spec.target_inlet_velocity_mps is not None:
        duct_height = 0.04
        reynolds = float(spec.target_inlet_velocity_mps) * duct_height / float(spec.fluid_kinematic_viscosity_m2_s)
    target_match = None
    if reynolds is not None and spec.target_reynolds_number is not None:
        target_match = bool(math.isclose(reynolds, float(spec.target_reynolds_number), rel_tol=1.0e-9, abs_tol=1.0e-9))
    tau_margin_pass = bool(tau_minus_half >= float(spec.lbm_min_tau_margin))
    return {
        "lbm_viscosity_semantics": spec.lbm_viscosity_semantics,
        "lbm_relaxation_semantics": STANDARD_LATTICE_KINEMATIC_VISCOSITY,
        "lbm_niu": float(nu_lbm),
        "tau": float(tau),
        "tau_minus_half": tau_minus_half,
        "lbm_min_tau_margin": float(spec.lbm_min_tau_margin),
        "lbm_tau_stability_policy": spec.lbm_tau_stability_policy,
        "tau_margin_pass": tau_margin_pass,
        "mach_proxy": abs(float(spec.inlet_u_lbm)) / CS_LBM,
        "reynolds_from_config": reynolds,
        "target_reynolds_number": None if spec.target_reynolds_number is None else float(spec.target_reynolds_number),
        "target_reynolds_match": target_match,
        "physical_reynolds_direct_simulation_feasible_with_current_lbm": bool(tau_margin_pass and abs(float(spec.inlet_u_lbm)) / CS_LBM <= 0.2),
        "dx_phys_m": dx,
        "dt_phys_s": dt,
        "nu_lbm": float(nu_lbm),
    }


def _finite_report(spec: Step116RunSpec, final: Dict[str, Any], records: Sequence[Dict[str, Any]], tau_report: Dict[str, Any]) -> Dict[str, Any]:
    finite_pass = bool(all(record["all_finite"] for record in records))
    density_gate_pass = bool(final["rho_min"] > 0.8 and final["rho_max"] < 1.2)
    mass_drift_gate_pass = bool(abs(final["mass_total_delta_rel"]) < 0.05)
    requested_window_completed = bool(spec.n_steps == spec.requested_steps() and spec.nx == spec.requested_grid())
    summary_row = {
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_nx": int(spec.nx),
        "requested_n_steps": spec.requested_steps(),
        "steps_completed": int(spec.n_steps),
        "requested_window_completed": requested_window_completed,
        "finite_pass": finite_pass,
        "density_gate_pass": density_gate_pass,
        "mass_drift_gate_pass": mass_drift_gate_pass,
        "flux_balance_reported": True,
        "flux_imbalance_rel_final": final["flux_imbalance_rel"],
        "mass_total_delta_rel_final": final["mass_total_delta_rel"],
        "skipped_due_to_tau_margin": False,
        "tau_margin_pass": tau_report["tau_margin_pass"],
    }
    return {
        **summary_row,
        "skipped_due_to_tau_margin": False,
        "skipped_reason": None,
        "step116_gate_pass": bool(finite_pass and density_gate_pass and mass_drift_gate_pass),
        "final_diagnostics": final,
        "tau_feasibility_report": tau_report,
        "summary_row": summary_row,
    }


def _write_skipped_row(spec: Step116RunSpec, row_path: Path, tau_report: Dict[str, Any], reason: str) -> Dict[str, Any]:
    metadata = _metadata(spec, tau_report, skipped=True)
    boundary = _boundary_report(spec)
    summary_row = {
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_nx": int(spec.nx),
        "requested_n_steps": spec.requested_steps(),
        "steps_completed": 0,
        "requested_window_completed": False,
        "finite_pass": False,
        "density_gate_pass": False,
        "mass_drift_gate_pass": False,
        "flux_balance_reported": False,
        "flux_imbalance_rel_final": None,
        "mass_total_delta_rel_final": None,
        "skipped_due_to_tau_margin": reason == "tau_margin",
        "tau_margin_pass": tau_report["tau_margin_pass"],
    }
    finite = {
        **summary_row,
        "skipped_reason": reason,
        "step116_gate_pass": False,
        "tau_feasibility_report": tau_report,
        "summary_row": summary_row,
    }
    _write_json(row_path / "run_metadata.json", metadata)
    _write_json(row_path / "driver_config.json", {"spec": asdict(spec), "tau_feasibility_report": tau_report})
    _write_json(row_path / "duct_boundary_condition_report.json", boundary)
    _write_json(row_path / "finite_stability_report.json", finite)
    _write_csv(row_path / "fluid_diagnostics_timeseries.csv", [])
    _write_csv(row_path / "boundary_flux_timeseries.csv", [])
    _write_csv(row_path / "density_drift_timeseries.csv", [])
    _write_json(row_path / "velocity_profile_summary.json", {"skipped": True, "reason": reason})
    return summary_row


def _metadata(spec: Step116RunSpec, tau_report: Dict[str, Any], skipped: bool) -> Dict[str, Any]:
    return {
        "step": 116,
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "requested_nx": spec.requested_grid(),
        "executed_shape": [int(spec.nx), int(spec.ny), int(spec.nz)],
        "requested_n_steps": spec.requested_steps(),
        "steps_configured": int(spec.n_steps),
        "artifact_scope_note": spec.artifact_scope_note,
        "simulation_backed_artifact": not skipped,
        "fluid_only": True,
        "full_fsi_rerun_done": False,
        "fluent_validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "tau_feasibility_report": tau_report,
    }


def _boundary_report(spec: Step116RunSpec) -> Dict[str, Any]:
    return {
        "lbm_boundary_condition_mode": "duct_velocity_inlet_pressure_outlet",
        "lbm_open_boundary_semantics": spec.open_boundary_semantics,
        "unknown_population_reconstruction_used": spec.open_boundary_semantics == "regularized_velocity_pressure",
        "all_population_equilibrium_reset_used": spec.open_boundary_semantics == "equilibrium_all_population_reset",
        "implemented_axis": "x",
        "unknown_x_min_populations": list(UNKNOWN_X_MIN_POPULATIONS),
        "unknown_x_max_populations": list(UNKNOWN_X_MAX_POPULATIONS),
        "pressure_outlet_density": float(spec.outlet_rho),
        "velocity_inlet_target": [float(spec.inlet_u_lbm), 0.0, 0.0],
        "boundary_condition_equivalence_claim_allowed": False,
        "validation_claim_allowed": False,
    }


def _lbm_config_report(config: LBMConfig, spec: Step116RunSpec, tau_report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "lbm_config": {
            "nx": config.nx,
            "ny": config.ny,
            "nz": config.nz,
            "niu": config.niu,
            "rho0": config.rho0,
            "relaxation_semantics": config.relaxation_semantics,
            "open_boundary_semantics": config.open_boundary_semantics,
            "bc_x_left": config.bc_x_left,
            "bc_x_right": config.bc_x_right,
            "vel_bc_x_left": list(config.vel_bc_x_left),
            "rho_bc_x_right": config.rho_bc_x_right,
            "open_boundary_mass_neutral_flux_control_enabled": bool(
                config.open_boundary_mass_neutral_flux_control_enabled
            ),
            "open_boundary_mass_neutral_flux_control_mode": config.open_boundary_mass_neutral_flux_control_mode,
            "open_boundary_mass_neutral_mass_error_gain": float(
                config.open_boundary_mass_neutral_mass_error_gain
            ),
            "open_boundary_mass_neutral_mass_error_cap": float(config.open_boundary_mass_neutral_mass_error_cap),
            "open_boundary_mass_neutral_correction_blend": float(
                config.open_boundary_mass_neutral_correction_blend
            ),
            "open_boundary_mass_neutral_reference_mass_mode": config.open_boundary_mass_neutral_reference_mass_mode,
        },
        "step116_spec": asdict(spec),
        "tau_feasibility_report": tau_report,
    }


def _velocity_profile_report(lbm: LBMFluid3D, spec: Step116RunSpec, records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    snap = {
        "rho": lbm.rho.to_numpy(),
        "v": lbm.v.to_numpy(),
        "solid": lbm.solid.to_numpy(),
    }
    return {
        "name": spec.name,
        "geometry_mode": spec.geometry_mode,
        "centerline_profile_x": centerline_profile_x(snap),
        "final_outlet_reflection_proxy": outlet_reflection_proxy(snap),
        "final_flux_imbalance_rel": records[-1]["flux_imbalance_rel"],
    }


def _write_static_flap_reports(row_path: Path, lbm: LBMFluid3D, spec: Step116RunSpec, final: Dict[str, Any]) -> None:
    snap = {"rho": lbm.rho.to_numpy(), "v": lbm.v.to_numpy(), "solid": lbm.solid.to_numpy()}
    mask = fluid_mask(snap)
    speed = np.linalg.norm(snap["v"], axis=3)
    throat_x = max(1, spec.nx // 2)
    x0 = max(0, throat_x - 1)
    x1 = min(spec.nx, throat_x + 2)
    throat_mask = mask[x0:x1, :, :]
    throat_speed = speed[x0:x1, :, :][throat_mask] if np.any(throat_mask) else np.array([0.0])
    near_flap_ux = snap["v"][x0:x1, :, :, 0][throat_mask] if np.any(throat_mask) else np.array([0.0])
    _write_json(
        row_path / "flap_region_flow_summary.json",
        {
            "static_flap_fluid_only": True,
            "full_fsi_rerun_done": False,
            "fluid_cell_count_near_flaps": int(throat_speed.size),
            "mean_speed_near_flaps": _finite_float(np.mean(throat_speed)),
            "max_speed_near_flaps": _finite_float(np.max(throat_speed)),
            "downstream_flow_reported": True,
        },
    )
    _write_json(
        row_path / "throat_speed_summary.json",
        {
            "finite_pass": bool(np.all(np.isfinite(throat_speed))),
            "throat_x_index": int(throat_x),
            "max_speed": _finite_float(np.max(throat_speed)),
            "mean_speed": _finite_float(np.mean(throat_speed)),
            "final_midplane_mean_ux": final["midplane_mean_ux"],
        },
    )
    _write_json(
        row_path / "recirculation_proxy_summary.json",
        {
            "proxy_name": "negative_ux_fraction_near_flaps",
            "negative_ux_fraction": _finite_float(np.mean(near_flap_ux < 0.0)),
            "ux_std": _finite_float(np.std(near_flap_ux)),
        },
    )


def _write_timeseries(path: Path, records: Sequence[Dict[str, Any]]) -> None:
    rows = []
    for record in records:
        rows.append({key: record[key] for key in _TIMESERIES_FIELDS})
    _write_csv(path, rows, _TIMESERIES_FIELDS)


def _write_boundary_flux_timeseries(path: Path, records: Sequence[Dict[str, Any]]) -> None:
    fields = ["step", "inlet_flux", "outlet_flux", "flux_imbalance_abs", "flux_imbalance_rel"]
    _write_csv(path, [{key: record[key] for key in fields} for record in records], fields)


def _write_density_drift_timeseries(path: Path, records: Sequence[Dict[str, Any]]) -> None:
    fields = ["step", "rho_min", "rho_max", "rho_mean", "mass_total", "mass_total_delta_from_initial", "mass_total_delta_rel"]
    _write_csv(path, [{key: record[key] for key in fields} for record in records], fields)


def _write_matrix_summary(out: Path, rows: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary = {
        "step": 116,
        "simulation_backed_artifacts": any(not row.get("skipped_due_to_tau_margin", False) for row in rows),
        "fluent_validation_claim_allowed": False,
        "full_fsi_rerun_done": False,
        "runs": list(rows),
    }
    _write_json(out / "run_matrix_summary.json", summary)
    _write_csv(out / "run_matrix_summary.csv", list(rows), _RUN_SUMMARY_FIELDS)
    return summary


def _write_solver_report(out: Path, rows: Sequence[Dict[str, Any]]) -> None:
    regularized_rows = [row for row in rows if row["lbm_open_boundary_semantics"] == "regularized_velocity_pressure"]
    legacy_rows = [row for row in rows if row["lbm_open_boundary_semantics"] == "equilibrium_all_population_reset"]
    _write_json(
        out / "solver_report.json",
        {
            "step": 116,
            "step_name": "regularized LBM duct flow baseline",
            "simulation_backed_artifacts": True,
            "regularized_velocity_pressure_used": bool(regularized_rows),
            "legacy_boundary_compared": bool(legacy_rows),
            "static_flap_fluid_only_rows": [row["name"] for row in rows if row["geometry_mode"] == "static_two_flap"],
            "fluent_validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
            "full_fsi_rerun_done": False,
            "official_mesh_or_case_used": False,
            "answers": {
                "regularized_more_stable_than_legacy": _compare_regularized_legacy(rows),
                "duct_only_48_96_long_window_finite": "bounded committed rows are finite where completed; requested full windows remain open unless requested_window_completed is true",
                "static_two_flap_finite_development": "reported by static_two_flap row artifacts, fluid-only and not FSI",
                "physical_re_direct_simulation_blocked_by_tau": any(row.get("tau_margin_pass") is False for row in rows),
                "ready_for_fluent_equivalent_fsi": False,
            },
            "remaining_gaps": [
                "committed rows are bounded fluid-only baselines, not full Fluent-length validation",
                "no quasi-2D or periodic-z semantics",
                "no conservative interface traction transfer",
                "no small-strain solid model",
                "no full FSI rerun",
            ],
        },
    )


def _compare_regularized_legacy(rows: Sequence[Dict[str, Any]]) -> str:
    regularized = [row for row in rows if row["name"].startswith("duct_only_48_regularized")]
    legacy = [row for row in rows if row["name"].startswith("duct_only_48_legacy")]
    if not regularized or not legacy:
        return "not compared"
    reg = regularized[0]
    leg = legacy[0]
    if reg["density_gate_pass"] and reg["finite_pass"] and reg["mass_total_delta_rel_final"] <= leg["mass_total_delta_rel_final"]:
        return "regularized is finite and not worse by final mass drift in this bounded committed row"
    return "not proven better; inspect committed flux and density diagnostics"


def _row_complete(row_dir: Path) -> bool:
    return (row_dir / "finite_stability_report.json").is_file()


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Optional[Sequence[str]] = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(fieldnames or (rows[0].keys() if rows else _TIMESERIES_FIELDS))
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _ensure_taichi() -> None:
    ti.init(arch=ti.cpu, cpu_max_num_threads=1)


def _finite_float(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        return 0.0
    return result


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run Step116 regularized LBM duct-flow baselines.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    run_step116_matrix(args.output_dir, force=args.force, resume=not args.no_resume)
    return 0


_TIMESERIES_FIELDS = [
    "step",
    "rho_min",
    "rho_max",
    "rho_mean",
    "mass_total",
    "mass_total_delta_from_initial",
    "mass_total_delta_rel",
    "inlet_mean_ux",
    "outlet_mean_ux",
    "midplane_mean_ux",
    "inlet_flux",
    "outlet_flux",
    "flux_imbalance_abs",
    "flux_imbalance_rel",
    "max_v",
    "mach_proxy_observed",
]

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
]


if __name__ == "__main__":
    raise SystemExit(main())
