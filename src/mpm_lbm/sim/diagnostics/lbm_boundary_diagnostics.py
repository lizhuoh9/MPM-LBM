from __future__ import annotations

import math
from typing import Any, Dict, Optional

import numpy as np


def snapshot_from_lbm(lbm: Any) -> Dict[str, np.ndarray]:
    return {
        "rho": np.asarray(lbm.rho.to_numpy(), dtype=float),
        "v": np.asarray(lbm.v.to_numpy(), dtype=float),
        "solid": np.asarray(lbm.solid.to_numpy(), dtype=np.int8),
    }


def _snapshot(data: Any) -> Dict[str, np.ndarray]:
    if isinstance(data, dict):
        return {
            "rho": np.asarray(data["rho"], dtype=float),
            "v": np.asarray(data["v"], dtype=float),
            "solid": np.asarray(data["solid"], dtype=np.int8),
        }
    return snapshot_from_lbm(data)


def fluid_mask(lbm_or_snapshot: Any) -> np.ndarray:
    snap = _snapshot(lbm_or_snapshot)
    return np.asarray(snap["solid"] == 0, dtype=bool)


def plane_flux_x(lbm_or_snapshot: Any, x_index: int) -> float:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    x = _clamp_index(int(x_index), snap["rho"].shape[0])
    plane = mask[x, :, :]
    if not np.any(plane):
        return 0.0
    return _finite_float(np.sum(snap["rho"][x, :, :][plane] * snap["v"][x, :, :, 0][plane]))


def plane_mean_velocity_x(lbm_or_snapshot: Any, x_index: int) -> float:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    x = _clamp_index(int(x_index), snap["rho"].shape[0])
    plane = mask[x, :, :]
    if not np.any(plane):
        return 0.0
    return _finite_float(np.mean(snap["v"][x, :, :, 0][plane]))


def density_stats(lbm_or_snapshot: Any) -> Dict[str, float]:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    if not np.any(mask):
        return {
            "fluid_cell_count": 0,
            "rho_min": 0.0,
            "rho_max": 0.0,
            "rho_mean": 0.0,
            "rho_std": 0.0,
        }
    rho = snap["rho"][mask]
    return {
        "fluid_cell_count": int(rho.size),
        "rho_min": _finite_float(np.min(rho)),
        "rho_max": _finite_float(np.max(rho)),
        "rho_mean": _finite_float(np.mean(rho)),
        "rho_std": _finite_float(np.std(rho)),
    }


def mass_total(lbm_or_snapshot: Any) -> float:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    if not np.any(mask):
        return 0.0
    return _finite_float(np.sum(snap["rho"][mask]))


