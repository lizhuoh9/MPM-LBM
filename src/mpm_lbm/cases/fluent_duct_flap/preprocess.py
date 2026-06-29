from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .case_schema import (
    BoundaryConditionSpec,
    CompiledOfficialDuctFlapCase,
    DimensionlessMapping,
    FSIInterfaceSpec,
    MonitorSpec,
    OfficialMaterial,
    OfficialTutorialSetup,
    SolverGeometryMapping,
    SolverGrid,
    to_json_dict,
)


STEP = 154
CASE_NAME = "official_tutorial_duct_flap_proxy_case"
CASE_VERSION = 1


def load_step153_setup(step153_root: Path) -> dict:
    root = Path(step153_root)
    setup_report = _read_json(root / "official_tutorial_setup_report.json")
    summary = _read_json(root / "solver_reproduction_summary.json")
    boundary = _read_json_optional(root / "boundary_semantics_gap_report.json")
    material = _read_json_optional(root / "material_mapping_report.json")
    geometry = _read_json_optional(root / "geometry_mapping_report.json")
    reference = _read_json_optional(root / "official_reference_gap_report.json")

    setup = setup_report.get("official_tutorial_setup") or {}
    official_material = setup_report.get("official_tutorial_material") or {}
    _validate_setup_constants(setup, official_material, summary)

    return {
        "step153_root": root,
        "setup_report": setup_report,
        "summary": summary,
        "boundary_report": boundary,
        "material_report": material,
        "geometry_report": geometry,
        "reference_gap_report": reference,
        "official_tutorial_setup": setup,
        "official_material": official_material,
    }


def compile_official_duct_flap_case(
    step153_root: Path,
    output_dir: Path,
    grid: int,
    z_cells: int | None = None,
) -> dict:
    loaded = load_step153_setup(step153_root)
    output_dir = Path(output_dir)
    nz = int(z_cells if z_cells is not None else grid)
    solver_grid = SolverGrid(nx=int(grid), ny=int(grid), nz=nz)
    setup = _canonical_setup(loaded["official_tutorial_setup"])
    material = _canonical_material(loaded["official_material"])
    geometry_mapping = _solver_geometry_mapping()
    monitor_spec = _monitor_spec(setup, solver_grid, geometry_mapping)

    mask_artifacts = {
        "geometry_masks": _display_path(output_dir / "geometry_masks.npz"),
        "boundary_masks": _display_path(output_dir / "boundary_masks.npz"),
        "fsi_interface_masks": _display_path(output_dir / "fsi_interface_masks.npz"),
    }
    case = CompiledOfficialDuctFlapCase(
        step=STEP,
        status="compiled_case_ready_for_step155",
        case_name=CASE_NAME,
        case_version=CASE_VERSION,
        source_step=153,
        source_step153_root=_display_path(Path(step153_root)),
        source_step153_status=str(loaded["summary"].get("status")),
        official_tutorial_setup=to_json_dict(setup),
        official_material=to_json_dict(material),
        solver_grid=to_json_dict(solver_grid),
        solver_geometry_mapping=to_json_dict(geometry_mapping),
        boundary_condition_spec=to_json_dict(
            BoundaryConditionSpec(
                inlet="velocity_inlet",
                inlet_velocity_mps=float(setup.inlet_air_velocity_mps),
                outlet="pressure_outlet",
                wall="no_slip",
                flap_wall="fsi_moving_wall",
                z_boundary_proxy="periodic_or_symmetry_proxy_reported",
            )
        ),
        fsi_interface_spec=to_json_dict(
            FSIInterfaceSpec(
                interface_connectivity="6_neighbor",
                solid_interface="flap_solid_cells_adjacent_to_fluid",
                fluid_interface="fluid_cells_adjacent_to_flap_solid",
                fixed_base_policy="lower_wall_fixed_base_band",
                moving_wall_semantics="proxy_mpm_moving_boundary_interface",
                fluent_intrinsic_fsi_equivalence_claim_allowed=False,
            )
        ),
        monitor_spec=to_json_dict(monitor_spec),
        dimensionless_mapping={},
        lbm_boundary_semantics_required_for_step155={
            "legacy_all_population_reset_allowed": False,
            "minimum_open_boundary_semantics": "regularized_velocity_pressure_limited",
        },
        mask_artifacts=mask_artifacts,
        postprocess_spec_path=_display_path(output_dir / "postprocess_spec.json"),
        official_mesh_imported=False,
        official_fluent_files_used_as_runtime_input=False,
        validation_claim_allowed=False,
        figure_29_3_parity_claim_allowed=False,
        selected96_execution_allowed=False,
    )
    return to_json_dict(case)


