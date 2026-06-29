from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.geometry.config import GeometryConfig


STEP = 155
REQUIRED_CASE_STATUS = "compiled_case_ready_for_step155"
REQUIRED_OPEN_BOUNDARY_SEMANTICS = "regularized_velocity_pressure_limited"


def load_compiled_case(case_path: Path | str) -> dict[str, Any]:
    path = _resolve_repo_path(case_path)
    with path.open("r", encoding="utf-8") as f:
        compiled_case = json.load(f)
    compiled_case["_compiled_case_path"] = _display_path(path)
    return compiled_case


def validate_compiled_case_for_step155(compiled_case: dict[str, Any]) -> None:
    if int(compiled_case.get("step", -1)) != 154:
        raise ValueError("Step155 requires a Step154 compiled case")
    if compiled_case.get("status") != REQUIRED_CASE_STATUS:
        raise ValueError("Step155 requires compiled_case_ready_for_step155")
    if compiled_case.get("compiled_case_ready_for_step155") is False:
        raise ValueError("compiled_case_ready_for_step155 is explicitly false")

    setup = compiled_case.get("official_tutorial_setup") or {}
    boundary = compiled_case.get("boundary_condition_spec") or {}
    lbm_required = compiled_case.get("lbm_boundary_semantics_required_for_step155") or {}
    expected = {
        "official_tutorial_time_steps": 50,
        "official_tutorial_dt_s": 0.0005,
        "official_tutorial_total_time_s": 0.025,
    }
    for key, value in expected.items():
        if key not in setup:
            raise ValueError(f"missing official tutorial constant: {key}")
        if not math.isclose(float(setup[key]), float(value), rel_tol=1.0e-12, abs_tol=1.0e-15):
            raise ValueError(f"inconsistent official tutorial constant: {key}")

    if boundary.get("inlet") != "velocity_inlet":
        raise ValueError("Step155 requires velocity_inlet")
    if boundary.get("outlet") != "pressure_outlet":
        raise ValueError("Step155 requires pressure_outlet")
    if bool(lbm_required.get("legacy_all_population_reset_allowed", True)):
        raise ValueError("legacy all-population reset is not allowed for Step155")
    if lbm_required.get("minimum_open_boundary_semantics") != REQUIRED_OPEN_BOUNDARY_SEMANTICS:
        raise ValueError("Step155 requires regularized_velocity_pressure_limited")

    grid = compiled_case.get("solver_grid") or {}
    nx, ny, nz = int(grid.get("nx", 0)), int(grid.get("ny", 0)), int(grid.get("nz", 0))
    if nx <= 0 or ny <= 0 or nz <= 0 or nx != ny or nx != nz:
        raise ValueError("Step155 requires a positive cubic solver grid")


def write_generated_geometry_config(
    compiled_case: dict[str, Any],
    output_dir: Path | str,
    n_particles: int,
) -> Path:
    validate_compiled_case_for_step155(compiled_case)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    setup = compiled_case["official_tutorial_setup"]
    material = compiled_case["official_material"]
    mapping = compiled_case["solver_geometry_mapping"]
    duct = dict(mapping["duct_normalized"])
    flap_mapping = dict(mapping["flap_normalized"])
    duct_height_norm = float(duct["y"][1]) - float(duct["y"][0])
    geometry_payload = {
        "geometry_type": "duct_flap_proxy",
        "n_particles": int(n_particles),
        "duct": duct,
        "flap": {
            "anchor_x": float(flap_mapping["anchor_x"]),
            "anchor_y": float(flap_mapping["anchor_y"]),
            "height_over_duct_height": round(float(flap_mapping["height"]) / duct_height_norm, 12),
            "thickness_over_duct_height": round(float(flap_mapping["thickness"]) / duct_height_norm, 12),
            "normalized_height": float(flap_mapping["height"]),
            "normalized_thickness": float(flap_mapping["thickness"]),
            "z": [float(v) for v in flap_mapping["z"]],
            "fixed_base": True,
            "mirrored_pair": bool(flap_mapping.get("mirrored_pair", False)),
        },
        "material_reference": {
            "density": float(material["solid_density_kg_m3"]),
            "youngs_modulus": float(material["youngs_modulus_pa"]),
            "poisson_ratio": float(material["poisson_ratio"]),
            "used_for_mpm_config": True,
            "used_for_exact_structural_model": False,
        },
        "dimensional_reference": {
            "duct_length_m": float(setup["duct_length_m"]),
            "duct_height_m": float(setup["duct_height_m"]),
            "flap_height_m": float(setup["flap_height_m"]),
            "flap_thickness_m": float(setup["flap_thickness_m"]),
            "inlet_velocity_mps": float(setup["inlet_air_velocity_mps"]),
            "official_transient_steps": int(setup["official_tutorial_time_steps"]),
            "transient_dt_s": float(setup["official_tutorial_dt_s"]),
        },
        "monitor_reference": {
            "flap_tip_monitor_enabled": True,
            "monitor_is_direct_fluent_equivalent": False,
            "monitor_point_m": [float(v) for v in setup["monitor_point_m"]],
        },
        "p_rho": float(material["solid_density_kg_m3"]),
        "particles_per_axis_hint": int(compiled_case["solver_grid"]["nx"]),
        "quality_check_enabled": True,
        "quality_check_strict": False,
    }
    path = output_dir / "generated_geometry_config.json"
    _write_json(path, geometry_payload)
    GeometryConfig.from_json(str(path))
    return path


def build_step155_fsi_driver_config(
    compiled_case: dict[str, Any],
    geometry_config_path: Path,
    n_particles: int = 1024,
    target_u_lbm: tuple[float, float, float] = (0.02, 0.0, 0.0),
    monitor_interval: int = 1,
) -> FSIDriverConfig:
    validate_compiled_case_for_step155(compiled_case)
    setup = compiled_case["official_tutorial_setup"]
    grid = compiled_case["solver_grid"]
    return FSIDriverConfig(
        coupling_mode="moving_boundary",
        geometry_type="duct_flap_proxy",
        geometry_config_path=_display_path(geometry_config_path),
        n_grid=int(grid["nx"]),
        n_particles=int(n_particles),
        n_lbm_steps=int(setup["official_tutorial_time_steps"]),
        mpm_dt=float(setup["official_tutorial_dt_s"]),
        mpm_substeps_per_lbm_step=1,
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
        physical_duct_length_m=float(setup["duct_length_m"]),
        target_inlet_velocity_mps=float(setup["inlet_air_velocity_mps"]),
        official_fsi_dt_s=float(setup["official_tutorial_dt_s"]),
        target_u_lbm_for_dimensional_mapping=float(target_u_lbm[0]),
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
        output_interval=max(1, int(monitor_interval)),
        quality_check_enabled=True,
        quality_check_strict=False,
        write_particles=False,
        write_vtk=False,
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve_repo_path(path: Path | str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return _repo_root() / candidate


def _display_path(path: Path | str) -> str:
    try:
        return str(Path(path).resolve().relative_to(_repo_root()))
    except ValueError:
        return str(path)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
