import csv
import json
import math
import os
from pathlib import Path

import numpy as np


SCHEDULE_SCOPE_NOTE = "Step 32 schedule contract only; no driver integration and no moving wall velocity application"

SCHEDULE_FIELDS = [
    "sample_index",
    "phase",
    "cycle_time_fraction",
    "mantle_radius_scale",
    "mantle_radius_rate",
    "cavity_volume_scale",
    "cavity_volume_rate",
    "funnel_aperture_scale",
    "funnel_aperture_rate",
    "phase_label",
    "ramp_weight",
    "driver_integration_enabled",
    "actuation_enabled",
    "scope_note",
]


def phase_samples(config) -> np.ndarray:
    return np.linspace(0.0, 1.0, int(config.sample_count), dtype=np.float64)


def smoothstep(x) -> np.ndarray:
    clipped = np.clip(np.asarray(x, dtype=np.float64), 0.0, 1.0)
    return clipped * clipped * (3.0 - 2.0 * clipped)


def window_weight(phase, start: float, end: float, ramp_fraction: float) -> np.ndarray:
    phases = np.asarray(phase, dtype=np.float64)
    if end <= start:
        return np.zeros_like(phases)
    width = end - start
    ramp_width = max(width * float(ramp_fraction), 1.0e-12)
    open_weight = smoothstep((phases - start) / ramp_width)
    close_weight = 1.0 - smoothstep((phases - (end - ramp_width)) / ramp_width)
    return np.clip(open_weight * close_weight, 0.0, 1.0)


def mantle_radius_scale(phase, config) -> np.ndarray:
    phases = np.asarray(phase, dtype=np.float64)
    contraction = _progress(phases, config.contraction_start_phase, config.contraction_end_phase)
    refill = _progress(phases, config.refill_start_phase, config.refill_end_phase)
    amplitude = float(config.mantle_radius_scale_rest) - float(config.mantle_radius_scale_min)
    values = float(config.mantle_radius_scale_rest) - amplitude * contraction + amplitude * refill
    return np.clip(values, float(config.mantle_radius_scale_min), float(config.mantle_radius_scale_rest))


def cavity_volume_scale(phase, config) -> np.ndarray:
    phases = np.asarray(phase, dtype=np.float64)
    contraction = _progress(phases, config.contraction_start_phase, config.contraction_end_phase)
    refill = _progress(phases, config.refill_start_phase, config.refill_end_phase)
    amplitude = float(config.cavity_volume_scale_rest) - float(config.cavity_volume_scale_min)
    values = float(config.cavity_volume_scale_rest) - amplitude * contraction + amplitude * refill
    return np.clip(values, float(config.cavity_volume_scale_min), float(config.cavity_volume_scale_rest))


def funnel_aperture_scale(phase, config) -> np.ndarray:
    phases = np.asarray(phase, dtype=np.float64)
    weight = window_weight(phases, config.funnel_open_phase_start, config.funnel_open_phase_end, config.ramp_fraction)
    amplitude = float(config.funnel_aperture_scale_max) - float(config.funnel_aperture_scale_rest)
    values = float(config.funnel_aperture_scale_rest) + amplitude * weight
    return np.clip(values, float(config.funnel_aperture_scale_rest), float(config.funnel_aperture_scale_max))


def schedule_rows(config) -> list[dict]:
    phases = phase_samples(config)
    mantle = mantle_radius_scale(phases, config)
    cavity = cavity_volume_scale(phases, config)
    funnel = funnel_aperture_scale(phases, config)
    mantle_rate = _rate(mantle, phases)
    cavity_rate = _rate(cavity, phases)
    funnel_rate = _rate(funnel, phases)
    funnel_weight = window_weight(phases, config.funnel_open_phase_start, config.funnel_open_phase_end, config.ramp_fraction)
    rows = []
    for index, phase in enumerate(phases):
        row = {
            "sample_index": index,
            "phase": float(phase),
            "cycle_time_fraction": float(phase),
            "mantle_radius_scale": float(mantle[index]),
            "mantle_radius_rate": float(mantle_rate[index]),
            "cavity_volume_scale": float(cavity[index]),
            "cavity_volume_rate": float(cavity_rate[index]),
            "funnel_aperture_scale": float(funnel[index]),
            "funnel_aperture_rate": float(funnel_rate[index]),
            "phase_label": _phase_label(float(phase), config, bool(funnel_weight[index] > 0.0)),
            "ramp_weight": float(_ramp_weight(float(phase), config, funnel_weight[index])),
            "driver_integration_enabled": bool(config.driver_integration_enabled),
            "actuation_enabled": bool(config.actuation_enabled),
            "scope_note": SCHEDULE_SCOPE_NOTE,
        }
        rows.append(row)
    return rows


