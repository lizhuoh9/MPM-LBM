from __future__ import annotations

import ast
from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import read_json


BATCH_A_EVIDENCE_FILES = {
    "batch_behavior_preservation_audit.py",
    "batch_import_execution_audit.py",
    "batch_legacy_shim_audit.py",
    "batch_migration_audit.py",
    "code_placement_freeze_audit.py",
    "encoding_policy_audit.py",
    "regression_snapshot_consistency_audit.py",
    "remaining_solver_inventory_audit.py",
    "simulation_freeze_audit.py",
    "solver_completion_roadmap_audit.py",
    "step63_67_regression_guard.py",
}


def build_simulation_freeze_audit(
    root: Path,
    policy_path: str = "configs/step63_simulation_freeze_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    files = batch_a_executable_files(root, policy)
    rows = [freeze_row(path, root, policy) for path in files]
    output_dir_hits = forbidden_output_dir_hits(root, policy)
    vtr_hits = list((root / "outputs").glob("step6[3-7]*/*.vtr")) if (root / "outputs").exists() else []
    particle_hits = [
        path
        for path in (root / "outputs").glob("step6[3-7]*/*.npy")
        if "particle" in path.name.lower()
    ] if (root / "outputs").exists() else []
    summary = {
        "file_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "new_simulation_run_count": sum(int(row["forbidden_driver_call_count"]) for row in rows),
        "new_driver_run_output_dir_count": len(output_dir_hits),
        "forbidden_runtime_flag_count": sum(int(row["forbidden_runtime_flag_count"]) for row in rows),
        "step63_67_vtr_count": len(vtr_hits),
        "step63_67_particle_npy_count": len(particle_hits),
        "runtime_code_changed": bool(policy["runtime_code_changed"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "simulation_freeze_audit_pass": False,
    }
    summary["simulation_freeze_audit_pass"] = bool(
        summary["file_count"] > 0
        and summary["file_count"] == summary["pass_count"]
        and summary["new_simulation_run_count"] == 0
        and summary["new_driver_run_output_dir_count"] == 0
        and summary["forbidden_runtime_flag_count"] == 0
        and summary["step63_67_vtr_count"] == 0
        and summary["step63_67_particle_npy_count"] == 0
        and not summary["runtime_code_changed"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def batch_a_executable_files(root: Path, policy: dict) -> list[Path]:
    files = set()
    for pattern in policy["scan_globs"]:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            if path.parts[-2:] and "src" in path.parts and path.parent.name == "evidence":
                if path.name not in BATCH_A_EVIDENCE_FILES:
                    continue
            files.add(path)
    return sorted(files)


def freeze_row(path: Path, root: Path, policy: dict) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    driver_hits = forbidden_driver_calls(path, policy)
    string_hits = forbidden_string_hits(path, policy)
    rel = path.relative_to(root).as_posix()
    return {
        "path": rel,
        "forbidden_driver_call_count": len(driver_hits),
        "forbidden_driver_calls": driver_hits,
        "forbidden_runtime_flag_count": len(string_hits),
        "forbidden_runtime_flags": string_hits,
        "readable_utf8": isinstance(text, str),
        "pass": not driver_hits and not string_hits,
    }


def forbidden_driver_calls(path: Path, policy: dict) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    hits = []
    forbidden_attrs = set(policy["forbidden_driver_call_attrs"])
    forbidden_names = set(policy["forbidden_driver_names"])
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in forbidden_attrs:
            continue
        if isinstance(node.func.value, ast.Name) and node.func.value.id in forbidden_names:
            hits.append(f"{path.as_posix()}:{node.lineno}:{node.func.attr}")
        elif isinstance(node.func.value, ast.Call) and is_fsi_driver_constructor(node.func.value):
            hits.append(f"{path.as_posix()}:{node.lineno}:{node.func.attr}")
    return hits


def is_fsi_driver_constructor(node: ast.Call) -> bool:
    if isinstance(node.func, ast.Name):
        return node.func.id == "FSIDriver3D"
    if isinstance(node.func, ast.Attribute):
        return node.func.attr == "FSIDriver3D"
    return False


def forbidden_string_hits(path: Path, policy: dict) -> list[str]:
    text = path.read_text(encoding="utf-8-sig")
    hits = []
    for token in policy["forbidden_output_dirs"] + policy["forbidden_runtime_flags"]:
        if token in text:
            hits.append(token)
    return hits


def forbidden_output_dir_hits(root: Path, policy: dict) -> list[str]:
    return [token for token in policy["forbidden_output_dirs"] if (root / token).exists()]
