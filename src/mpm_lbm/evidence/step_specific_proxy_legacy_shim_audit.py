from __future__ import annotations

import json
from pathlib import Path


def build_step68_legacy_shim_audit(
    root: Path,
    policy_path: str = "configs/step68_legacy_shim_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    migration_policy = read_json(root / policy["migration_policy_path"])
    rows = [legacy_shim_row(root, migration_policy, migration) for migration in migration_policy["migrations"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "legacy_shim_count": sum(1 for row in rows if row["legacy_is_shim"]),
        "legacy_implementation_body_count": sum(1 for row in rows if row["legacy_contains_implementation_body"]),
        "step68_legacy_shim_audit_pass": False,
    }
    summary["step68_legacy_shim_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and summary["legacy_implementation_body_count"] == 0
    )
    return rows, summary


def legacy_shim_row(root: Path, migration_policy: dict, migration: dict) -> dict:
    path = root / migration["legacy_path"]
    text = path.read_text(encoding="utf-8-sig") if path.is_file() else ""
    nonblank_line_count = sum(1 for line in text.splitlines() if line.strip())
    legacy_contains_implementation_body = any(
        token in text for token in ("def ", "class ", "legacy_getattr", "_LEGACY_MODULE", "@ti.")
    )
    legacy_import = f"from {migration['experiment_module']} import *"
    legacy_imports_experiment = legacy_import in text
    legacy_is_shim = bool(
        path.is_file()
        and migration_policy["legacy_shim_required_phrase"] in text
        and legacy_imports_experiment
        and nonblank_line_count <= int(migration_policy["max_nonblank_lines_per_shim"])
        and not legacy_contains_implementation_body
    )
    return {
        "legacy_path": migration["legacy_path"],
        "experiment_path": migration["experiment_path"],
        "legacy_is_shim": legacy_is_shim,
        "legacy_imports_experiment": legacy_imports_experiment,
        "legacy_contains_implementation_body": legacy_contains_implementation_body,
        "nonblank_line_count": nonblank_line_count,
        "pass": legacy_is_shim,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