def summarize_schedule(rows: list[dict]) -> dict:
    if not rows:
        return {
            "row_count": 0,
            "phase_min": 0.0,
            "phase_max": 0.0,
            "finite_pass": False,
            "endpoint_repeatability_pass": False,
        }
    return {
        "row_count": len(rows),
        "phase_min": min(float(row["phase"]) for row in rows),
        "phase_max": max(float(row["phase"]) for row in rows),
        "finite_pass": _finite_rows(rows),
        "mantle_radius_scale_min_observed": min(float(row["mantle_radius_scale"]) for row in rows),
        "mantle_radius_scale_max_observed": max(float(row["mantle_radius_scale"]) for row in rows),
        "cavity_volume_scale_min_observed": min(float(row["cavity_volume_scale"]) for row in rows),
        "cavity_volume_scale_max_observed": max(float(row["cavity_volume_scale"]) for row in rows),
        "funnel_aperture_scale_min_observed": min(float(row["funnel_aperture_scale"]) for row in rows),
        "funnel_aperture_scale_max_observed": max(float(row["funnel_aperture_scale"]) for row in rows),
        "max_abs_mantle_radius_rate": max(abs(float(row["mantle_radius_rate"])) for row in rows),
        "max_abs_cavity_volume_rate": max(abs(float(row["cavity_volume_rate"])) for row in rows),
        "max_abs_funnel_aperture_rate": max(abs(float(row["funnel_aperture_rate"])) for row in rows),
        "endpoint_repeatability_pass": _endpoint_repeatability(rows),
        "driver_integration_enabled_count": sum(1 for row in rows if bool(row["driver_integration_enabled"])),
        "actuation_enabled_count": sum(1 for row in rows if bool(row["actuation_enabled"])),
    }


def write_schedule_outputs(rows: list[dict], csv_path, json_path, summary=None) -> None:
    summary_payload = summarize_schedule(rows) if summary is None else summary
    _write_csv(csv_path, rows, SCHEDULE_FIELDS)
    _write_json(json_path, {"summary": summary_payload, "rows": rows})


def _progress(phase: np.ndarray, start: float, end: float) -> np.ndarray:
    if end <= start:
        return np.zeros_like(phase)
    return smoothstep((phase - start) / (end - start))


def _rate(values: np.ndarray, phases: np.ndarray) -> np.ndarray:
    if len(values) <= 1:
        return np.zeros_like(values)
    return np.gradient(values, phases, edge_order=1)


def _phase_label(phase: float, config, funnel_open: bool) -> str:
    parts = []
    if math.isclose(phase, 0.0, abs_tol=1.0e-12) or math.isclose(phase, 1.0, abs_tol=1.0e-12):
        parts.append("cycle_endpoint")
    elif config.contraction_start_phase <= phase <= config.contraction_end_phase:
        parts.append("contraction")
    elif config.refill_start_phase <= phase <= config.refill_end_phase:
        parts.append("refill")
    else:
        parts.append("rest")
    if funnel_open:
        parts.append("funnel_open")
    return "+".join(parts)


def _ramp_weight(phase: float, config, funnel_weight: float) -> float:
    contraction = float(_progress(np.asarray([phase]), config.contraction_start_phase, config.contraction_end_phase)[0])
    refill = float(_progress(np.asarray([phase]), config.refill_start_phase, config.refill_end_phase)[0])
    return max(contraction, refill, float(funnel_weight))


def _endpoint_repeatability(rows: list[dict]) -> bool:
    first = rows[0]
    last = rows[-1]
    for field in ("mantle_radius_scale", "cavity_volume_scale", "funnel_aperture_scale"):
        if abs(float(first[field]) - float(last[field])) > 1.0e-12:
            return False
    return True


def _finite_rows(rows: list[dict]) -> bool:
    numeric_fields = [
        "phase",
        "cycle_time_fraction",
        "mantle_radius_scale",
        "mantle_radius_rate",
        "cavity_volume_scale",
        "cavity_volume_rate",
        "funnel_aperture_scale",
        "funnel_aperture_rate",
        "ramp_weight",
    ]
    for row in rows:
        for field in numeric_fields:
            if not math.isfinite(float(row[field])):
                return False
    return True


def _write_csv(path, rows: list[dict], fieldnames: list[str]) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_json(path, payload) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj
