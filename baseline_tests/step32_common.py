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

STEP32_SCHEDULE_CONFIG_PATH = "configs/step32_squid_proxy_kinematics_schedule.json"
STEP32_SAMPLING_CONFIG_PATH = "configs/step32_squid_proxy_kinematics_sampling.json"

STEP32_LOG_MARKERS = {
    "logs/step32_schedule_config_validation.log": "[OK] Step 32 schedule config validation finished",
    "logs/step32_generate_kinematics_schedule.log": "[OK] Step 32 generate kinematics schedule finished",
    "logs/step32_schedule_quality.log": "[OK] Step 32 schedule quality finished",
    "logs/step32_schedule_repeatability.log": "[OK] Step 32 schedule repeatability finished",
    "logs/step32_region_mapping_validation.log": "[OK] Step 32 region mapping validation finished",
    "logs/step32_schedule_envelope_summary.log": "[OK] Step 32 schedule envelope summary finished",
    "logs/step32_step31_regression_guard.log": "[OK] Step 32 Step 31 regression guard finished",
    "logs/step32_artifact_manifest.log": "[OK] Step 32 artifact manifest finished",
}


def load_schedule_config():
    from src.squid_kinematics_config import SquidKinematicsScheduleConfig

    return SquidKinematicsScheduleConfig.from_json(resolve_path(STEP32_SCHEDULE_CONFIG_PATH))


def load_sampling_config():
    return read_json(STEP32_SAMPLING_CONFIG_PATH)


def make_schedule_rows():
    from src.squid_kinematics_schedule import schedule_rows

    return schedule_rows(load_schedule_config())


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


def relative_path(path) -> str:
    return os.path.relpath(resolve_path(path), ROOT).replace("\\", "/")


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


def canonical_schedule_hash(rows: list[dict], fields: list[str], precision=12) -> str:
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


def schedule_hashes(rows: list[dict], precision=12) -> dict:
    return {
        "schedule_hash": canonical_schedule_hash(
            rows,
            [
                "phase",
                "mantle_radius_scale",
                "cavity_volume_scale",
                "funnel_aperture_scale",
                "mantle_radius_rate",
                "cavity_volume_rate",
                "funnel_aperture_rate",
            ],
            precision=precision,
        ),
        "mantle_hash": canonical_schedule_hash(rows, ["phase", "mantle_radius_scale", "mantle_radius_rate"], precision=precision),
        "cavity_hash": canonical_schedule_hash(rows, ["phase", "cavity_volume_scale", "cavity_volume_rate"], precision=precision),
        "funnel_hash": canonical_schedule_hash(rows, ["phase", "funnel_aperture_scale", "funnel_aperture_rate"], precision=precision),
    }
