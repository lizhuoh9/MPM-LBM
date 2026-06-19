import csv
import json
import os
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


STEP26_DESCRIPTORS = [
    "configs/step25_candidate_smoke_mesh_descriptor.json",
    "configs/step25_candidate_smoke_voxel_descriptor.json",
]

STEP26_GEOMETRY_CONFIGS = {
    "real_candidate_smoke_mesh": "configs/step26_real_candidate_smoke_mesh_geometry.json",
    "real_candidate_smoke_voxel": "configs/step26_real_candidate_smoke_voxel_geometry.json",
}

STEP26_PROJECTION_CONFIGS = [
    f"configs/step26_projection_{candidate}_{n_grid}.json"
    for candidate in ("real_candidate_smoke_mesh", "real_candidate_smoke_voxel")
    for n_grid in (32, 48, 64)
]

STEP26_DRIVER_CONFIGS_BY_KIND = {
    "mesh": [
        "configs/step26_driver_real_candidate_smoke_mesh_48_none.json",
        "configs/step26_driver_real_candidate_smoke_mesh_48_penalty.json",
        "configs/step26_driver_real_candidate_smoke_mesh_48_moving_boundary.json",
        "configs/step26_driver_real_candidate_smoke_mesh_48_link_area.json",
    ],
    "voxel": [
        "configs/step26_driver_real_candidate_smoke_voxel_48_none.json",
        "configs/step26_driver_real_candidate_smoke_voxel_48_penalty.json",
        "configs/step26_driver_real_candidate_smoke_voxel_48_moving_boundary.json",
        "configs/step26_driver_real_candidate_smoke_voxel_48_link_area.json",
    ],
}

STEP26_LOG_MARKERS = {
    "logs/step26_candidate_fingerprint_guard.log": "[OK] Step 26 candidate fingerprint guard finished",
    "logs/step26_generate_driver_geometry_configs.log": "[OK] Step 26 generated driver geometry configs finished",
    "logs/step26_projection_scale_diagnostics.log": "[OK] Step 26 projection scale diagnostics finished",
    "logs/step26_step25_projection_regression.log": "[OK] Step 26 Step 25 projection regression finished",
    "logs/step26_short_driver_mesh_48_modes.log": "[OK] Step 26 mesh 48 short driver modes finished",
    "logs/step26_short_driver_voxel_48_modes.log": "[OK] Step 26 voxel 48 short driver modes finished",
    "logs/step26_short_driver_summary.log": "[OK] Step 26 short driver summary finished",
    "logs/step26_quality_report_aggregation.log": "[OK] Step 26 quality report aggregation finished",
    "logs/step26_step25_regression_guard.log": "[OK] Step 26 Step 25 regression guard finished",
    "logs/step26_artifact_manifest.log": "[OK] Step 26 artifact manifest finished",
}


def load_json(path):
    with resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def read_csv_rows(path):
    with resolve_path(path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path, rows, fieldnames):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fieldnames})


def write_rows_csv_npz(rows, csv_path, npz_path, fieldnames):
    write_csv_rows(csv_path, rows, fieldnames)
    payload = {"columns": np.asarray(fieldnames)}
    for field in fieldnames:
        values = [row.get(field, "") for row in rows]
        if _is_string_field(values):
            payload[field + "s"] = np.asarray([str(value) for value in values])
            continue
        try:
            payload[field] = np.asarray([_bool_to_float(value) for value in values], dtype=np.float64)
        except (TypeError, ValueError):
            payload[field + "s"] = np.asarray([str(value) for value in values])
    resolved = resolve_path(npz_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    np.savez(resolved, **payload)


def write_log(relative_path, lines):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line).rstrip() + "\n")


def relative_path(path) -> str:
    return os.path.relpath(resolve_path(path), ROOT).replace("\\", "/")


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _is_string_field(values) -> bool:
    for value in values:
        if value == "":
            continue
        try:
            _bool_to_float(value)
        except (TypeError, ValueError):
            return True
    return False


def _bool_to_float(value):
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    text = str(value).strip().lower()
    if text in {"true", "false"}:
        return 1.0 if text == "true" else 0.0
    return float(value)