def build_geometry_masks(case: dict) -> dict[str, np.ndarray]:
    grid = case["solver_grid"]
    nx, ny, nz = int(grid["nx"]), int(grid["ny"]), int(grid["nz"])
    centers = _centers(nx), _centers(ny), _centers(nz)
    x, y, z = np.meshgrid(*centers, indexing="ij")
    duct = case["solver_geometry_mapping"]["duct_normalized"]
    flap = case["solver_geometry_mapping"]["flap_normalized"]
    duct_context = _between(x, duct["x"]) & _between(y, duct["y"]) & _between(z, duct["z"])
    half_thickness = 0.5 * float(flap["thickness"])
    flap_x = (x >= float(flap["anchor_x"]) - half_thickness) & (
        x <= float(flap["anchor_x"]) + half_thickness
    )
    flap_y = (y >= float(flap["anchor_y"])) & (
        y <= float(flap["anchor_y"]) + float(flap["height"])
    )
    flap_z = _between(z, flap["z"])
    flap_solid = duct_context & flap_x & flap_y & flap_z
    fluid = duct_context & ~flap_solid
    solid = ~fluid

    fixed_band = max(float(flap["thickness"]), 0.2 * float(flap["height"]))
    flap_fixed = flap_solid & (y <= float(flap["anchor_y"]) + fixed_band)
    flap_free = flap_solid & ~flap_fixed
    duct_wall = solid & (_adjacent6(fluid) | ~duct_context)
    monitor = np.zeros((nx, ny, nz), dtype=bool)
    mi, mj, mk = [int(value) for value in case["monitor_spec"]["monitor_index"]]
    monitor[mi, mj, mk] = True
    return {
        "fluid_mask": fluid.astype(bool),
        "solid_mask": solid.astype(bool),
        "duct_context_mask": duct_context.astype(bool),
        "duct_wall_mask": duct_wall.astype(bool),
        "flap_solid_mask": flap_solid.astype(bool),
        "flap_fixed_base_mask": flap_fixed.astype(bool),
        "flap_free_region_mask": flap_free.astype(bool),
        "monitor_cell_mask": monitor,
    }


