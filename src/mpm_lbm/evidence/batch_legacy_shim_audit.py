from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import read_json, read_text


def build_batch_legacy_shim_audit(root: Path, policy_path: str) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [legacy_shim_row(root, policy, migration) for migration in policy["migrations"]]
    summary = {
        "policy_id": policy["policy_id"],
        "step": int(policy["step"]),
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "legacy_shim_count": sum(1 for row in rows if row["legacy_is_shim"]),
        "legacy_implementation_body_count": sum(
            1 for row in rows if row["legacy_contains_implementation_body"]
        ),
        "batch_legacy_shim_audit_pass": False,
    }
    summary["batch_legacy_shim_audit_pass"] = bool(
        summary["row_count"] > 0 and summary["row_count"] == summary["pass_count"]
    )
    return rows, summary


def legacy_shim_row(root: Path, policy: dict, migration: dict) -> dict:
    path = root / migration["legacy_path"]
    text = read_text(path)
    nonblank_line_count = sum(1 for line in text.splitlines() if line.strip())
    legacy_contains_implementation_body = any(
        token in text for token in ("def ", "class ", "@ti.", "legacy_getattr", "_LEGACY_MODULE")
    )
    legacy_import = f"from {migration['canonical_module']} import *"
    legacy_imports_canonical = legacy_import in text
    legacy_is_shim = bool(
        path.is_file()
        and policy["legacy_shim_required_phrase"] in text
        and legacy_imports_canonical
        and nonblank_line_count <= int(policy["max_nonblank_lines_per_shim"])
        and not legacy_contains_implementation_body
    )
    return {
        "legacy_path": migration["legacy_path"],
        "canonical_path": migration["canonical_path"],
        "nonblank_line_count": nonblank_line_count,
        "legacy_contains_implementation_body": legacy_contains_implementation_body,
        "legacy_imports_canonical": legacy_imports_canonical,
        "legacy_is_shim": legacy_is_shim,
        "pass": legacy_is_shim,
    }
