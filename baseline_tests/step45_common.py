import csv
import json
import math
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP45_CONFIG_PATH = "configs/step45_runtime_geometry_projection_integration.json"
STEP45_ORIGINAL_1STEP_CONFIG = "configs/step45_original_32_static_1step.json"
STEP45_DISPLACED_ENGINEERING_1STEP_CONFIG = "configs/step45_displaced_phase035_32_moving_boundary_1step.json"
STEP45_DISPLACED_LINK_AREA_1STEP_CONFIG = "configs/step45_displaced_phase035_32_link_area_1step.json"

STEP45_LOG_MARKERS = {
    "logs/step45_projection_integration_config_validation.log": "[OK] Step 45 projection integration config validation finished",
    "logs/step45_runtime_projection_integration.log": "[OK] Step 45 runtime projection integration finished",
    "logs/step45_runtime_projection_quality.log": "[OK] Step 45 runtime projection quality finished",
    "logs/step45_original_vs_runtime_projection_comparison.log": "[OK] Step 45 original-vs-runtime projection comparison finished",
    "logs/step45_projection_phase_closure.log": "[OK] Step 45 projection phase closure finished",
    "logs/step45_step44_projection_alignment.log": "[OK] Step 45 Step 44 projection alignment finished",
    "logs/step45_runtime_projection_state_guard.log": "[OK] Step 45 runtime projection state guard finished",
    "logs/step45_ultrashort_projection_driver_smoke.log": "[OK] Step 45 ultra-short projection driver smoke finished",
    "logs/step45_step44_regression_guard.log": "[OK] Step 45 Step 44 regression guard finished",
    "logs/step45_artifact_manifest.log": "[OK] Step 45 artifact manifest finished",
}


def load_step45_config():
    from src.runtime_geometry_projection_config import RuntimeGeometryProjectionIntegrationConfig

    return RuntimeGeometryProjectionIntegrationConfig.from_json(resolve_path(STEP45_CONFIG_PATH))


def runtime_projection_rows():
    from src.runtime_geometry_projection import compute_runtime_projection_rows

    return compute_runtime_projection_rows(STEP45_CONFIG_PATH)


def original_projection_rows():
    from src.runtime_geometry_projection import compute_original_projection_rows

    return compute_original_projection_rows(STEP45_CONFIG_PATH)


def read_json(path):
    with resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def write_csv_rows(path, rows, fieldnames=None):
    resolved = resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    fields = list(fieldnames or (rows[0].keys() if rows else []))
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in fields})


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