def centerline_profile_x(lbm_or_snapshot: Any, y_index: Optional[int] = None, z_index: Optional[int] = None) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    nx, ny, nz = snap["rho"].shape
    y = _clamp_index(ny // 2 if y_index is None else int(y_index), ny)
    z = _clamp_index(nz // 2 if z_index is None else int(z_index), nz)

    values = []
    source = []
    for x in range(nx):
        if mask[x, y, z]:
            values.append(_finite_float(snap["v"][x, y, z, 0]))
            source.append("centerline")
        else:
            plane = mask[x, :, :]
            values.append(_finite_float(np.mean(snap["v"][x, :, :, 0][plane])) if np.any(plane) else 0.0)
            source.append("plane_mean_fallback")
    return {
        "axis": "x",
        "y_index": int(y),
        "z_index": int(z),
        "ux": values,
        "source": source,
    }


def outlet_reflection_proxy(lbm_or_snapshot: Any) -> Dict[str, float]:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    nx = snap["rho"].shape[0]
    x = _clamp_index(nx - 2 if nx > 2 else nx - 1, nx)
    plane = mask[x, :, :]
    if not np.any(plane):
        return {
            "proxy_name": "outlet_near_plane_ux_density_variation",
            "x_index": int(x),
            "fluid_cell_count": 0,
            "ux_std": 0.0,
            "negative_ux_fraction": 0.0,
            "rho_std": 0.0,
            "rho_peak_to_peak": 0.0,
        }
    ux = snap["v"][x, :, :, 0][plane]
    rho = snap["rho"][x, :, :][plane]
    return {
        "proxy_name": "outlet_near_plane_ux_density_variation",
        "x_index": int(x),
        "fluid_cell_count": int(ux.size),
        "ux_std": _finite_float(np.std(ux)),
        "negative_ux_fraction": _finite_float(np.mean(ux < 0.0)),
        "rho_std": _finite_float(np.std(rho)),
        "rho_peak_to_peak": _finite_float(np.max(rho) - np.min(rho)),
    }


def plane_velocity_x_stats(lbm_or_snapshot: Any, x_index: int) -> Dict[str, float]:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    x = _clamp_index(int(x_index), snap["rho"].shape[0])
    plane = mask[x, :, :]
    if not np.any(plane):
        return {
            "x_index": int(x),
            "fluid_cell_count": 0,
            "ux_min": 0.0,
            "ux_max": 0.0,
            "ux_mean": 0.0,
            "negative_ux_fraction": 0.0,
        }
    ux = snap["v"][x, :, :, 0][plane]
    return {
        "x_index": int(x),
        "fluid_cell_count": int(ux.size),
        "ux_min": _finite_float(np.min(ux)),
        "ux_max": _finite_float(np.max(ux)),
        "ux_mean": _finite_float(np.mean(ux)),
        "negative_ux_fraction": _finite_float(np.mean(ux < 0.0)),
    }


def plane_density_stats(lbm_or_snapshot: Any, x_index: int) -> Dict[str, float]:
    snap = _snapshot(lbm_or_snapshot)
    mask = fluid_mask(snap)
    x = _clamp_index(int(x_index), snap["rho"].shape[0])
    plane = mask[x, :, :]
    if not np.any(plane):
        return {
            "x_index": int(x),
            "fluid_cell_count": 0,
            "rho_mean": 0.0,
            "rho_std": 0.0,
        }
    rho = snap["rho"][x, :, :][plane]
    return {
        "x_index": int(x),
        "fluid_cell_count": int(rho.size),
        "rho_mean": _finite_float(np.mean(rho)),
        "rho_std": _finite_float(np.std(rho)),
    }


def sampled_x_profile_flux(lbm_or_snapshot: Any) -> str:
    snap = _snapshot(lbm_or_snapshot)
    nx = snap["rho"].shape[0]
    sample_indices = sorted({0, nx // 2, nx - 1})
    return ";".join(f"{x}:{plane_flux_x(snap, x):.12g}" for x in sample_indices)


def summarize_lbm_boundary_diagnostics(
    lbm_or_snapshot: Any,
    step: int,
    mass_initial: Optional[float] = None,
) -> Dict[str, Any]:
    snap = _snapshot(lbm_or_snapshot)
    density = density_stats(snap)
    mass = mass_total(snap)
    if mass_initial is None:
        mass_initial = mass
    mass_delta = mass - float(mass_initial)
    mass_delta_rel = 0.0 if float(mass_initial) == 0.0 else mass_delta / float(mass_initial)
    nx = snap["rho"].shape[0]
    mid_x = nx // 2
    inlet_flux = plane_flux_x(snap, 0)
    outlet_flux = plane_flux_x(snap, nx - 1)
    midplane_flux = plane_flux_x(snap, mid_x)
    near_outlet_flux_xminus1 = plane_flux_x(snap, nx - 2)
    near_outlet_flux_xminus2 = plane_flux_x(snap, nx - 3)
    near_outlet_flux_xminus3 = plane_flux_x(snap, nx - 4)
    outlet_plane = plane_velocity_x_stats(snap, nx - 1)
    outlet_plane_density = plane_density_stats(snap, nx - 1)
    scale = max(abs(inlet_flux), abs(outlet_flux), 1.0e-12)
    flux_imbalance_abs = abs(inlet_flux - outlet_flux)
    max_v = _max_velocity(snap)
    return {
        "step": int(step),
        **density,
        "mass_total": mass,
        "mass_total_delta_from_initial": _finite_float(mass_delta),
        "mass_total_delta_rel": _finite_float(mass_delta_rel),
        "inlet_mean_ux": plane_mean_velocity_x(snap, 0),
        "outlet_mean_ux": plane_mean_velocity_x(snap, nx - 1),
        "midplane_mean_ux": plane_mean_velocity_x(snap, mid_x),
        "inlet_flux": inlet_flux,
        "outlet_flux": outlet_flux,
        "midplane_flux": midplane_flux,
        "near_outlet_flux_xminus1": near_outlet_flux_xminus1,
        "near_outlet_flux_xminus2": near_outlet_flux_xminus2,
        "near_outlet_flux_xminus3": near_outlet_flux_xminus3,
        "near_outlet_to_outlet_flux_ratio": _safe_ratio(near_outlet_flux_xminus1, outlet_flux),
        "flux_imbalance_abs": _finite_float(flux_imbalance_abs),
        "flux_imbalance_rel": _finite_float(flux_imbalance_abs / scale),
        "flux_balance_reported": True,
        "max_v": max_v,
        "mach_proxy_observed": _finite_float(max_v / math.sqrt(1.0 / 3.0)),
        "centerline_ux_profile": centerline_profile_x(snap),
        "sampled_x_profile_flux": sampled_x_profile_flux(snap),
        "outlet_reflection_proxy": outlet_reflection_proxy(snap),
        "outlet_plane_ux_min": outlet_plane["ux_min"],
        "outlet_plane_ux_max": outlet_plane["ux_max"],
        "outlet_plane_ux_mean": outlet_plane["ux_mean"],
        "outlet_plane_negative_ux_fraction": outlet_plane["negative_ux_fraction"],
        "outlet_plane_rho_mean": outlet_plane_density["rho_mean"],
        "outlet_plane_rho_std": outlet_plane_density["rho_std"],
        "all_finite": _all_numeric_finite(snap),
    }


def summarize_timeseries_trends(records: Any, tail_fraction: float = 0.2) -> Dict[str, Any]:
    rows = list(records)
    if not rows:
        raise ValueError("records must not be empty")
    if tail_fraction <= 0.0 or tail_fraction > 1.0:
        raise ValueError("tail_fraction must be in (0, 1]")

    tail_count = max(1, int(math.ceil(len(rows) * float(tail_fraction))))
    tail = rows[-tail_count:]
    final = rows[-1]
    inlet_flux_tail_values = [_record_float(row, "inlet_flux") for row in tail]
    outlet_flux_tail_values = [_record_float(row, "outlet_flux") for row in tail]
    flux_imbalance_tail_values = [_record_float(row, "flux_imbalance_rel") for row in tail]
    inlet_flux_tail_mean = _finite_float(np.mean(inlet_flux_tail_values))
    outlet_flux_tail_mean = _finite_float(np.mean(outlet_flux_tail_values))
    inlet_mean_ux_tail_mean = _finite_float(np.mean([_record_float(row, "inlet_mean_ux") for row in tail]))
    midplane_mean_ux_tail_mean = _finite_float(np.mean([_record_float(row, "midplane_mean_ux") for row in tail]))

    return {
        "record_count": int(len(rows)),
        "tail_fraction": float(tail_fraction),
        "tail_record_count": int(tail_count),
        "step_initial": int(_record_float(rows[0], "step")),
        "step_final": int(_record_float(final, "step")),
        "rho_min_global": _finite_float(min(_record_float(row, "rho_min") for row in rows)),
        "rho_max_global": _finite_float(max(_record_float(row, "rho_max") for row in rows)),
        "mass_drift_final": _record_float(final, "mass_total_delta_rel"),
        "mass_drift_abs_max": _finite_float(max(abs(_record_float(row, "mass_total_delta_rel")) for row in rows)),
        "mass_drift_tail_mean": _finite_float(np.mean([_record_float(row, "mass_total_delta_rel") for row in tail])),
        "flux_imbalance_rel_final": _record_float(final, "flux_imbalance_rel"),
        "flux_imbalance_rel_min": _finite_float(min(_record_float(row, "flux_imbalance_rel") for row in rows)),
        "flux_imbalance_rel_max": _finite_float(max(_record_float(row, "flux_imbalance_rel") for row in rows)),
        "flux_imbalance_rel_tail_mean": _finite_float(np.mean(flux_imbalance_tail_values)),
        "flux_imbalance_rel_tail_max": _finite_float(max(flux_imbalance_tail_values)),
        "outlet_flux_final": _record_float(final, "outlet_flux"),
        "inlet_flux_tail_mean": inlet_flux_tail_mean,
        "outlet_flux_tail_mean": outlet_flux_tail_mean,
        "outlet_flux_tail_cv": _safe_cv(outlet_flux_tail_values),
        "outlet_to_inlet_flux_ratio_tail_mean": _safe_ratio(outlet_flux_tail_mean, inlet_flux_tail_mean),
        "inlet_mean_ux_tail_mean": inlet_mean_ux_tail_mean,
        "midplane_mean_ux_tail_mean": midplane_mean_ux_tail_mean,
        "midplane_to_inlet_flux_ratio_tail_mean": _safe_ratio(midplane_mean_ux_tail_mean, inlet_mean_ux_tail_mean),
        "max_v_global": _finite_float(max(_record_float(row, "max_v") for row in rows)),
        "mach_proxy_observed_max": _finite_float(max(_record_float(row, "mach_proxy_observed") for row in rows)),
        "negative_ux_fraction_tail_mean": _finite_float(
            np.mean([_outlet_proxy_float(row, "negative_ux_fraction") for row in tail])
        ),
        "rho_std_outlet_tail_mean": _finite_float(np.mean([_outlet_proxy_float(row, "rho_std") for row in tail])),
        "ux_std_outlet_tail_mean": _finite_float(np.mean([_outlet_proxy_float(row, "ux_std") for row in tail])),
    }


def _max_velocity(snap: Dict[str, np.ndarray]) -> float:
    mask = fluid_mask(snap)
    if not np.any(mask):
        return 0.0
    speeds = np.linalg.norm(snap["v"][mask], axis=1)
    return _finite_float(np.max(speeds))


def _all_numeric_finite(snap: Dict[str, np.ndarray]) -> bool:
    return bool(np.all(np.isfinite(snap["rho"])) and np.all(np.isfinite(snap["v"])))


def _record_float(record: Dict[str, Any], key: str) -> float:
    return _finite_float(record.get(key, 0.0))


def _outlet_proxy_float(record: Dict[str, Any], key: str) -> float:
    proxy = record.get("outlet_reflection_proxy", {})
    if not isinstance(proxy, dict):
        return 0.0
    return _finite_float(proxy.get(key, 0.0))


def _safe_ratio(numerator: float, denominator: float) -> float:
    if abs(float(denominator)) < 1.0e-12:
        return 0.0
    return _finite_float(float(numerator) / float(denominator))


def _safe_cv(values: Any) -> float:
    array = np.asarray(list(values), dtype=float)
    if array.size == 0:
        return 0.0
    mean = _finite_float(np.mean(array))
    if abs(mean) < 1.0e-12:
        return 0.0
    return _finite_float(np.std(array) / abs(mean))


def _clamp_index(index: int, size: int) -> int:
    if size <= 0:
        raise ValueError("axis size must be positive")
    return max(0, min(index, size - 1))


def _finite_float(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        return 0.0
    return result
