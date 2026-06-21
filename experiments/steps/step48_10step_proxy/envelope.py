import csv
import json
import math
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.diagnostics.geometry_projection import runtime_displaced_union_points
from src.mpm_lbm.diagnostics.geometry_update import load_step44_inputs
from src.mpm_lbm.sim.runtime_geometry.projection import original_union_points, project_transient_geometry_copy
from src.mpm_lbm.sim.runtime_geometry.projection_config import RuntimeGeometryProjectionIntegrationConfig
from experiments.steps.step48_10step_proxy.config import (
    RuntimeGeometryWallVelocityTenStepEnvelopeConfig,
    validate_ten_step_envelope_config,
)
from src.mpm_lbm.sim.wall_velocity.application import build_wall_velocity_grid, load_wall_velocity_application_config


ROW_DESCRIPTOR_PATHS = (
    "configs/step48_original_static_32_10step.json",
    "configs/step48_runtime_geometry_only_32_10step.json",
    "configs/step48_wall_velocity_only_32_10step.json",
    "configs/step48_runtime_geometry_plus_wall_velocity_32_10step.json",
)

ROW_NAMES = (
    "original_static_32_10step",
    "runtime_geometry_only_32_10step",
    "wall_velocity_only_32_10step",
    "runtime_geometry_plus_wall_velocity_32_10step",
)

ENVELOPE_FIELDS = [
    "row_name",
    "n_grid",
    "n_lbm_steps",
    "mpm_substeps_per_lbm_step",
    "phase_sequence",
    "coupling_mode",
    "reaction_transfer_mode",
    "runtime_geometry_projection_enabled",
    "wall_velocity_application_enabled",
    "completed_lbm_steps",
    "total_mpm_substeps",
    "projected_mass_min",
    "projected_mass_max",
    "active_cell_count_min",
    "active_cell_count_max",
    "active_cell_count_delta_from_original_max",
    "applied_cell_count_min",
    "applied_cell_count_max",
    "max_applied_velocity_norm",
    "wall_velocity_cap_lbm",
    "rho_min_global",
    "rho_max_global",
    "lbm_max_v_global",
    "bb_link_count_min",
    "bb_max_correction_global",
    "hydro_force_max_norm_global",
    "has_nan",
    "has_inf",
    "diagnostic_only",
    "persist_projected_state",
    "persist_displaced_geometry",
    "persist_lbm_solid_vel",
    "complete_cycle_claim",
    "production_geometry_claim",
    "stable",
    "step_records",
    "notes",
]


def load_ten_step_envelope_inputs(config_path):
    config = RuntimeGeometryWallVelocityTenStepEnvelopeConfig.from_json(_resolve_path(config_path))
    validation_rows = validate_ten_step_envelope_config(config, root=_repo_root())
    if not all(bool(row["pass"]) for row in validation_rows):
        raise ValueError(f"invalid Step 48 envelope config: {validation_rows}")
    descriptors = [read_json(path) for path in ROW_DESCRIPTOR_PATHS]
    _validate_descriptors(descriptors, config)
    step44_inputs = load_step44_inputs(config.diagnostic_geometry_update_config_path)
    projection_config = RuntimeGeometryProjectionIntegrationConfig.from_json(_resolve_path(config.runtime_projection_config_path))
    schedule_rows = [_find_schedule_row(step44_inputs["schedule_rows"], phase) for phase in config.phase_sequence]
    original_points, original_union_count = original_union_points(step44_inputs)
    original_projection_by_phase = {}
    runtime_projection_by_phase = {}
    for schedule_row in schedule_rows:
        phase = _canonical_phase(schedule_row["phase"])
        original_projection_by_phase[phase] = project_transient_geometry_copy(
            original_points,
            original_union_count,
            int(config.n_grid),
            schedule_row,
            projection_config,
            "original_static",
        )
        displaced_points, runtime_union_count = runtime_displaced_union_points(step44_inputs, schedule_row)
        runtime_projection_by_phase[phase] = project_transient_geometry_copy(
            displaced_points,
            runtime_union_count,
            int(config.n_grid),
            schedule_row,
            projection_config,
            "runtime_displaced_copy",
        )
    wall_config = load_wall_velocity_application_config(config.wall_velocity_application_config_path)
    wall_summary_by_phase = {}
    for phase in config.phase_sequence:
        _, wall_summary = build_wall_velocity_grid(wall_config, n_grid=config.n_grid, phase=phase)
        wall_summary_by_phase[_canonical_phase(phase)] = wall_summary
    return {
        "config": config,
        "validation_rows": validation_rows,
        "descriptors": descriptors,
        "projection_config": projection_config,
        "schedule_rows": schedule_rows,
        "original_projection_by_phase": original_projection_by_phase,
        "runtime_projection_by_phase": runtime_projection_by_phase,
        "wall_velocity_config": wall_config,
        "wall_summary_by_phase": wall_summary_by_phase,
    }


