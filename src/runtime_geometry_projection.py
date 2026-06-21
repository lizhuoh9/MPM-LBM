import csv
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from .diagnostic_geometry_projection import runtime_displaced_union_points
from .diagnostic_geometry_update import _canonical_phase, geometry_and_region_hashes, load_step44_inputs, selected_schedule_rows
from .runtime_geometry_projection_config import (
    RuntimeGeometryProjectionIntegrationConfig,
    validate_runtime_geometry_projection_config,
)


RUNTIME_PROJECTION_FIELDS = [
    "grid_size",
    "phase",
    "sample_index",
    "source_kind",
    "projected_mass",
    "active_cell_count",
    "solid_phi_min",
    "solid_phi_max",
    "boundary_cell_count",
    "region_coverage_count",
    "region_coverage",
    "bbox_cell_min_x",
    "bbox_cell_min_y",
    "bbox_cell_min_z",
    "bbox_cell_max_x",
    "bbox_cell_max_y",
    "bbox_cell_max_z",
    "has_nan",
    "has_inf",
    "transient_only",
    "persist_projected_state",
    "persist_displaced_geometry",
    "apply_to_driver_state",
    "apply_to_default_lbm_state",
    "apply_to_default_mpm_state",
    "apply_to_default_projection_state",
    "update_dynamic_solid",
    "projection_pass",
    "occupancy_hash",
    "notes",
]


def load_runtime_projection_inputs(config_path):
    config = RuntimeGeometryProjectionIntegrationConfig.from_json(_resolve_path(config_path))
    validation_rows = validate_runtime_geometry_projection_config(config, root=_repo_root())
    if not all(bool(row["pass"]) for row in validation_rows):
        raise ValueError(f"invalid Step 45 runtime projection config: {validation_rows}")
    step44_inputs = load_step44_inputs(config.diagnostic_geometry_update_config_path)
    _assert_step44_matches_step45(config, step44_inputs["config"])
    return {
        "config": config,
        "validation_rows": validation_rows,
        "step44_inputs": step44_inputs,
    }


def compute_runtime_projection_rows(config_path) -> list[dict]:
    inputs = load_runtime_projection_inputs(config_path)
    config = inputs["config"]
    step44_inputs = inputs["step44_inputs"]
    rows = []
    for schedule_row in selected_schedule_rows(step44_inputs):
        displaced_points, union_count = runtime_displaced_union_points(step44_inputs, schedule_row)
        for grid_size in config.grid_sizes:
            rows.append(project_transient_geometry_copy(displaced_points, union_count, int(grid_size), schedule_row, config, "runtime_displaced_copy"))
    return rows


def compute_original_projection_rows(config_path) -> list[dict]:
    inputs = load_runtime_projection_inputs(config_path)
    config = inputs["config"]
    step44_inputs = inputs["step44_inputs"]
    original_points, union_count = original_union_points(step44_inputs)
    rows = []
    for schedule_row in selected_schedule_rows(step44_inputs):
        for grid_size in config.grid_sizes:
            rows.append(project_transient_geometry_copy(original_points, union_count, int(grid_size), schedule_row, config, "original_static"))
    return rows


def original_union_points(step44_inputs):
    config = step44_inputs["config"]
    points = np.asarray(step44_inputs["points"], dtype=np.float64)
    masks = step44_inputs["masks"]
    union_mask = np.zeros(len(points), dtype=bool)
    for region_id in config.tracked_regions:
        union_mask |= np.asarray(masks[region_id], dtype=bool)
    return points[union_mask].copy(), int(np.count_nonzero(union_mask))


