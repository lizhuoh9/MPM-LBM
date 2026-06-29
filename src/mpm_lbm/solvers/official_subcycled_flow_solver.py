from __future__ import annotations

import csv
import math
import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np

from src.mpm_lbm.postprocessing.fluent_duct_flap_velocity_render import (
    load_step154_masks,
    write_official_style_velocity_cloud_plot,
    write_velocity_component_plot,
    write_velocity_magnitude_plot,
    write_x_plane_flux_profile,
)
from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

from .official_duct_flap_io import display_path, load_npz, read_json, resolve_repo_path, write_csv, write_json
from .official_subcycled_flow_config import (
    build_step157_subcycled_fsi_config,
    build_step157_subcycled_geometry_config,
    load_compiled_case_for_step157,
    validate_step157_inputs,
    write_step157_subcycle_config_report,
)
from .official_subcycled_flow_diagnostics import (
    build_flow_development_comparison_report,
    diagnose_step155_time_scale,
    summarize_step156_flux_failure,
)


STEP = 157
DEFAULT_OUTPUT_DIR = Path("outputs") / "step157_official_subcycled_flow_development_repair"
DEFAULT_RAW_OUTPUT_DIR = Path("outputs") / "tmp" / "step157_official_subcycled_flow_development_driver_raw"

BASE_FIELDS = [
    "official_step",
    "time_s",
    "lbm_substeps_per_fsi_step",
    "total_lbm_substeps",
    "fsi_exchange_mode",
]

