import csv
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np

from src.mpm_lbm.diagnostics.geometry_update_config import (
    DiagnosticGeometryUpdateConfig,
    mutation_flags,
    validate_diagnostic_geometry_update_config,
)
from src.mpm_lbm.sim.geometry_displacement.field import (
    displacement_vectors_for_region,
    load_geometry_displacement_inputs,
)
from src.mpm_lbm.sim.squid_proxy.regions import region_assignment_hash, sampled_position_hash


RUNTIME_COPY_FIELDS = [
    "phase",
    "sample_index",
    "region_id",
    "point_count",
    "original_bbox_min_x",
    "original_bbox_min_y",
    "original_bbox_min_z",
    "original_bbox_max_x",
    "original_bbox_max_y",
    "original_bbox_max_z",
    "displaced_bbox_min_x",
    "displaced_bbox_min_y",
    "displaced_bbox_min_z",
    "displaced_bbox_max_x",
    "displaced_bbox_max_y",
    "displaced_bbox_max_z",
    "bbox_delta_norm",
    "displacement_norm_min",
    "displacement_norm_max",
    "displacement_norm_mean",
    "original_hash",
    "displaced_summary_hash",
    "bounds_pass",
    "coverage_pass",
    "finite_pass",
    "diagnostic_only",
    "persist_displaced_geometry",
    "write_displaced_particles",
    "write_dense_displacement_field",
    "write_vtk",
    "mutate_original_geometry",
]


def load_step44_inputs(config_path):
    config = DiagnosticGeometryUpdateConfig.from_json(_resolve_path(config_path))
    validation_rows = validate_diagnostic_geometry_update_config(config, root=_repo_root())
    if not all(bool(row["pass"]) for row in validation_rows):
        raise ValueError(f"invalid Step 44 diagnostic geometry update config: {validation_rows}")
    displacement_inputs = load_geometry_displacement_inputs(config.displacement_config_path)
    return {
        "config": config,
        "validation_rows": validation_rows,
        "displacement_config": displacement_inputs["config"],
        "geometry_config": displacement_inputs["geometry_config"],
        "region_config": displacement_inputs["region_config"],
        "schedule_rows": displacement_inputs["schedule_rows"],
        "points": displacement_inputs["points"],
        "masks": displacement_inputs["masks"],
    }


def compute_runtime_displaced_copy_rows(config_path) -> list[dict]:
    inputs = load_step44_inputs(config_path)
    config = inputs["config"]
    points = _as_points(inputs["points"])
    masks = inputs["masks"]
    rows = []
    for schedule_row in selected_schedule_rows(inputs):
        phase = float(schedule_row["phase"])
        for region_id in config.tracked_regions:
            selected = points[np.asarray(masks[region_id], dtype=bool)]
            vectors = displacement_vectors_for_region(region_id, selected, inputs["geometry_config"], schedule_row)
            displaced = selected + vectors
            rows.append(runtime_copy_row(config, schedule_row, region_id, selected, displaced, vectors))
    return rows


def runtime_copy_row(config: DiagnosticGeometryUpdateConfig, schedule_row, region_id, original_points, displaced_points, vectors) -> dict:
    original = _as_points(original_points)
    displaced = _as_points(displaced_points)
    vec = np.asarray(vectors, dtype=np.float64)
    norms = np.linalg.norm(vec, axis=1) if len(vec) else np.zeros(0, dtype=np.float64)
    original_min, original_max = _bbox(original)
    displaced_min, displaced_max = _bbox(displaced)
    row = {
        "phase": _canonical_phase(schedule_row["phase"]),
        "sample_index": int(schedule_row["sample_index"]),
        "region_id": region_id,
        "point_count": int(len(original)),
        "original_bbox_min_x": float(original_min[0]),
        "original_bbox_min_y": float(original_min[1]),
        "original_bbox_min_z": float(original_min[2]),
        "original_bbox_max_x": float(original_max[0]),
        "original_bbox_max_y": float(original_max[1]),
        "original_bbox_max_z": float(original_max[2]),
        "displaced_bbox_min_x": float(displaced_min[0]),
        "displaced_bbox_min_y": float(displaced_min[1]),
        "displaced_bbox_min_z": float(displaced_min[2]),
        "displaced_bbox_max_x": float(displaced_max[0]),
        "displaced_bbox_max_y": float(displaced_max[1]),
        "displaced_bbox_max_z": float(displaced_max[2]),
        "bbox_delta_norm": float(np.linalg.norm((displaced_max - displaced_min) - (original_max - original_min))),
        "displacement_norm_min": _safe_min(norms),
        "displacement_norm_max": _safe_max(norms),
        "displacement_norm_mean": _safe_mean(norms),
        "original_hash": _array_hash(original),
        "diagnostic_only": bool(config.diagnostic_only),
        "persist_displaced_geometry": bool(config.persist_displaced_geometry),
        "write_displaced_particles": bool(config.write_displaced_particles),
        "write_dense_displacement_field": bool(config.write_dense_displacement_field),
        "write_vtk": bool(config.write_vtk),
        "mutate_original_geometry": bool(config.mutate_original_geometry),
    }
    row["displaced_summary_hash"] = _summary_hash(row)
    row["finite_pass"] = _finite_row(row)
    row["coverage_pass"] = int(row["point_count"]) > 0
    row["bounds_pass"] = (
        row["finite_pass"]
        and row["coverage_pass"]
        and 0.0 <= float(row["displacement_norm_min"]) <= float(row["displacement_norm_mean"]) <= float(row["displacement_norm_max"])
        and float(row["displacement_norm_max"]) <= 0.25 + 1.0e-12
        and bool(row["diagnostic_only"])
        and not bool(row["persist_displaced_geometry"])
        and not bool(row["write_displaced_particles"])
        and not bool(row["write_dense_displacement_field"])
        and not bool(row["write_vtk"])
        and not bool(row["mutate_original_geometry"])
    )
    return row


