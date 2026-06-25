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
        "flux_imbalance_abs": _finite_float(flux_imbalance_abs),
        "flux_imbalance_rel": _finite_float(flux_imbalance_abs / scale),
        "flux_balance_reported": True,
        "max_v": max_v,
        "mach_proxy_observed": _finite_float(max_v / math.sqrt(1.0 / 3.0)),
        "centerline_ux_profile": centerline_profile_x(snap),
        "outlet_reflection_proxy": outlet_reflection_proxy(snap),
        "all_finite": _all_numeric_finite(snap),
    }


def _max_velocity(snap: Dict[str, np.ndarray]) -> float:
    mask = fluid_mask(snap)
    if not np.any(mask):
        return 0.0
    speeds = np.linalg.norm(snap["v"][mask], axis=1)
    return _finite_float(np.max(speeds))


def _all_numeric_finite(snap: Dict[str, np.ndarray]) -> bool:
    return bool(np.all(np.isfinite(snap["rho"])) and np.all(np.isfinite(snap["v"])))


def _clamp_index(index: int, size: int) -> int:
    if size <= 0:
        raise ValueError("axis size must be positive")
    return max(0, min(index, size - 1))


def _finite_float(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        return 0.0
    return result
