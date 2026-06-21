from __future__ import annotations

import ast
import json
from pathlib import Path


def build_step68_step_specific_proxy_migration_audit(
    root: Path,
    policy_path: str = "configs/step68_step_specific_proxy_migration_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [migration_row(root, policy, migration) for migration in policy["migrations"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "experiment_real_implementation_count": sum(
            1 for row in rows if row["experiment_contains_real_implementation"]
        ),
        "experiment_legacy_getattr_count": sum(1 for row in rows if row["experiment_uses_legacy_getattr"]),
        "experiment_root_proxy_import_count": sum(1 for row in rows if row["experiment_imports_root_proxy"]),
        "legacy_shim_count": sum(1 for row in rows if row["legacy_is_shim"]),
        "root_step_specific_implementation_count": sum(
            1 for row in rows if not row["legacy_is_shim"] or row["legacy_contains_implementation_body"]
        ),
        "quarantined_historical_driver_helper_count": sum(
            1 for row in rows if row["quarantined_historical_driver_helper"]
        ),
        "step68_proxy_migration_audit_pass": False,
    }
    summary["step68_proxy_migration_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and summary["root_step_specific_implementation_count"] == 0
        and summary["experiment_legacy_getattr_count"] == 0
        and summary["experiment_root_proxy_import_count"] == 0
    )
    return rows, summary


def migration_row(root: Path, policy: dict, migration: dict) -> dict:
    experiment_path = root / migration["experiment_path"]
    legacy_path = root / migration["legacy_path"]
    experiment_text = read_text(experiment_path)
    legacy_text = read_text(legacy_path)
    missing_symbols = sorted(set(migration["public_symbols"]) - defined_public_symbols(experiment_path))
    experiment_contains_real_implementation = bool(
        experiment_path.is_file() and migration["public_symbols"] and not missing_symbols
    )
    experiment_uses_legacy_getattr = any(
        token in experiment_text for token in policy["forbidden_experiment_tokens"]
    )
    experiment_imports_root_proxy = imports_root_proxy(experiment_text, policy)
    legacy_import = f"from {migration['experiment_module']} import *"
    legacy_imports_experiment = legacy_import in legacy_text
    nonblank_line_count = sum(1 for line in legacy_text.splitlines() if line.strip())
    legacy_contains_implementation_body = any(
        token in legacy_text for token in ("def ", "class ", "legacy_getattr", "_LEGACY_MODULE", "@ti.")
    )
    legacy_is_shim = bool(
        legacy_path.is_file()
        and policy["legacy_shim_required_phrase"] in legacy_text
        and legacy_imports_experiment
        and nonblank_line_count <= int(policy["max_nonblank_lines_per_shim"])
        and not legacy_contains_implementation_body
    )
    passed = bool(
        legacy_path.is_file()
        and experiment_path.is_file()
        and experiment_contains_real_implementation
        and not experiment_uses_legacy_getattr
        and not experiment_imports_root_proxy
        and legacy_is_shim
    )
    return {
        "legacy_path": migration["legacy_path"],
        "experiment_path": migration["experiment_path"],
        "legacy_file_exists": legacy_path.is_file(),
        "experiment_file_exists": experiment_path.is_file(),
        "experiment_contains_real_implementation": experiment_contains_real_implementation,
        "experiment_missing_symbols": missing_symbols,
        "experiment_uses_legacy_getattr": experiment_uses_legacy_getattr,
        "experiment_imports_root_proxy": experiment_imports_root_proxy,
        "legacy_is_shim": legacy_is_shim,
        "legacy_imports_experiment": legacy_imports_experiment,
        "legacy_contains_implementation_body": legacy_contains_implementation_body,
        "quarantined_historical_driver_helper": bool(migration["quarantined_historical_driver_helper"]),
        "pass": passed,
    }


def imports_root_proxy(text: str, policy: dict) -> bool:
    for migration in policy["migrations"]:
        module = migration["legacy_module"]
        stem = module.rsplit(".", 1)[-1]
        if f"from {module} import" in text or f"import {module}" in text:
            return True
        if f"from src import {stem}" in text or f"import src.{stem}" in text:
            return True
        if f"from .{stem} import" in text:
            return True
    return False


def defined_public_symbols(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    symbols = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
            symbols.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    if target.id.isupper() or target.id.endswith("_FIELDS"):
                        symbols.add(target.id)
    return symbols


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