def project_transient_geometry_copy(points, union_count: int, grid_size: int, schedule_row, config: RuntimeGeometryProjectionIntegrationConfig, source_kind: str) -> dict:
    pts = _as_points(points)
    has_nan = bool(np.isnan(pts).any())
    has_inf = bool(np.isinf(pts).any())
    clipped = np.clip(pts, 0.0, np.nextafter(1.0, 0.0))
    indices = np.floor(clipped * float(grid_size)).astype(np.int64)
    indices = np.clip(indices, 0, grid_size - 1)
    unique = _unique_cell_indices(indices)
    active_cell_count = int(len(unique))
    projected_mass = float(len(pts)) / float(max(union_count, 1))
    solid_phi_min = 0.0
    solid_phi_max = 1.0 if active_cell_count > 0 else 0.0
    bbox_min, bbox_max = _bbox_cells(unique)
    boundary_cell_count = _boundary_cell_count(unique, grid_size)
    region_coverage = float(active_cell_count) / float(grid_size**3)
    row = {
        "grid_size": int(grid_size),
        "phase": _canonical_phase(schedule_row["phase"]),
        "sample_index": int(schedule_row["sample_index"]),
        "source_kind": source_kind,
        "projected_mass": projected_mass,
        "active_cell_count": active_cell_count,
        "solid_phi_min": solid_phi_min,
        "solid_phi_max": solid_phi_max,
        "boundary_cell_count": boundary_cell_count,
        "region_coverage_count": active_cell_count,
        "region_coverage": region_coverage,
        "bbox_cell_min_x": int(bbox_min[0]),
        "bbox_cell_min_y": int(bbox_min[1]),
        "bbox_cell_min_z": int(bbox_min[2]),
        "bbox_cell_max_x": int(bbox_max[0]),
        "bbox_cell_max_y": int(bbox_max[1]),
        "bbox_cell_max_z": int(bbox_max[2]),
        "has_nan": has_nan,
        "has_inf": has_inf,
        "transient_only": bool(config.diagnostic_only),
        "persist_projected_state": bool(config.persist_projected_state),
        "persist_displaced_geometry": bool(config.persist_displaced_geometry),
        "apply_to_driver_state": bool(config.apply_to_driver_state),
        "apply_to_default_lbm_state": bool(config.apply_to_default_lbm_state),
        "apply_to_default_mpm_state": bool(config.apply_to_default_mpm_state),
        "apply_to_default_projection_state": bool(config.apply_to_default_projection_state),
        "update_dynamic_solid": bool(config.update_dynamic_solid),
        "occupancy_hash": _occupancy_hash(unique, grid_size),
        "notes": "Step 45 transient projection integration smoke; no persistent LBM/projected-state update",
    }
    row["projection_pass"] = _projection_pass(row)
    return row


