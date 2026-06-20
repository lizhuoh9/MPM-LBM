import csv
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

GEOMETRY_CONFIG_PATH = "configs/step30_squid_proxy_geometry.json"
REGION_CONFIG_PATH = "configs/step30_squid_proxy_region_config.json"
SAMPLE_COUNT = 32**3

STEP30_LOG_MARKERS = {
    "logs/step30_region_schema_validation.log": "[OK] Step 30 region schema validation finished",
    "logs/step30_region_mask_sampling.log": "[OK] Step 30 region mask sampling finished",
    "logs/step30_region_quality.log": "[OK] Step 30 region quality finished",
    "logs/step30_region_overlap_diagnostics.log": "[OK] Step 30 region overlap diagnostics finished",
    "logs/step30_region_projection_smoke.log": "[OK] Step 30 region projection smoke finished",
    "logs/step30_step29_regression_guard.log": "[OK] Step 30 Step 29 regression guard finished",
    "logs/step30_artifact_manifest.log": "[OK] Step 30 artifact manifest finished",
}


def load_step30_geometry_config():
    from src.geometry_config import GeometryConfig

    return GeometryConfig.from_json(ROOT / GEOMETRY_CONFIG_PATH)


def load_step30_region_config():
    from src.squid_region_config import load_squid_proxy_region_config

    return load_squid_proxy_region_config(ROOT / REGION_CONFIG_PATH)


def make_step30_region_sample():
    from src.squid_proxy_regions import sample_squid_proxy_region_points, sample_squid_proxy_regions, summarize_region_masks

    geometry_config = load_step30_geometry_config()
    region_config = load_step30_region_config()
    points = sample_squid_proxy_region_points(geometry_config, count=SAMPLE_COUNT, seed=30)
    masks = sample_squid_proxy_regions(geometry_config, region_config, points)
    region_rows = summarize_region_masks(points, masks, geometry_config, region_config)
    return geometry_config, region_config, points, masks, region_rows


def resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def read_json(path):
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
            writer.writerow({field: csv_value(row.get(field, "")) for field in fieldnames})


def write_log(relative_path, lines):
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line).rstrip() + "\n")


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def fieldnames_from_rows(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}
