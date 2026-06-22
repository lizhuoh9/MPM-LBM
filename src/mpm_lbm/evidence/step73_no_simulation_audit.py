from __future__ import annotations

import ast
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json, read_text
from src.mpm_lbm.evidence.wall_velocity_output_policy_audit import step73_related_files


def build_step73_no_simulation_audit(
    root: Path,
    policy_path: str = "configs/step73_no_simulation_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [python_call_scan_row(root, path) for path in policy["scan_python_paths"]]
    forbidden_dirs = [path for path in policy["forbidden_output_directories"] if (root / path).exists()]
    related_files = step73_related_files(root)
    vtr_files = [path for path in related_files if path.lower().endswith(".vtr")]
    particle_npy_files = [path for path in related_files if path.lower().endswith(".npy") and "particle" in path.lower()]
    protected_files = [
        path for path in related_files if any(path.startswith(prefix) for prefix in policy["protected_prefixes"])
    ]
    rows.extend(absence_row("forbidden_output_directory_absent", path) for path in forbidden_dirs)
    rows.extend(absence_row("no_step73_vtr", path) for path in vtr_files)
    rows.extend(absence_row("no_step73_particle_npy", path) for path in particle_npy_files)
    rows.extend(absence_row("no_protected_step73_file", path) for path in protected_files)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "forbidden_python_call_count": sum(int(row.get("forbidden_call_count", 0)) for row in rows),
        "forbidden_output_directory_count": len(forbidden_dirs),
        "step73_vtr_count": len(vtr_files),
        "step73_particle_npy_count": len(particle_npy_files),
        "protected_step73_file_count": len(protected_files),
        "no_simulation_audit_pass": False,
    }
    summary["no_simulation_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["forbidden_python_call_count"] == 0
        and summary["forbidden_output_directory_count"] == 0
        and summary["step73_vtr_count"] == 0
        and summary["step73_particle_npy_count"] == 0
        and summary["protected_step73_file_count"] == 0
    )
    return rows, summary


def python_call_scan_row(root: Path, relative_path: str) -> dict:
    path = root / relative_path
    text = read_text(path)
    found_calls: list[str] = []
    error = ""
    if path.is_file():
        try:
            tree = ast.parse(text)
            found_calls = forbidden_calls(tree)
        except SyntaxError as exc:  # pragma: no cover - artifact row captures details
            error = f"SyntaxError: {exc}"
    return {
        "check": "python_no_simulation_calls",
        "path": relative_path,
        "file_exists": path.is_file(),
        "found_calls": found_calls,
        "forbidden_call_count": len(found_calls),
        "pass": bool(path.is_file() and not found_calls and not error),
        "error": error,
    }


def forbidden_calls(tree: ast.AST) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute):
            if func.attr in {"initialize", "step_once"} and isinstance(func.value, ast.Name) and func.value.id == "driver":
                found.append(f"driver.{func.attr}")
            if func.attr == "run":
                if isinstance(func.value, ast.Name) and func.value.id == "driver":
                    found.append("driver.run")
                if isinstance(func.value, ast.Call) and isinstance(func.value.func, ast.Name) and func.value.func.id == "FSIDriver3D":
                    found.append("FSIDriver3D(...).run")
    return sorted(found)


def absence_row(check: str, path: str) -> dict:
    return {
        "check": check,
        "path": path,
        "file_exists": False,
        "found_calls": [],
        "forbidden_call_count": 0,
        "pass": False,
        "error": "",
    }
