from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional

import numpy as np


def snapshot_from_lbm(lbm: Any) -> Dict[str, np.ndarray]:
    return {
        "rho": np.asarray(lbm.rho.to_numpy(), dtype=float),
        "v": np.asarray(lbm.v.to_numpy(), dtype=float),
        "solid": np.asarray(lbm.solid.to_numpy(), dtype=np.int8),
        "f": np.asarray(lbm.f.to_numpy(), dtype=float),
        "F": np.asarray(lbm.F.to_numpy(), dtype=float),
    }


def population_stats(lbm_or_snapshot: Any) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    f = _population_array(snap, "f")
    F = _population_array(snap, "F")
    return {
        "f_min": _finite_float(np.nanmin(f)),
        "f_max": _finite_float(np.nanmax(f)),
        "F_min": _finite_float(np.nanmin(F)),
        "F_max": _finite_float(np.nanmax(F)),
        "f_all_finite": bool(np.all(np.isfinite(f))),
        "F_all_finite": bool(np.all(np.isfinite(F))),
        "all_finite": bool(np.all(np.isfinite(f)) and np.all(np.isfinite(F))),
    }


def negative_population_stats(lbm_or_snapshot: Any) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    f = _population_array(snap, "f")
    F = _population_array(snap, "F")
    f_neg = np.asarray(f < 0.0, dtype=bool)
    F_neg = np.asarray(F < 0.0, dtype=bool)
    count = int(np.count_nonzero(f_neg) + np.count_nonzero(F_neg))
    total = int(f.size + F.size)
    return {
        "negative_population_count": count,
        "negative_population_fraction": _finite_float(count / total if total else 0.0),
        "f_negative_population_count": int(np.count_nonzero(f_neg)),
        "F_negative_population_count": int(np.count_nonzero(F_neg)),
        "population_entry_count": total,
    }


def boundary_population_stats(lbm_or_snapshot: Any, side: str) -> Dict[str, Any]:
    if side not in ("x_min", "x_max"):
        raise ValueError("side must be 'x_min' or 'x_max'")
    snap = _snapshot(lbm_or_snapshot)
    f = _population_array(snap, "f")
    F = _population_array(snap, "F")
    x = 0 if side == "x_min" else f.shape[0] - 1
    f_plane = f[x, :, :, :]
    F_plane = F[x, :, :, :]
    neg_count = int(np.count_nonzero(f_plane < 0.0) + np.count_nonzero(F_plane < 0.0))
    total = int(f_plane.size + F_plane.size)
    return {
        "side": side,
        "x_index": int(x),
        "f_min": _finite_float(np.nanmin(f_plane)),
        "f_max": _finite_float(np.nanmax(f_plane)),
        "F_min": _finite_float(np.nanmin(F_plane)),
        "F_max": _finite_float(np.nanmax(F_plane)),
        "negative_population_count": neg_count,
        "negative_population_fraction": _finite_float(neg_count / total if total else 0.0),
        "all_finite": bool(np.all(np.isfinite(f_plane)) and np.all(np.isfinite(F_plane))),
    }


def density_outlier_stats(lbm_or_snapshot: Any, low: float = 0.0, high: float = 1.2) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    rho = np.asarray(snap["rho"], dtype=float)
    mask = _fluid_mask(snap)
    rho_fluid = rho[mask]
    low_locations = _locations(mask & (rho < float(low)))
    high_locations = _locations(mask & (rho > float(high)))
    return {
        "rho_min": _finite_float(np.nanmin(rho_fluid)) if rho_fluid.size else 0.0,
        "rho_max": _finite_float(np.nanmax(rho_fluid)) if rho_fluid.size else 0.0,
        "rho_low_threshold": float(low),
        "rho_high_threshold": float(high),
        "rho_below_low_count": int(len(low_locations)),
        "rho_above_high_count": int(len(high_locations)),
        "first_negative_density_location": low_locations[0] if low_locations else None,
        "first_high_density_location": high_locations[0] if high_locations else None,
        "all_finite": bool(np.all(np.isfinite(rho_fluid))) if rho_fluid.size else True,
    }


def velocity_outlier_stats(lbm_or_snapshot: Any, max_v_threshold: float = 0.2) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    vel = np.asarray(snap["v"], dtype=float)
    mask = _fluid_mask(snap)
    if not np.any(mask):
        return {
            "max_v": 0.0,
            "max_v_threshold": float(max_v_threshold),
            "velocity_outlier_count": 0,
            "velocity_outlier_fraction": 0.0,
            "first_velocity_outlier_location": None,
            "all_finite": True,
        }
    speeds = np.linalg.norm(vel, axis=-1)
    outliers = mask & (speeds > float(max_v_threshold))
    locations = _locations(outliers)
    return {
        "max_v": _finite_float(np.nanmax(speeds[mask])),
        "max_v_threshold": float(max_v_threshold),
        "velocity_outlier_count": int(len(locations)),
        "velocity_outlier_fraction": _finite_float(len(locations) / int(np.count_nonzero(mask))),
        "first_velocity_outlier_location": locations[0] if locations else None,
        "all_finite": bool(np.all(np.isfinite(vel[mask]))),
    }


