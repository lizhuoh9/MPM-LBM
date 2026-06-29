"""Step153 official tutorial setup parity runner.

This step runs the repository FSIDriver3D path via the Step148 solver helper
surface, but constrains the reproduction to the public Ansys Chapter 29
tutorial setup window and records the remaining setup/semantic gaps.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import sys
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.steps.step148_our_solver_fluent_official_case_reproduction import (  # noqa: E402
    DEFAULT_GEOMETRY_CONFIG,
    FORCE_MONITOR_FIELDS,
    MONITOR_FIELDS,
    create_fluent_official_proxy_fsi_config,
    extract_solver_monitors,
    run_our_solver_fsi_case,
)
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig  # noqa: E402
from src.mpm_lbm.sim.geometry.config import GeometryConfig  # noqa: E402


STEP = 153
DEFAULT_PRIVATE_ROOT = Path("benchmarks") / "private" / "fluent_fsi_2way"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step153_official_tutorial_setup_parity"
DEFAULT_RAW_OUTPUT_DIR = Path("outputs") / "tmp" / "step153_official_tutorial_setup_parity_driver_raw"

OFFICIAL_TUTORIAL_SETUP = {
    "source": "Ansys Chapter 29 public two-way FSI tutorial setup",
    "duct_length_m": 0.10,
    "duct_height_m": 0.04,
    "flap_height_m": 0.01,
    "flap_thickness_m": 0.003,
    "half_domain_mode": True,
    "inlet_air_velocity_mps": 10.0,
    "outlet_type": "pressure_outlet",
    "monitor_point_m": [0.0505, 0.0095],
    "monitor_quantity": "Structure / Total Displacement",
    "official_tutorial_time_steps": 50,
    "official_tutorial_dt_s": 0.0005,
    "official_tutorial_total_time_s": 0.025,
    "max_iterations_per_time_step": 40,
}

OFFICIAL_TUTORIAL_MATERIAL = {
    "material_name": "silicone-rubber",
    "solid_density_kg_m3": 1600.0,
    "youngs_modulus_pa": 1.0e6,
    "poisson_ratio": 0.47,
}

OUTPUT_FILES = (
    "official_tutorial_setup_report.json",
    "official_tutorial_setup_report.md",
    "solver_run_manifest.json",
    "solver_monitor.csv",
    "solver_force_monitor.csv",
    "solver_reproduction_summary.json",
    "geometry_mapping_report.json",
    "material_mapping_report.json",
    "boundary_semantics_gap_report.json",
    "official_reference_gap_report.json",
    "report.md",
)


def create_official_tutorial_setup_fsi_config(
    grid: int = 48,
    n_steps: int = 50,
    dt_s: float = 0.0005,
    geometry_config_path: Path | str = DEFAULT_GEOMETRY_CONFIG,
    n_particles: int = 1024,
) -> FSIDriverConfig:
    _validate_official_window(n_steps, dt_s)
    config = create_fluent_official_proxy_fsi_config(
        grid=grid,
        n_steps=n_steps,
        geometry_config_path=geometry_config_path,
        n_particles=n_particles,
    )
    return replace(
        config,
        n_lbm_steps=int(n_steps),
        mpm_dt=float(dt_s),
        official_fsi_dt_s=float(dt_s),
        physical_duct_length_m=float(OFFICIAL_TUTORIAL_SETUP["duct_length_m"]),
        target_inlet_velocity_mps=float(OFFICIAL_TUTORIAL_SETUP["inlet_air_velocity_mps"]),
        fluent_like_monitor_physical_point_m=tuple(OFFICIAL_TUTORIAL_SETUP["monitor_point_m"]),
        output_interval=max(1, min(5, int(n_steps))),
    )


def run_step153_official_tutorial_setup_parity(
    official_private_root: Path | str = DEFAULT_PRIVATE_ROOT,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    grid: int = 48,
    n_steps: int = 50,
    dt_s: float = 0.0005,
    force: bool = False,
    raw_output_dir: Path | str | None = None,
) -> dict[str, Any]:
    output_dir = Path(output_dir)
    raw_dir = Path(raw_output_dir) if raw_output_dir is not None else DEFAULT_RAW_OUTPUT_DIR
    if force:
        _clear_known_outputs(output_dir)
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    config: FSIDriverConfig | None = None
    try:
        config = create_official_tutorial_setup_fsi_config(grid=grid, n_steps=n_steps, dt_s=dt_s)
        geometry_report = _write_geometry_mapping_report(output_dir, official_private_root, config)
        reference_gap_report = _write_official_reference_gap_report(output_dir, official_private_root)
        setup_report = _write_official_setup_report(output_dir, config, geometry_report, reference_gap_report)
        boundary_report = _write_boundary_semantics_gap_report(output_dir, config)

        driver, diagnostics, run_report = run_our_solver_fsi_case(
            config,
            output_dir,
            force=force,
            raw_output_dir=raw_dir,
        )
        run_report = dict(run_report)
        run_report["material_reference_used_for_mpm_config"] = bool(
            getattr(driver, "material_reference_used_for_mpm_config", False)
        )
        monitor_rows, force_rows, coupling_report = extract_solver_monitors(driver, diagnostics)
        _write_csv(output_dir / "solver_monitor.csv", monitor_rows, MONITOR_FIELDS)
        _write_csv(output_dir / "solver_force_monitor.csv", force_rows, FORCE_MONITOR_FIELDS)

        material_report = _write_material_mapping_report(output_dir, config, run_report)
        manifest = _write_manifest(
            output_dir=output_dir,
            official_private_root=official_private_root,
            config=config,
            run_report=run_report,
            setup_report=setup_report,
            material_report=material_report,
            boundary_report=boundary_report,
            reference_gap_report=reference_gap_report,
        )
        summary = _success_summary(
            output_dir=output_dir,
            config=config,
            monitor_rows=monitor_rows,
            force_rows=force_rows,
            setup_report=setup_report,
            material_report=material_report,
            geometry_report=geometry_report,
            boundary_report=boundary_report,
            reference_gap_report=reference_gap_report,
            manifest=manifest,
            coupling_report=coupling_report,
        )
        _write_json(output_dir / "solver_reproduction_summary.json", summary)
        _write_step_report(output_dir, summary, setup_report, material_report, boundary_report)
        return summary
    except Exception as exc:
        summary = _failure_summary(output_dir, official_private_root, config, exc)
        _write_json(output_dir / "solver_reproduction_summary.json", summary)
        _write_step_report(output_dir, summary, {}, {}, {})
        return summary


def _success_summary(
    output_dir: Path,
    config: FSIDriverConfig,
    monitor_rows: list[dict[str, Any]],
    force_rows: list[dict[str, Any]],
    setup_report: dict[str, Any],
    material_report: dict[str, Any],
    geometry_report: dict[str, Any],
    boundary_report: dict[str, Any],
    reference_gap_report: dict[str, Any],
    manifest: dict[str, Any],
    coupling_report: dict[str, Any],
) -> dict[str, Any]:
    solver_time_end_s = _time_end(monitor_rows)
    return {
        "step": STEP,
        "status": "official_tutorial_setup_parity_run_complete",
        "our_solver_run_executed": True,
        "solver_monitor_found": bool(monitor_rows),
        "solver_monitor_rows": len(monitor_rows),
        "solver_force_monitor_rows": len(force_rows),
        "official_tutorial_time_steps": int(config.n_lbm_steps),
        "official_tutorial_dt_s": float(config.mpm_dt),
        "official_tutorial_total_time_s": int(config.n_lbm_steps) * float(config.mpm_dt),
        "solver_time_end_s": solver_time_end_s,
        "solver_time_window_matches_official_tutorial": math.isclose(
            solver_time_end_s,
            float(OFFICIAL_TUTORIAL_SETUP["official_tutorial_total_time_s"]),
            rel_tol=1.0e-9,
            abs_tol=1.0e-12,
        ),
        "monitor_point_m": list(config.fluent_like_monitor_physical_point_m),
        "material_density_kg_m3": material_report["solid_density_kg_m3"],
        "youngs_modulus_pa": material_report["youngs_modulus_pa"],
        "poisson_ratio": material_report["poisson_ratio"],
        "official_structural_material_applied": material_report["official_structural_material_applied"],
        "material_mapping_gap_blocks_physics_parity": material_report[
            "material_mapping_gap_blocks_physics_parity"
        ],
        "official_monitor_required_for_error_metrics": True,
        "official_monitor_loaded": bool(reference_gap_report["official_monitor_loaded"]),
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "selected96_ready": False,
        "official_payload_committed": False,
        "official_monitor_committed": False,
        "official_payload_used_as_solver_input": False,
        "private_official_monitor_available": bool(reference_gap_report["official_monitor_loaded"]),
        "fluid_solver": "LBM",
        "solid_solver": "MPM",
        "two_way_coupling_attempted": True,
        "fsi_coupling_mode": config.coupling_mode,
        "force_is_direct_fluent_wall_integral": False,
        "fluent_structural_model_equivalence_claim_allowed": False,
        "geometry_mapping_report": _display_path(output_dir / "geometry_mapping_report.json"),
        "material_mapping_report": _display_path(output_dir / "material_mapping_report.json"),
        "boundary_semantics_gap_report": _display_path(output_dir / "boundary_semantics_gap_report.json"),
        "official_reference_gap_report": _display_path(output_dir / "official_reference_gap_report.json"),
        "official_tutorial_setup_report": _display_path(output_dir / "official_tutorial_setup_report.json"),
        "solver_run_manifest": _display_path(output_dir / "solver_run_manifest.json"),
        "driver_raw_output_dir": manifest["driver_raw_output_dir"],
        "coupling_force_found": bool(coupling_report["coupling_force_found"]),
        "solid_motion_found": bool(coupling_report["solid_motion_found"]),
        "failure_stage": None,
        "next_step_if_official_monitor_available": "Step155 official error localization after setup parity",
        "next_step_if_official_monitor_missing": "Step154 diagnostic official reference extraction",
        "setup_report_status": setup_report["status"],
        "boundary_semantics_status": boundary_report["status"],
        "reference_gap_status": reference_gap_report["status"],
        "code_path_note": "Step153 uses Step148 solver helpers that instantiate FSIDriver3D",
    }


def _failure_summary(
    output_dir: Path,
    official_private_root: Path | str,
    config: FSIDriverConfig | None,
    exc: Exception,
) -> dict[str, Any]:
    placeholder = {
        "step": STEP,
        "status": "failed",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    for name in (
        "official_tutorial_setup_report.json",
        "geometry_mapping_report.json",
        "material_mapping_report.json",
        "boundary_semantics_gap_report.json",
        "official_reference_gap_report.json",
        "solver_run_manifest.json",
    ):
        _write_json(output_dir / name, placeholder)
    return {
        "step": STEP,
        "status": "official_tutorial_setup_parity_run_failed",
        "our_solver_run_executed": False,
        "solver_monitor_found": False,
        "solver_monitor_rows": 0,
        "official_tutorial_time_steps": None if config is None else int(config.n_lbm_steps),
        "official_tutorial_dt_s": None if config is None else float(config.mpm_dt),
        "official_tutorial_total_time_s": None if config is None else int(config.n_lbm_steps) * float(config.mpm_dt),
        "solver_time_end_s": None,
        "official_monitor_required_for_error_metrics": True,
        "official_monitor_loaded": False,
        "official_private_root": _display_path(Path(official_private_root)),
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "selected96_ready": False,
        "official_payload_committed": False,
        "official_monitor_committed": False,
        "failure_stage": "official_tutorial_setup_parity_failed",
        "error_type": type(exc).__name__,
        "error_message": str(exc),
    }


def _write_official_setup_report(
    output_dir: Path,
    config: FSIDriverConfig,
    geometry_report: dict[str, Any],
    reference_gap_report: dict[str, Any],
) -> dict[str, Any]:
    requested_total = int(config.n_lbm_steps) * float(config.mpm_dt)
    report = {
        "step": STEP,
        "status": "official_tutorial_setup_encoded",
        "official_tutorial_setup": dict(OFFICIAL_TUTORIAL_SETUP),
        "official_tutorial_material": dict(OFFICIAL_TUTORIAL_MATERIAL),
        "requested_n_steps": int(config.n_lbm_steps),
        "requested_dt_s": float(config.mpm_dt),
        "requested_total_time_s": requested_total,
        "time_window_matches_official_tutorial": math.isclose(
            requested_total,
            float(OFFICIAL_TUTORIAL_SETUP["official_tutorial_total_time_s"]),
            rel_tol=1.0e-12,
            abs_tol=1.0e-15,
        ),
        "monitor_point_m": list(config.fluent_like_monitor_physical_point_m),
        "monitor_quantity": OFFICIAL_TUTORIAL_SETUP["monitor_quantity"],
        "geometry_mapping_report": _display_path(output_dir / "geometry_mapping_report.json"),
        "official_reference_gap_report": _display_path(output_dir / "official_reference_gap_report.json"),
        "official_monitor_loaded": bool(reference_gap_report["official_monitor_loaded"]),
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
        "geometry_mapping_status": geometry_report["geometry_mapping_status"],
    }
    _write_json(output_dir / "official_tutorial_setup_report.json", report)
    _write_setup_markdown(output_dir / "official_tutorial_setup_report.md", report)
    return report


def _write_geometry_mapping_report(
    output_dir: Path,
    official_private_root: Path | str,
    config: FSIDriverConfig,
) -> dict[str, Any]:
    geometry = GeometryConfig.from_json(str(_repo_path(config.geometry_config_path)))
    dimensional = geometry.dimensional_reference or {}
    report = {
        "step": STEP,
        "geometry_mapping_status": "official_tutorial_proxy_geometry_mapped",
        "geometry_type": config.geometry_type,
        "geometry_config_path": config.geometry_config_path,
        "official_mesh_path": _display_path(Path(official_private_root) / "flap.msh"),
        "official_mesh_found": (Path(official_private_root) / "flap.msh").is_file(),
        "official_mesh_imported": False,
        "proxy_geometry_used": True,
        "official_tutorial_geometry": {
            "duct_length_m": OFFICIAL_TUTORIAL_SETUP["duct_length_m"],
            "duct_height_m": OFFICIAL_TUTORIAL_SETUP["duct_height_m"],
            "flap_height_m": OFFICIAL_TUTORIAL_SETUP["flap_height_m"],
            "flap_thickness_m": OFFICIAL_TUTORIAL_SETUP["flap_thickness_m"],
            "half_domain_mode": OFFICIAL_TUTORIAL_SETUP["half_domain_mode"],
        },
        "geometry_config_dimensional_reference": dimensional,
        "geometry_config_matches_official_tutorial": _geometry_matches_official(dimensional),
        "duct": geometry.duct,
        "flap": geometry.flap,
        "monitor_reference": geometry.monitor_reference,
        "mapping_scope": "procedural duct-flap proxy with official tutorial dimensional ratios; not a Fluent mesh import",
        "validation_claim_allowed": False,
    }
    _write_json(output_dir / "geometry_mapping_report.json", report)
    return report


def _write_material_mapping_report(
    output_dir: Path,
    config: FSIDriverConfig,
    run_report: dict[str, Any],
) -> dict[str, Any]:
    geometry = GeometryConfig.from_json(str(_repo_path(config.geometry_config_path)))
    material = geometry.material_reference or {}
    official_material_in_geometry = _material_matches_official(material)
    used_for_mpm_config = bool(material.get("used_for_mpm_config", False))
    driver_used_material = bool(run_report.get("material_reference_used_for_mpm_config", False))
    applied = bool(official_material_in_geometry and used_for_mpm_config and driver_used_material)
    report = {
        "step": STEP,
        "status": "official_structural_material_mapped_to_mpm_config" if applied else "material_mapping_gap",
        "material_name": OFFICIAL_TUTORIAL_MATERIAL["material_name"],
        "solid_density_kg_m3": OFFICIAL_TUTORIAL_MATERIAL["solid_density_kg_m3"],
        "youngs_modulus_pa": OFFICIAL_TUTORIAL_MATERIAL["youngs_modulus_pa"],
        "poisson_ratio": OFFICIAL_TUTORIAL_MATERIAL["poisson_ratio"],
        "geometry_material_reference": material,
        "geometry_material_matches_official_tutorial": official_material_in_geometry,
        "geometry_material_used_for_mpm_config": used_for_mpm_config,
        "driver_material_reference_used_for_mpm_config": driver_used_material,
        "official_structural_material_applied": applied,
        "official_structural_material_application_scope": "MPM config overrides p_rho, young_modulus, and poisson_ratio",
        "material_mapping_gap_blocks_physics_parity": not applied,
        "fluent_structural_model_equivalence_claim_allowed": False,
        "semantic_note": "Fluent intrinsic FSI uses a FEM-like structural zone; this runner maps public material constants into the MPM proxy only.",
        "validation_claim_allowed": False,
    }
    _write_json(output_dir / "material_mapping_report.json", report)
    return report


def _write_boundary_semantics_gap_report(output_dir: Path, config: FSIDriverConfig) -> dict[str, Any]:
    report = {
        "step": STEP,
        "status": "official_boundary_semantics_reported",
        "official_velocity_inlet_present": True,
        "official_pressure_outlet_present": True,
        "official_fixed_flap_attach_present": True,
        "official_intrinsic_fsi_wall_present": True,
        "official_dynamic_mesh_fsi_wall_shadow_present": True,
        "official_dynamic_mesh_smoothing_method": "Linearly Elastic Solid",
        "official_stationary_dynamic_mesh_zones": [
            "pressure_outlet",
            "symmetry",
            "velocity_inlet",
            "wall",
        ],
        "our_solver_lbm_boundary_condition_mode": config.lbm_boundary_condition_mode,
        "our_solver_open_boundary_semantics": config.lbm_open_boundary_semantics,
        "our_solver_equivalent_moving_boundary_mode": config.coupling_mode,
        "our_solver_solid_model": config.solid_model,
        "our_solver_solid_dimensionality": config.solid_dimensionality,
        "semantic_gaps": [
            "Fluent intrinsic FSI solid zone is FEM-like linear elasticity; our solid is MPM",
            "Fluent dynamic mesh smoothing is linearly elastic solid; our LBM grid uses moving-boundary/proxy coupling",
            "The current proxy geometry is procedural and is not a direct import of the private Fluent mesh",
        ],
        "boundary_equivalence_claim_allowed": False,
        "validation_claim_allowed": False,
    }
    _write_json(output_dir / "boundary_semantics_gap_report.json", report)
    return report


def _write_official_reference_gap_report(output_dir: Path, official_private_root: Path | str) -> dict[str, Any]:
    monitor_path = Path(official_private_root) / "outputs" / "official_monitor.csv"
    report: dict[str, Any] = {
        "step": STEP,
        "status": "official_monitor_available" if monitor_path.is_file() else "official_monitor_missing",
        "official_monitor_required_for_error_metrics": True,
        "official_monitor_loaded": monitor_path.is_file(),
        "official_monitor_path": _display_path(monitor_path),
        "official_monitor_committed": False,
        "official_payload_committed": False,
        "official_monitor_used_for_setup_parity_run": False,
        "comparison_scope": "setup_parity_only",
        "validation_claim_allowed": False,
        "next_action_if_missing": "Step154 diagnostic official reference extraction or provide Fluent report CSV",
        "next_action_if_available": "Step155 official error localization using Step153 solver monitor",
    }
    if monitor_path.is_file():
        report["official_monitor_sha256"] = sha256(monitor_path.read_bytes()).hexdigest()
        report["official_monitor_size_bytes"] = monitor_path.stat().st_size
    _write_json(output_dir / "official_reference_gap_report.json", report)
    return report


def _write_manifest(
    output_dir: Path,
    official_private_root: Path | str,
    config: FSIDriverConfig,
    run_report: dict[str, Any],
    setup_report: dict[str, Any],
    material_report: dict[str, Any],
    boundary_report: dict[str, Any],
    reference_gap_report: dict[str, Any],
) -> dict[str, Any]:
    manifest = {
        "step": STEP,
        "command": (
            "python -m experiments.steps.step153_official_tutorial_setup_parity "
            "--official-private-root benchmarks/private/fluent_fsi_2way "
            "--output-dir outputs/step153_official_tutorial_setup_parity "
            "--grid 48 --n-steps 50 --dt-s 0.0005 --force"
        ),
        "official_private_root": _display_path(Path(official_private_root)),
        "driver_raw_output_dir": run_report["raw_output_dir"],
        "driver_class": run_report.get("driver_class", "FSIDriver3D"),
        "uses_step148_solver_helper_path": True,
        "config": config.to_dict(),
        "run_report": run_report,
        "setup_report_status": setup_report["status"],
        "material_mapping_status": material_report["status"],
        "boundary_semantics_status": boundary_report["status"],
        "official_reference_gap_status": reference_gap_report["status"],
        "official_payload_committed": False,
        "official_monitor_committed": False,
        "validation_claim_allowed": False,
        "selected96_execution_allowed": False,
    }
    _write_json(output_dir / "solver_run_manifest.json", manifest)
    return manifest


def _write_step_report(
    output_dir: Path,
    summary: dict[str, Any],
    setup_report: dict[str, Any],
    material_report: dict[str, Any],
    boundary_report: dict[str, Any],
) -> None:
    lines = [
        "# Step153 Official Tutorial Setup Parity Correction",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Solver run executed: `{summary.get('our_solver_run_executed')}`",
        f"- Solver monitor rows: `{summary.get('solver_monitor_rows')}`",
        f"- Solver time end s: `{summary.get('solver_time_end_s')}`",
        f"- Official tutorial time steps: `{summary.get('official_tutorial_time_steps')}`",
        f"- Official tutorial dt s: `{summary.get('official_tutorial_dt_s')}`",
        f"- Official tutorial total time s: `{summary.get('official_tutorial_total_time_s')}`",
        f"- Time window matches official tutorial: `{summary.get('solver_time_window_matches_official_tutorial')}`",
        f"- Monitor point m: `{summary.get('monitor_point_m')}`",
        f"- Official structural material applied: `{summary.get('official_structural_material_applied')}`",
        f"- Material gap blocks physics parity: `{summary.get('material_mapping_gap_blocks_physics_parity')}`",
        f"- Official monitor loaded: `{summary.get('official_monitor_loaded')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        f"- Selected96 execution allowed: `{summary.get('selected96_execution_allowed')}`",
        "",
        "Step153 runs the repository FSIDriver3D proxy reproduction in the public official tutorial setup window.",
        "It records geometry, material, monitor-point, boundary, and official-reference gaps without claiming validation.",
        "",
    ]
    if setup_report:
        lines.append(f"- Setup report status: `{setup_report.get('status')}`")
    if material_report:
        lines.append(f"- Material report status: `{material_report.get('status')}`")
    if boundary_report:
        lines.append(f"- Boundary report status: `{boundary_report.get('status')}`")
    lines.append("")

    text = "\n".join(lines)
    (output_dir / "report.md").write_text(text, encoding="utf-8")
    if _is_default_output_dir(output_dir):
        doc_report = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "153" / "report.md"
        doc_report.parent.mkdir(parents=True, exist_ok=True)
        doc_report.write_text(text, encoding="utf-8")


def _write_setup_markdown(path: Path, report: dict[str, Any]) -> None:
    setup = report["official_tutorial_setup"]
    material = report["official_tutorial_material"]
    lines = [
        "# Step153 Official Tutorial Setup Report",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Time steps: `{setup['official_tutorial_time_steps']}`",
        f"- Time step size s: `{setup['official_tutorial_dt_s']}`",
        f"- Total time s: `{setup['official_tutorial_total_time_s']}`",
        f"- Duct length m: `{setup['duct_length_m']}`",
        f"- Duct height m: `{setup['duct_height_m']}`",
        f"- Flap height m: `{setup['flap_height_m']}`",
        f"- Flap thickness m: `{setup['flap_thickness_m']}`",
        f"- Monitor point m: `{setup['monitor_point_m']}`",
        f"- Material: `{material['material_name']}`",
        f"- Density kg/m^3: `{material['solid_density_kg_m3']}`",
        f"- Young's modulus Pa: `{material['youngs_modulus_pa']}`",
        f"- Poisson ratio: `{material['poisson_ratio']}`",
        f"- Official monitor loaded: `{report.get('official_monitor_loaded')}`",
        f"- Validation claim allowed: `{report.get('validation_claim_allowed')}`",
        "",
        "This is setup parity evidence only. Error metrics still require a real official monitor.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _validate_official_window(n_steps: int, dt_s: float) -> None:
    expected_steps = int(OFFICIAL_TUTORIAL_SETUP["official_tutorial_time_steps"])
    expected_dt = float(OFFICIAL_TUTORIAL_SETUP["official_tutorial_dt_s"])
    if int(n_steps) != expected_steps:
        raise ValueError(f"Step153 official tutorial mode requires n_steps={expected_steps}")
    if not math.isclose(float(dt_s), expected_dt, rel_tol=1.0e-12, abs_tol=1.0e-15):
        raise ValueError(f"Step153 official tutorial mode requires dt_s={expected_dt}")


def _geometry_matches_official(dimensional: dict[str, Any]) -> bool:
    checks = {
        "duct_length_m": OFFICIAL_TUTORIAL_SETUP["duct_length_m"],
        "duct_height_m": OFFICIAL_TUTORIAL_SETUP["duct_height_m"],
        "flap_height_m": OFFICIAL_TUTORIAL_SETUP["flap_height_m"],
        "flap_thickness_m": OFFICIAL_TUTORIAL_SETUP["flap_thickness_m"],
        "inlet_velocity_mps": OFFICIAL_TUTORIAL_SETUP["inlet_air_velocity_mps"],
        "official_transient_steps": OFFICIAL_TUTORIAL_SETUP["official_tutorial_time_steps"],
        "transient_dt_s": OFFICIAL_TUTORIAL_SETUP["official_tutorial_dt_s"],
    }
    for key, expected in checks.items():
        if key not in dimensional:
            return False
        if not math.isclose(float(dimensional[key]), float(expected), rel_tol=1.0e-12, abs_tol=1.0e-15):
            return False
    return True


def _material_matches_official(material: dict[str, Any]) -> bool:
    required = {
        "density": OFFICIAL_TUTORIAL_MATERIAL["solid_density_kg_m3"],
        "youngs_modulus": OFFICIAL_TUTORIAL_MATERIAL["youngs_modulus_pa"],
        "poisson_ratio": OFFICIAL_TUTORIAL_MATERIAL["poisson_ratio"],
    }
    for key, expected in required.items():
        if key not in material:
            return False
        if not math.isclose(float(material[key]), float(expected), rel_tol=1.0e-12, abs_tol=1.0e-15):
            return False
    return True


def _time_end(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return max(float(row["time_s"]) for row in rows)


def _clear_known_outputs(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.is_file():
            path.unlink()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return _display_path(value)
    if hasattr(value, "item"):
        return value.item()
    return value


def _repo_path(path: Path | str) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _display_path(path: Path | str) -> str:
    try:
        return str(Path(path).relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _is_default_output_dir(output_dir: Path) -> bool:
    try:
        return output_dir.resolve() == (REPO_ROOT / DEFAULT_OUTPUT_DIR).resolve()
    except Exception:
        return False


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-private-root", type=Path, default=DEFAULT_PRIVATE_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--grid", type=int, default=48)
    parser.add_argument("--n-steps", type=int, default=50)
    parser.add_argument("--dt-s", type=float, default=0.0005)
    parser.add_argument("--raw-output-dir", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step153_official_tutorial_setup_parity(
        official_private_root=args.official_private_root,
        output_dir=args.output_dir,
        grid=args.grid,
        n_steps=args.n_steps,
        dt_s=args.dt_s,
        force=args.force,
        raw_output_dir=args.raw_output_dir,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary.get("status") == "official_tutorial_setup_parity_run_complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