def summarize_runtime_projection_rows(rows: list[dict], config: RuntimeGeometryProjectionIntegrationConfig) -> dict:
    phases = sorted({float(row["phase"]) for row in rows})
    grids = sorted({int(row["grid_size"]) for row in rows})
    no_persistent_state_pass = all(
        not bool(row["persist_projected_state"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["apply_to_driver_state"])
        and not bool(row["apply_to_default_lbm_state"])
        and not bool(row["apply_to_default_mpm_state"])
        and not bool(row["apply_to_default_projection_state"])
        and not bool(row["update_dynamic_solid"])
        for row in rows
    )
    return {
        "row_count": len(rows),
        "grid_size_count": len(grids),
        "grid_sizes": grids,
        "phase_count": len(phases),
        "selected_phases": phases,
        "projection_pass_count": sum(1 for row in rows if bool(row["projection_pass"])),
        "min_projected_mass": min(float(row["projected_mass"]) for row in rows) if rows else 0.0,
        "min_active_cell_count": min(int(row["active_cell_count"]) for row in rows) if rows else 0,
        "max_solid_phi_max": max(float(row["solid_phi_max"]) for row in rows) if rows else 0.0,
        "has_nan_count": sum(1 for row in rows if bool(row["has_nan"])),
        "has_inf_count": sum(1 for row in rows if bool(row["has_inf"])),
        "transient_only_pass": all(bool(row["transient_only"]) for row in rows),
        "no_persistent_state_pass": no_persistent_state_pass,
        "runtime_projection_integration_pass": bool(
            len(rows) == len(config.selected_phases) * len(config.grid_sizes)
            and phases == list(config.selected_phases)
            and grids == list(config.grid_sizes)
            and all(bool(row["projection_pass"]) for row in rows)
            and no_persistent_state_pass
        ),
    }


def write_runtime_projection_rows(rows: list[dict], csv_path, json_path, summary: dict | None = None) -> None:
    payload_summary = summarize_runtime_projection_rows(rows, _fallback_config()) if summary is None else summary
    write_csv_rows(csv_path, rows, RUNTIME_PROJECTION_FIELDS)
    write_json(json_path, {"summary": payload_summary, "rows": rows})


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


def step45_geometry_and_region_hashes(config_path) -> dict:
    config = RuntimeGeometryProjectionIntegrationConfig.from_json(_resolve_path(config_path))
    return geometry_and_region_hashes(config.diagnostic_geometry_update_config_path)


def _assert_step44_matches_step45(config, step44_config):
    if tuple(config.selected_phases) != tuple(step44_config.selected_phases):
        raise ValueError("Step 45 selected phases must match Step 44")
    if tuple(config.grid_sizes) != tuple(step44_config.grid_sizes):
        raise ValueError("Step 45 grid sizes must match Step 44")
    if tuple(config.tracked_regions) != tuple(step44_config.tracked_regions):
        raise ValueError("Step 45 tracked regions must match Step 44")


def _projection_pass(row: dict) -> bool:
    return bool(
        int(row["grid_size"]) > 0
        and int(row["active_cell_count"]) > 0
        and int(row["region_coverage_count"]) > 0
        and float(row["projected_mass"]) > 0.0
        and 0.0 <= float(row["solid_phi_min"]) <= float(row["solid_phi_max"]) <= 1.0
        and not bool(row["has_nan"])
        and not bool(row["has_inf"])
        and bool(row["transient_only"])
        and not bool(row["persist_projected_state"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["apply_to_driver_state"])
        and not bool(row["apply_to_default_lbm_state"])
        and not bool(row["apply_to_default_mpm_state"])
        and not bool(row["apply_to_default_projection_state"])
        and not bool(row["update_dynamic_solid"])
        and math.isfinite(float(row["projected_mass"]))
        and math.isfinite(float(row["region_coverage"]))
    )


def _unique_cell_indices(indices: np.ndarray) -> np.ndarray:
    if len(indices) == 0:
        return np.zeros((0, 3), dtype=np.int64)
    return np.unique(np.asarray(indices, dtype=np.int64), axis=0)


def _boundary_cell_count(unique: np.ndarray, grid_size: int) -> int:
    if len(unique) == 0:
        return 0
    boundary = np.any((unique == 0) | (unique == int(grid_size) - 1), axis=1)
    return int(np.count_nonzero(boundary))


def _bbox_cells(unique: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(unique) == 0:
        zeros = np.zeros(3, dtype=np.int64)
        return zeros, zeros
    return np.min(unique, axis=0), np.max(unique, axis=0)


def _occupancy_hash(unique: np.ndarray, grid_size: int) -> str:
    header = np.asarray([int(grid_size), int(len(unique))], dtype=np.int64)
    payload = np.ascontiguousarray(unique, dtype=np.int64).tobytes()
    return hashlib.sha256(header.tobytes() + payload).hexdigest()


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array


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


def _fallback_config() -> RuntimeGeometryProjectionIntegrationConfig:
    return RuntimeGeometryProjectionIntegrationConfig(
        projection_integration_id="step45_runtime_geometry_projection_integration_smoke",
        diagnostic_geometry_update_config_path="configs/step44_diagnostic_geometry_update.json",
        geometry_motion_interface_config_path="configs/step43_geometry_motion_interface_prescribed_diagnostic_only.json",
        displacement_artifact_path="outputs/step42_geometry_displacement/geometry_displacement.json",
        geometry_config_path="configs/step30_squid_proxy_geometry.json",
        region_config_path="configs/step30_squid_proxy_region_config.json",
        step44_projection_artifact_path="outputs/step44_projection_only_smoke/projection_only_smoke.json",
        selected_phases=(0.0, 0.2, 0.35, 0.5, 1.0),
        grid_sizes=(32, 48),
        tracked_regions=("mantle_outer", "mantle_cavity_proxy", "funnel_outlet_proxy"),
        integration_mode="transient_projection_only",
    )