def mass_source_sink_by_step(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(records)
    if not rows:
        return {
            "record_count": 0,
            "mass_drift_initial": None,
            "mass_drift_final": None,
            "mass_drift_delta_final": None,
            "mass_drift_abs_max": None,
        }
    values = [_record_float(row, "mass_total_delta_rel") for row in rows]
    return {
        "record_count": int(len(rows)),
        "mass_drift_initial": values[0],
        "mass_drift_final": values[-1],
        "mass_drift_delta_final": _finite_float(values[-1] - values[0]),
        "mass_drift_abs_max": _finite_float(max(abs(value) for value in values)),
    }


def first_gate_failure_detector(
    records: Iterable[Dict[str, Any]],
    rho_low: float = 0.0,
    rho_high: float = 1.2,
    mass_drift_abs: float = 0.05,
    max_v: float = 0.2,
) -> Dict[str, Any]:
    rows = list(records)
    result = {
        "record_count": int(len(rows)),
        "all_records_finite": True,
        "first_nonfinite_step": None,
        "first_negative_density_step": None,
        "first_high_density_step": None,
        "first_mass_drift_step": None,
        "first_max_v_step": None,
        "first_failure_step": None,
        "first_failure_reason": None,
    }
    failures = []
    for row in rows:
        step = int(_record_float(row, "step"))
        values = [
            _record_float(row, "rho_min"),
            _record_float(row, "rho_max"),
            _record_float(row, "mass_total_delta_rel"),
            _record_float(row, "max_v"),
        ]
        if not all(math.isfinite(value) for value in values):
            result["all_records_finite"] = False
            _set_first(result, "first_nonfinite_step", step)
            failures.append((step, "nonfinite"))
        if _record_float(row, "rho_min") < float(rho_low):
            _set_first(result, "first_negative_density_step", step)
            failures.append((step, "negative_density"))
        if _record_float(row, "rho_max") > float(rho_high):
            _set_first(result, "first_high_density_step", step)
            failures.append((step, "high_density"))
        if abs(_record_float(row, "mass_total_delta_rel")) > float(mass_drift_abs):
            _set_first(result, "first_mass_drift_step", step)
            failures.append((step, "mass_drift"))
        if _record_float(row, "max_v") > float(max_v):
            _set_first(result, "first_max_v_step", step)
            failures.append((step, "max_v"))

    if failures:
        failures.sort(key=lambda item: item[0])
        result["first_failure_step"] = int(failures[0][0])
        result["first_failure_reason"] = failures[0][1]
    return result


def classify_first_failure_location(lbm_or_snapshot: Any) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    density = density_outlier_stats(snap)
    velocity = velocity_outlier_stats(snap)
    candidates = [
        density["first_negative_density_location"],
        density["first_high_density_location"],
        velocity["first_velocity_outlier_location"],
    ]
    location = next((candidate for candidate in candidates if candidate is not None), None)
    return {
        "first_failure_location": _location_label(location, snap["rho"].shape) if location is not None else None,
        "first_failure_cell": location,
    }


def summarize_lbm_stability_diagnostics(lbm_or_snapshot: Any, step: int) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    density = density_outlier_stats(snap)
    velocity = velocity_outlier_stats(snap)
    negative = negative_population_stats(snap)
    inlet = boundary_population_stats(snap, "x_min")
    outlet = boundary_population_stats(snap, "x_max")
    location = classify_first_failure_location(snap)
    return {
        "step": int(step),
        **population_stats(snap),
        **negative,
        "rho_below_low_count": density["rho_below_low_count"],
        "rho_above_high_count": density["rho_above_high_count"],
        "first_negative_density_location": density["first_negative_density_location"],
        "first_high_density_location": density["first_high_density_location"],
        "velocity_outlier_count": velocity["velocity_outlier_count"],
        "first_velocity_outlier_location": velocity["first_velocity_outlier_location"],
        "boundary_x_min_negative_population_count": inlet["negative_population_count"],
        "boundary_x_max_negative_population_count": outlet["negative_population_count"],
        "first_failure_location": location["first_failure_location"],
        "first_failure_cell": location["first_failure_cell"],
        "stability_all_finite": bool(
            density["all_finite"] and velocity["all_finite"] and inlet["all_finite"] and outlet["all_finite"]
        ),
    }


def _snapshot(data: Any) -> Dict[str, np.ndarray]:
    if isinstance(data, dict):
        snap = {
            "rho": np.asarray(data["rho"], dtype=float),
            "v": np.asarray(data["v"], dtype=float),
            "solid": np.asarray(data["solid"], dtype=np.int8),
        }
        if "f" in data:
            snap["f"] = np.asarray(data["f"], dtype=float)
        if "F" in data:
            snap["F"] = np.asarray(data["F"], dtype=float)
        return snap
    return snapshot_from_lbm(data)


def _population_array(snap: Dict[str, np.ndarray], key: str) -> np.ndarray:
    if key in snap:
        return np.asarray(snap[key], dtype=float)
    rho = np.asarray(snap["rho"], dtype=float)
    return np.zeros(rho.shape + (19,), dtype=float)


def _fluid_mask(snap: Dict[str, np.ndarray]) -> np.ndarray:
    return np.asarray(snap["solid"] == 0, dtype=bool)


def _locations(mask: np.ndarray) -> List[List[int]]:
    return [[int(value) for value in loc] for loc in np.argwhere(mask)]


def _location_label(location: Optional[List[int]], shape: Any) -> Optional[str]:
    if location is None:
        return None
    x, y, z = location
    nx, ny, nz = shape
    if x == 0:
        return "inlet"
    if x == nx - 1:
        return "outlet"
    if y in (0, ny - 1) or z in (0, nz - 1):
        return "wall_or_open_boundary_corner"
    return "interior"


def _set_first(result: Dict[str, Any], key: str, step: int) -> None:
    if result[key] is None:
        result[key] = int(step)


def _record_float(record: Dict[str, Any], key: str) -> float:
    value = record.get(key, 0.0)
    if value is None:
        return float("nan")
    return float(value)


def _finite_float(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        return result
    return result