def summarize_runtime_displaced_copy_rows(rows: list[dict], config: DiagnosticGeometryUpdateConfig) -> dict:
    phases = sorted({float(row["phase"]) for row in rows})
    regions = sorted({str(row["region_id"]) for row in rows}, key=list(config.tracked_regions).index)
    return {
        "row_count": len(rows),
        "phase_count": len(phases),
        "selected_phases": phases,
        "tracked_region_count": len(regions),
        "tracked_regions": regions,
        "max_displacement_norm": max(float(row["displacement_norm_max"]) for row in rows) if rows else 0.0,
        "finite_pass": all(bool(row["finite_pass"]) for row in rows),
        "bounds_pass": all(bool(row["bounds_pass"]) for row in rows),
        "coverage_pass": all(bool(row["coverage_pass"]) for row in rows),
        "diagnostic_only_pass": all(bool(row["diagnostic_only"]) for row in rows),
        "no_persistent_output_pass": all(
            not bool(row["persist_displaced_geometry"])
            and not bool(row["write_displaced_particles"])
            and not bool(row["write_dense_displacement_field"])
            and not bool(row["write_vtk"])
            and not bool(row["mutate_original_geometry"])
            for row in rows
        ),
        "original_hash_stable": _original_hash_stable(rows),
        "runtime_copy_pass": bool(
            len(rows) == len(config.selected_phases) * len(config.tracked_regions)
            and all(bool(row["finite_pass"]) and bool(row["bounds_pass"]) and bool(row["coverage_pass"]) for row in rows)
        ),
    }


def runtime_copy_quality_summary(rows: list[dict], config: DiagnosticGeometryUpdateConfig) -> dict:
    summary = summarize_runtime_displaced_copy_rows(rows, config)
    phase0_rows = [row for row in rows if math.isclose(float(row["phase"]), 0.0, abs_tol=1.0e-12)]
    phase1_rows = [row for row in rows if math.isclose(float(row["phase"]), 1.0, abs_tol=1.0e-12)]
    closure_support_pass = len(phase0_rows) == len(config.tracked_regions) and len(phase1_rows) == len(config.tracked_regions)
    return {
        **summary,
        "closure_support_pass": bool(closure_support_pass),
        "quality_pass": bool(
            summary["runtime_copy_pass"]
            and summary["bounds_pass"]
            and summary["coverage_pass"]
            and summary["finite_pass"]
            and summary["diagnostic_only_pass"]
            and summary["no_persistent_output_pass"]
            and closure_support_pass
        ),
    }


def original_vs_displaced_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        phase = float(row["phase"])
        displacement_nonzero = float(row["displacement_norm_max"]) > 1.0e-12
        close_to_rest = float(row["displacement_norm_max"]) <= 1.0e-12
        is_midcycle = not (math.isclose(phase, 0.0, abs_tol=1.0e-12) or math.isclose(phase, 1.0, abs_tol=1.0e-12))
        comparison_pass = bool(
            row["finite_pass"]
            and row["bounds_pass"]
            and (True if is_midcycle else close_to_rest)
        )
        out.append(
            {
                "phase": phase,
                "region_id": row["region_id"],
                "original_hash": row["original_hash"],
                "displaced_summary_hash": row["displaced_summary_hash"],
                "original_hash_stable": True,
                "displacement_norm_max": float(row["displacement_norm_max"]),
                "bbox_delta_norm": float(row["bbox_delta_norm"]),
                "midcycle": bool(is_midcycle),
                "displacement_nonzero": bool(displacement_nonzero),
                "close_to_rest": bool(close_to_rest),
                "comparison_pass": comparison_pass,
            }
        )
    return out


