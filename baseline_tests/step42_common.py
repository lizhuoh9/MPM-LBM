import csv
import json
import math
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP42_DISPLACEMENT_CONFIG_PATH = "configs/step42_squid_proxy_geometry_displacement.json"
STEP42_DISPLACEMENT_SAMPLING_CONFIG_PATH = "configs/step42_squid_proxy_displacement_sampling.json"

STEP42_LOG_MARKERS = {
    "logs/step42_displacement_config_validation.log": "[OK] Step 42 displacement config validation finished",
    "logs/step42_generate_geometry_displacement.log": "[OK] Step 42 generate geometry displacement finished",
    "logs/step42_displacement_quality.log": "[OK] Step 42 displacement quality finished",
    "logs/step42_displacement_repeatability.log": "[OK] Step 42 displacement repeatability finished",
    "logs/step42_schedule_displacement_consistency.log": "[OK] Step 42 schedule-displacement consistency finished",
    "logs/step42_motion_displacement_consistency.log": "[OK] Step 42 motion-displacement consistency finished",
    "logs/step42_grid_displacement_diagnostics.log": "[OK] Step 42 grid displacement diagnostics finished",
    "logs/step42_cycle_closure_diagnostics.log": "[OK] Step 42 cycle closure diagnostics finished",
    "logs/step42_no_driver_update_guard.log": "[OK] Step 42 no driver update guard finished",
    "logs/step42_step41_regression_guard.log": "[OK] Step 42 Step 41 regression guard finished",
    "logs/step42_artifact_manifest.log": "[OK] Step 42 artifact manifest finished",
}


def load_displacement_config():
    from src.geometry_displacement_config import GeometryDisplacementConfig

    return GeometryDisplacementConfig.from_json(resolve_path(STEP42_DISPLACEMENT_CONFIG_PATH))


def load_displacement_sampling_config():
    return read_json(STEP42_DISPLACEMENT_SAMPLING_CONFIG_PATH)


def load_displacement_inputs():
    from src.geometry_displacement_field import load_geometry_displacement_inputs

    return load_geometry_displacement_inputs(STEP42_DISPLACEMENT_CONFIG_PATH)


def make_displacement_rows():
    from src.geometry_displacement_field import compute_geometry_displacement_rows

    inputs = load_displacement_inputs()
    return compute_geometry_displacement_rows(
        inputs["config"],
        inputs["schedule_rows"],
        inputs["geometry_config"],
        inputs["points"],
        inputs["masks"],
    )


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


def check_row(check, passed, value, notes):
    return {"check": check, "pass": bool(passed), "value": value, "notes": notes}


def csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


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
