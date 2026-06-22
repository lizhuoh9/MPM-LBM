from __future__ import annotations

import ast
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json, read_text


def build_step71_no_simulation_audit(
    root: Path,
    policy_path: str = "configs/step71_no_simulation_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [python_call_scan_row(root, path) for path in policy["scan_python_paths"]]
    forbidden_dirs = [path for path in policy["forbidden_output_directories"] if (root / path).exists()]
    related_files = step71_related_files(root)
    vtr_files = [path for path in related_files if path.lower().endswith(".vtr")]
    particle_npy_files = [
        path for path in related_files if path.lower().endswith(".npy") and "particle" in path.lower()
    ]
    protected_files = [
        path for path in related_files if any(path.startswith(prefix) for prefix in policy["protected_prefixes"])
    ]
    rows.extend(absence_row("forbidden_output_directory_absent", path) for path in forbidden_dirs)
    rows.extend(absence_row("no_step71_vtr", path) for path in vtr_files)
    rows.extend(absence_row("no_step71_particle_npy", path) for path in particle_npy_files)
    rows.extend(absence_row("no_protected_step71_file", path) for path in protected_files)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "forbidden_python_call_count": sum(int(row.get("forbidden_call_count", 0)) for row in rows),
        "forbidden_output_directory_count": len(forbidden_dirs),
        "step71_vtr_count": len(vtr_files),
        "step71_particle_npy_count": len(particle_npy_files),
        "protected_step71_file_count": len(protected_files),
        "no_simulation_audit_pass": False,
    }
    summary["no_simulation_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["forbidden_python_call_count"] == 0
        and summary["forbidden_output_directory_count"] == 0
        and summary["step71_vtr_count"] == 0
        and summary["step71_particle_npy_count"] == 0
        and summary["protected_step71_file_count"] == 0
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
        "forbidden_call_count": 0,
        "pass": False,
    }


def step71_related_files(root: Path) -> list[str]:
    rows = []
    explicit_paths = {
        "README.md",
        "src/mpm_lbm/sim/drivers/fsi_config.py",
        "src/mpm_lbm/sim/lbm/relaxation_semantics.py",
        "docs/CONFIG_SCHEMA_FREEZE.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
        "docs/OUTPUT_DEFAULT_SAFETY_POLICY.md",
        "docs/LBM_TAU_CONVENTION_DECISION.md",
        "docs/LBM_RELAXATION_SEMANTICS.md",
    }
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        lower = rel.lower()
        if (
            "step71" in lower
            or "output_default" in lower
            or "tau_convention" in lower
            or "output_default_safety" in lower
            or rel in explicit_paths
        ):
            rows.append(rel)
    return sorted(rows)
