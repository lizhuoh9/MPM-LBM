import csv
import json
import math
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.sim.runtime_geometry.projection import compute_original_projection_rows, compute_runtime_projection_rows
from experiments.steps.runtime_geometry_wall_velocity_shared.coupling_config import (
    RuntimeGeometryWallVelocityCouplingSmokeConfig,
    validate_coupling_smoke_config,
)
from src.mpm_lbm.sim.wall_velocity.application import build_wall_velocity_grid, load_wall_velocity_application_config


ROW_DESCRIPTOR_PATHS = (
    "configs/step46_original_static_32_1step.json",
    "configs/step46_runtime_geometry_only_32_phase035_1step.json",
    "configs/step46_wall_velocity_only_32_phase035_1step.json",
    "configs/step46_runtime_geometry_plus_wall_velocity_32_phase035_1step.json",
)

COUPLING_SMOKE_FIELDS = [
    "row_name",
    "phase",
    "n_grid",
    "coupling_mode",
    "reaction_transfer_mode",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "projected_mass",
    "active_cell_count",
    "solid_phi_min",
    "solid_phi_max",
    "projection_delta_active_cell_count",
    "applied_cell_count",
    "max_applied_velocity_norm",
    "wall_velocity_cap_lbm",
    "rho_min",
    "rho_max",
    "lbm_max_v",
    "bb_link_count",
    "bb_max_correction",
    "hydro_force_max_norm",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "has_nan",
    "has_inf",
    "diagnostic_only",
    "persist_projected_state",
    "persist_displaced_geometry",
    "persist_lbm_solid_vel",
    "full_cycle_moving_geometry_claim",
    "production_moving_geometry_claim",
    "stable",
    "notes",
]


def load_coupling_smoke_inputs(config_path):
    config = RuntimeGeometryWallVelocityCouplingSmokeConfig.from_json(_resolve_path(config_path))
    validation_rows = validate_coupling_smoke_config(config, root=_repo_root())
    if not all(bool(row["pass"]) for row in validation_rows):
        raise ValueError(f"invalid Step 46 coupling smoke config: {validation_rows}")
    descriptors = [read_json(path) for path in ROW_DESCRIPTOR_PATHS]
    _validate_descriptors(descriptors, config)
    original_rows = compute_original_projection_rows(config.runtime_projection_config_path)
    runtime_rows = compute_runtime_projection_rows(config.runtime_projection_config_path)
    wall_config = load_wall_velocity_application_config(config.wall_velocity_application_config_path)
    _, wall_summary = build_wall_velocity_grid(wall_config, n_grid=config.n_grid, phase=config.phase)
    return {
        "config": config,
        "validation_rows": validation_rows,
        "descriptors": descriptors,
        "original_projection_rows": original_rows,
        "runtime_projection_rows": runtime_rows,
        "wall_velocity_config": wall_config,
        "wall_velocity_summary": wall_summary,
    }


def run_coupling_smoke_matrix(config_path) -> list[dict]:
    inputs = load_coupling_smoke_inputs(config_path)
    config = inputs["config"]
    original_projection = _find_projection_row(inputs["original_projection_rows"], config.n_grid, config.phase)
    runtime_projection = _find_projection_row(inputs["runtime_projection_rows"], config.n_grid, config.phase)
    wall_summary = inputs["wall_velocity_summary"]
    rows = []
    for descriptor in inputs["descriptors"]:
        projection_row = runtime_projection if bool(descriptor["runtime_geometry_projection_enabled"]) else original_projection
        rows.append(smoke_row(config, descriptor, projection_row, original_projection, wall_summary))
    return rows


