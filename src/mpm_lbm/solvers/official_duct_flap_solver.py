from __future__ import annotations

import math
import shutil
from pathlib import Path
from typing import Any

import numpy as np

from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

from .official_duct_flap_config import (
    build_step155_fsi_driver_config,
    load_compiled_case,
    validate_compiled_case_for_step155,
    write_generated_geometry_config,
)
from .official_duct_flap_io import display_path, load_npz, read_json, resolve_repo_path, write_csv, write_json


STEP = 155
DEFAULT_OUTPUT_DIR = Path("outputs") / "step155_official_tutorial_solver_v1"
DEFAULT_RAW_OUTPUT_DIR = Path("outputs") / "tmp" / "step155_official_tutorial_solver_v1_driver_raw"

SOLVER_TIMESERIES_FIELDS = [
    "step",
    "time_s",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "fluid_mean_ux",
    "projection_zone_fluid_mean_ux",
    "far_field_fluid_mean_ux",
    "solid_mean_vx_norm",
    "mpm_min_J",
    "mpm_max_speed",
    "projected_mass",
    "active_cell_count",
    "cell_force_max_norm",
    "hydro_force_max_norm",
    "bb_link_count",
    "bb_max_correction",
    "mb_subcycle_force_sample_count",
    "mb_subcycle_force_accum_norm_max",
    "mb_subcycle_force_mean_norm_max",
    "active_reaction_particle_count",
    "max_grid_reaction_norm",
]
SOLVER_MONITOR_FIELDS = [
    "time_s",
    "step",
    "flap_tip_total_displacement_m",
    "flap_tip_x_displacement_m",
    "flap_tip_y_displacement_m",
    "flap_tip_velocity_m_per_s",
    "official_point_like_total_displacement_m",
    "official_point_like_x_displacement_m",
    "official_point_like_y_displacement_m",
    "official_point_like_z_displacement_m",
    "official_point_like_particle_count",
    "fluid_force_x_n",
    "fluid_force_y_n",
    "fluid_force_magnitude_n",
]
SOLVER_FORCE_FIELDS = [
    "time_s",
    "step",
    "fluid_force_x_n",
    "fluid_force_y_n",
    "fluid_force_magnitude_n",
    "force_proxy_source",
    "force_is_direct_fluent_wall_integral",
]
STABILITY_FIELDS = [
    "step",
    "time_s",
    "rho_min",
    "rho_max",
    "rho_finite",
    "velocity_finite",
    "population_finite",
    "lbm_max_v",
    "mpm_min_J",
    "mpm_max_speed",
    "density_gate_pass_step",
    "mpm_j_gate_pass_step",
    "finite_gate_pass_step",
]
MASS_FLUX_FIELDS = [
    "step",
    "time_s",
    "total_fluid_mass",
    "mass_delta_rel",
    "inlet_flux",
    "outlet_flux",
    "midplane_flux",
    "flux_imbalance_rel",
    "outlet_to_inlet_flux_ratio",
    "midplane_to_inlet_flux_ratio",
]


