from __future__ import annotations

import json
import tempfile
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig


def build_step71_output_default_alignment_audit(
    root: Path,
    policy_path: str = "configs/step71_output_default_alignment_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    step70_policy = read_json(root / policy["step70_output_policy_path"])
    default_config = FSIDriverConfig()
    explicit_true = from_json_config({"write_vtk": True, "write_particles": True})
    explicit_false = from_json_config({"write_vtk": False, "write_particles": False})
    rows = [
        bool_row("default_write_vtk", default_config.write_vtk, policy["required_defaults"]["FSIDriverConfig.write_vtk"]),
        bool_row("default_write_particles", default_config.write_particles, policy["required_defaults"]["FSIDriverConfig.write_particles"]),
        bool_row("step70_default_write_vtk_allowed", step70_policy["default_write_vtk_allowed"], False),
        bool_row("step70_default_write_particles_allowed", step70_policy["default_write_particles_allowed"], False),
        bool_row("step70_vtr_default_allowed", step70_policy["vtr_default_allowed"], False),
        bool_row("step70_particle_npy_default_allowed", step70_policy["particle_npy_default_allowed"], False),
        bool_row("explicit_true_write_vtk", explicit_true.write_vtk, True),
        bool_row("explicit_true_write_particles", explicit_true.write_particles, True),
        bool_row("explicit_false_write_vtk", explicit_false.write_vtk, False),
        bool_row("explicit_false_write_particles", explicit_false.write_particles, False),
        bool_row("runtime_output_default_changed", policy["runtime_output_default_changed"], True),
        bool_row("solver_numerical_behavior_changed", policy["solver_numerical_behavior_changed"], False),
        bool_row("physics_feature_expansion", policy["physics_feature_expansion"], False),
        bool_row("explicit_opt_in_remains_allowed", policy["explicit_opt_in_remains_allowed"], True),
    ]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "fsidriver_default_write_vtk": bool(default_config.write_vtk),
        "fsidriver_default_write_particles": bool(default_config.write_particles),
        "explicit_true_write_vtk": bool(explicit_true.write_vtk),
        "explicit_true_write_particles": bool(explicit_true.write_particles),
        "explicit_false_write_vtk": bool(explicit_false.write_vtk),
        "explicit_false_write_particles": bool(explicit_false.write_particles),
        "step70_default_write_vtk_allowed": bool(step70_policy["default_write_vtk_allowed"]),
        "step70_default_write_particles_allowed": bool(step70_policy["default_write_particles_allowed"]),
        "runtime_output_default_changed": bool(policy["runtime_output_default_changed"]),
        "solver_numerical_behavior_changed": bool(policy["solver_numerical_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "output_default_alignment_audit_pass": False,
    }
    summary["output_default_alignment_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["fsidriver_default_write_vtk"] is False
        and summary["fsidriver_default_write_particles"] is False
        and summary["explicit_true_write_vtk"] is True
        and summary["explicit_true_write_particles"] is True
        and summary["explicit_false_write_vtk"] is False
        and summary["explicit_false_write_particles"] is False
        and summary["step70_default_write_vtk_allowed"] is False
        and summary["step70_default_write_particles_allowed"] is False
        and summary["runtime_output_default_changed"] is True
        and summary["solver_numerical_behavior_changed"] is False
        and summary["physics_feature_expansion"] is False
    )
    return rows, summary


def from_json_config(payload: dict) -> FSIDriverConfig:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "fsi_driver_config.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return FSIDriverConfig.from_json(path)


def bool_row(check: str, actual, expected) -> dict:
    return {
        "check": check,
        "actual": bool(actual),
        "expected": bool(expected),
        "pass": bool(actual) is bool(expected),
    }