def build_boundary_masks(case: dict, geometry_masks: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    fluid = geometry_masks["fluid_mask"]
    flap = geometry_masks["flap_solid_mask"]
    duct_wall = geometry_masks["duct_wall_mask"]
    nx, ny, nz = fluid.shape
    velocity_inlet = np.zeros_like(fluid, dtype=bool)
    velocity_inlet[0, :, :] = fluid[0, :, :]
    pressure_outlet = np.zeros_like(fluid, dtype=bool)
    pressure_outlet[nx - 1, :, :] = fluid[nx - 1, :, :]
    flap_wall = flap & _adjacent6(fluid)
    fsi_wall = fluid & _adjacent6(flap)
    no_slip = duct_wall & _adjacent6(fluid)
    z_min = np.zeros_like(fluid, dtype=bool)
    z_min[:, :, 0] = True
    z_max = np.zeros_like(fluid, dtype=bool)
    z_max[:, :, nz - 1] = True
    return {
        "velocity_inlet_mask": velocity_inlet,
        "pressure_outlet_mask": pressure_outlet,
        "no_slip_wall_mask": no_slip,
        "symmetry_or_periodic_z_min_mask": z_min,
        "symmetry_or_periodic_z_max_mask": z_max,
        "flap_wall_mask": flap_wall,
        "fsi_wall_mask": fsi_wall,
    }


def build_fsi_interface_masks(
    case: dict,
    geometry_masks: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    del case
    fluid = geometry_masks["fluid_mask"]
    flap = geometry_masks["flap_solid_mask"]
    fixed = geometry_masks["flap_fixed_base_mask"]
    free = geometry_masks["flap_free_region_mask"]
    solid_interface = flap & _adjacent6(fluid)
    fluid_interface = fluid & _adjacent6(flap)
    return {
        "fluid_interface_mask": fluid_interface,
        "solid_interface_mask": solid_interface,
        "flap_fixed_interface_mask": fixed & solid_interface,
        "flap_free_interface_mask": free & solid_interface,
    }


def write_preprocess_artifacts(case: dict, masks: dict, output_dir: Path) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    geometry_masks = masks["geometry"]
    boundary_masks = masks["boundary"]
    fsi_masks = masks["fsi_interface"]
    np.savez(output_dir / "geometry_masks.npz", **geometry_masks)
    np.savez(output_dir / "boundary_masks.npz", **boundary_masks)
    np.savez(output_dir / "fsi_interface_masks.npz", **fsi_masks)

    dimensionless = _dimensionless_mapping(case, geometry_masks)
    case["dimensionless_mapping"] = dimensionless
    material_report = _material_mapping(case)
    preprocess_report = _preprocess_report(case, geometry_masks, boundary_masks, fsi_masks)
    _write_json(output_dir / "compiled_case.json", case)
    _write_json(output_dir / "dimensionless_mapping.json", dimensionless)
    _write_json(output_dir / "material_model_mapping.json", material_report)
    _write_json(output_dir / "preprocess_report.json", preprocess_report)
    return preprocess_report


def _canonical_setup(data: dict[str, Any]) -> OfficialTutorialSetup:
    return OfficialTutorialSetup(
        duct_length_m=float(data["duct_length_m"]),
        duct_height_m=float(data["duct_height_m"]),
        flap_height_m=float(data["flap_height_m"]),
        flap_thickness_m=float(data["flap_thickness_m"]),
        half_domain_mode=bool(data["half_domain_mode"]),
        inlet_air_velocity_mps=float(data["inlet_air_velocity_mps"]),
        outlet_type=str(data["outlet_type"]),
        monitor_point_m=[float(value) for value in data["monitor_point_m"]],
        monitor_quantity=str(data["monitor_quantity"]),
        official_tutorial_time_steps=int(data["official_tutorial_time_steps"]),
        official_tutorial_dt_s=float(data["official_tutorial_dt_s"]),
        official_tutorial_total_time_s=float(data["official_tutorial_total_time_s"]),
        max_iterations_per_time_step=int(data["max_iterations_per_time_step"]),
    )


def _canonical_material(data: dict[str, Any]) -> OfficialMaterial:
    return OfficialMaterial(
        material_name=str(data.get("material_name", "silicone-rubber")),
        solid_density_kg_m3=float(data["solid_density_kg_m3"]),
        youngs_modulus_pa=float(data["youngs_modulus_pa"]),
        poisson_ratio=float(data["poisson_ratio"]),
    )


def _solver_geometry_mapping() -> SolverGeometryMapping:
    return SolverGeometryMapping(
        solver_domain_normalized={"x": [0.0, 1.0], "y": [0.0, 1.0], "z": [0.0, 1.0]},
        duct_normalized={"x": [0.0, 1.0], "y": [0.3, 0.7], "z": [0.45, 0.55]},
        flap_normalized={
            "anchor_x": 0.505,
            "anchor_y": 0.3,
            "height": 0.10,
            "thickness": 0.03,
            "z": [0.45, 0.55],
            "mirrored_pair": False,
            "anchor_side": "lower_wall",
        },
        physical_to_normalized_mapping={
            "x_norm": "x_m / duct_length_m",
            "y_norm": "duct_y_min_norm + (y_m / duct_height_m) * (duct_y_max_norm - duct_y_min_norm)",
            "z_norm": "0.5",
        },
        geometry_equivalence_claim_allowed=False,
    )


def _monitor_spec(
    setup: OfficialTutorialSetup,
    grid: SolverGrid,
    geometry: SolverGeometryMapping,
) -> MonitorSpec:
    duct_y = geometry.duct_normalized["y"]
    x_norm = float(setup.monitor_point_m[0]) / float(setup.duct_length_m)
    y_norm = float(duct_y[0]) + (float(setup.monitor_point_m[1]) / float(setup.duct_height_m)) * (
        float(duct_y[1]) - float(duct_y[0])
    )
    normalized = [x_norm, y_norm, 0.5]
    index = [
        _nearest_cell_index(normalized[0], grid.nx),
        _nearest_cell_index(normalized[1], grid.ny),
        _nearest_cell_index(normalized[2], grid.nz),
    ]
    return MonitorSpec(
        monitor_point_m=list(setup.monitor_point_m),
        monitor_point_normalized=normalized,
        monitor_index=index,
        monitor_quantity=setup.monitor_quantity,
        nearest_cell_policy="nearest_cell_center",
    )


def _dimensionless_mapping(case: dict, geometry_masks: dict[str, np.ndarray]) -> dict[str, Any]:
    setup = case["official_tutorial_setup"]
    grid = case["solver_grid"]
    duct = case["solver_geometry_mapping"]["duct_normalized"]
    y_centers = _centers(int(grid["ny"]))
    duct_height_cells = int(np.count_nonzero((y_centers >= duct["y"][0]) & (y_centers <= duct["y"][1])))
    mapping = DimensionlessMapping(
        duct_length_m=float(setup["duct_length_m"]),
        duct_height_m=float(setup["duct_height_m"]),
        solver_nx=int(grid["nx"]),
        solver_ny=int(grid["ny"]),
        solver_nz=int(grid["nz"]),
        dx_m_if_x_length_controls=float(setup["duct_length_m"]) / float(grid["nx"]),
        dy_m_if_duct_height_controls=float(setup["duct_height_m"]) / float(duct_height_cells),
        inlet_velocity_mps=float(setup["inlet_air_velocity_mps"]),
        official_dt_s=float(setup["official_tutorial_dt_s"]),
        official_total_time_s=float(setup["official_tutorial_total_time_s"]),
        official_time_steps=int(setup["official_tutorial_time_steps"]),
        mapping_scope="preprocessor_case_metadata_only",
        direct_physical_reynolds_validation_allowed=False,
        physical_reynolds_parity_claim_allowed=False,
        tau_margin_validation_required_before_physical_re_claim=True,
    )
    data = to_json_dict(mapping)
    data["duct_height_cells"] = duct_height_cells
    data["fluid_cell_count_for_mapping_context"] = int(geometry_masks["fluid_mask"].sum())
    return data


def _material_mapping(case: dict) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": "material_mapping_compiled",
        "official_material": case["official_material"],
        "current_solver_structural_model": "finite_deformation_mpm",
        "official_structural_model": "Fluent intrinsic FSI / FEM-like structural model",
        "material_constants_available_to_step155": True,
        "fluent_structural_model_equivalence_claim_allowed": False,
        "validation_claim_allowed": False,
    }


def _preprocess_report(
    case: dict,
    geometry_masks: dict[str, np.ndarray],
    boundary_masks: dict[str, np.ndarray],
    fsi_masks: dict[str, np.ndarray],
) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": "preprocess_complete",
        "preprocessor_ready": True,
        "official_tutorial_constants_loaded": True,
        "solver_input_case_written": True,
        "geometry_masks_written": True,
        "boundary_masks_written": True,
        "fsi_interface_masks_written": True,
        "monitor_point_mapped": True,
        "grid": case["solver_grid"],
        "mask_counts": {
            "fluid_cell_count": int(geometry_masks["fluid_mask"].sum()),
            "solid_cell_count": int(geometry_masks["solid_mask"].sum()),
            "flap_solid_cell_count": int(geometry_masks["flap_solid_mask"].sum()),
            "velocity_inlet_cell_count": int(boundary_masks["velocity_inlet_mask"].sum()),
            "pressure_outlet_cell_count": int(boundary_masks["pressure_outlet_mask"].sum()),
            "fsi_wall_cell_count": int(boundary_masks["fsi_wall_mask"].sum()),
            "fluid_interface_cell_count": int(fsi_masks["fluid_interface_mask"].sum()),
            "solid_interface_cell_count": int(fsi_masks["solid_interface_mask"].sum()),
            "monitor_cell_count": int(geometry_masks["monitor_cell_mask"].sum()),
        },
        "geometry_equivalence_claim_allowed": False,
        "validation_claim_allowed": False,
    }


