import csv
import json
import math
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP35_WALL_VELOCITY_CONFIG_PATH = "configs/step35_squid_proxy_wall_velocity_field.json"
STEP35_WALL_VELOCITY_SAMPLING_PATH = "configs/step35_squid_proxy_wall_velocity_sampling.json"

STEP35_LOG_MARKERS = {
    "logs/step35_wall_velocity_config_validation.log": "[OK] Step 35 wall velocity config validation finished",
    "logs/step35_generate_wall_velocity_field.log": "[OK] Step 35 generate wall velocity field finished",
    "logs/step35_wall_velocity_quality.log": "[OK] Step 35 wall velocity quality finished",
    "logs/step35_wall_velocity_repeatability.log": "[OK] Step 35 wall velocity repeatability finished",
    "logs/step35_motion_velocity_consistency.log": "[OK] Step 35 motion velocity consistency finished",
    "logs/step35_grid_coverage_diagnostics.log": "[OK] Step 35 grid coverage diagnostics finished",
    "logs/step35_no_lbm_update_guard.log": "[OK] Step 35 no LBM update guard finished",
    "logs/step35_step34_regression_guard.log": "[OK] Step 35 Step 34 regression guard finished",
    "logs/step35_artifact_manifest.log": "[OK] Step 35 artifact manifest finished",
}


def load_wall_velocity_config():
    from src.wall_velocity_config import WallVelocityFieldConfig

    return WallVelocityFieldConfig.from_json(resolve_path(STEP35_WALL_VELOCITY_CONFIG_PATH))


def load_wall_velocity_sampling_config():
    return read_json(STEP35_WALL_VELOCITY_SAMPLING_PATH)


def load_step35_inputs():
    from src.wall_velocity_field import load_wall_velocity_inputs

    return load_wall_velocity_inputs(STEP35_WALL_VELOCITY_CONFIG_PATH)


def make_wall_velocity_rows():
    from src.wall_velocity_field import generate_wall_velocity_field_rows

    return generate_wall_velocity_field_rows(STEP35_WALL_VELOCITY_CONFIG_PATH)


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
