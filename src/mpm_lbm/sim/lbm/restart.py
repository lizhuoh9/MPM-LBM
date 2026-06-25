from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


RESTART_ARRAY_KEYS = ("rho", "v", "f", "F", "solid", "static_solid")
RESTART_METADATA_KEY = "metadata_json"


def write_lbm_restart_npz(path: str | Path, arrays: dict[str, np.ndarray], metadata: dict[str, Any]) -> dict:
    path = Path(path)
    missing = [key for key in RESTART_ARRAY_KEYS if key not in arrays]
    if missing:
        raise ValueError("missing LBM restart arrays: " + ", ".join(missing))
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {key: np.asarray(arrays[key]) for key in RESTART_ARRAY_KEYS}
    payload[RESTART_METADATA_KEY] = np.asarray(json.dumps(metadata, sort_keys=True))
    np.savez_compressed(path, **payload)
    return restart_payload_stats(payload, metadata)


def read_lbm_restart_npz(path: str | Path) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"LBM restart not found: {path}")
    with np.load(path, allow_pickle=False) as data:
        arrays = {key: np.asarray(data[key]) for key in RESTART_ARRAY_KEYS}
        metadata_raw = str(np.asarray(data[RESTART_METADATA_KEY]).item())
    return arrays, json.loads(metadata_raw)


def validate_lbm_restart_metadata(metadata: dict[str, Any], expected: dict[str, Any]) -> dict:
    n_grid_matches = int(metadata.get("n_grid", -1)) == int(expected.get("n_grid", -2))
    boundary_matches = str(metadata.get("lbm_boundary_condition_mode", "")) == str(
        expected.get("lbm_boundary_condition_mode", "")
    )
    target_matches = _float_list(metadata.get("target_u_lbm", [])) == _float_list(expected.get("target_u_lbm", []))
    return {
        "restart_lbm_boundary_condition_mode_matches": bool(boundary_matches),
        "restart_n_grid_matches": bool(n_grid_matches),
        "restart_target_u_lbm_matches": bool(target_matches),
    }


def load_lbm_restart_to_lbm(lbm, path: str | Path, expected_metadata: dict[str, Any], required: bool = False) -> dict:
    try:
        arrays, metadata = read_lbm_restart_npz(path)
    except FileNotFoundError:
        if required:
            raise
        return {"restart_loaded": False, "restart_missing": True}

    guard = validate_lbm_restart_metadata(metadata, expected_metadata)
    if not all(guard.values()):
        raise ValueError(f"LBM restart metadata mismatch: {guard}")
    _validate_restart_shapes(arrays, int(expected_metadata["n_grid"]))
    lbm.rho.from_numpy(arrays["rho"].astype(np.float32, copy=False))
    lbm.v.from_numpy(arrays["v"].astype(np.float32, copy=False))
    lbm.f.from_numpy(arrays["f"].astype(np.float32, copy=False))
    lbm.F.from_numpy(arrays["F"].astype(np.float32, copy=False))
    lbm.solid.from_numpy(arrays["solid"].astype(np.int8, copy=False))
    lbm.static_solid.from_numpy(arrays["static_solid"].astype(np.int8, copy=False))
    report = restart_payload_stats(arrays, metadata)
    report.update(guard)
    report.update(
        {
            "restart_loaded": True,
            "restart_missing": False,
            "restart_path": str(path),
        }
    )
    return report


def save_lbm_restart_from_lbm(lbm, path: str | Path, metadata: dict[str, Any]) -> dict:
    arrays = {
        "rho": lbm.rho.to_numpy(),
        "v": lbm.v.to_numpy(),
        "f": lbm.f.to_numpy(),
        "F": lbm.F.to_numpy(),
        "solid": lbm.solid.to_numpy(),
        "static_solid": lbm.static_solid.to_numpy(),
    }
    return write_lbm_restart_npz(path, arrays, metadata)


def expected_restart_metadata_from_config(config) -> dict:
    return {
        "lbm_boundary_condition_mode": config.lbm_boundary_condition_mode,
        "lbm_restart_scope": config.lbm_restart_scope,
        "n_grid": int(config.n_grid),
        "target_u_lbm": [float(value) for value in config.target_u_lbm],
    }


def restart_payload_stats(arrays: dict[str, np.ndarray], metadata: dict[str, Any]) -> dict:
    rho = np.asarray(arrays["rho"], dtype=np.float64)
    v = np.asarray(arrays["v"], dtype=np.float64)
    solid = np.asarray(arrays["solid"])
    fluid = solid == 0
    if np.any(fluid):
        rho_fluid = rho[fluid]
        v_fluid = v[fluid]
        rho_min = float(np.min(rho_fluid))
        rho_max = float(np.max(rho_fluid))
        max_v = float(np.max(np.linalg.norm(v_fluid, axis=1)))
    else:
        rho_min = 0.0
        rho_max = 0.0
        max_v = 0.0
    numeric = [np.asarray(arrays[key]) for key in RESTART_ARRAY_KEYS]
    has_nan = any(np.issubdtype(array.dtype, np.floating) and bool(np.isnan(array).any()) for array in numeric)
    has_inf = any(np.issubdtype(array.dtype, np.floating) and bool(np.isinf(array).any()) for array in numeric)
    return {
        "array_keys": list(RESTART_ARRAY_KEYS),
        "has_inf": bool(has_inf),
        "has_nan": bool(has_nan),
        "metadata": dict(metadata),
        "rho_max": rho_max,
        "rho_min": rho_min,
        "velocity_max_norm": max_v,
    }


def _validate_restart_shapes(arrays: dict[str, np.ndarray], n_grid: int) -> None:
    expected_scalar = (n_grid, n_grid, n_grid)
    expected_vector = (n_grid, n_grid, n_grid, 3)
    expected_populations = (n_grid, n_grid, n_grid, 19)
    expected = {
        "F": expected_populations,
        "f": expected_populations,
        "rho": expected_scalar,
        "solid": expected_scalar,
        "static_solid": expected_scalar,
        "v": expected_vector,
    }
    bad = {key: arrays[key].shape for key, shape in expected.items() if arrays[key].shape != shape}
    if bad:
        raise ValueError(f"LBM restart array shape mismatch: {bad}")


def _float_list(values) -> list[float]:
    return [float(value) for value in values]
