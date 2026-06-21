from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import is_compatibility_shim, read_json, read_text


def build_step69_code_placement_audit(
    root: Path,
    policy_path: str = "configs/step69_code_placement_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    migration_policy = read_json(root / policy["remaining_support_migration_policy_path"])
    rows = []
    for migration in migration_policy["migrations"]:
        rows.append(code_placement_row(root, policy, migration))
    protected_step69_files = protected_related_files(root, policy["forbidden_step69_paths"])
    for path in protected_step69_files:
        rows.append(
            {
                "check": "protected_path_step69_file",
                "path": path,
                "canonical_allowed_prefix": "",
                "legacy_is_shim": "",
                "pass": False,
            }
        )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "canonical_path_count": len(migration_policy["migrations"]),
        "canonical_allowed_prefix_count": sum(1 for row in rows if row.get("canonical_allowed_prefix")),
        "legacy_shim_count": sum(1 for row in rows if row.get("legacy_is_shim") is True),
        "protected_step69_file_count": len(protected_step69_files),
        "runtime_code_changed": bool(policy["runtime_code_changed"]),
        "solver_behavior_changed": bool(policy["solver_behavior_changed"]),
        "physics_feature_expansion": bool(policy["physics_feature_expansion"]),
        "code_placement_audit_pass": False,
    }
    summary["code_placement_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and summary["canonical_path_count"] == 6
        and summary["canonical_allowed_prefix_count"] == 6
        and summary["legacy_shim_count"] == 6
        and summary["protected_step69_file_count"] == 0
        and not summary["runtime_code_changed"]
        and not summary["solver_behavior_changed"]
        and not summary["physics_feature_expansion"]
    )
    return rows, summary


def code_placement_row(root: Path, policy: dict, migration: dict) -> dict:
    canonical_path = migration["canonical_path"]
    legacy_path = migration["legacy_path"]
    canonical_allowed_prefix = any(canonical_path.startswith(prefix) for prefix in policy["allowed_canonical_prefixes"])
    canonical_exists = (root / canonical_path).is_file()
    legacy_text = read_text(root / legacy_path)
    legacy_is_shim = is_compatibility_shim(legacy_text)
    passed = bool(canonical_exists and canonical_allowed_prefix and legacy_is_shim)
    return {
        "check": "migration_code_placement",
        "legacy_path": legacy_path,
        "canonical_path": canonical_path,
        "classification": migration["classification"],
        "canonical_exists": canonical_exists,
        "canonical_allowed_prefix": canonical_allowed_prefix,
        "legacy_is_shim": legacy_is_shim,
        "pass": passed,
    }


def protected_related_files(root: Path, forbidden_prefixes: list[str]) -> list[str]:
    rows = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "step69" not in rel.lower():
            continue
        if any(rel.startswith(prefix) for prefix in forbidden_prefixes):
            rows.append(rel)
    return sorted(rows)