SOLVER_TIMESERIES_FIELDS = BASE_FIELDS + [
    "step",
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

SOLVER_MONITOR_FIELDS = BASE_FIELDS + [
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

SOLVER_FORCE_FIELDS = BASE_FIELDS + [
    "step",
    "fluid_force_x_n",
    "fluid_force_y_n",
    "fluid_force_magnitude_n",
    "force_proxy_source",
    "force_is_direct_fluent_wall_integral",
]

STABILITY_FIELDS = BASE_FIELDS + [
    "step",
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
    "official_step",
    "time_s",
    "total_lbm_substeps",
    "total_fluid_mass",
    "mass_delta_rel",
    "inlet_flux",
    "outlet_flux",
    "midplane_flux",
    "flux_imbalance_rel",
    "outlet_to_inlet_flux_ratio",
    "midplane_to_inlet_flux_ratio",
]


def run_step157_subcycled_flow_repair(
    compiled_case_path: Path,
    step155_root: Path,
    step156_root: Path,
    output_dir: Path,
    raw_output_dir: Path | None = None,
    force: bool = False,
    n_particles: int = 1024,
    target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0),
    lbm_substeps_per_fsi_step: int | None = None,
    snapshot_official_steps: tuple[int, ...] = (0, 5, 10, 20, 30, 40, 50),
    tail_fraction: float = 0.2,
    max_wall_seconds: float | None = None,
) -> dict[str, Any]:
    compiled_case_path = resolve_repo_path(compiled_case_path)
    step155_root = resolve_repo_path(step155_root)
    step156_root = resolve_repo_path(step156_root)
    output_dir = resolve_repo_path(output_dir)
    raw_dir = resolve_repo_path(raw_output_dir or DEFAULT_RAW_OUTPUT_DIR)
    if force:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    try:
        compiled_case = load_compiled_case_for_step157(compiled_case_path)
        step155_summary = read_json(step155_root / "solver_v1_summary.json")
        step156_summary = read_json(step156_root / "postprocess_summary.json")
        step156_acceptance = read_json(step156_root / "solver_acceptance_report.json")
        validate_step157_inputs(compiled_case, step155_summary, step156_summary)
        time_scale = diagnose_step155_time_scale(step155_summary, step156_acceptance, compiled_case)
        write_json(output_dir / "step157_time_scale_diagnosis.json", time_scale)
        flux_failure = summarize_step156_flux_failure(
            step156_root / "x_plane_flux_profile.csv",
            step156_acceptance,
        )

        geometry_config_path = build_step157_subcycled_geometry_config(
            compiled_case,
            output_dir,
            n_particles=n_particles,
        )
        config = build_step157_subcycled_fsi_config(
            compiled_case,
            geometry_config_path,
            n_particles=n_particles,
            target_u_lbm=target_u_lbm,
            lbm_substeps_per_fsi_step=lbm_substeps_per_fsi_step,
        )
        write_json(output_dir / "solver_driver_config.json", config.to_dict())
        subcycle_config = write_step157_subcycle_config_report(
            output_dir / "step157_subcycle_config_report.json",
            config,
        )
        manifest = _write_manifest(
            output_dir,
            compiled_case_path,
            geometry_config_path,
            config,
            snapshot_official_steps,
        )
        masks = _load_and_validate_masks(compiled_case, int(config.n_grid))
        driver = FSIDriver3D(config, out_dir=str(raw_dir))
        capture = _run_subcycled_driver_capture(
            driver,
            compiled_case,
            output_dir,
            masks,
            tuple(int(step) for step in snapshot_official_steps),
            max_wall_seconds=max_wall_seconds,
        )
        final_snapshot = _load_snapshot(output_dir / "velocity_snapshots" / "velocity_snapshot_step050.npz")
        post_masks = load_step154_masks(compiled_case)
        write_x_plane_flux_profile(
            final_snapshot,
            post_masks,
            compiled_case,
            output_dir / "x_plane_flux_profile_step050.csv",
        )
        _annotate_x_plane_flux_profile(
            output_dir / "x_plane_flux_profile_step050.csv",
            final_snapshot,
        )
        write_official_style_velocity_cloud_plot(
            final_snapshot,
            post_masks,
            compiled_case,
            output_dir / "official_style_velocity_cloud_step050.png",
            int(compiled_case["monitor_spec"]["monitor_index"][2]),
            title="Step157 subcycled proxy solver result; not Fluent validation",
        )
        write_velocity_magnitude_plot(
            final_snapshot,
            post_masks,
            compiled_case,
            output_dir / "velocity_magnitude_step050.png",
            int(compiled_case["monitor_spec"]["monitor_index"][2]),
            title=(
                "Step157 step 50, t = "
                f"{float(np.asarray(final_snapshot['time_s']).item()):.3f} s; "
                "subcycled proxy result"
            ),
        )
        write_velocity_component_plot(
            final_snapshot,
            post_masks,
            compiled_case,
            output_dir / "velocity_ux_step050.png",
            "ux",
            int(compiled_case["monitor_spec"]["monitor_index"][2]),
            title="Step157 step 50 ux; subcycled proxy; not Fluent validation",
        )
        write_velocity_component_plot(
            final_snapshot,
            post_masks,
            compiled_case,
            output_dir / "velocity_uy_step050.png",
            "uy",
            int(compiled_case["monitor_spec"]["monitor_index"][2]),
            title="Step157 step 50 uy; subcycled proxy; not Fluent validation",
        )
        comparison = build_flow_development_comparison_report(
            step156_acceptance,
            output_dir / "subcycled_mass_flux_timeseries.csv",
            output_dir / "flow_development_comparison_report.json",
            tail_fraction=tail_fraction,
            stability_csv=output_dir / "subcycled_stability_timeseries.csv",
        )
        acceptance = _write_solver_acceptance_report(
            output_dir,
            config,
            capture,
            comparison,
        )
        official_status = _write_official_comparison_status_report(output_dir)
        summary = _build_summary(
            time_scale,
            subcycle_config,
            manifest,
            capture,
            comparison,
            acceptance,
            official_status,
        )
        write_json(output_dir / "step157_summary.json", summary)
        _write_report(output_dir, summary, comparison)
        return summary
    except Exception as exc:
        failure = _write_failure_artifacts(output_dir, exc)
        raise RuntimeError(f"Step157 failed; failure artifact written: {failure['error_type']}: {failure['error_message']}") from exc


def _run_subcycled_driver_capture(
    driver: FSIDriver3D,
    compiled_case: dict[str, Any],
    output_dir: Path,
    masks: dict[str, dict[str, np.ndarray]],
    snapshot_official_steps: tuple[int, ...],
    max_wall_seconds: float | None,
) -> dict[str, Any]:
    snapshot_dir = output_dir / "velocity_snapshots"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    driver.initialize()
    start_time = time.perf_counter()
    n_steps = int(driver.config.n_lbm_steps)
    dt_s = float(driver.config.official_fsi_dt_s)

    solver_rows: list[dict[str, Any]] = []
    monitor_rows: list[dict[str, Any]] = []
    force_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    mass_flux_rows: list[dict[str, Any]] = []
    snapshot_steps: list[int] = []
    previous_monitor: dict[str, Any] | None = None
    initial_mass: float | None = None

    for official_step in range(0, n_steps + 1):
        if max_wall_seconds is not None and time.perf_counter() - start_time > max_wall_seconds:
            raise TimeoutError(f"Step157 exceeded max_wall_seconds={max_wall_seconds}")
        if official_step > 0:
            driver.step_once()
        if int(driver.current_lbm_step) != official_step:
            raise RuntimeError(
                f"driver official step mismatch: expected {official_step}, got {driver.current_lbm_step}"
            )
        diagnostics = driver.collect_diagnostics(official_step)
        fields = _copy_lbm_fields(driver)
        _assert_mask_shapes(masks, fields["rho"].shape)
        base = _base_row(driver, official_step, dt_s)
        solver_rows.append(_solver_row(base, diagnostics))
        monitor_row, previous_monitor = _monitor_row(driver, base, diagnostics, previous_monitor)
        monitor_rows.append(monitor_row)
        force_rows.append(_force_row(base, monitor_row))
        stability_rows.append(_stability_row(base, diagnostics, fields))
        mass_row, initial_mass = _mass_flux_row(base, fields, masks, initial_mass)
        mass_flux_rows.append(mass_row)
        if official_step in snapshot_official_steps:
            _write_velocity_snapshot(snapshot_dir, official_step, fields, compiled_case, driver)
            snapshot_steps.append(official_step)

    driver.export_outputs(driver.current_lbm_step)
    driver.save_timeseries()
    write_csv(output_dir / "subcycled_solver_timeseries.csv", solver_rows, SOLVER_TIMESERIES_FIELDS)
    write_csv(output_dir / "subcycled_solver_monitor.csv", monitor_rows, SOLVER_MONITOR_FIELDS)
    write_csv(output_dir / "subcycled_solver_force_monitor.csv", force_rows, SOLVER_FORCE_FIELDS)
    write_csv(output_dir / "subcycled_stability_timeseries.csv", stability_rows, STABILITY_FIELDS)
    write_csv(output_dir / "subcycled_mass_flux_timeseries.csv", mass_flux_rows, MASS_FLUX_FIELDS)
    return {
        "driver_class": "FSIDriver3D",
        "n_official_steps_completed": int(driver.current_lbm_step),
        "total_lbm_substeps_completed": int(driver.total_lbm_substeps),
        "official_time_end_s": n_steps * dt_s,
        "solver_rows": solver_rows,
        "monitor_rows": monitor_rows,
        "force_rows": force_rows,
        "stability_rows": stability_rows,
        "mass_flux_rows": mass_flux_rows,
        "snapshot_steps": snapshot_steps,
        "raw_output_dir": display_path(driver.out_dir),
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


def _base_row(driver: FSIDriver3D, official_step: int, dt_s: float) -> dict[str, Any]:
    return {
        "official_step": int(official_step),
        "time_s": int(official_step) * float(dt_s),
        "lbm_substeps_per_fsi_step": int(driver.config.lbm_substeps_per_fsi_step),
        "total_lbm_substeps": int(driver.total_lbm_substeps),
        "fsi_exchange_mode": str(driver.config.fsi_exchange_mode),
    }


def _solver_row(base: dict[str, Any], diagnostics: dict[str, Any]) -> dict[str, Any]:
    row = dict(base)
    row["step"] = int(base["official_step"])
    for field in SOLVER_TIMESERIES_FIELDS:
        if field in row:
            continue
        if field in diagnostics:
            row[field] = diagnostics[field]
    return row


def _monitor_row(
    driver: FSIDriver3D,
    base: dict[str, Any],
    diagnostics: dict[str, Any],
    previous: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    tip = driver.flap_tip_monitor_rows[-1] if driver.flap_tip_monitor_rows else {}
    official = driver.fluent_like_monitor_rows[-1] if driver.fluent_like_monitor_rows else {}
    total = float(tip.get("flap_tip_total_displacement_m", 0.0))
    if previous is None:
        velocity = 0.0
    else:
        elapsed = float(base["time_s"]) - float(previous["time_s"])
        velocity = 0.0 if abs(elapsed) <= 1.0e-30 else abs(total - float(previous["flap_tip_total_displacement_m"])) / elapsed
    force = _diagnostic_force_magnitude(diagnostics)
    row = {
        **base,
        "step": int(base["official_step"]),
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


def _force_row(base: dict[str, Any], monitor_row: dict[str, Any]) -> dict[str, Any]:
    return {
        **base,
        "step": int(base["official_step"]),
        "fluid_force_x_n": monitor_row["fluid_force_x_n"],
        "fluid_force_y_n": monitor_row["fluid_force_y_n"],
        "fluid_force_magnitude_n": monitor_row["fluid_force_magnitude_n"],
        "force_proxy_source": "max of driver diagnostics hydro/cell/reaction force norms",
        "force_is_direct_fluent_wall_integral": False,
    }


def _stability_row(
    base: dict[str, Any],
    diagnostics: dict[str, Any],
    fields: dict[str, np.ndarray],
) -> dict[str, Any]:
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
        **base,
        "step": int(base["official_step"]),
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
    base: dict[str, Any],
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
        "official_step": int(base["official_step"]),
        "time_s": float(base["time_s"]),
        "total_lbm_substeps": int(base["total_lbm_substeps"]),
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
    official_step: int,
    fields: dict[str, np.ndarray],
    compiled_case: dict[str, Any],
    driver: FSIDriver3D,
) -> Path:
    velocity = fields["velocity"]
    rho = fields["rho"]
    solid = fields["solid"]
    speed = fields["speed"]
    fluid = solid == 0
    if not np.all(np.isfinite(velocity[fluid])):
        raise RuntimeError(f"nonfinite velocity in fluid cells at official step {official_step}")
    if not np.all(np.isfinite(rho[fluid])):
        raise RuntimeError(f"nonfinite rho in fluid cells at official step {official_step}")
    path = snapshot_dir / f"velocity_snapshot_step{official_step:03d}.npz"
    np.savez_compressed(
        path,
        velocity=velocity,
        rho=rho,
        solid=solid,
        speed=speed,
        ux=velocity[..., 0],
        uy=velocity[..., 1],
        uz=velocity[..., 2],
        official_step=np.asarray(official_step, dtype=np.int32),
        time_s=np.asarray(float(official_step) * float(driver.config.official_fsi_dt_s), dtype=np.float64),
        total_lbm_substeps=np.asarray(int(driver.total_lbm_substeps), dtype=np.int32),
        lbm_substeps_per_fsi_step=np.asarray(int(driver.config.lbm_substeps_per_fsi_step), dtype=np.int32),
        compiled_case_path=np.asarray(compiled_case.get("_compiled_case_path", "")),
        validation_claim_allowed=np.asarray(False),
    )
    return path


def _load_snapshot(path: Path) -> dict[str, np.ndarray]:
    return load_npz(path)


def _annotate_x_plane_flux_profile(path: Path, snapshot: dict[str, Any]) -> None:
    with Path(path).open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        existing_fields = list(reader.fieldnames or [])
    if not rows:
        raise ValueError(f"x-plane flux profile has no rows: {path}")

    metadata = {
        "official_step": int(np.asarray(snapshot["official_step"]).item()),
        "time_s": float(np.asarray(snapshot["time_s"]).item()),
        "total_lbm_substeps": int(np.asarray(snapshot["total_lbm_substeps"]).item()),
        "lbm_substeps_per_fsi_step": int(np.asarray(snapshot["lbm_substeps_per_fsi_step"]).item()),
    }
    annotated = [{**metadata, **row} for row in rows]
    fields = [key for key in metadata if key not in existing_fields] + existing_fields
    write_csv(path, annotated, fields)


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
    snapshot_official_steps: tuple[int, ...],
) -> dict[str, Any]:
    manifest = {
        "step": STEP,
        "status": "subcycled_solver_manifest_written",
        "compiled_case_path": display_path(compiled_case_path),
        "generated_geometry_config_path": display_path(geometry_config_path),
        "solver_driver_config_path": display_path(output_dir / "solver_driver_config.json"),
        "driver_class": "FSIDriver3D",
        "fsi_exchange_mode": config.fsi_exchange_mode,
        "lbm_substeps_per_fsi_step": int(config.lbm_substeps_per_fsi_step),
        "lbm_dt_phys_override_s": float(config.lbm_dt_phys_override_s),
        "n_official_steps_requested": int(config.n_lbm_steps),
        "official_dt_s": float(config.official_fsi_dt_s),
        "target_time_end_s": int(config.n_lbm_steps) * float(config.official_fsi_dt_s),
        "target_total_lbm_substeps": int(config.n_lbm_steps) * int(config.lbm_substeps_per_fsi_step),
        "snapshot_official_steps": list(snapshot_official_steps),
        "validation_claim_allowed": False,
    }
    write_json(output_dir / "solver_run_manifest.json", manifest)
    return manifest


def _write_solver_acceptance_report(
    output_dir: Path,
    config,
    capture: dict[str, Any],
    comparison: dict[str, Any],
) -> dict[str, Any]:
    stability_rows = capture["stability_rows"]
    monitor_rows = capture["monitor_rows"]
    force_rows = capture["force_rows"]
    report = {
        "step": STEP,
        "status": "subcycled_solver_acceptance_report_written",
        "subcycled_solver_run_executed": True,
        "fsi_exchange_mode": config.fsi_exchange_mode,
        "lbm_substeps_per_fsi_step": int(config.lbm_substeps_per_fsi_step),
        "n_official_steps_completed": int(capture["n_official_steps_completed"]),
        "official_time_end_s": float(capture["official_time_end_s"]),
        "total_lbm_substeps_completed": int(capture["total_lbm_substeps_completed"]),
        "density_gate_pass": all(bool(row["density_gate_pass_step"]) for row in stability_rows),
        "finite_gate_pass": all(bool(row["finite_gate_pass_step"]) for row in stability_rows),
        "mpm_j_gate_pass": all(bool(row["mpm_j_gate_pass_step"]) for row in stability_rows),
        "monitor_displacement_finite": _rows_finite(monitor_rows),
        "force_monitor_finite": _rows_finite(force_rows),
        "mass_flux_reported": bool(capture["mass_flux_rows"]),
        "flow_development_gate_pass": bool(
            comparison["subcycled_step157"]["flow_development_gate_pass"]
        ),
        "outlet_flux_ratio_improved": bool(comparison["outlet_flux_ratio_improved"]),
        "flux_imbalance_improved": bool(comparison["flux_imbalance_improved"]),
        "flow_metrics_valid_for_gate": bool(comparison["flow_metrics_valid_for_gate"]),
        "flow_metrics_invalid_reason": comparison["flow_metrics_invalid_reason"],
        "first_density_gate_failure_step": comparison["first_density_gate_failure_step"],
        "first_finite_gate_failure_step": comparison["first_finite_gate_failure_step"],
        "official_monitor_loaded": False,
        "official_error_metrics_available": False,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    write_json(output_dir / "solver_acceptance_report.json", report)
    return report


def _write_official_comparison_status_report(output_dir: Path) -> dict[str, Any]:
    report = {
        "step": STEP,
        "status": "official_monitor_missing",
        "official_monitor_loaded": False,
        "official_error_metrics_available": False,
        "comparison_scope": "subcycled_solver_repair_only",
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
    }
    write_json(output_dir / "official_comparison_status_report.json", report)
    return report


def _build_summary(
    time_scale: dict[str, Any],
    subcycle_config: dict[str, Any],
    manifest: dict[str, Any],
    capture: dict[str, Any],
    comparison: dict[str, Any],
    acceptance: dict[str, Any],
    official_status: dict[str, Any],
) -> dict[str, Any]:
    flow_pass = bool(acceptance["flow_development_gate_pass"])
    status = (
        "subcycled_flow_development_repair_complete"
        if flow_pass
        else "subcycled_flow_development_repair_attempt_complete_but_flow_gate_failed"
    )
    return {
        "step": STEP,
        "status": status,
        "time_scale_mismatch_diagnosed": time_scale["status"] == "time_scale_mismatch_diagnosed",
        "compiled_case_consumed": True,
        "step155_baseline_consumed": True,
        "step156_acceptance_consumed": True,
        "subcycled_solver_run_executed": True,
        "fsi_exchange_mode": subcycle_config["fsi_exchange_mode"],
        "lbm_substeps_per_fsi_step": int(subcycle_config["lbm_substeps_per_fsi_step"]),
        "lbm_dt_phys_override_s": float(subcycle_config["lbm_dt_phys_override_s"]),
        "n_official_steps_completed": int(capture["n_official_steps_completed"]),
        "official_time_end_s": float(capture["official_time_end_s"]),
        "total_lbm_substeps_completed": int(capture["total_lbm_substeps_completed"]),
        "density_gate_pass": bool(acceptance["density_gate_pass"]),
        "finite_gate_pass": bool(acceptance["finite_gate_pass"]),
        "mpm_j_gate_pass": bool(acceptance["mpm_j_gate_pass"]),
        "mass_flux_reported": bool(acceptance["mass_flux_reported"]),
        "source_step156_flow_development_gate_pass": bool(
            comparison["baseline_step155_step156"]["flow_development_gate_pass"]
        ),
        "step157_flow_development_gate_reported": True,
        "step157_flow_development_gate_pass": flow_pass,
        "outlet_flux_ratio_improved": bool(comparison["outlet_flux_ratio_improved"]),
        "flux_imbalance_improved": bool(comparison["flux_imbalance_improved"]),
        "raw_outlet_flux_ratio_improved": bool(comparison["raw_outlet_flux_ratio_improved"]),
        "raw_flux_imbalance_improved": bool(comparison["raw_flux_imbalance_improved"]),
        "flow_metrics_valid_for_gate": bool(comparison["flow_metrics_valid_for_gate"]),
        "flow_metrics_invalid_reason": comparison["flow_metrics_invalid_reason"],
        "first_density_gate_failure_step": comparison["first_density_gate_failure_step"],
        "first_finite_gate_failure_step": comparison["first_finite_gate_failure_step"],
        "official_monitor_loaded": bool(official_status["official_monitor_loaded"]),
        "official_error_metrics_available": bool(official_status["official_error_metrics_available"]),
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
        "solver_run_manifest": manifest,
        "step158_recommended_next": (
            "postprocess_subcycled_solver_and_compare_if_official_monitor_available"
            if flow_pass
            else "open_boundary_or_geometry_obstruction_diagnosis"
        ),
    }


def _write_report(output_dir: Path, summary: dict[str, Any], comparison: dict[str, Any]) -> None:
    flow_pass = bool(summary["step157_flow_development_gate_pass"])
    outcome = (
        "Subcycling repaired the flow-development gate for the proxy solver. The next "
        "step may postprocess the subcycled result and prepare official-monitor "
        "comparison, but validation remains blocked until official reference data and "
        "explicit thresholds are available."
        if flow_pass
        else "Subcycling alone did not close the flow-development gate. The next step must "
        "diagnose open-boundary behavior, outlet propagation, or geometry/mask mismatch."
    )
    if not bool(summary.get("flow_metrics_valid_for_gate", True)):
        outcome = (
            "Subcycling reached a density instability before the flow-development tail "
            "window, so the raw tail flux ratios are not valid improvement evidence. "
            "The next step must diagnose open-boundary behavior, outlet propagation, "
            "or geometry/mask mismatch before re-evaluating flow development."
        )
    text = (
        "# Step157 Official Subcycled Flow Development Repair\n\n"
        "Step157 diagnosed the Step155/Step156 flow-development failure as a\n"
        "time-scale/subcycling mismatch candidate. Step155 used one LBM step per\n"
        "official FSI step, while the Step154/Step155 dimensional velocity mapping\n"
        "requires 120 LBM substeps per 0.0005 s official FSI step on the 48^3 grid.\n\n"
        "Step157 ran the official tutorial proxy case with\n"
        "fsi_exchange_mode = lbm_subcycled_per_fsi_step,\n"
        "lbm_substeps_per_fsi_step = 120,\n"
        "lbm_dt_phys_override_s = 4.166666666666667e-6 s,\n"
        "for 50 official steps and 6000 total LBM substeps.\n\n"
        "Step157 did not run Fluent, did not load or fabricate official monitor data,\n"
        "did not run Step150, did not run selected96, and does not make a validation\n"
        "claim.\n\n"
        f"{outcome}\n\n"
        "The flow-development comparison against Step156 is recorded in:\n"
        "`outputs/step157_official_subcycled_flow_development_repair/flow_development_comparison_report.json`.\n\n"
        "## Current Comparison\n\n"
        f"- Step157 flow gate pass: `{summary['step157_flow_development_gate_pass']}`\n"
        f"- Outlet ratio improved: `{comparison['outlet_flux_ratio_improved']}`\n"
        f"- Flux imbalance improved: `{comparison['flux_imbalance_improved']}`\n"
        f"- Flow metrics valid for gate: `{comparison['flow_metrics_valid_for_gate']}`\n"
        f"- Flow metrics invalid reason: `{comparison['flow_metrics_invalid_reason']}`\n"
        f"- First density gate failure step: `{comparison['first_density_gate_failure_step']}`\n"
        f"- Validation claim allowed: `{summary['validation_claim_allowed']}`\n"
    )
    (output_dir / "report.md").write_text(text, encoding="utf-8")
    doc_report = Path("docs") / "campaigns" / "fluent_duct_flap" / "steps" / "157" / "report.md"
    doc_report.parent.mkdir(parents=True, exist_ok=True)
    doc_report.write_text(text, encoding="utf-8")


def _write_failure_artifacts(output_dir: Path, exc: Exception) -> dict[str, Any]:
    report = {
        "step": STEP,
        "status": "subcycled_solver_acceptance_failed",
        "subcycled_solver_run_executed": False,
        "failure_stage": "step157_subcycled_solver",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    write_json(output_dir / "solver_acceptance_report.json", report)
    write_json(output_dir / "step157_summary.json", report)
    return report


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
