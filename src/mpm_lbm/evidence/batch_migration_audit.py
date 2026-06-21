from __future__ import annotations

import ast
import json
from pathlib import Path


def build_batch_migration_audit(root: Path, policy_path: str) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [migration_row(root, policy, migration) for migration in policy["migrations"]]
    summary = {
        "policy_id": policy["policy_id"],
        "step": int(policy["step"]),
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "canonical_missing_count": sum(1 for row in rows if not row["canonical_path_exists"]),
        "legacy_missing_count": sum(1 for row in rows if not row["legacy_path_exists"]),
        "canonical_real_implementation_count": sum(
            1 for row in rows if row["canonical_contains_real_implementation"]
        ),
        "canonical_imports_legacy_root_count": sum(
            1 for row in rows if row["canonical_imports_legacy_root"]
        ),
        "canonical_forbidden_bridge_token_count": sum(
            int(row["canonical_forbidden_bridge_token_count"]) for row in rows
        ),
        "legacy_shim_count": sum(1 for row in rows if row["legacy_is_shim"]),
        "runtime_code_changed": bool(policy["runtime_code_changed"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "batch_migration_audit_pass": False,
    }
    summary["batch_migration_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and not summary["runtime_code_changed"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def migration_row(root: Path, policy: dict, migration: dict) -> dict:
    canonical_path = root / migration["canonical_path"]
    legacy_path = root / migration["legacy_path"]
    canonical_text = read_text(canonical_path)
    legacy_text = read_text(legacy_path)
    required_symbols = set(migration.get("symbols", []))
    canonical_symbols = defined_public_symbols(canonical_path)
    missing_symbols = sorted(required_symbols.difference(canonical_symbols))
    forbidden_bridge_tokens = [
        token for token in policy["canonical_forbidden_tokens"] if token in canonical_text
    ]
    canonical_contains_real_implementation = bool(
        canonical_path.is_file() and required_symbols and not missing_symbols
    )
    canonical_imports_legacy_root = has_legacy_root_import(canonical_text, policy, migration)
    legacy_import = f"from {migration['canonical_module']} import *"
    legacy_imports_canonical = legacy_import in legacy_text
    nonblank_line_count = sum(1 for line in legacy_text.splitlines() if line.strip())
    legacy_contains_implementation_body = any(
        token in legacy_text for token in ("def ", "class ", "@ti.", "legacy_getattr", "_LEGACY_MODULE")
    )
    legacy_is_shim = bool(
        legacy_path.is_file()
        and policy["legacy_shim_required_phrase"] in legacy_text
        and legacy_imports_canonical
        and nonblank_line_count <= int(policy["max_nonblank_lines_per_shim"])
        and not legacy_contains_implementation_body
    )
    passed = bool(
        canonical_path.is_file()
        and legacy_path.is_file()
        and canonical_contains_real_implementation
        and not canonical_imports_legacy_root
        and not forbidden_bridge_tokens
        and legacy_is_shim
    )
    return {
        "legacy_path": migration["legacy_path"],
        "canonical_path": migration["canonical_path"],
        "classification": migration["classification"],
        "canonical_path_exists": canonical_path.is_file(),
        "legacy_path_exists": legacy_path.is_file(),
        "canonical_contains_real_implementation": canonical_contains_real_implementation,
        "canonical_missing_symbols": missing_symbols,
        "canonical_imports_legacy_root": canonical_imports_legacy_root,
        "canonical_uses_legacy_getattr": "legacy_getattr" in canonical_text,
        "canonical_forbidden_bridge_token_count": len(forbidden_bridge_tokens),
        "canonical_forbidden_bridge_tokens": forbidden_bridge_tokens,
        "legacy_is_shim": legacy_is_shim,
        "legacy_imports_canonical": legacy_imports_canonical,
        "support_dependency": bool(migration.get("support_dependency", False)),
        "pass": passed,
    }


def has_legacy_root_import(canonical_text: str, policy: dict, migration: dict) -> bool:
    legacy_modules = [item["legacy_module"] for item in policy["migrations"]]
    legacy_modules.append(migration["legacy_module"])
    tokens = []
    for module_name in sorted(set(legacy_modules)):
        stem = module_name.rsplit(".", 1)[-1]
        tokens.extend(
            [
                f"from {module_name} import",
                f"import {module_name}",
                f"from src import {stem}",
                f"import src.{stem}",
                f"from .{stem} import",
                f"from ..{stem} import",
            ]
        )
    return any(token in canonical_text for token in tokens)


def defined_public_symbols(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
    }


def batch_symbol_pairs(policy: dict) -> list[dict]:
    pairs = []
    for migration in policy["migrations"]:
        for symbol in migration.get("symbols", []):
            pairs.append(
                {
                    "symbol": symbol,
                    "canonical_module": migration["canonical_module"],
                    "legacy_module": migration["legacy_module"],
                    "legacy_path": migration["legacy_path"],
                    "canonical_path": migration["canonical_path"],
                    "classification": migration["classification"],
                }
            )
    return pairs


def output_snapshot(root: Path) -> list[tuple[str, int]]:
    output_root = Path(root) / "outputs"
    if not output_root.exists():
        return []
    return sorted(
        (path.relative_to(root).as_posix(), int(path.stat().st_size))
        for path in output_root.rglob("*")
        if path.is_file()
    )


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
