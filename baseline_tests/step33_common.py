import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP33_MOTION_MAPPING_CONFIG_PATH = "configs/step33_squid_proxy_motion_mapping.json"
STEP33_MOTION_SAMPLING_CONFIG_PATH = "configs/step33_squid_proxy_motion_sampling.json"

STEP33_LOG_MARKERS = {
    "logs/step33_motion_mapping_config_validation.log": "[OK] Step 33 motion mapping config validation finished",
    "logs/step33_generate_motion_mapping.log": "[OK] Step 33 generate motion mapping finished",
    "logs/step33_motion_quality.log": "[OK] Step 33 motion quality finished",
    "logs/step33_motion_repeatability.log": "[OK] Step 33 motion repeatability finished",
    "logs/step33_motion_grid_diagnostics.log": "[OK] Step 33 motion grid diagnostics finished",
    "logs/step33_schedule_motion_consistency.log": "[OK] Step 33 schedule-motion consistency finished",
    "logs/step33_step32_regression_guard.log": "[OK] Step 33 Step 32 regression guard finished",
    "logs/step33_artifact_manifest.log": "[OK] Step 33 artifact manifest finished",
}


def load_motion_mapping_config():
    from src.squid_motion_mapping_config import SquidMotionMappingConfig

    return SquidMotionMappingConfig.from_json(resolve_path(STEP33_MOTION_MAPPING_CONFIG_PATH))


def load_motion_sampling_config():
    return read_json(STEP33_MOTION_SAMPLING_CONFIG_PATH)


def load_motion_inputs():
    from src.squid_motion_mapping import load_motion_mapping_inputs

    return load_motion_mapping_inputs(STEP33_MOTION_MAPPING_CONFIG_PATH)


def make_motion_rows():
    from src.squid_motion_mapping import compute_region_motion_rows

    inputs = load_motion_inputs()
    rows = compute_region_motion_rows(
        inputs["mapping_config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["region_config"],
        inputs["points"],
        inputs["masks"],
    )
    return rows


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


def resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return ROOT / path_obj


def summary_rows(summary: dict) -> list[dict]:
    return [{"metric": key, "value": value} for key, value in sorted(summary.items())]


def csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def finite_values(row, excluded=()) -> bool:
    for key, value in row.items():
        if key in excluded or value == "":
            continue
        if isinstance(value, bool):
            continue
        if str(value).strip().lower() in {"true", "false"}:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def canonical_motion_hash(rows: list[dict], fields: list[str], precision=12) -> str:
    parts = []
    for row in rows:
        values = []
        for field in fields:
            value = row[field]
            if isinstance(value, bool):
                values.append("1" if value else "0")
            else:
                try:
                    values.append(f"{float(value):.{int(precision)}g}")
                except (TypeError, ValueError):
                    values.append(str(value))
        parts.append(",".join(values))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def motion_hashes(rows: list[dict], precision=12) -> dict:
    return {
        "motion_hash": canonical_motion_hash(
            rows,
            [
                "sample_index",
                "phase",
                "region_id",
                "displacement_norm_max",
                "velocity_norm_max",
                "mantle_radius_scale",
                "mantle_radius_rate",
                "volume_scale",
                "volume_rate",
                "aperture_scale",
                "aperture_rate",
            ],
            precision=precision,
        ),
        "mantle_motion_hash": canonical_motion_hash(
            [row for row in rows if row["region_id"] == "mantle_outer"],
            ["sample_index", "phase", "displacement_norm_max", "velocity_norm_max", "mantle_radius_scale", "mantle_radius_rate"],
            precision=precision,
        ),
        "cavity_motion_hash": canonical_motion_hash(
            [row for row in rows if row["region_id"] == "mantle_cavity_proxy"],
            ["sample_index", "phase", "volume_scale", "volume_rate"],
            precision=precision,
        ),
        "funnel_motion_hash": canonical_motion_hash(
            [row for row in rows if row["region_id"] == "funnel_outlet_proxy"],
            ["sample_index", "phase", "aperture_scale", "aperture_rate"],
            precision=precision,
        ),
    }
