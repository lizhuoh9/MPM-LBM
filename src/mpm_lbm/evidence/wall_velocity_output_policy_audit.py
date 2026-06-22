from __future__ import annotations

import re
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig


PRIVATE_ABSOLUTE_RE = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+")


def build_step73_wall_velocity_output_policy_audit(
    root: Path,
    policy_path: str = "configs/step73_wall_velocity_output_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    step70 = read_json(root / policy["step70_output_policy_path"])
    step71 = read_json(root / policy["step71_output_default_artifact_path"])["summary"]
    default_config = FSIDriverConfig()
    rows = [
        bool_row("step70_default_write_vtk_allowed", step70["default_write_vtk_allowed"], False, ""),
        bool_row("step70_default_write_particles_allowed", step70["default_write_particles_allowed"], False, ""),
        bool_row("step71_fsidriver_default_write_vtk", step71["fsidriver_default_write_vtk"], False, ""),
        bool_row("step71_fsidriver_default_write_particles", step71["fsidriver_default_write_particles"], False, ""),
        bool_row("current_fsidriver_default_write_vtk", default_config.write_vtk, False, ""),
        bool_row("current_fsidriver_default_write_particles", default_config.write_particles, False, ""),
    ]
    rows.extend(json_policy_row(root, path, policy["controlled_output_keys"]) for path in policy["scan_json_paths"])
    forbidden_dirs = [path for path in policy["forbidden_output_directories"] if (root / path).exists()]
    related_files = step73_related_files(root)
    vtr_files = [path for path in related_files if path.lower().endswith(".vtr")]
    particle_npy_files = [path for path in related_files if path.lower().endswith(".npy") and "particle" in path.lower()]
    dense_wall_velocity_files = [path for path in related_files if "dense_wall_velocity" in path.lower() or "dense_field" in path.lower()]
    sparse_wall_velocity_files = [path for path in related_files if "sparse_wall_velocity" in path.lower() or "sparse_samples" in path.lower()]
    protected_files = [
        path for path in related_files if any(path.startswith(prefix) for prefix in policy["protected_prefixes"])
    ]
    private_absolute_paths = private_absolute_path_rows(root)
    rows.extend(absence_row("forbidden_output_directory_absent", path) for path in forbidden_dirs)
    rows.extend(absence_row("no_step73_vtr", path) for path in vtr_files)
    rows.extend(absence_row("no_step73_particle_npy", path) for path in particle_npy_files)
    rows.extend(absence_row("no_step73_dense_wall_velocity", path) for path in dense_wall_velocity_files)
    rows.extend(absence_row("no_step73_sparse_wall_velocity", path) for path in sparse_wall_velocity_files)
    rows.extend(absence_row("no_protected_step73_file", path) for path in protected_files)
    rows.extend(absence_row("no_private_absolute_path", path) for path in private_absolute_paths)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "current_fsidriver_default_write_vtk": bool(default_config.write_vtk),
        "current_fsidriver_default_write_particles": bool(default_config.write_particles),
        "json_controlled_true_count": sum(int(row.get("controlled_true_count", 0)) for row in rows),
        "forbidden_output_directory_count": len(forbidden_dirs),
        "step73_vtr_count": len(vtr_files),
        "step73_particle_npy_count": len(particle_npy_files),
        "step73_dense_wall_velocity_count": len(dense_wall_velocity_files),
        "step73_sparse_wall_velocity_count": len(sparse_wall_velocity_files),
        "protected_step73_file_count": len(protected_files),
        "private_absolute_path_count": len(private_absolute_paths),
        "wall_velocity_output_policy_audit_pass": False,
    }
    summary["wall_velocity_output_policy_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["current_fsidriver_default_write_vtk"] is False
        and summary["current_fsidriver_default_write_particles"] is False
        and summary["json_controlled_true_count"] == 0
        and summary["forbidden_output_directory_count"] == 0
        and summary["step73_vtr_count"] == 0
        and summary["step73_particle_npy_count"] == 0
        and summary["step73_dense_wall_velocity_count"] == 0
        and summary["step73_sparse_wall_velocity_count"] == 0
        and summary["protected_step73_file_count"] == 0
        and summary["private_absolute_path_count"] == 0
    )
    return rows, summary


def bool_row(check: str, actual, expected, path: str) -> dict:
    return {
        "check": check,
        "path": path,
        "actual": actual,
        "expected": expected,
        "controlled_true_count": 0,
        "pass": actual == expected,
    }


def json_policy_row(root: Path, relative_path: str, controlled_keys: list[str]) -> dict:
    payload = read_json(root / relative_path)
    true_keys = sorted(controlled_true_keys(payload, set(controlled_keys)))
    return {
        "check": "json_controlled_output_keys_false",
        "path": relative_path,
        "actual": true_keys,
        "expected": [],
        "controlled_true_count": len(true_keys),
        "pass": not true_keys,
    }


def controlled_true_keys(payload, controlled_keys: set[str], prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in controlled_keys and value is True:
                found.append(path)
            found.extend(controlled_true_keys(value, controlled_keys, path))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            found.extend(controlled_true_keys(value, controlled_keys, f"{prefix}[{index}]"))
    return found


def absence_row(check: str, path: str) -> dict:
    return {
        "check": check,
        "path": path,
        "actual": True,
        "expected": False,
        "controlled_true_count": 0,
        "pass": False,
    }


def private_absolute_path_rows(root: Path) -> list[str]:
    paths = []
    for relative in step73_related_files(root):
        if not relative.startswith(("outputs/step73_", "logs/step73_")):
            continue
        path = root / relative
        if path.is_file() and PRIVATE_ABSOLUTE_RE.search(path.read_text(encoding="utf-8-sig", errors="ignore")):
            paths.append(relative)
    return paths


def step73_related_files(root: Path) -> list[str]:
    explicit_paths = {
        "README.md",
        "docs/00_project_status.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
        "docs/WALL_VELOCITY_ACTIVATION_READINESS.md",
        "docs/73_wall_velocity_activation_readiness_audit.md",
        "STEP73_WALL_VELOCITY_ACTIVATION_READINESS_AUDIT_GOAL.md",
        "STEP73_WALL_VELOCITY_ACTIVATION_READINESS_AUDIT_REPORT.md",
    }
    rows = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        lower = rel.lower()
        if "step73" in lower or "wall_velocity_activation_readiness" in lower or rel in explicit_paths:
            rows.append(rel)
    return sorted(rows)
