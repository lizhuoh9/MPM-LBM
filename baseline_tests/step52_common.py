import csv
import json
import math
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP52_CONFIG_PATH = "configs/step52_48_engineering_one_cycle_feasibility.json"


def load_step52_config():
    from src.runtime_geometry_wall_velocity_48_feasibility_config import RuntimeGeometryWallVelocity48FeasibilityConfig

    return RuntimeGeometryWallVelocity48FeasibilityConfig.from_json(resolve_path(STEP52_CONFIG_PATH))


def feasibility_rows():
    from src.runtime_geometry_wall_velocity_48_feasibility_envelope import run_48_feasibility_matrix

    return run_48_feasibility_matrix(STEP52_CONFIG_PATH)


def closure_rows():
    from src.runtime_geometry_wall_velocity_48_feasibility_envelope import build_48_closure_rows

    return build_48_closure_rows(STEP52_CONFIG_PATH)


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