def summarize_original_vs_displaced(rows: list[dict]) -> dict:
    midcycle = [row for row in rows if bool(row["midcycle"])]
    midcycle_phases = sorted({float(row["phase"]) for row in midcycle})
    phase0 = [row for row in rows if math.isclose(float(row["phase"]), 0.0, abs_tol=1.0e-12)]
    phase1 = [row for row in rows if math.isclose(float(row["phase"]), 1.0, abs_tol=1.0e-12)]
    return {
        "row_count": len(rows),
        "comparison_pass_count": sum(1 for row in rows if bool(row["comparison_pass"])),
        "comparison_pass": all(bool(row["comparison_pass"]) for row in rows),
        "original_hash_stable": all(bool(row["original_hash_stable"]) for row in rows),
        "displacement_nonzero_for_midcycle_phases": all(
            any(bool(row["displacement_nonzero"]) for row in midcycle if math.isclose(float(row["phase"]), phase, abs_tol=1.0e-12))
            for phase in midcycle_phases
        ),
        "phase0_displacement_close_to_rest": all(bool(row["close_to_rest"]) for row in phase0),
        "phase1_displacement_close_to_rest": all(bool(row["close_to_rest"]) for row in phase1),
        "max_bbox_delta_norm": max(float(row["bbox_delta_norm"]) for row in rows) if rows else 0.0,
    }


def cycle_phase_closure_rows(rows: list[dict], config: DiagnosticGeometryUpdateConfig) -> list[dict]:
    out = []
    by_region_phase = {(row["region_id"], float(row["phase"])): row for row in rows}
    for region_id in config.tracked_regions:
        phase0 = by_region_phase[(region_id, 0.0)]
        phase1 = by_region_phase[(region_id, 1.0)]
        delta = abs(float(phase1["displacement_norm_max"]) - float(phase0["displacement_norm_max"]))
        out.append(
            {
                "region_id": region_id,
                "phase0_displacement_norm_max": float(phase0["displacement_norm_max"]),
                "phase1_displacement_norm_max": float(phase1["displacement_norm_max"]),
                "phase0_phase1_displacement_delta": float(delta),
                "closure_pass": bool(delta <= 1.0e-12),
            }
        )
    return out


def summarize_cycle_phase_closure(rows: list[dict], config: DiagnosticGeometryUpdateConfig) -> dict:
    return {
        "row_count": len(rows),
        "tracked_regions": list(config.tracked_regions),
        "closure_pass_count": sum(1 for row in rows if bool(row["closure_pass"])),
        "closure_pass": all(bool(row["closure_pass"]) for row in rows),
        "max_phase0_phase1_displacement_delta": max(float(row["phase0_phase1_displacement_delta"]) for row in rows) if rows else 0.0,
    }


def selected_schedule_rows(inputs) -> list[dict]:
    selected = []
    schedule_rows = list(inputs["schedule_rows"])
    for requested in inputs["config"].selected_phases:
        matches = [row for row in schedule_rows if math.isclose(float(row["phase"]), float(requested), rel_tol=0.0, abs_tol=1.0e-12)]
        if not matches:
            raise ValueError(f"selected phase {requested} is not present in Step 42 schedule rows")
        selected.append(matches[0])
    return selected


def _canonical_phase(value) -> float:
    return float(round(float(value), 12))


def geometry_and_region_hashes(config_path) -> dict:
    inputs = load_step44_inputs(config_path)
    return {
        "sampled_position_hash": sampled_position_hash(inputs["points"]),
        "region_mask_hash": region_assignment_hash(inputs["masks"]),
        "geometry_config_hash": file_hash(inputs["config"].geometry_config_path),
        "region_config_hash": file_hash(inputs["config"].region_config_path),
    }


def write_runtime_copy_rows(rows: list[dict], csv_path, json_path, summary: dict) -> None:
    write_csv_rows(csv_path, rows, RUNTIME_COPY_FIELDS)
    write_json(json_path, {"summary": summary, "rows": rows})


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


def file_hash(path) -> str:
    return hashlib.sha256(_resolve_path(path).read_bytes()).hexdigest()


def _original_hash_stable(rows) -> bool:
    by_region = {}
    for row in rows:
        by_region.setdefault(row["region_id"], set()).add(row["original_hash"])
    return all(len(values) == 1 for values in by_region.values())


def _array_hash(points: np.ndarray) -> str:
    pts = np.ascontiguousarray(_as_points(points), dtype=np.float64)
    return hashlib.sha256(pts.tobytes()).hexdigest()


def _summary_hash(row: dict) -> str:
    keys = [
        "phase",
        "region_id",
        "point_count",
        "displaced_bbox_min_x",
        "displaced_bbox_min_y",
        "displaced_bbox_min_z",
        "displaced_bbox_max_x",
        "displaced_bbox_max_y",
        "displaced_bbox_max_z",
        "displacement_norm_max",
        "displacement_norm_mean",
    ]
    text = json.dumps({key: row[key] for key in keys}, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _bbox(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if len(points) == 0:
        nan = np.array([float("nan"), float("nan"), float("nan")], dtype=np.float64)
        return nan, nan
    return np.min(points, axis=0), np.max(points, axis=0)


def _safe_min(values: np.ndarray) -> float:
    return float(np.min(values)) if len(values) else 0.0


def _safe_max(values: np.ndarray) -> float:
    return float(np.max(values)) if len(values) else 0.0


def _safe_mean(values: np.ndarray) -> float:
    return float(np.mean(values)) if len(values) else 0.0


def _finite_row(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool) or value == "":
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


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