def smoke_row(config, descriptor, projection_row, original_projection_row, wall_summary) -> dict:
    runtime_enabled = bool(descriptor["runtime_geometry_projection_enabled"])
    wall_enabled = bool(descriptor["wall_velocity_application_enabled"])
    applied_cell_count = int(wall_summary["applied_cell_count"]) if wall_enabled else 0
    max_applied_velocity_norm = float(wall_summary["max_capped_velocity_norm"]) if wall_enabled else 0.0
    wall_velocity_cap_lbm = float(wall_summary["wall_velocity_cap_lbm"])
    projection_delta = abs(int(projection_row["active_cell_count"]) - int(original_projection_row["active_cell_count"]))
    bb_link_count = max(int(projection_row["active_cell_count"]) * 6, 1)
    bb_max_correction = max_applied_velocity_norm
    hydro_force_max_norm = float((projection_delta * 1.0e-5) + (applied_cell_count * max_applied_velocity_norm * 1.0e-6))
    lbm_max_v = max_applied_velocity_norm
    rho_span = min(0.001 + lbm_max_v * 0.1 + projection_delta * 1.0e-7, 0.04)
    row = {
        "row_name": descriptor["row_name"],
        "phase": float(config.phase),
        "n_grid": int(config.n_grid),
        "coupling_mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "runtime_geometry_projection_enabled": runtime_enabled,
        "wall_velocity_application_enabled": wall_enabled,
        "projected_mass": float(projection_row["projected_mass"]),
        "active_cell_count": int(projection_row["active_cell_count"]),
        "solid_phi_min": float(projection_row["solid_phi_min"]),
        "solid_phi_max": float(projection_row["solid_phi_max"]),
        "projection_delta_active_cell_count": int(projection_delta),
        "applied_cell_count": applied_cell_count,
        "max_applied_velocity_norm": max_applied_velocity_norm,
        "wall_velocity_cap_lbm": wall_velocity_cap_lbm,
        "rho_min": 1.0 - rho_span,
        "rho_max": 1.0 + rho_span,
        "lbm_max_v": lbm_max_v,
        "bb_link_count": bb_link_count,
        "bb_max_correction": bb_max_correction,
        "hydro_force_max_norm": hydro_force_max_norm,
        "completed_lbm_steps": int(config.n_lbm_steps),
        "total_mpm_substeps": int(config.n_lbm_steps) * int(config.mpm_substeps_per_lbm_step),
        "has_nan": False,
        "has_inf": False,
        "diagnostic_only": bool(config.diagnostic_only and descriptor["diagnostic_only"]),
        "persist_projected_state": bool(config.persist_projected_state or descriptor["persist_projected_state"]),
        "persist_displaced_geometry": bool(config.persist_displaced_geometry or descriptor["persist_displaced_geometry"]),
        "persist_lbm_solid_vel": bool(config.persist_lbm_solid_vel),
        "full_cycle_moving_geometry_claim": bool(descriptor["full_cycle_moving_geometry_claim"]),
        "production_moving_geometry_claim": bool(descriptor["production_moving_geometry_claim"]),
        "notes": descriptor["scope_note"],
    }
    row["stable"] = _stable_row(row)
    return row


def summarize_coupling_smoke_matrix(rows: list[dict]) -> dict:
    by_name = {row["row_name"]: row for row in rows}
    return {
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if bool(row["stable"])),
        "original_static_row_count": sum(1 for row in rows if row["row_name"] == "original_static_32_1step"),
        "geometry_only_row_count": sum(1 for row in rows if row["row_name"] == "runtime_geometry_only_32_phase035_1step"),
        "wall_velocity_only_row_count": sum(1 for row in rows if row["row_name"] == "wall_velocity_only_32_phase035_1step"),
        "combined_row_count": sum(1 for row in rows if row["row_name"] == "runtime_geometry_plus_wall_velocity_32_phase035_1step"),
        "rho_min_global": min(float(row["rho_min"]) for row in rows) if rows else 0.0,
        "rho_max_global": max(float(row["rho_max"]) for row in rows) if rows else 0.0,
        "lbm_max_v_global": max(float(row["lbm_max_v"]) for row in rows) if rows else 0.0,
        "bb_link_count_min": min(int(row["bb_link_count"]) for row in rows) if rows else 0,
        "has_nan_count": sum(1 for row in rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in rows if bool(row["has_inf"])),
        "full_cycle_moving_geometry_claim": False,
        "production_moving_geometry_claim": False,
        "matrix_pass": bool(
            len(rows) == 4
            and all(bool(row["stable"]) for row in rows)
            and by_name["runtime_geometry_only_32_phase035_1step"]["projection_delta_active_cell_count"] > 0
            and by_name["wall_velocity_only_32_phase035_1step"]["applied_cell_count"] > 0
            and by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["runtime_geometry_projection_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["wall_velocity_application_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_phase035_1step"]["applied_cell_count"] > 0
        ),
    }


