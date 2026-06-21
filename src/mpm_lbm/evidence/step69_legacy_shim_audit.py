from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import (
    is_compatibility_shim,
    legacy_contains_implementation_body,
    read_json,
    read_text,
)


def build_step69_legacy_shim_audit(
    root: Path,
    policy_path: str = "configs/step69_remaining_support_migration_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [legacy_shim_row(root, policy, migration) for migration in policy["migrations"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "legacy_shim_count_for_six_support_rows": sum(1 for row in rows if row["legacy_is_shim"]),
        "legacy_implementation_body_count_for_six_support_rows": sum(1 for row in rows if row["legacy_contains_implementation_body"]),
        "step69_legacy_shim_audit_pass": False,
    }
    summary["step69_legacy_shim_audit_pass"] = bool(
        summary["row_count"] == 6
        and summary["row_count"] == summary["pass_count"]
        and summary["legacy_shim_count_for_six_support_rows"] == 6
        and summary["legacy_implementation_body_count_for_six_support_rows"] == 0
    )
    return rows, summary


def legacy_shim_row(root: Path, policy: dict, migration: dict) -> dict:
    path = root / migration["legacy_path"]
    text = read_text(path)
    nonblank_line_count = sum(1 for line in text.splitlines() if line.strip())
    legacy_import = f"from {migration['canonical_module']} import *"
    legacy_imports_canonical = legacy_import in text
    legacy_contains_body = legacy_contains_implementation_body(text)
    legacy_is_shim = bool(
        path.is_file()
        and is_compatibility_shim(text, policy["legacy_shim_required_phrase"])
        and legacy_imports_canonical
        and nonblank_line_count <= int(policy["max_nonblank_lines_per_shim"])
        and not legacy_contains_body
    )
    return {
        "legacy_path": migration["legacy_path"],
        "canonical_path": migration["canonical_path"],
        "legacy_is_shim": legacy_is_shim,
        "legacy_imports_canonical": legacy_imports_canonical,
        "legacy_contains_implementation_body": legacy_contains_body,
        "nonblank_line_count": nonblank_line_count,
        "pass": legacy_is_shim,
    }
