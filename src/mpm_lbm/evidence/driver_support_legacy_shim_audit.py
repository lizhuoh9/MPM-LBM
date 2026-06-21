from __future__ import annotations

import json
from pathlib import Path


def build_driver_support_legacy_shim_audit(
    root: Path,
    policy_path: str = "configs/step57_legacy_shim_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    migration_policy = read_json(root / policy["migrations_policy_path"])
    rows = [legacy_shim_row(root, policy, migration) for migration in migration_policy["migrations"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "legacy_shim_count": sum(1 for row in rows if row["legacy_is_shim"]),
        "legacy_implementation_body_count": sum(1 for row in rows if row["legacy_contains_implementation_body"]),
        "driver_support_legacy_shim_audit_pass": False,
    }
    summary["driver_support_legacy_shim_audit_pass"] = bool(
        summary["row_count"] > 0 and summary["row_count"] == summary["pass_count"]
    )
    return rows, summary


def legacy_shim_row(root: Path, policy: dict, migration: dict) -> dict:
    path = root / migration["legacy_path"]
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    nonblank_line_count = sum(1 for line in text.splitlines() if line.strip())
    legacy_contains_implementation_body = any(
        token in text for token in policy["legacy_files_must_not_contain_tokens"]
    )
    legacy_imports_canonical = migration["legacy_import"] in text
    legacy_is_shim = bool(
        path.is_file()
        and "Compatibility shim. Canonical implementation lives in " in text
        and legacy_imports_canonical
        and nonblank_line_count <= int(policy["max_nonblank_lines_per_shim"])
        and not legacy_contains_implementation_body
    )
    return {
        "legacy_path": migration["legacy_path"],
        "canonical_path": migration["canonical_path"],
        "legacy_file_exists": path.is_file(),
        "legacy_is_shim": legacy_is_shim,
        "legacy_imports_canonical": legacy_imports_canonical,
        "legacy_contains_implementation_body": legacy_contains_implementation_body,
        "nonblank_line_count": nonblank_line_count,
        "pass": legacy_is_shim,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
