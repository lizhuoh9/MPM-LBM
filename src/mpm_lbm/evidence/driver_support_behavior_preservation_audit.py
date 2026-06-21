from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

import numpy as np


def build_driver_support_behavior_preservation_audit(
    root: Path,
    policy_path: str = "configs/step57_behavior_preservation_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [
        sim_config_defaults_row(policy),
        fsi_driver_config_defaults_row(policy),
        geometry_config_defaults_row(policy),
        geometry_sampler_determinism_row(),
        geometry_quality_gate_row(),
        link_area_policy_constants_row(policy),
        fsi_mode_constants_row(policy),
        geometry_type_constants_row(policy),
        {
            "check": "solver_behavior_changed",
            "expected": False,
            "actual": bool(policy["solver_behavior_changed"]),
            "pass": not bool(policy["solver_behavior_changed"]),
            "notes": "Step 57 only migrates driver support ownership.",
        },
        {
            "check": "physics_feature_expansion",
            "expected": False,
            "actual": bool(policy["physics_feature_expansion"]),
            "pass": not bool(policy["physics_feature_expansion"]),
            "notes": "Step 57 does not add or validate new physics.",
        },
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "solver_object_construction_required": False,
        "driver_support_behavior_preservation_audit_pass": False,
    }
    summary["driver_support_behavior_preservation_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
        and not summary["solver_object_construction_required"]
    )
    return rows, summary


def sim_config_defaults_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.sim_config import UnifiedSimConfig

    expected = policy["sim_config_selected_defaults"]
    actual = selected_dataclass_defaults(UnifiedSimConfig, expected)
    return comparison_row("unified_sim_config_selected_defaults", expected, actual)


def fsi_driver_config_defaults_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    expected = policy["fsi_driver_config_selected_defaults"]
    actual = selected_dataclass_defaults(FSIDriverConfig, expected)
    return comparison_row("fsi_driver_config_selected_defaults", expected, actual)


def geometry_config_defaults_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.geometry.config import GeometryConfig

    expected = policy["geometry_config_selected_defaults"]
    actual = selected_dataclass_defaults(GeometryConfig, expected)
    return comparison_row("geometry_config_selected_defaults", expected, actual)


def geometry_sampler_determinism_row() -> dict:
    from src.mpm_lbm.sim.geometry.config import GeometryConfig
    from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D

    config = GeometryConfig(n_particles=8, particles_per_axis_hint=8)
    first = GeometrySampler3D(config).sample_particles()
    second = GeometrySampler3D(config).sample_particles()
    actual = {
        "particle_count": int(len(first["x"])),
        "same_x": bool(np.array_equal(first["x"], second["x"])),
        "same_vol0": bool(np.array_equal(first["vol0"], second["vol0"])),
        "same_mass": bool(np.array_equal(first["mass"], second["mass"])),
        "deterministic": bool(first["sampling_stats"]["deterministic"]),
    }
    expected = {
        "particle_count": 8,
        "same_x": True,
        "same_vol0": True,
        "same_mass": True,
        "deterministic": True,
    }
    return comparison_row("geometry_sampler_determinism", expected, actual)


def geometry_quality_gate_row() -> dict:
    from src.mpm_lbm.sim.geometry.quality import GeometryQualityGate

    mesh_report = {
        "quality_kind": "mesh",
        "vertices_count": 8,
        "faces_count": 12,
        "has_valid_face_indices": True,
        "degenerate_face_count": 1,
        "boundary_edge_count": 1,
        "nonmanifold_edge_count": 0,
        "duplicate_vertex_count": 0,
        "volume_abs": 1.0,
    }
    non_strict = GeometryQualityGate(strict=False).evaluate(mesh_report)
    strict = GeometryQualityGate(strict=True).evaluate(mesh_report)
    actual = {
        "non_strict_pass": bool(non_strict["pass"]),
        "non_strict_warning_count": len(non_strict["warnings"]),
        "strict_pass": bool(strict["pass"]),
        "strict_reason_count": len(strict["reasons"]),
    }
    expected = {
        "non_strict_pass": True,
        "non_strict_warning_count": 2,
        "strict_pass": False,
        "strict_reason_count": 2,
    }
    return comparison_row("geometry_quality_gate_strict_non_strict", expected, actual)


def link_area_policy_constants_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.coupling.link_area_accounting import VALID_AREA_POLICIES

    return comparison_row("link_area_policy_constants", policy["link_area_policy_constants"], list(VALID_AREA_POLICIES))


def fsi_mode_constants_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import VALID_COUPLING_MODES, VALID_REACTION_TRANSFER_MODES

    actual = {
        "valid_coupling_modes": list(VALID_COUPLING_MODES),
        "valid_reaction_transfer_modes": list(VALID_REACTION_TRANSFER_MODES),
    }
    expected = {
        "valid_coupling_modes": policy["valid_coupling_modes"],
        "valid_reaction_transfer_modes": policy["valid_reaction_transfer_modes"],
    }
    return comparison_row("fsi_mode_constants", expected, actual)


def geometry_type_constants_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.geometry.config import VALID_GEOMETRY_TYPES

    return comparison_row("valid_geometry_types", policy["valid_geometry_types"], list(VALID_GEOMETRY_TYPES))


def selected_dataclass_defaults(cls, expected: dict) -> dict:
    defaults = dataclass_defaults(cls)
    return {key: defaults[key] for key in expected}


def dataclass_defaults(cls) -> dict:
    defaults = {}
    for field in dataclasses.fields(cls):
        if field.default is dataclasses.MISSING:
            continue
        defaults[field.name] = normalize_value(field.default)
    return defaults


def comparison_row(check: str, expected, actual) -> dict:
    return {
        "check": check,
        "expected": normalize_value(expected),
        "actual": normalize_value(actual),
        "pass": values_match(expected, actual),
        "notes": "lightweight semantic preservation check",
    }


def values_match(expected, actual) -> bool:
    expected = normalize_value(expected)
    actual = normalize_value(actual)
    if isinstance(expected, dict) and isinstance(actual, dict):
        return expected.keys() == actual.keys() and all(values_match(expected[key], actual[key]) for key in expected)
    if isinstance(expected, list) and isinstance(actual, list):
        return len(expected) == len(actual) and all(values_match(left, right) for left, right in zip(expected, actual))
    if isinstance(expected, float) or isinstance(actual, float):
        return math.isclose(float(expected), float(actual), rel_tol=1.0e-12, abs_tol=1.0e-12)
    return expected == actual


def normalize_value(value):
    if isinstance(value, tuple):
        return [normalize_value(item) for item in value]
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