def run_official_tutorial_solver_v1(
    compiled_case_path: Path | str,
    output_dir: Path | str,
    raw_output_dir: Path | str | None = None,
    force: bool = False,
    n_particles: int = 1024,
    target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0),
    snapshot_interval: int = 5,
    monitor_interval: int = 1,
    allow_test_grid_override: bool = False,
    test_grid: int | None = None,
    test_n_steps: int | None = None,
) -> dict[str, Any]:
    compiled_case_path = resolve_repo_path(compiled_case_path)
    output_dir = Path(output_dir)
    raw_dir = Path(raw_output_dir) if raw_output_dir is not None else DEFAULT_RAW_OUTPUT_DIR
    if force:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    try:
        compiled_case = load_compiled_case(compiled_case_path)
        validate_compiled_case_for_step155(compiled_case)
        compiled_case = _compiled_case_with_test_overrides(
            compiled_case,
            allow_test_grid_override=allow_test_grid_override,
            test_grid=test_grid,
            test_n_steps=test_n_steps,
        )
        geometry_config_path = write_generated_geometry_config(compiled_case, output_dir, n_particles)
        config = build_step155_fsi_driver_config(
            compiled_case,
            geometry_config_path,
            n_particles=n_particles,
            target_u_lbm=target_u_lbm,
            monitor_interval=monitor_interval,
        )
        write_json(output_dir / "compiled_case_consumed.json", compiled_case)
        write_json(output_dir / "solver_driver_config.json", config.to_dict())
        masks = _load_and_validate_masks(compiled_case, config.n_grid)
        geometry_report = _write_case_to_driver_geometry_report(
            compiled_case_path,
            output_dir,
            geometry_config_path,
            masks,
        )
        unit_report = _write_unit_mapping_report(output_dir, compiled_case, config)
        manifest = _write_manifest(output_dir, compiled_case_path, geometry_config_path, config, snapshot_interval, monitor_interval)

        driver = FSIDriver3D(config, out_dir=str(raw_dir))
        capture = run_driver_with_step155_capture(
            driver,
            compiled_case,
            output_dir,
            snapshot_interval=snapshot_interval,
            masks=masks,
        )
        boundary_report = _write_boundary_semantics_runtime_report(output_dir, raw_dir)
        physics_gap = _write_physics_gap_report(output_dir, config)
        summary = _success_summary(
            compiled_case=compiled_case,
            config=config,
            output_dir=output_dir,
            manifest=manifest,
            geometry_report=geometry_report,
            unit_report=unit_report,
            boundary_report=boundary_report,
            physics_gap=physics_gap,
            capture=capture,
        )
        write_json(output_dir / "solver_v1_summary.json", summary)
        _write_report(output_dir, summary)
        return summary
    except Exception as exc:
        summary = _failure_summary(exc)
        write_json(output_dir / "solver_v1_summary.json", summary)
        _write_report(output_dir, summary)
        raise