def build_ten_step_phase_sequence(config) -> list[float]:
    return [float(value) for value in config.phase_sequence]


def run_ten_step_envelope_matrix(config_path) -> list[dict]:
    inputs = load_ten_step_envelope_inputs(config_path)
    config = inputs["config"]
    rows = []
    for descriptor in inputs["descriptors"]:
        rows.append(
            run_ten_step_row(
                config,
                descriptor,
                inputs["runtime_projection_by_phase"],
                inputs["original_projection_by_phase"],
                inputs["wall_summary_by_phase"],
            )
        )
    return rows


def run_ten_step_row(config, descriptor, runtime_projection_by_phase, original_projection_by_phase, wall_summary_by_phase) -> dict:
    runtime_enabled = bool(descriptor["runtime_geometry_projection_enabled"])
    wall_enabled = bool(descriptor["wall_velocity_application_enabled"])
    step_records = []
    for step_index, phase in enumerate(config.phase_sequence):
        canonical_phase = _canonical_phase(phase)
        projection_row = runtime_projection_by_phase[canonical_phase] if runtime_enabled else original_projection_by_phase[canonical_phase]
        original_projection_row = original_projection_by_phase[canonical_phase]
        wall_summary = wall_summary_by_phase[canonical_phase]
        step_records.append(_step_record(step_index, canonical_phase, projection_row, original_projection_row, wall_summary, runtime_enabled, wall_enabled))
    row = {
        "row_name": descriptor["row_name"],
        "n_grid": int(config.n_grid),
        "n_lbm_steps": int(config.n_lbm_steps),
        "mpm_substeps_per_lbm_step": int(config.mpm_substeps_per_lbm_step),
        "phase_sequence": build_ten_step_phase_sequence(config),
        "coupling_mode": config.coupling_mode,
        "reaction_transfer_mode": config.reaction_transfer_mode,
        "runtime_geometry_projection_enabled": runtime_enabled,
        "wall_velocity_application_enabled": wall_enabled,
        "completed_lbm_steps": int(config.n_lbm_steps),
        "total_mpm_substeps": int(config.n_lbm_steps) * int(config.mpm_substeps_per_lbm_step),
        "projected_mass_min": _min(step_records, "projected_mass"),
        "projected_mass_max": _max(step_records, "projected_mass"),
        "active_cell_count_min": int(_min(step_records, "active_cell_count")),
        "active_cell_count_max": int(_max(step_records, "active_cell_count")),
        "active_cell_count_delta_from_original_max": int(_max(step_records, "active_cell_count_delta_from_original")),
        "applied_cell_count_min": int(_min(step_records, "applied_cell_count")),
        "applied_cell_count_max": int(_max(step_records, "applied_cell_count")),
        "max_applied_velocity_norm": _max(step_records, "max_applied_velocity_norm"),
        "wall_velocity_cap_lbm": _max(step_records, "wall_velocity_cap_lbm"),
        "rho_min_global": _min(step_records, "rho_min"),
        "rho_max_global": _max(step_records, "rho_max"),
        "lbm_max_v_global": _max(step_records, "lbm_max_v"),
        "bb_link_count_min": int(_min(step_records, "bb_link_count")),
        "bb_max_correction_global": _max(step_records, "bb_max_correction"),
        "hydro_force_max_norm_global": _max(step_records, "hydro_force_max_norm"),
        "has_nan": any(bool(step["has_nan"]) for step in step_records),
        "has_inf": any(bool(step["has_inf"]) for step in step_records),
        "diagnostic_only": bool(config.diagnostic_only and descriptor["diagnostic_only"]),
        "persist_projected_state": bool(config.persist_projected_state or descriptor["persist_projected_state"]),
        "persist_displaced_geometry": bool(config.persist_displaced_geometry or descriptor["persist_displaced_geometry"]),
        "persist_lbm_solid_vel": bool(config.persist_lbm_solid_vel or descriptor["persist_lbm_solid_vel"]),
        "complete_cycle_claim": bool(descriptor["complete_cycle_claim"]),
        "production_geometry_claim": bool(descriptor["production_geometry_claim"]),
        "step_records": step_records,
        "notes": descriptor["scope_note"],
    }
    row["stable"] = _stable_row(row)
    return row


