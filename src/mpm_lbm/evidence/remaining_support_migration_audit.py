from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import (
    imports_any_legacy_root_module,
    is_compatibility_shim,
    legacy_contains_implementation_body,
    public_symbol_entries,
    read_json,
    read_text,
)


def build_step69_remaining_support_migration_audit(
    root: Path,
    policy_path: str = "configs/step69_remaining_support_migration_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    step63 = read_json(root / policy["migration_required_source_path"])
    step63_required = {row["path"]: row for row in step63["rows"] if row.get("migration_required")}
    rows = [migration_row(root, policy, migration, step63_required) for migration in policy["migrations"]]
    summary = {
        "row_count": len(rows),
        "policy_migration_count": len(policy["migrations"]),
        "migration_required_count_from_step63": len(step63_required),
        "migrated_support_count": sum(1 for row in rows if row["pass"]),
        "remaining_migration_required_count": sum(1 for row in rows if row["source_migration_required"] and not row["pass"]),
        "legacy_shim_count_for_six_support_rows": sum(1 for row in rows if row["legacy_is_shim"]),
        "legacy_implementation_body_count_for_six_support_rows": sum(1 for row in rows if row["legacy_contains_implementation_body"]),
        "canonical_imports_legacy_root_count": sum(1 for row in rows if row["canonical_imports_legacy_root"]),
        "policy_symbol_list_matches_canonical_ast_count": sum(1 for row in rows if row["policy_symbol_list_matches_canonical_ast"]),
        "remaining_support_migration_audit_pass": False,
    }
    summary["remaining_support_migration_audit_pass"] = bool(
        summary["policy_migration_count"] == 6
        and summary["migration_required_count_from_step63"] == 6
        and summary["migrated_support_count"] == 6
        and summary["remaining_migration_required_count"] == 0
        and summary["legacy_shim_count_for_six_support_rows"] == 6
        and summary["legacy_implementation_body_count_for_six_support_rows"] == 0
        and summary["canonical_imports_legacy_root_count"] == 0
        and summary["policy_symbol_list_matches_canonical_ast_count"] == 6
        and all(row["pass"] for row in rows)
    )
    return rows, summary


def migration_row(root: Path, policy: dict, migration: dict, step63_required: dict[str, dict]) -> dict:
    canonical_path = root / migration["canonical_path"]
    legacy_path = root / migration["legacy_path"]
    canonical_text = read_text(canonical_path)
    legacy_text = read_text(legacy_path)
    canonical_symbols = public_symbol_entries(canonical_path)
    canonical_symbol_names = [entry["name"] for entry in canonical_symbols]
    policy_symbols = list(migration["public_symbols"])
    missing_symbols = sorted(set(policy_symbols) - set(canonical_symbol_names))
    extra_public_symbols = sorted(set(canonical_symbol_names) - set(policy_symbols))
    policy_symbol_entries = sorted(migration["symbol_kinds"], key=lambda item: item["name"])
    canonical_symbol_entries = sorted(
        [entry for entry in canonical_symbols if entry["name"] in policy_symbols],
        key=lambda item: item["name"],
    )
    policy_symbol_list_matches_canonical_ast = bool(
        policy_symbols
        and not missing_symbols
        and policy_symbol_entries == canonical_symbol_entries
    )
    legacy_import = f"from {migration['canonical_module']} import *"
    legacy_is_shim = bool(
        legacy_path.is_file()
        and is_compatibility_shim(legacy_text, policy["legacy_shim_required_phrase"])
        and legacy_import in legacy_text
        and sum(1 for line in legacy_text.splitlines() if line.strip()) <= int(policy["max_nonblank_lines_per_shim"])
    )
    canonical_imports_legacy_root = imports_any_legacy_root_module(
        canonical_text,
        policy["forbidden_canonical_legacy_import_modules"],
    )
    source_row = step63_required.get(migration["legacy_path"], {})
    source_migration_required = bool(source_row.get("migration_required", False))
    passed = bool(
        canonical_path.is_file()
        and legacy_path.is_file()
        and source_migration_required
        and policy_symbol_list_matches_canonical_ast
        and legacy_is_shim
        and not legacy_contains_implementation_body(legacy_text)
        and not canonical_imports_legacy_root
    )
    return {
        "legacy_path": migration["legacy_path"],
        "canonical_path": migration["canonical_path"],
        "legacy_module": migration["legacy_module"],
        "canonical_module": migration["canonical_module"],
        "classification": migration["classification"],
        "source_migration_required": source_migration_required,
        "canonical_file_exists": canonical_path.is_file(),
        "legacy_file_exists": legacy_path.is_file(),
        "canonical_public_symbols": canonical_symbol_names,
        "policy_public_symbols": policy_symbols,
        "missing_symbols": missing_symbols,
        "extra_public_symbols": extra_public_symbols,
        "policy_symbol_list_matches_canonical_ast": policy_symbol_list_matches_canonical_ast,
        "legacy_is_shim": legacy_is_shim,
        "legacy_contains_implementation_body": legacy_contains_implementation_body(legacy_text),
        "canonical_imports_legacy_root": canonical_imports_legacy_root,
        "classification_decision": migration.get("classification_decision", ""),
        "pass": passed,
    }
