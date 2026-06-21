from __future__ import annotations

import ast
import json
from pathlib import Path


def build_step69_current_root_inventory_audit(
    root: Path,
    policy_path: str = "configs/step69_current_root_inventory_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    step63 = read_json(root / policy["source_step63_inventory_path"])
    step68_policy = read_json(root / policy["step68_migration_policy_path"])
    step69_policy = read_json(root / policy["remaining_support_migration_policy_path"])
    approved_policy = read_json(root / policy["root_src_approved_legacy_policy_path"])

    source_rows = {row["path"]: row for row in step63["rows"]}
    step68_legacy_paths = {row["legacy_path"] for row in step68_policy["migrations"]}
    step69_legacy_paths = {row["legacy_path"] for row in step69_policy["migrations"]}
    approved_legacy_paths = {
        row["path"]
        for row in step63["rows"]
        if row.get("classification") == approved_policy["approved_legacy_source_classification"]
    }

    rows = [
        current_root_row(
            root,
            path,
            source_rows.get(path.relative_to(root).as_posix(), {}),
            step68_legacy_paths,
            step69_legacy_paths,
            approved_legacy_paths,
            policy,
        )
        for path in sorted((root / "src").glob("*.py"))
    ]
    summary = {
        "row_count": len(rows),
        "current_root_file_count": len(rows),
        "root_compatibility_shim_count": sum(1 for row in rows if row["current_classification"] == "root_compatibility_shim"),
        "approved_legacy_support_count": sum(1 for row in rows if row["current_classification"] == "approved_legacy_support"),
        "step69_support_shim_count": sum(1 for row in rows if row["step69_support_shim"]),
        "current_step_specific_proxy_remaining_count": sum(1 for row in rows if row["current_step_specific_proxy_remaining"]),
        "current_root_step_specific_implementation_count": sum(1 for row in rows if row["current_root_step_specific_implementation"]),
        "current_migration_required_count": sum(1 for row in rows if row["current_migration_required"]),
        "current_unknown_requires_review_count": sum(1 for row in rows if row["current_classification"] == "unknown_requires_review"),
        "current_root_inventory_audit_pass": False,
    }
    summary["current_root_inventory_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["current_step_specific_proxy_remaining_count"] == 0
        and summary["current_root_step_specific_implementation_count"] == 0
        and summary["current_migration_required_count"] == 0
        and summary["current_unknown_requires_review_count"] == 0
        and all(row["pass"] for row in rows)
    )
    return rows, summary


def current_root_row(
    root: Path,
    path: Path,
    source_row: dict,
    step68_legacy_paths: set[str],
    step69_legacy_paths: set[str],
    approved_legacy_paths: set[str],
    policy: dict,
) -> dict:
    rel = path.relative_to(root).as_posix()
    text = read_text(path)
    shim = is_compatibility_shim(text, policy["legacy_shim_required_phrase"])
    source_classification = source_row.get("classification", "")
    source_migration_required = bool(source_row.get("migration_required", False))
    current_classification = "unknown_requires_review"
    if rel in step69_legacy_paths and shim:
        current_classification = "root_compatibility_shim"
    elif rel in step68_legacy_paths and shim:
        current_classification = "root_compatibility_shim"
    elif shim:
        current_classification = "root_compatibility_shim"
    elif rel in approved_legacy_paths:
        current_classification = "approved_legacy_support"

    current_step_specific_proxy_remaining = bool(source_classification == "step_specific_proxy_remaining" and not shim)
    current_root_step_specific_implementation = current_step_specific_proxy_remaining
    current_migration_required = bool(source_migration_required and not (rel in step69_legacy_paths and shim))
    passed = bool(
        current_classification != "unknown_requires_review"
        and not current_step_specific_proxy_remaining
        and not current_root_step_specific_implementation
        and not current_migration_required
    )
    return {
        "path": rel,
        "source_classification": source_classification,
        "source_migration_required": source_migration_required,
        "current_classification": current_classification,
        "is_root_shim": shim,
        "step68_step_specific_shim": rel in step68_legacy_paths and shim,
        "step69_support_shim": rel in step69_legacy_paths and shim,
        "approved_legacy_source": rel in approved_legacy_paths,
        "current_step_specific_proxy_remaining": current_step_specific_proxy_remaining,
        "current_root_step_specific_implementation": current_root_step_specific_implementation,
        "current_migration_required": current_migration_required,
        "unknown_requires_review": current_classification == "unknown_requires_review",
        "public_symbols": public_symbol_names(path),
        "pass": passed,
    }


def public_symbol_names(path: Path) -> list[str]:
    return [entry["name"] for entry in public_symbol_entries(path)]


def public_symbol_entries(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    symbols = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
            kind = "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class"
            symbols.append({"name": node.name, "kind": kind})
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    if target.id.isupper() or target.id.endswith("_FIELDS"):
                        symbols.append({"name": target.id, "kind": "constant"})
    return symbols


def is_compatibility_shim(text: str, required_phrase: str = "Compatibility shim") -> bool:
    if required_phrase not in text:
        return False
    if " import *" not in text:
        return False
    return not legacy_contains_implementation_body(text)


def legacy_contains_implementation_body(text: str) -> bool:
    return any(token in text for token in ("def ", "class ", "legacy_getattr", "_LEGACY_MODULE", "@ti."))


def imports_any_legacy_root_module(text: str, modules: list[str]) -> bool:
    for module in modules:
        stem = module.rsplit(".", 1)[-1]
        if f"from {module} import" in text or f"import {module}" in text:
            return True
        if f"from src import {stem}" in text or f"import src.{stem}" in text:
            return True
    return False


def output_snapshot(root: Path) -> list[tuple[str, int]]:
    output_root = root / "outputs"
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
