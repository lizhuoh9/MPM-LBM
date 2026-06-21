from __future__ import annotations

import json
from pathlib import Path


def build_fsidriver_migration_audit(
    root: Path,
    policy_path: str = "configs/step58_fsidriver_migration_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    row = migration_row(root, policy)
    rows = [row]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "canonical_missing_count": sum(1 for item in rows if not item["canonical_path_exists"]),
        "legacy_missing_count": sum(1 for item in rows if not item["legacy_path_exists"]),
        "canonical_real_implementation_count": sum(
            1 for item in rows if item["canonical_contains_real_implementation"]
        ),
        "canonical_forbidden_token_count": sum(1 for item in rows if item["canonical_has_forbidden_tokens"]),
        "canonical_legacy_root_import_count": sum(1 for item in rows if item["canonical_imports_legacy_root"]),
        "legacy_shim_count": sum(1 for item in rows if item["legacy_is_shim"]),
        "forbidden_reverse_dependency_count": sum(1 for item in rows if item["forbidden_reverse_dependency"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "fsidriver_migration_audit_pass": False,
    }
    summary["fsidriver_migration_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def migration_row(root: Path, policy: dict) -> dict:
    migration = policy["migration"]
    canonical_path = root / migration["canonical_path"]
    legacy_path = root / migration["legacy_path"]
    canonical_text = canonical_path.read_text(encoding="utf-8") if canonical_path.is_file() else ""
    legacy_text = legacy_path.read_text(encoding="utf-8") if legacy_path.is_file() else ""
    forbidden_tokens = [
        token for token in policy["forbidden_legacy_import_tokens"] if token in canonical_text
    ]
    canonical_contains_real_implementation = bool(
        canonical_path.is_file()
        and all(token in canonical_text for token in migration["implementation_tokens"])
        and all(symbol in canonical_text for symbol in migration["required_symbols"])
        and not forbidden_tokens
    )
    canonical_imports_legacy_root = has_legacy_root_import(canonical_text, migration["legacy_module"])
    legacy_imports_canonical = migration["legacy_import"] in legacy_text
    legacy_is_shim = is_legacy_shim(legacy_text, migration, policy)
    forbidden_reverse_dependency = canonical_imports_legacy_root
    passed = bool(
        canonical_path.is_file()
        and legacy_path.is_file()
        and canonical_contains_real_implementation
        and not canonical_imports_legacy_root
        and legacy_imports_canonical
        and legacy_is_shim
        and not forbidden_reverse_dependency
    )
    return {
        "canonical_path": migration["canonical_path"],
        "legacy_path": migration["legacy_path"],
        "migration_status": "migrated" if passed else "failed",
        "canonical_path_exists": canonical_path.is_file(),
        "legacy_path_exists": legacy_path.is_file(),
        "canonical_contains_real_implementation": canonical_contains_real_implementation,
        "canonical_has_forbidden_tokens": bool(forbidden_tokens),
        "canonical_forbidden_tokens": forbidden_tokens,
        "canonical_imports_legacy_root": canonical_imports_legacy_root,
        "legacy_is_shim": legacy_is_shim,
        "legacy_imports_canonical": legacy_imports_canonical,
        "forbidden_reverse_dependency": forbidden_reverse_dependency,
        "pass": passed,
    }


def is_legacy_shim(text: str, migration: dict, policy: dict) -> bool:
    nonblank_lines = [line for line in text.splitlines() if line.strip()]
    forbidden_tokens = ["@ti.data_oriented", "class FSIDriver3D", "DIAGNOSTIC_FIELDS = [", "_LEGACY_MODULE", "legacy_getattr"]
    return bool(
        policy["legacy_required_docstring"] in text
        and migration["legacy_import"] in text
        and len(nonblank_lines) <= 4
        and not any(token in text for token in forbidden_tokens)
    )


def has_legacy_root_import(canonical_text: str, legacy_module: str) -> bool:
    legacy_stem = legacy_module.rsplit(".", 1)[-1]
    tokens = [
        f'"{legacy_module}"',
        f"'{legacy_module}'",
        f"from {legacy_module}",
        f"import {legacy_module}",
        f"from src import {legacy_stem}",
        f"from src.{legacy_stem}",
        f"import src.{legacy_stem}",
        f"from .{legacy_stem}",
        f"from ..{legacy_stem}",
        f"import {legacy_stem}",
    ]
    return any(token in canonical_text for token in tokens)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
