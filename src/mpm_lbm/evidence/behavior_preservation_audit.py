from __future__ import annotations

import dataclasses
import json
import math
import subprocess
from pathlib import Path

import numpy as np


def build_behavior_preservation_audit(
    root: Path,
    policy_path: str = "configs/step56_behavior_preservation_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [
        lbm_config_defaults_row(policy),
        mpm_config_defaults_row(policy),
        grid_unit_mapper_row(policy),
        legacy_tau_row(policy),
        standard_tau_row(policy),
        unmigrated_paths_row(root, policy),
        {
            "check": "solver_behavior_changed",
            "expected": False,
            "actual": bool(policy["solver_behavior_changed"]),
            "pass": not bool(policy["solver_behavior_changed"]),
            "notes": "Step 56 only migrates module ownership for the Wave 1 batch.",
        },
        {
            "check": "physics_feature_expansion",
            "expected": False,
            "actual": bool(policy["physics_feature_expansion"]),
            "pass": not bool(policy["physics_feature_expansion"]),
            "notes": "Step 56 does not add or validate new physics.",
        },
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "object_construction_required_for_lbm_fluid_or_mpm_solid": False,
        "behavior_preservation_audit_pass": False,
    }
    summary["behavior_preservation_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
        and not summary["object_construction_required_for_lbm_fluid_or_mpm_solid"]
    )
    return rows, summary


def lbm_config_defaults_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.lbm.config import LBMConfig

    actual = dataclass_defaults(LBMConfig)
    expected = policy["lbm_config_required_defaults"]
    return comparison_row("lbm_config_defaults", expected, actual)


def mpm_config_defaults_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.mpm.config import MPMConfig

    actual = dataclass_defaults(MPMConfig)
    expected = policy["mpm_config_required_defaults"]
    return comparison_row("mpm_config_defaults", expected, actual)


def grid_unit_mapper_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.units.mapper import GridUnitMapper

    sample = policy["mapper_sample"]
    mapper = GridUnitMapper(
        n_grid=int(sample["n_grid"]),
        dx_norm=float(sample["dx_norm"]),
        lbm_dt_phys=float(sample["lbm_dt_phys"]),
    )
    actual = {
        "norm_to_lbm_coord": mapper.norm_to_lbm_coord(sample["norm_coord"]).tolist(),
        "lbm_coord_to_norm": mapper.lbm_coord_to_norm(sample["lbm_coord"]).tolist(),
        "norm_to_lbm_index": mapper.norm_to_lbm_index(sample["norm_coord"]).tolist(),
        "lbm_index_to_norm_center": mapper.lbm_index_to_norm_center([2, 16, 30]).tolist(),
        "velocity_norm_to_lbm": mapper.velocity_norm_to_lbm(sample["velocity_norm"]).tolist(),
        "velocity_lbm_to_norm": mapper.velocity_lbm_to_norm(sample["velocity_lbm"]).tolist(),
    }
    expected = {
        "norm_to_lbm_coord": sample["lbm_coord"],
        "lbm_coord_to_norm": sample["norm_coord"],
        "norm_to_lbm_index": [2, 16, 30],
        "lbm_index_to_norm_center": [0.078125, 0.515625, 0.953125],
        "velocity_norm_to_lbm": sample["velocity_lbm"],
        "velocity_lbm_to_norm": sample["velocity_norm"],
    }
    return comparison_row("grid_unit_mapper_conversions", expected, actual)


def legacy_tau_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.lbm.relaxation_semantics import tau_from_legacy_external_solver_parameter

    actual = tau_from_legacy_external_solver_parameter(0.1)
    expected = policy["tau_expectations"]["legacy_tau_for_0_1"]
    return comparison_row("legacy_tau_for_0_1", expected, actual)


def standard_tau_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.lbm.relaxation_semantics import tau_from_lattice_kinematic_viscosity

    actual = tau_from_lattice_kinematic_viscosity(0.1)
    expected = policy["tau_expectations"]["standard_tau_for_0_1"]
    return comparison_row("standard_tau_for_0_1", expected, actual)


def unmigrated_paths_row(root: Path, policy: dict) -> dict:
    paths = list(policy["protected_unmigrated_paths"])
    diff = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", *paths],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    changed_paths = [line.strip() for line in diff.stdout.splitlines() if line.strip()]
    return {
        "check": "unmigrated_driver_and_coupling_paths_unchanged",
        "expected": [],
        "actual": changed_paths,
        "pass": diff.returncode == 0 and changed_paths == [],
        "notes": "Protected files are intentionally outside the Step 56 migration wave.",
    }


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
        "expected": expected,
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