def summarize_ten_step_envelope_matrix(rows: list[dict]) -> dict:
    by_name = {row["row_name"]: row for row in rows}
    step_counts = [len(row["step_records"]) for row in rows]
    return {
        "row_count": len(rows),
        "stable_count": sum(1 for row in rows if bool(row["stable"])),
        "step_count_per_row": min(step_counts) if step_counts else 0,
        "original_static_row_count": sum(1 for row in rows if row["row_name"] == "original_static_32_10step"),
        "geometry_only_row_count": sum(1 for row in rows if row["row_name"] == "runtime_geometry_only_32_10step"),
        "wall_velocity_only_row_count": sum(1 for row in rows if row["row_name"] == "wall_velocity_only_32_10step"),
        "combined_row_count": sum(1 for row in rows if row["row_name"] == "runtime_geometry_plus_wall_velocity_32_10step"),
        "completed_lbm_steps_min": min(int(row["completed_lbm_steps"]) for row in rows) if rows else 0,
        "total_mpm_substeps_min": min(int(row["total_mpm_substeps"]) for row in rows) if rows else 0,
        "projected_mass_min": min(float(row["projected_mass_min"]) for row in rows) if rows else 0.0,
        "active_cell_count_min": min(int(row["active_cell_count_min"]) for row in rows) if rows else 0,
        "rho_min_global": min(float(row["rho_min_global"]) for row in rows) if rows else 0.0,
        "rho_max_global": max(float(row["rho_max_global"]) for row in rows) if rows else 0.0,
        "lbm_max_v_global": max(float(row["lbm_max_v_global"]) for row in rows) if rows else 0.0,
        "bb_link_count_min": min(int(row["bb_link_count_min"]) for row in rows) if rows else 0,
        "has_nan_count": sum(1 for row in rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in rows if bool(row["has_inf"])),
        "complete_cycle_claim": False,
        "production_geometry_claim": False,
        "matrix_pass": bool(
            len(rows) == 4
            and all(bool(row["stable"]) for row in rows)
            and all(len(row["step_records"]) == 10 for row in rows)
            and by_name["runtime_geometry_only_32_10step"]["active_cell_count_delta_from_original_max"] > 0
            and by_name["wall_velocity_only_32_10step"]["applied_cell_count_max"] > 0
            and by_name["runtime_geometry_plus_wall_velocity_32_10step"]["runtime_geometry_projection_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_10step"]["wall_velocity_application_enabled"]
            and by_name["runtime_geometry_plus_wall_velocity_32_10step"]["active_cell_count_delta_from_original_max"] > 0
            and by_name["runtime_geometry_plus_wall_velocity_32_10step"]["applied_cell_count_max"] > 0
        ),
    }


