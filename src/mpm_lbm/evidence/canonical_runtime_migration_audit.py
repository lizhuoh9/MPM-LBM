from __future__ import annotations

import json
from pathlib import Path


def build_canonical_runtime_migration_audit(
    root: Path,
    policy_path: str = "configs/step56_canonical_runtime_migration_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [migration_row(root, policy, migration) for migration in policy["migrations"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "canonical_real_implementation_count": sum(
            1 for row in rows if row["canonical_contains_real_implementation"]
        ),
        "canonical_legacy_getattr_count": sum(1 for row in rows if row["canonical_uses_legacy_getattr"]),
        "legacy_shim_count": sum(1 for row in rows if row["legacy_is_shim"]),
        "forbidden_reverse_dependency_count": sum(1 for row in rows if row["forbidden_reverse_dependency"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "canonical_runtime_migration_audit_pass": False,
    }
    summary["canonical_runtime_migration_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def migration_row(root: Path, policy: dict, migration: dict) -> dict:
    canonical_path = root / migration["canonical_path"]
    legacy_path = root / migration["legacy_path"]
    canonical_text = canonical_path.read_text(encoding="utf-8") if canonical_path.is_file() else ""
    legacy_text = legacy_path.read_text(encoding="utf-8") if legacy_path.is_file() else ""
    canonical_uses_legacy_getattr = any(
        token in canonical_text for token in policy["canonical_forbidden_tokens"]
    )
    canonical_contains_real_implementation = bool(
        canonical_path.is_file()
        and all(token in canonical_text for token in migration["implementation_tokens"])
        and not canonical_uses_legacy_getattr
    )
    legacy_is_shim = is_legacy_shim(legacy_text, migration, policy)
    legacy_imports_canonical = migration["legacy_import"] in legacy_text
    forbidden_reverse_dependency = has_forbidden_reverse_dependency(canonical_text, migration)
    passed = bool(
        canonical_contains_real_implementation
        and not canonical_uses_legacy_getattr
        and legacy_is_shim
        and legacy_imports_canonical
        and not forbidden_reverse_dependency
    )
    return {
        "canonical_path": migration["canonical_path"],
        "legacy_path": migration["legacy_path"],
        "migration_status": "migrated" if passed else "failed",
        "canonical_contains_real_implementation": canonical_contains_real_implementation,
        "canonical_uses_legacy_getattr": canonical_uses_legacy_getattr,
        "legacy_is_shim": legacy_is_shim,
        "legacy_imports_canonical": legacy_imports_canonical,
        "forbidden_reverse_dependency": forbidden_reverse_dependency,
        "pass": passed,
    }


def is_legacy_shim(text: str, migration: dict, policy: dict) -> bool:
    nonblank_lines = [line for line in text.splitlines() if line.strip()]
    return bool(
        policy["legacy_required_docstring"] in text
        and migration["legacy_import"] in text
        and len(nonblank_lines) <= 4
        and not any(token in text for token in ["@ti.data_oriented", "class ", "def ", "_LEGACY_MODULE", "legacy_getattr"])
    )


def has_forbidden_reverse_dependency(canonical_text: str, migration: dict) -> bool:
    legacy_module = migration["legacy_module"]
    legacy_stem = legacy_module.rsplit(".", 1)[-1]
    tokens = [
        f'"{legacy_module}"',
        f"'{legacy_module}'",
        f"from {legacy_module}",
        f"import {legacy_module}",
        f"from .{legacy_stem}",
        f"from ..{legacy_stem}",
        f"import {legacy_stem}",
    ]
    return any(token in canonical_text for token in tokens)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
