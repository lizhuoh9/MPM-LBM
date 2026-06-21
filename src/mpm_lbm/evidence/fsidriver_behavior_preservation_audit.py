from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

import numpy as np


def build_fsidriver_behavior_preservation_audit(
    root: Path,
    policy_path: str = "configs/step58_behavior_preservation_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [
        diagnostic_fields_row(policy),
        fsi_driver_config_defaults_row(policy),
        constructor_no_run_row(root, policy),
        {
            "check": "solver_behavior_changed",
            "expected": False,
            "actual": bool(policy["solver_behavior_changed"]),
            "pass": not bool(policy["solver_behavior_changed"]),
            "notes": "Step 58 only migrates FSIDriver3D implementation ownership.",
        },
        {
            "check": "physics_feature_expansion",
            "expected": False,
            "actual": bool(policy["physics_feature_expansion"]),
            "pass": not bool(policy["physics_feature_expansion"]),
            "notes": "Step 58 does not add runtime geometry, motion, or wall velocity behavior.",
        },
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "solver_run": False,
        "constructor_no_run_probe_used": True,
        "output_dir_created_by_constructor": bool(
            next(row for row in rows if row["check"] == "constructor_no_run_state")["actual"][
                "output_dir_exists_after"
            ]
        ),
        "fsidriver_behavior_preservation_audit_pass": False,
    }
    summary["fsidriver_behavior_preservation_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
        and not summary["solver_run"]
        and not summary["output_dir_created_by_constructor"]
    )
    return rows, summary


def diagnostic_fields_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_driver import DIAGNOSTIC_FIELDS

    return comparison_row("diagnostic_fields", policy["diagnostic_fields"], list(DIAGNOSTIC_FIELDS))


def fsi_driver_config_defaults_row(policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    expected = policy["fsi_driver_config_selected_defaults"]
    actual = selected_dataclass_defaults(FSIDriverConfig, expected)
    return comparison_row("fsi_driver_config_selected_defaults", expected, actual)


def constructor_no_run_row(root: Path, policy: dict) -> dict:
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    out_dir = root / policy["constructor_probe_out_dir"]
    output_dir_exists_before = out_dir.exists()
    driver = FSIDriver3D(
        FSIDriverConfig(n_lbm_steps=1, write_vtk=False, write_particles=False),
        out_dir=str(out_dir),
    )
    output_dir_exists_after = out_dir.exists()
    actual = {
        "initialized": bool(driver.initialized),
        "current_lbm_step": int(driver.current_lbm_step),
        "total_mpm_substeps": int(driver.total_mpm_substeps),
        "timing_keys": list(driver.timing.keys()),
        "lbm_is_none": driver.lbm is None,
        "solid_is_none": driver.solid is None,
        "projector_is_none": driver.projector is None,
        "output_dir_exists_before": output_dir_exists_before,
        "output_dir_exists_after": output_dir_exists_after,
    }
    expected = {
        **policy["expected_constructor_state"],
        "timing_keys": policy["expected_timing_keys"],
        "lbm_is_none": True,
        "solid_is_none": True,
        "projector_is_none": True,
        "output_dir_exists_before": False,
        "output_dir_exists_after": False,
    }
    row = comparison_row("constructor_no_run_state", expected, actual)
    row["notes"] = "constructor only; initialize, step_once, and run are not called"
    return row


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