def run_driver_with_step155_capture(
    driver: FSIDriver3D,
    compiled_case: dict[str, Any],
    output_dir: Path | str,
    snapshot_interval: int,
    masks: dict[str, dict[str, np.ndarray]] | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    snapshot_dir = output_dir / "velocity_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    masks = masks or _load_and_validate_masks(compiled_case, int(compiled_case["solver_grid"]["nx"]))

    driver.initialize()
    solver_rows: list[dict[str, Any]] = []
    monitor_rows: list[dict[str, Any]] = []
    force_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    mass_flux_rows: list[dict[str, Any]] = []
    snapshot_steps: list[int] = []
    previous_monitor: dict[str, Any] | None = None
    initial_mass: float | None = None

    n_steps = int(compiled_case["official_tutorial_setup"]["official_tutorial_time_steps"])
    dt_s = float(compiled_case["official_tutorial_setup"]["official_tutorial_dt_s"])
    for expected_step in range(0, n_steps + 1):
        if expected_step > 0:
            driver.step_once()
        step = int(driver.current_lbm_step)
        if step != expected_step:
            raise RuntimeError(f"driver step mismatch: expected {expected_step}, got {step}")
        diagnostics = driver.collect_diagnostics(step)
        fields = _copy_lbm_fields(driver)
        _assert_mask_shapes(masks, fields["rho"].shape)
        mass_flux_row, initial_mass = _mass_flux_row(step, dt_s, fields, masks, initial_mass)
        stability_row = _stability_row(step, dt_s, diagnostics, fields)
        solver_rows.append(_solver_row(diagnostics, dt_s))
        monitor_row, previous_monitor = _monitor_row(driver, diagnostics, dt_s, previous_monitor)
        monitor_rows.append(monitor_row)
        force_rows.append(_force_row(monitor_row))
        stability_rows.append(stability_row)
        mass_flux_rows.append(mass_flux_row)
        if step % int(snapshot_interval) == 0 or step == n_steps:
            _write_velocity_snapshot(snapshot_dir, step, dt_s, fields, compiled_case)
            snapshot_steps.append(step)

    driver.export_outputs(driver.current_lbm_step)
    driver.save_timeseries()
    write_csv(output_dir / "solver_timeseries.csv", solver_rows, SOLVER_TIMESERIES_FIELDS)
    write_csv(output_dir / "solver_monitor.csv", monitor_rows, SOLVER_MONITOR_FIELDS)
    write_csv(output_dir / "solver_force_monitor.csv", force_rows, SOLVER_FORCE_FIELDS)
    write_csv(output_dir / "stability_timeseries.csv", stability_rows, STABILITY_FIELDS)
    write_csv(output_dir / "mass_flux_timeseries.csv", mass_flux_rows, MASS_FLUX_FIELDS)
    return {
        "driver_class": "FSIDriver3D",
        "n_steps_completed": int(driver.current_lbm_step),
        "solver_rows": solver_rows,
        "monitor_rows": monitor_rows,
        "force_rows": force_rows,
        "stability_rows": stability_rows,
        "mass_flux_rows": mass_flux_rows,
        "snapshot_steps": snapshot_steps,
        "raw_output_dir": display_path(driver.out_dir),
        "final_diagnostics": driver.final_diagnostics(),
        "performance": driver.performance_row(),
    }


def _copy_lbm_fields(driver: FSIDriver3D) -> dict[str, np.ndarray]:
    velocity = np.asarray(driver.lbm.v.to_numpy(), dtype=np.float32)
    rho = np.asarray(driver.lbm.rho.to_numpy(), dtype=np.float32)
    solid = np.asarray(driver.lbm.solid.to_numpy(), dtype=np.int8)
    population = np.asarray(driver.lbm.f.to_numpy(), dtype=np.float32)
    speed = np.linalg.norm(velocity, axis=3).astype(np.float32)
    return {
        "velocity": velocity,
        "rho": rho,
        "solid": solid,
        "population": population,
        "speed": speed,
    }


def _solver_row(diagnostics: dict[str, Any], dt_s: float) -> dict[str, Any]:
    row = {field: diagnostics[field] for field in SOLVER_TIMESERIES_FIELDS if field in diagnostics}
    row["time_s"] = float(diagnostics["step"]) * dt_s
    return row


def _monitor_row(
    driver: FSIDriver3D,
    diagnostics: dict[str, Any],
    dt_s: float,
    previous: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    step = int(diagnostics["step"])
    time_s = float(step) * dt_s
    tip = driver.flap_tip_monitor_rows[-1] if driver.flap_tip_monitor_rows else {}
    official = driver.fluent_like_monitor_rows[-1] if driver.fluent_like_monitor_rows else {}
    total = float(tip.get("flap_tip_total_displacement_m", 0.0))
    if previous is None:
        velocity = 0.0
    else:
        elapsed = time_s - float(previous["time_s"])
        velocity = 0.0 if abs(elapsed) <= 1.0e-30 else abs(total - float(previous["flap_tip_total_displacement_m"])) / elapsed
    force = _diagnostic_force_magnitude(diagnostics)
    row = {
        "time_s": time_s,
        "step": step,
        "flap_tip_total_displacement_m": total,
        "flap_tip_x_displacement_m": float(tip.get("flap_tip_x_displacement_m", 0.0)),
        "flap_tip_y_displacement_m": float(tip.get("flap_tip_y_displacement_m", 0.0)),
        "flap_tip_velocity_m_per_s": velocity,
        "official_point_like_total_displacement_m": float(
            official.get("official_point_like_total_displacement_m", 0.0)
        ),
        "official_point_like_x_displacement_m": float(
            official.get("official_point_like_x_displacement_m", 0.0)
        ),
        "official_point_like_y_displacement_m": float(
            official.get("official_point_like_y_displacement_m", 0.0)
        ),
        "official_point_like_z_displacement_m": float(
            official.get("official_point_like_z_displacement_m", 0.0)
        ),
        "official_point_like_particle_count": int(official.get("official_point_like_particle_count", 0)),
        "fluid_force_x_n": 0.0,
        "fluid_force_y_n": force,
        "fluid_force_magnitude_n": force,
    }
    _assert_finite_row(row)
    return row, row


def _force_row(monitor_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "time_s": monitor_row["time_s"],
        "step": monitor_row["step"],
        "fluid_force_x_n": monitor_row["fluid_force_x_n"],
        "fluid_force_y_n": monitor_row["fluid_force_y_n"],
        "fluid_force_magnitude_n": monitor_row["fluid_force_magnitude_n"],
        "force_proxy_source": "max of driver diagnostics hydro/cell/reaction force norms",
        "force_is_direct_fluent_wall_integral": False,
    }


def _stability_row(step: int, dt_s: float, diagnostics: dict[str, Any], fields: dict[str, np.ndarray]) -> dict[str, Any]:
    fluid = fields["solid"] == 0
    rho_fluid = fields["rho"][fluid]
    velocity_fluid = fields["velocity"][fluid]
    population_fluid = fields["population"][fluid]
    rho_finite = bool(np.all(np.isfinite(rho_fluid)))
    velocity_finite = bool(np.all(np.isfinite(velocity_fluid)))
    population_finite = bool(np.all(np.isfinite(population_fluid)))
    density_gate = bool(rho_finite and float(diagnostics["rho_min"]) > 0.0 and float(diagnostics["rho_max"]) < 5.0)
    mpm_j_gate = bool(math.isfinite(float(diagnostics["mpm_min_J"])) and float(diagnostics["mpm_min_J"]) > 0.0)
    finite_gate = bool(rho_finite and velocity_finite and population_finite)
    row = {
        "step": step,
        "time_s": float(step) * dt_s,
        "rho_min": float(diagnostics["rho_min"]),
        "rho_max": float(diagnostics["rho_max"]),
        "rho_finite": rho_finite,
        "velocity_finite": velocity_finite,
        "population_finite": population_finite,
        "lbm_max_v": float(diagnostics["lbm_max_v"]),
        "mpm_min_J": float(diagnostics["mpm_min_J"]),
        "mpm_max_speed": float(diagnostics["mpm_max_speed"]),
        "density_gate_pass_step": density_gate,
        "mpm_j_gate_pass_step": mpm_j_gate,
        "finite_gate_pass_step": finite_gate,
    }
    _assert_finite_row({k: v for k, v in row.items() if not isinstance(v, bool)})
    return row


def _mass_flux_row(
    step: int,
    dt_s: float,
    fields: dict[str, np.ndarray],
    masks: dict[str, dict[str, np.ndarray]],
    initial_mass: float | None,
) -> tuple[dict[str, Any], float]:
    rho = fields["rho"].astype(np.float64)
    ux = fields["velocity"][..., 0].astype(np.float64)
    solid = fields["solid"] != 0
    fluid_dynamic = ~solid
    boundary = masks["boundary"]
    geometry = masks["geometry"]
    inlet_mask = boundary["velocity_inlet_mask"].astype(bool)
    outlet_mask = boundary["pressure_outlet_mask"].astype(bool)
    static_fluid = geometry["fluid_mask"].astype(bool)
    midplane_mask = np.zeros_like(static_fluid, dtype=bool)
    midplane_mask[static_fluid.shape[0] // 2, :, :] = static_fluid[static_fluid.shape[0] // 2, :, :]
    total_mass = float(np.sum(rho[fluid_dynamic]))
    if initial_mass is None:
        initial_mass = total_mass
    inlet_flux = float(np.sum(rho[inlet_mask] * ux[inlet_mask]))
    outlet_flux = float(np.sum(rho[outlet_mask] * ux[outlet_mask]))
    midplane_flux = float(np.sum(rho[midplane_mask] * ux[midplane_mask]))
    denom = max(abs(inlet_flux), 1.0e-30)
    row = {
        "step": int(step),
        "time_s": float(step) * dt_s,
        "total_fluid_mass": total_mass,
        "mass_delta_rel": (total_mass - initial_mass) / max(abs(initial_mass), 1.0e-30),
        "inlet_flux": inlet_flux,
        "outlet_flux": outlet_flux,
        "midplane_flux": midplane_flux,
        "flux_imbalance_rel": (outlet_flux - inlet_flux) / denom,
        "outlet_to_inlet_flux_ratio": outlet_flux / denom,
        "midplane_to_inlet_flux_ratio": midplane_flux / denom,
    }
    _assert_finite_row(row)
    return row, initial_mass


def _write_velocity_snapshot(
    snapshot_dir: Path,
    step: int,
    dt_s: float,
    fields: dict[str, np.ndarray],
    compiled_case: dict[str, Any],
) -> Path:
    velocity = fields["velocity"]
    rho = fields["rho"]
    solid = fields["solid"]
    speed = fields["speed"]
    fluid = solid == 0
    if not np.all(np.isfinite(velocity[fluid])):
        raise RuntimeError(f"nonfinite velocity in fluid cells at step {step}")
    if not np.all(np.isfinite(rho[fluid])):
        raise RuntimeError(f"nonfinite rho in fluid cells at step {step}")
    path = snapshot_dir / f"velocity_snapshot_step{step:03d}.npz"
    np.savez_compressed(
        path,
        velocity=velocity,
        rho=rho,
        solid=solid,
        speed=speed,
        ux=velocity[..., 0],
        uy=velocity[..., 1],
        uz=velocity[..., 2],
        step=np.asarray(step, dtype=np.int32),
        time_s=np.asarray(float(step) * dt_s, dtype=np.float64),
        compiled_case_path=np.asarray(compiled_case.get("_compiled_case_path", "")),
        validation_claim_allowed=np.asarray(False),
    )
    return path


def _load_and_validate_masks(compiled_case: dict[str, Any], n_grid: int) -> dict[str, dict[str, np.ndarray]]:
    mask_paths = compiled_case["mask_artifacts"]
    masks = {
        "geometry": load_npz(mask_paths["geometry_masks"]),
        "boundary": load_npz(mask_paths["boundary_masks"]),
        "fsi_interface": load_npz(mask_paths["fsi_interface_masks"]),
    }
    expected = (int(n_grid), int(n_grid), int(n_grid))
    for group in masks.values():
        for name, value in group.items():
            if value.shape != expected:
                raise ValueError(f"mask {name} shape {value.shape} does not match {expected}")
    return masks


def _assert_mask_shapes(masks: dict[str, dict[str, np.ndarray]], shape: tuple[int, int, int]) -> None:
    for group in masks.values():
        for name, value in group.items():
            if value.shape != shape:
                raise ValueError(f"mask {name} shape {value.shape} does not match solver grid {shape}")


def _write_manifest(
    output_dir: Path,
    compiled_case_path: Path,
    geometry_config_path: Path,
    config,
    snapshot_interval: int,
    monitor_interval: int,
) -> dict[str, Any]:
    manifest = {
        "step": STEP,
        "status": "solver_manifest_written",
        "compiled_case_path": display_path(compiled_case_path),
        "generated_geometry_config_path": display_path(geometry_config_path),
        "solver_driver_config_path": display_path(output_dir / "solver_driver_config.json"),
        "driver_class": "FSIDriver3D",
        "step148_helper_used": False,
        "step153_helper_used": False,
        "n_steps_requested": int(config.n_lbm_steps),
        "dt_s": float(config.mpm_dt),
        "target_time_end_s": int(config.n_lbm_steps) * float(config.mpm_dt),
        "snapshot_interval": int(snapshot_interval),
        "monitor_interval": int(monitor_interval),
        "validation_claim_allowed": False,
    }
    write_json(output_dir / "solver_run_manifest.json", manifest)
    return manifest


def _write_case_to_driver_geometry_report(
    compiled_case_path: Path,
    output_dir: Path,
    geometry_config_path: Path,
    masks: dict[str, dict[str, np.ndarray]],
) -> dict[str, Any]:
    geometry = masks["geometry"]
    report = {
        "step": STEP,
        "status": "case_geometry_mapped_to_driver_config",
        "compiled_case_path": display_path(compiled_case_path),
        "generated_geometry_config_path": display_path(geometry_config_path),
        "official_mesh_imported": False,
        "proxy_geometry_used": True,
        "step154_geometry_masks_loaded": True,
        "driver_static_lbm_geometry_includes_flap": False,
        "flap_represented_by_mpm_particles": True,
        "static_duct_geometry_compatible_with_step154_duct_context": bool(
            int(np.count_nonzero(geometry["fluid_mask"])) > 0
        ),
        "step154_flap_solid_cell_count": int(np.count_nonzero(geometry["flap_solid_mask"])),
        "geometry_equivalence_claim_allowed": False,
        "validation_claim_allowed": False,
    }
    write_json(output_dir / "case_to_driver_geometry_report.json", report)
    return report


def _write_unit_mapping_report(output_dir: Path, compiled_case: dict[str, Any], config) -> dict[str, Any]:
    setup = compiled_case["official_tutorial_setup"]
    report = {
        "step": STEP,
        "status": "unit_mapping_report_only",
        "physical_duct_length_m": float(setup["duct_length_m"]),
        "duct_height_m": float(setup["duct_height_m"]),
        "target_inlet_velocity_mps": float(setup["inlet_air_velocity_mps"]),
        "official_fsi_dt_s": float(setup["official_tutorial_dt_s"]),
        "target_u_lbm": list(config.target_u_lbm),
        "lbm_viscosity_semantics": config.lbm_viscosity_semantics,
        "physical_reynolds_parity_claim_allowed": False,
        "tau_margin_validation_required_before_physical_re_claim": True,
        "validation_claim_allowed": False,
    }
    write_json(output_dir / "unit_mapping_report.json", report)
    return report


def _write_boundary_semantics_runtime_report(output_dir: Path, raw_dir: Path) -> dict[str, Any]:
    driver_report = read_json(raw_dir / "duct_boundary_condition_report.json")
    report = {
        "step": STEP,
        "status": "boundary_semantics_runtime_checked",
        "velocity_inlet_active": bool(driver_report.get("target_u_lbm_applied_to_inlet")),
        "pressure_outlet_active": bool(driver_report.get("pressure_outlet_cell_count", 0) > 0),
        "legacy_all_population_reset_used": bool(driver_report["all_population_equilibrium_reset_used"]),
        "unknown_population_reconstruction_used": bool(driver_report["unknown_population_reconstruction_used"]),
        "open_boundary_limiter_enabled": bool(driver_report.get("open_boundary_limiter_enabled", False)),
        "lbm_open_boundary_semantics": driver_report["lbm_open_boundary_semantics"],
        "driver_boundary_report_path": display_path(raw_dir / "duct_boundary_condition_report.json"),
        "validation_claim_allowed": False,
    }
    write_json(output_dir / "boundary_semantics_runtime_report.json", report)
    return report


def _write_physics_gap_report(output_dir: Path, config) -> dict[str, Any]:
    report = {
        "step": STEP,
        "status": "physics_gaps_reported",
        "solver_pipeline_stage": "real_solver_run",
        "fluid_solver": "LBM",
        "solid_solver": config.solid_model,
        "coupling_mode": config.coupling_mode,
        "official_structural_model": "Fluent intrinsic FSI / FEM-like structural model",
        "official_dynamic_mesh_model": "linearly elastic dynamic mesh smoothing",
        "our_dynamic_mesh_equivalent": "moving-boundary/proxy coupling on fixed LBM grid",
        "official_mesh_imported": False,
        "proxy_geometry_used": True,
        "official_monitor_loaded": False,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
    }
    write_json(output_dir / "physics_gap_report.json", report)
    return report


def _success_summary(
    compiled_case: dict[str, Any],
    config,
    output_dir: Path,
    manifest: dict[str, Any],
    geometry_report: dict[str, Any],
    unit_report: dict[str, Any],
    boundary_report: dict[str, Any],
    physics_gap: dict[str, Any],
    capture: dict[str, Any],
) -> dict[str, Any]:
    del output_dir, geometry_report, unit_report, physics_gap
    n_steps = int(config.n_lbm_steps)
    time_end_s = n_steps * float(config.mpm_dt)
    stability_rows = capture["stability_rows"]
    monitor_rows = capture["monitor_rows"]
    force_rows = capture["force_rows"]
    return {
        "step": STEP,
        "status": "official_tutorial_solver_v1_run_complete",
        "solver_v1_run_executed": True,
        "compiled_case_consumed": True,
        "compiled_case_ready_for_step155": True,
        "step148_helper_used": False,
        "step153_helper_used": False,
        "driver_class": "FSIDriver3D",
        "n_steps_requested": n_steps,
        "n_steps_completed": int(capture["n_steps_completed"]),
        "time_end_s": time_end_s,
        "official_tutorial_time_steps": int(compiled_case["official_tutorial_setup"]["official_tutorial_time_steps"]),
        "official_tutorial_dt_s": float(compiled_case["official_tutorial_setup"]["official_tutorial_dt_s"]),
        "official_tutorial_total_time_s": float(compiled_case["official_tutorial_setup"]["official_tutorial_total_time_s"]),
        "time_window_matches_official_tutorial": math.isclose(
            time_end_s,
            float(compiled_case["official_tutorial_setup"]["official_tutorial_total_time_s"]),
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ),
        "velocity_inlet_active": bool(boundary_report["velocity_inlet_active"]),
        "pressure_outlet_active": bool(boundary_report["pressure_outlet_active"]),
        "legacy_all_population_reset_used": bool(boundary_report["legacy_all_population_reset_used"]),
        "unknown_population_reconstruction_used": bool(boundary_report["unknown_population_reconstruction_used"]),
        "open_boundary_limiter_enabled": bool(boundary_report["open_boundary_limiter_enabled"]),
        "lbm_open_boundary_semantics": str(boundary_report["lbm_open_boundary_semantics"]),
        "solver_monitor_rows": len(monitor_rows),
        "solver_force_monitor_rows": len(force_rows),
        "stability_rows": len(stability_rows),
        "mass_flux_rows": len(capture["mass_flux_rows"]),
        "velocity_snapshot_count": len(capture["snapshot_steps"]),
        "final_velocity_snapshot_written": bool(n_steps in capture["snapshot_steps"]),
        "monitor_displacement_finite": _rows_finite(monitor_rows),
        "force_monitor_finite": _rows_finite(force_rows),
        "density_gate_pass": all(bool(row["density_gate_pass_step"]) for row in stability_rows),
        "finite_gate_pass": all(bool(row["finite_gate_pass_step"]) for row in stability_rows),
        "mpm_j_gate_pass": all(bool(row["mpm_j_gate_pass_step"]) for row in stability_rows),
        "mass_flux_reported": bool(capture["mass_flux_rows"]),
        "official_monitor_loaded": False,
        "official_error_metrics_available": False,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
        "solver_run_manifest": manifest,
        "raw_output_dir": capture["raw_output_dir"],
    }


def _failure_summary(exc: Exception) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": "official_tutorial_solver_v1_run_failed",
        "failure_stage": "step155_runner",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "solver_v1_run_executed": False,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
    }


def _write_report(output_dir: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Step155 Official Tutorial Solver V1",
        "",
        "Step155 consumed the Step154 compiled case directly and ran the repository",
        "`FSIDriver3D` path for the public official tutorial window.",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Solver run executed: `{summary.get('solver_v1_run_executed')}`",
        f"- Steps completed: `{summary.get('n_steps_completed')}`",
        f"- Time end s: `{summary.get('time_end_s')}`",
        f"- Step148 helper used: `{summary.get('step148_helper_used')}`",
        f"- Step153 helper used: `{summary.get('step153_helper_used')}`",
        f"- Solver monitor rows: `{summary.get('solver_monitor_rows')}`",
        f"- Mass flux rows: `{summary.get('mass_flux_rows')}`",
        f"- Velocity snapshots: `{summary.get('velocity_snapshot_count')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        "",
        "Step155 did not run Fluent, did not load or fabricate official monitor data,",
        "did not run Step150, did not run selected96, and does not claim Fluent or",
        "Figure 29.3 parity.",
        "",
        "Step156 must consume Step155 solver outputs and produce the official-style",
        "velocity plots, monitor plots, flux profiles, solver acceptance report, and",
        "official comparison placeholder/report.",
        "",
    ]
    text = "\n".join(lines)
    (output_dir / "report.md").write_text(text, encoding="utf-8")
    default_doc = Path("docs") / "campaigns" / "fluent_duct_flap" / "steps" / "155" / "report.md"
    if display_path(output_dir) == display_path(DEFAULT_OUTPUT_DIR):
        default_doc.parent.mkdir(parents=True, exist_ok=True)
        default_doc.write_text(text, encoding="utf-8")


def _compiled_case_with_test_overrides(
    compiled_case: dict[str, Any],
    allow_test_grid_override: bool,
    test_grid: int | None,
    test_n_steps: int | None,
) -> dict[str, Any]:
    if not allow_test_grid_override:
        return dict(compiled_case)
    case = dict(compiled_case)
    if test_grid is not None:
        case["solver_grid"] = {"nx": int(test_grid), "ny": int(test_grid), "nz": int(test_grid)}
    if test_n_steps is not None:
        setup = dict(case["official_tutorial_setup"])
        setup["official_tutorial_time_steps"] = int(test_n_steps)
        setup["official_tutorial_total_time_s"] = int(test_n_steps) * float(setup["official_tutorial_dt_s"])
        case["official_tutorial_setup"] = setup
    return case


def _diagnostic_force_magnitude(row: dict[str, Any]) -> float:
    return float(
        max(
            abs(float(row.get("hydro_force_max_norm", 0.0))),
            abs(float(row.get("cell_force_max_norm", 0.0))),
            abs(float(row.get("max_grid_reaction_norm", 0.0))),
        )
    )


def _rows_finite(rows: list[dict[str, Any]]) -> bool:
    try:
        for row in rows:
            _assert_finite_row(row)
    except ValueError:
        return False
    return True


def _assert_finite_row(row: dict[str, Any]) -> None:
    for key, value in row.items():
        if isinstance(value, bool) or isinstance(value, str):
            continue
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            raise ValueError(f"nonfinite row value {key}={value}")
