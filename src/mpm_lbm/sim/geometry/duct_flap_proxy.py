from __future__ import annotations

import math
from typing import Any

import numpy as np


DEFAULT_DUCT = {
    "x": [0.0, 1.0],
    "y": [0.3, 0.7],
    "z": [0.45, 0.55],
}
DEFAULT_FLAP = {
    "anchor_x": 0.505,
    "anchor_y": 0.3,
    "height_over_duct_height": 0.25,
    "thickness_over_duct_height": 0.075,
    "normalized_height": 0.10,
    "normalized_thickness": 0.03,
    "z": [0.45, 0.55],
    "fixed_base": True,
}
DEFAULT_MATERIAL_REFERENCE = {
    "density": 1600.0,
    "youngs_modulus": 1.0e6,
    "poisson_ratio": 0.47,
    "used_for_exact_structural_model": False,
}


def validate_duct_flap_proxy_config(config) -> None:
    duct = _duct_dict(config)
    flap = _flap_dict(config)
    material = _material_dict(config)
    for key in ("x", "y", "z"):
        _validate_interval(duct[key], f"duct.{key}")
    _validate_interval(flap["z"], "flap.z")
    for key in ("anchor_x", "anchor_y", "height_over_duct_height", "thickness_over_duct_height"):
        _validate_finite_positive_or_position(flap[key], f"flap.{key}", position=key.startswith("anchor_"))
    for key in ("normalized_height", "normalized_thickness"):
        _validate_finite_positive_or_position(flap[key], f"flap.{key}", position=False)
    if flap["normalized_height"] <= 0.0 or flap["normalized_thickness"] <= 0.0:
        raise ValueError("duct_flap_proxy normalized dimensions must be positive")
    for key in ("density", "youngs_modulus", "poisson_ratio"):
        _validate_finite_positive_or_position(material[key], f"material_reference.{key}", position=False)
    if bool(material.get("used_for_exact_structural_model", True)):
        raise ValueError("duct_flap_proxy material_reference must not claim exact structural-model equivalence")


def inside_duct_flap_proxy(points: np.ndarray, config) -> np.ndarray:
    masks = duct_flap_proxy_component_masks(points, config)
    return masks["flap"].copy()


def duct_flap_proxy_component_masks(points: np.ndarray, config) -> dict[str, np.ndarray]:
    pts = _as_points(points)
    duct = _duct_dict(config)
    flap = _flap_dict(config)
    flap_min, flap_max = flap_bounds(config)
    duct_mask = _inside_bounds(pts, [duct["x"][0], duct["y"][0], duct["z"][0]], [duct["x"][1], duct["y"][1], duct["z"][1]])
    flap_mask = _inside_bounds(pts, flap_min, flap_max)

    base_top = min(flap_max[1], flap_min[1] + max(float(flap["normalized_thickness"]), 0.2 * float(flap["normalized_height"])))
    base_mask = _inside_bounds(pts, flap_min, [flap_max[0], base_top, flap_max[2]]) & flap_mask
    tip_start = max(flap_min[1], flap_max[1] - max(float(flap["normalized_thickness"]), 0.2 * float(flap["normalized_height"])))
    tip_mask = _inside_bounds(pts, [flap_min[0], tip_start, flap_min[2]], flap_max) & flap_mask
    return {
        "duct_context": duct_mask,
        "flap": flap_mask,
        "fixed_base": base_mask,
        "free_tip_proxy": tip_mask,
    }


