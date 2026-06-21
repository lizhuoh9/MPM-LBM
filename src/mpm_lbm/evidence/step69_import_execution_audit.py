from __future__ import annotations

import importlib
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import output_snapshot, read_json


def build_step69_import_execution_audit(
    root: Path,
    policy_path: str = "configs/step69_remaining_support_migration_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before_outputs = output_snapshot(root)
    rows = [symbol_import_row(migration, symbol) for migration in policy["migrations"] for symbol in migration["public_symbols"]]
    after_outputs = output_snapshot(root)
    summary = {
        "row_count": len(rows),
        "public_symbol_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "canonical_import_pass_count": sum(1 for row in rows if row["canonical_import_pass"]),
        "legacy_import_pass_count": sum(1 for row in rows if row["legacy_import_pass"]),
        "same_object_count": sum(1 for row in rows if row["same_object"]),
        "output_snapshot_unchanged": before_outputs == after_outputs,
        "solver_run": False,
        "step69_import_execution_audit_pass": False,
    }
    summary["step69_import_execution_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and summary["same_object_count"] == summary["public_symbol_count"]
        and summary["output_snapshot_unchanged"]
        and not summary["solver_run"]
    )
    return rows, summary


def symbol_import_row(migration: dict, symbol: str) -> dict:
    error = ""
    canonical_obj = None
    legacy_obj = None
    canonical_import_pass = False
    legacy_import_pass = False
    try:
        canonical_module = importlib.import_module(migration["canonical_module"])
        canonical_obj = getattr(canonical_module, symbol)
        canonical_import_pass = True
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = join_error(error, f"canonical_import_error={type(exc).__name__}: {exc}")
    try:
        legacy_module = importlib.import_module(migration["legacy_module"])
        legacy_obj = getattr(legacy_module, symbol)
        legacy_import_pass = True
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = join_error(error, f"legacy_import_error={type(exc).__name__}: {exc}")
    same_object = bool(canonical_import_pass and legacy_import_pass and canonical_obj is legacy_obj)
    return {
        "symbol": symbol,
        "canonical_module": migration["canonical_module"],
        "legacy_module": migration["legacy_module"],
        "canonical_import_pass": canonical_import_pass,
        "legacy_import_pass": legacy_import_pass,
        "same_object": same_object,
        "pass": bool(canonical_import_pass and legacy_import_pass and same_object),
        "error": error,
    }


def join_error(existing: str, new: str) -> str:
    if existing:
        return f"{existing}; {new}"
    return new