def _validate_setup_constants(setup: dict, material: dict, summary: dict) -> None:
    expected = {
        "duct_length_m": 0.10,
        "duct_height_m": 0.04,
        "flap_height_m": 0.01,
        "flap_thickness_m": 0.003,
        "inlet_air_velocity_mps": 10.0,
        "official_tutorial_time_steps": 50,
        "official_tutorial_dt_s": 0.0005,
        "official_tutorial_total_time_s": 0.025,
    }
    for key, value in expected.items():
        if key not in setup:
            raise ValueError(f"missing official tutorial setup constant: {key}")
        if not math.isclose(float(setup[key]), float(value), rel_tol=1.0e-12, abs_tol=1.0e-15):
            raise ValueError(f"inconsistent official tutorial setup constant: {key}")
    for key in ("monitor_point_m", "monitor_quantity", "outlet_type", "half_domain_mode"):
        if key not in setup:
            raise ValueError(f"missing official tutorial setup constant: {key}")
    for key in ("solid_density_kg_m3", "youngs_modulus_pa", "poisson_ratio"):
        if key not in material:
            raise ValueError(f"missing official material constant: {key}")
    if summary.get("status") != "official_tutorial_setup_parity_run_complete":
        raise ValueError("Step154 requires Step153 setup parity completion")


def _nearest_cell_index(norm: float, n: int) -> int:
    return max(0, min(n - 1, int(math.floor(float(norm) * float(n) - 0.5 + 0.5))))


def _centers(n: int) -> np.ndarray:
    return (np.arange(n, dtype=np.float64) + 0.5) / float(n)


def _between(values: np.ndarray, interval: list[float]) -> np.ndarray:
    return (values >= float(interval[0])) & (values <= float(interval[1]))


def _adjacent6(mask: np.ndarray) -> np.ndarray:
    out = np.zeros_like(mask, dtype=bool)
    out[1:, :, :] |= mask[:-1, :, :]
    out[:-1, :, :] |= mask[1:, :, :]
    out[:, 1:, :] |= mask[:, :-1, :]
    out[:, :-1, :] |= mask[:, 1:, :]
    out[:, :, 1:] |= mask[:, :, :-1]
    out[:, :, :-1] |= mask[:, :, 1:]
    return out


def _read_json(path: Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_json_optional(path: Path) -> dict:
    if not Path(path).is_file():
        return {}
    return _read_json(path)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_json_dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _display_path(path: Path | str) -> str:
    try:
        return str(Path(path).relative_to(_repo_root()))
    except ValueError:
        return str(path)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]