def duct_flap_proxy_sampling_stats(config) -> dict[str, Any]:
    duct = _duct_dict(config)
    flap = _flap_dict(config)
    material = _material_dict(config)
    ratios = geometry_ratios(config)
    return {
        "duct_flap_proxy_enabled": True,
        "fluent_inspired_geometry_ratios_recorded": True,
        "official_mesh_imported": False,
        "official_fluent_files_used_as_runtime_input": False,
        "duct_x_min": float(duct["x"][0]),
        "duct_x_max": float(duct["x"][1]),
        "duct_y_min": float(duct["y"][0]),
        "duct_y_max": float(duct["y"][1]),
        "duct_z_min": float(duct["z"][0]),
        "duct_z_max": float(duct["z"][1]),
        "flap_anchor_x": float(flap["anchor_x"]),
        "flap_anchor_y": float(flap["anchor_y"]),
        "flap_normalized_height": float(flap["normalized_height"]),
        "flap_normalized_thickness": float(flap["normalized_thickness"]),
        "flap_height_over_duct_height": float(ratios["height_over_duct_height"]),
        "flap_thickness_over_duct_height": float(ratios["thickness_over_duct_height"]),
        "material_density": float(material["density"]),
        "material_youngs_modulus": float(material["youngs_modulus"]),
        "material_poisson_ratio": float(material["poisson_ratio"]),
        "used_for_exact_structural_model": bool(material["used_for_exact_structural_model"]),
        "scope_note": (
            "procedural Fluent-inspired duct-flap proxy; not Fluent mesh import, not Fluent validation, "
            "and not an exact structural model"
        ),
    }


def duct_flap_proxy_quality_metadata(config) -> dict[str, Any]:
    metadata = duct_flap_proxy_sampling_stats(config)
    metadata.update(
        {
            "quality_scope": "procedural duct-flap proxy quality only",
            "official_case_dimensionality": "2D",
            "our_solver_dimensionality": "3D",
            "direct_quantitative_equivalence_allowed": False,
            "validation_claim_allowed": False,
        }
    )
    return metadata


def geometry_ratios(config) -> dict[str, float]:
    duct = _duct_dict(config)
    flap = _flap_dict(config)
    duct_height = float(duct["y"][1]) - float(duct["y"][0])
    return {
        "height_over_duct_height": float(flap["normalized_height"]) / duct_height,
        "thickness_over_duct_height": float(flap["normalized_thickness"]) / duct_height,
    }


def flap_bounds(config) -> tuple[np.ndarray, np.ndarray]:
    flap = _flap_dict(config)
    half_thickness = 0.5 * float(flap["normalized_thickness"])
    flap_min = np.array(
        [
            float(flap["anchor_x"]) - half_thickness,
            float(flap["anchor_y"]),
            float(flap["z"][0]),
        ],
        dtype=np.float64,
    )
    flap_max = np.array(
        [
            float(flap["anchor_x"]) + half_thickness,
            float(flap["anchor_y"]) + float(flap["normalized_height"]),
            float(flap["z"][1]),
        ],
        dtype=np.float64,
    )
    return flap_min, flap_max


def _inside_bounds(points: np.ndarray, lo, hi) -> np.ndarray:
    lo_array = np.asarray(lo, dtype=np.float64)
    hi_array = np.asarray(hi, dtype=np.float64)
    return np.all((points >= lo_array) & (points <= hi_array), axis=1)


def _duct_dict(config) -> dict[str, Any]:
    return dict(DEFAULT_DUCT if getattr(config, "duct", None) is None else config.duct)


def _flap_dict(config) -> dict[str, Any]:
    return dict(DEFAULT_FLAP if getattr(config, "flap", None) is None else config.flap)


def _material_dict(config) -> dict[str, Any]:
    return dict(
        DEFAULT_MATERIAL_REFERENCE
        if getattr(config, "material_reference", None) is None
        else config.material_reference
    )


def _as_points(points: np.ndarray) -> np.ndarray:
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError("points must have shape (n, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError("points must be finite")
    return array


def _validate_interval(values, name: str) -> None:
    if len(values) != 2:
        raise ValueError(f"{name} must contain exactly two values")
    lo = float(values[0])
    hi = float(values[1])
    if not math.isfinite(lo) or not math.isfinite(hi) or lo >= hi:
        raise ValueError(f"{name} must be finite and increasing")


def _validate_finite_positive_or_position(value, name: str, position: bool) -> None:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if not position and number <= 0.0:
        raise ValueError(f"{name} must be positive")