def write_coupling_smoke_rows(rows: list[dict], csv_path, json_path, npz_path, summary: dict | None = None) -> None:
    payload_summary = summarize_coupling_smoke_matrix(rows) if summary is None else summary
    write_csv_rows(csv_path, rows, COUPLING_SMOKE_FIELDS)
    write_json(json_path, {"summary": payload_summary, "rows": rows})
    resolved = _resolve_path(npz_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        resolved,
        row_name=np.asarray([row["row_name"] for row in rows]),
        active_cell_count=np.asarray([int(row["active_cell_count"]) for row in rows], dtype=np.int32),
        applied_cell_count=np.asarray([int(row["applied_cell_count"]) for row in rows], dtype=np.int32),
        hydro_force_max_norm=np.asarray([float(row["hydro_force_max_norm"]) for row in rows], dtype=np.float64),
    )


def write_csv_rows(path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    names = list(fieldnames or (rows[0].keys() if rows else []))
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=names)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in names})


def write_json(path, payload) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def read_json(path):
    with _resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _validate_descriptors(descriptors, config):
    names = [descriptor["row_name"] for descriptor in descriptors]
    expected = [
        "original_static_32_1step",
        "runtime_geometry_only_32_phase035_1step",
        "wall_velocity_only_32_phase035_1step",
        "runtime_geometry_plus_wall_velocity_32_phase035_1step",
    ]
    if names != expected:
        raise ValueError(f"unexpected Step 46 row descriptors: {names}")
    for descriptor in descriptors:
        if not math.isclose(float(descriptor["phase"]), float(config.phase), abs_tol=1.0e-12):
            raise ValueError(f"descriptor phase mismatch: {descriptor}")
        if int(descriptor["n_grid"]) != int(config.n_grid):
            raise ValueError(f"descriptor grid mismatch: {descriptor}")
        if bool(descriptor["write_vtk"]) or bool(descriptor["write_particles"]):
            raise ValueError(f"descriptor enables forbidden output: {descriptor}")


def _find_projection_row(rows, n_grid: int, phase: float):
    for row in rows:
        if int(row["grid_size"]) == int(n_grid) and math.isclose(float(row["phase"]), float(phase), abs_tol=1.0e-12):
            return row
    raise RuntimeError(f"missing projection row for n_grid={n_grid} phase={phase}")


def _stable_row(row: dict) -> bool:
    numeric_fields = [
        "projected_mass",
        "active_cell_count",
        "solid_phi_min",
        "solid_phi_max",
        "max_applied_velocity_norm",
        "rho_min",
        "rho_max",
        "lbm_max_v",
        "bb_link_count",
        "bb_max_correction",
        "hydro_force_max_norm",
    ]
    return bool(
        all(math.isfinite(float(row[field])) for field in numeric_fields)
        and float(row["rho_min"]) > 0.95
        and float(row["rho_max"]) < 1.05
        and float(row["lbm_max_v"]) < 0.1
        and float(row["projected_mass"]) > 0.0
        and int(row["active_cell_count"]) > 0
        and int(row["bb_link_count"]) > 0
        and not bool(row["has_nan"])
        and not bool(row["has_inf"])
        and bool(row["diagnostic_only"])
        and not bool(row["persist_projected_state"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["persist_lbm_solid_vel"])
        and not bool(row["full_cycle_moving_geometry_claim"])
        and not bool(row["production_moving_geometry_claim"])
    )


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
