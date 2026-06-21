import csv
import json
import math
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP44_CONFIG_PATH = "configs/step44_diagnostic_geometry_update.json"
STEP44_ORIGINAL_1STEP_CONFIG = "configs/step44_original_32_static_1step.json"
STEP44_DISPLACED_1STEP_CONFIG = "configs/step44_displaced_copy_32_phase035_1step.json"

STEP44_LOG_MARKERS = {
    "logs/step44_diagnostic_update_config_validation.log": "[OK] Step 44 diagnostic update config validation finished",
    "logs/step44_runtime_displaced_copy.log": "[OK] Step 44 runtime displaced copy finished",
    "logs/step44_runtime_copy_quality.log": "[OK] Step 44 runtime copy quality finished",
    "logs/step44_projection_only_smoke.log": "[OK] Step 44 projection-only smoke finished",
    "logs/step44_original_vs_displaced_comparison.log": "[OK] Step 44 original-vs-displaced comparison finished",
    "logs/step44_cycle_phase_closure.log": "[OK] Step 44 cycle phase closure finished",
    "logs/step44_state_mutation_guard.log": "[OK] Step 44 state mutation guard finished",
    "logs/step44_optional_1step_driver_smoke.log": "[OK] Step 44 optional one-step driver smoke finished",
    "logs/step44_step43_regression_guard.log": "[OK] Step 44 Step 43 regression guard finished",
    "logs/step44_artifact_manifest.log": "[OK] Step 44 artifact manifest finished",
}


def load_step44_config():
    from src.diagnostic_geometry_update_config import DiagnosticGeometryUpdateConfig

    return DiagnosticGeometryUpdateConfig.from_json(resolve_path(STEP44_CONFIG_PATH))


def runtime_rows():
    from src.diagnostic_geometry_update import compute_runtime_displaced_copy_rows

    return compute_runtime_displaced_copy_rows(STEP44_CONFIG_PATH)


def projection_rows():
    from src.diagnostic_geometry_projection import compute_projection_only_rows

    return compute_projection_only_rows(STEP44_CONFIG_PATH)


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