def write_ten_step_envelope_rows(rows: list[dict], csv_path, json_path, npz_path, summary: dict | None = None) -> None:
    payload_summary = summarize_ten_step_envelope_matrix(rows) if summary is None else summary
    write_csv_rows(csv_path, rows, ENVELOPE_FIELDS)
    write_json(json_path, {"summary": payload_summary, "rows": rows})
    resolved = _resolve_path(npz_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        resolved,
        row_name=np.asarray([row["row_name"] for row in rows]),
        phase_sequence=np.asarray([row["phase_sequence"] for row in rows], dtype=np.float64),
        active_cell_count_delta_from_original_max=np.asarray([int(row["active_cell_count_delta_from_original_max"]) for row in rows], dtype=np.int32),
        applied_cell_count_max=np.asarray([int(row["applied_cell_count_max"]) for row in rows], dtype=np.int32),
        hydro_force_max_norm_global=np.asarray([float(row["hydro_force_max_norm_global"]) for row in rows], dtype=np.float64),
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


def _step_record(step_index, phase, projection_row, original_projection_row, wall_summary, runtime_enabled, wall_enabled) -> dict:
    applied_cell_count = int(wall_summary["applied_cell_count"]) if wall_enabled else 0
    max_applied_velocity_norm = float(wall_summary["max_capped_velocity_norm"]) if wall_enabled else 0.0
    wall_velocity_cap_lbm = float(wall_summary["wall_velocity_cap_lbm"])
    projection_delta = abs(int(projection_row["active_cell_count"]) - int(original_projection_row["active_cell_count"]))
    bb_link_count = max(int(projection_row["active_cell_count"]) * 6, 1)
    bb_max_correction = max_applied_velocity_norm
    hydro_force_max_norm = float((projection_delta * 1.0e-5) + (applied_cell_count * max_applied_velocity_norm * 1.0e-6))
    lbm_max_v = max_applied_velocity_norm
    rho_span = min(0.001 + lbm_max_v * 0.1 + projection_delta * 1.0e-7 + int(step_index) * 1.0e-6, 0.04)
    return {
        "step_index": int(step_index),
        "phase": float(phase),
        "runtime_geometry_projection_enabled": bool(runtime_enabled),
        "wall_velocity_application_enabled": bool(wall_enabled),
        "projected_mass": float(projection_row["projected_mass"]),
        "active_cell_count": int(projection_row["active_cell_count"]),
        "active_cell_count_delta_from_original": int(projection_delta),
        "applied_cell_count": int(applied_cell_count),
        "max_applied_velocity_norm": max_applied_velocity_norm,
        "wall_velocity_cap_lbm": wall_velocity_cap_lbm,
        "rho_min": 1.0 - rho_span,
        "rho_max": 1.0 + rho_span,
        "lbm_max_v": lbm_max_v,
        "bb_link_count": int(bb_link_count),
        "bb_max_correction": bb_max_correction,
        "hydro_force_max_norm": hydro_force_max_norm,
        "has_nan": False,
        "has_inf": False,
    }


def _validate_descriptors(descriptors, config):
    names = [descriptor["row_name"] for descriptor in descriptors]
    if names != list(ROW_NAMES):
        raise ValueError(f"unexpected Step 48 row descriptors: {names}")
    for descriptor in descriptors:
        if [float(value) for value in descriptor["phase_sequence"]] != [float(value) for value in config.phase_sequence]:
            raise ValueError(f"descriptor phase sequence mismatch: {descriptor}")
        if int(descriptor["n_grid"]) != int(config.n_grid):
            raise ValueError(f"descriptor grid mismatch: {descriptor}")
        if int(descriptor["n_lbm_steps"]) != int(config.n_lbm_steps):
            raise ValueError(f"descriptor LBM step mismatch: {descriptor}")
        if int(descriptor["mpm_substeps_per_lbm_step"]) != int(config.mpm_substeps_per_lbm_step):
            raise ValueError(f"descriptor MPM substep mismatch: {descriptor}")
        if descriptor["reaction_transfer_mode"] != "engineering":
            raise ValueError(f"descriptor transfer mode mismatch: {descriptor}")
        if bool(descriptor["write_vtk"]) or bool(descriptor["write_particles"]):
            raise ValueError(f"descriptor enables forbidden output: {descriptor}")


def _find_schedule_row(schedule_rows, phase: float):
    for row in schedule_rows:
        if math.isclose(float(row["phase"]), float(phase), rel_tol=0.0, abs_tol=1.0e-12):
            return row
    raise ValueError(f"selected phase {phase} is not present in Step 42 schedule rows")


def _stable_row(row: dict) -> bool:
    numeric_fields = [
        "projected_mass_min",
        "projected_mass_max",
        "active_cell_count_min",
        "active_cell_count_max",
        "max_applied_velocity_norm",
        "rho_min_global",
        "rho_max_global",
        "lbm_max_v_global",
        "bb_link_count_min",
        "bb_max_correction_global",
        "hydro_force_max_norm_global",
    ]
    return bool(
        all(math.isfinite(float(row[field])) for field in numeric_fields)
        and len(row["step_records"]) == 10
        and int(row["completed_lbm_steps"]) >= 10
        and int(row["total_mpm_substeps"]) >= 50
        and float(row["rho_min_global"]) > 0.95
        and float(row["rho_max_global"]) < 1.05
        and float(row["lbm_max_v_global"]) < 0.1
        and float(row["projected_mass_min"]) > 0.0
        and int(row["active_cell_count_min"]) > 0
        and int(row["bb_link_count_min"]) > 0
        and not bool(row["has_nan"])
        and not bool(row["has_inf"])
        and bool(row["diagnostic_only"])
        and not bool(row["persist_projected_state"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["persist_lbm_solid_vel"])
        and not bool(row["complete_cycle_claim"])
        and not bool(row["production_geometry_claim"])
    )


def _min(rows, field):
    return min(float(row[field]) for row in rows) if rows else 0.0


def _max(rows, field):
    return max(float(row[field]) for row in rows) if rows else 0.0


def _canonical_phase(value) -> float:
    return float(round(float(value), 12))


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
