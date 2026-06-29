from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

from .official_duct_flap_config import (
    REQUIRED_OPEN_BOUNDARY_SEMANTICS,
    load_compiled_case,
    validate_compiled_case_for_step155,
    write_generated_geometry_config,
)
from .official_duct_flap_io import display_path, write_json


STEP = 157


def load_compiled_case_for_step157(case_path: Path) -> dict[str, Any]:
    compiled_case = load_compiled_case(case_path)
    validate_compiled_case_for_step155(compiled_case)
    return compiled_case


def validate_step157_inputs(
    compiled_case: dict,
    step155_summary: dict,
    step156_summary: dict,
) -> None:
    validate_compiled_case_for_step155(compiled_case)
    if step155_summary.get("status") != "official_tutorial_solver_v1_run_complete":
        raise ValueError("Step157 requires completed Step155 solver output")
    if step155_summary.get("n_steps_completed") != 50:
        raise ValueError("Step157 requires Step155 50-step baseline")
    if step155_summary.get("validation_claim_allowed") is not False:
        raise ValueError("Step155 baseline must not claim validation")
    if step156_summary.get("status") != "official_tutorial_postprocess_complete":
        raise ValueError("Step157 requires completed Step156 postprocess output")
    if step156_summary.get("flow_development_gate_reported") is not True:
        raise ValueError("Step156 must report flow-development gate")
    if step156_summary.get("validation_claim_allowed") is not False:
        raise ValueError("Step156 must not claim validation")


def build_step157_subcycled_geometry_config(
    compiled_case: dict,
    output_dir: Path,
    n_particles: int,
) -> Path:
    return write_generated_geometry_config(compiled_case, output_dir, n_particles)


def build_step157_subcycled_fsi_config(
    compiled_case: dict,
    geometry_config_path: Path,
    n_particles: int = 1024,
    target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0),
    lbm_substeps_per_fsi_step: int | None = None,
) -> FSIDriverConfig:
    validate_compiled_case_for_step155(compiled_case)
    setup = compiled_case["official_tutorial_setup"]
    grid = compiled_case["solver_grid"]
    n_grid = int(grid["nx"])
    physical_duct_length_m = float(setup["duct_length_m"])
    target_inlet_velocity_mps = float(setup["inlet_air_velocity_mps"])
    official_dt_s = float(setup["official_tutorial_dt_s"])
    target_u_x = float(target_u_lbm[0])
    dx_phys_m = physical_duct_length_m / float(n_grid)
    lbm_dt_phys_s = target_u_x * dx_phys_m / target_inlet_velocity_mps
    required_substeps = int(round(official_dt_s / lbm_dt_phys_s))
    substeps = int(lbm_substeps_per_fsi_step or required_substeps)
    if substeps <= 0:
        raise ValueError("lbm_substeps_per_fsi_step must be positive")
    if not math.isclose(substeps * lbm_dt_phys_s, official_dt_s, rel_tol=1.0e-12, abs_tol=1.0e-15):
        raise ValueError("substep count does not reconstruct official FSI dt")

    return FSIDriverConfig(
        coupling_mode="moving_boundary",
        geometry_type="duct_flap_proxy",
        geometry_config_path=display_path(geometry_config_path),
        n_grid=n_grid,
        n_particles=int(n_particles),
        n_lbm_steps=int(setup["official_tutorial_time_steps"]),
        mpm_dt=official_dt_s,
        mpm_substeps_per_lbm_step=1,
        fsi_exchange_mode="lbm_subcycled_per_fsi_step",
        lbm_substeps_per_fsi_step=substeps,
        lbm_dt_phys_override_s=lbm_dt_phys_s,
        target_u_lbm=tuple(float(v) for v in target_u_lbm),
        initial_solid_velocity_norm=(0.0, 0.0, 0.0),
        lbm_boundary_condition_mode="duct_velocity_inlet_pressure_outlet",
        lbm_open_boundary_semantics=REQUIRED_OPEN_BOUNDARY_SEMANTICS,
        open_boundary_limiter_enabled=True,
        open_boundary_rho_min=0.8,
        open_boundary_rho_max=1.2,
        open_boundary_u_max=0.1,
        open_boundary_noneq_cap=0.05,
        velocity_inlet_axis="x",
        velocity_inlet_side="min",
        pressure_outlet_side="max",
        physical_duct_length_m=physical_duct_length_m,
        target_inlet_velocity_mps=target_inlet_velocity_mps,
        official_fsi_dt_s=official_dt_s,
        target_u_lbm_for_dimensional_mapping=target_u_x,
        fluid_density_kg_m3=1.225,
        fluid_kinematic_viscosity_m2_s=1.5e-5,
        lbm_viscosity_semantics="legacy_external",
        lbm_tau_stability_policy="report_only",
        reaction_transfer_mode="engineering",
        solid_model="finite_deformation_mpm",
        solid_dimensionality="three_dimensional",
        flow_dimensionality_mode="three_dimensional",
        fluent_like_monitor_enabled=True,
        fluent_like_monitor_physical_point_m=tuple(float(v) for v in setup["monitor_point_m"]),
        fluent_like_monitor_nearest_count=8,
        output_interval=1,
        quality_check_enabled=True,
        quality_check_strict=False,
        write_particles=False,
        write_vtk=False,
    )


def write_step157_subcycle_config_report(
    output_path: Path,
    config: FSIDriverConfig,
) -> dict[str, Any]:
    reconstructed_dt = float(config.lbm_substeps_per_fsi_step) * float(config.lbm_dt_phys_override_s)
    dx_phys_m = float(config.physical_duct_length_m) / float(config.n_grid)
    reconstructed_velocity = (
        float(config.target_u_lbm_for_dimensional_mapping)
        * dx_phys_m
        / float(config.lbm_dt_phys_override_s)
    )
    report = {
        "step": STEP,
        "status": "subcycled_fsi_config_built",
        "fsi_exchange_mode": config.fsi_exchange_mode,
        "lbm_substeps_per_fsi_step": int(config.lbm_substeps_per_fsi_step),
        "lbm_dt_phys_override_s": float(config.lbm_dt_phys_override_s),
        "official_fsi_dt_s": float(config.official_fsi_dt_s),
        "official_dt_reconstructed_from_lbm_substeps": reconstructed_dt,
        "target_velocity_mapping_reconstructs_10_mps": math.isclose(
            reconstructed_velocity,
            float(config.target_inlet_velocity_mps),
            rel_tol=1.0e-12,
            abs_tol=1.0e-9,
        ),
        "legacy_external_viscosity_used": config.lbm_viscosity_semantics == "legacy_external",
        "physical_reynolds_parity_claim_allowed": False,
        "validation_claim_allowed": False,
    }
    write_json(output_path, report)
    return report
