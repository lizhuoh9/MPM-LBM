import csv
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


STEP25_DESCRIPTORS = [
    "configs/step25_candidate_smoke_mesh_descriptor.json",
    "configs/step25_candidate_smoke_voxel_descriptor.json",
]

STEP25_LOG_MARKERS = {
    "logs/step25_candidate_manifest.log": "[OK] Step 25 candidate manifest finished",
    "logs/step25_real_geometry_intake_smoke.log": "[OK] Step 25 real geometry intake smoke finished",
    "logs/step25_mesh_candidate_quality.log": "[OK] Step 25 mesh candidate quality finished",
    "logs/step25_voxel_candidate_quality.log": "[OK] Step 25 voxel candidate quality finished",
    "logs/step25_normalization_reports.log": "[OK] Step 25 normalization reports finished",
    "logs/step25_sampling_reproducibility.log": "[OK] Step 25 sampling reproducibility finished",
    "logs/step25_projection_smoke.log": "[OK] Step 25 projection smoke finished",
    "logs/step25_step24_regression_guard.log": "[OK] Step 25 Step 24 regression guard finished",
    "logs/step25_artifact_manifest.log": "[OK] Step 25 artifact manifest finished",
}


def descriptor_paths() -> list[Path]:
    return [ROOT / relative_path for relative_path in STEP25_DESCRIPTORS]


def load_json(path) -> dict:
    resolved = _resolve(path)
    with resolved.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    resolved = _resolve(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_log(relative_path, lines):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line).rstrip() + "\n")


def write_csv_rows(path, rows, fieldnames):
    resolved = _resolve(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fieldnames})


def relative_path(path) -> str:
    return os.path.relpath(_resolve(path), ROOT).replace("\\", "/")


def require_file(relative_path):
    path = ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"missing required file: {relative_path}")


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def _resolve(path) -> Path:
    path_obj = Path(path)
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def _csv_value(value):
    if isinstance(value, (list, tuple, dict)):
        return json.dumps(value, sort_keys=True)
    return value
