from __future__ import annotations

import importlib
from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import batch_symbol_pairs, output_snapshot, read_json


def build_batch_import_execution_audit(root: Path, policy_path: str) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before_outputs = output_snapshot(root)
    rows = [symbol_import_row(pair) for pair in batch_symbol_pairs(policy)]
    after_outputs = output_snapshot(root)
    output_snapshot_unchanged = before_outputs == after_outputs
    summary = {
        "policy_id": policy["policy_id"],
        "step": int(policy["step"]),
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "canonical_import_pass_count": sum(1 for row in rows if row["canonical_import_pass"]),
        "legacy_import_pass_count": sum(1 for row in rows if row["legacy_import_pass"]),
        "same_object_count": sum(1 for row in rows if row["same_object"]),
        "output_snapshot_unchanged": output_snapshot_unchanged,
        "solver_run": False,
        "runtime_object_construction_required": False,
        "batch_import_execution_audit_pass": False,
    }
    summary["batch_import_execution_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and output_snapshot_unchanged
        and not summary["solver_run"]
        and not summary["runtime_object_construction_required"]
    )
    return rows, summary


def symbol_import_row(pair: dict) -> dict:
    error = ""
    canonical_obj = None
    legacy_obj = None
    canonical_import_pass = False
    legacy_import_pass = False
    try:
        canonical_module = importlib.import_module(pair["canonical_module"])
        canonical_obj = getattr(canonical_module, pair["symbol"])
        canonical_import_pass = True
    except Exception as exc:  # pragma: no cover - written into artifact rows
        error = join_error(error, f"canonical_import_error={type(exc).__name__}: {exc}")
    try:
        legacy_module = importlib.import_module(pair["legacy_module"])
        legacy_obj = getattr(legacy_module, pair["symbol"])
        legacy_import_pass = True
    except Exception as exc:  # pragma: no cover - written into artifact rows
        error = join_error(error, f"legacy_import_error={type(exc).__name__}: {exc}")
    same_object = bool(canonical_import_pass and legacy_import_pass and canonical_obj is legacy_obj)
    return {
        "symbol": pair["symbol"],
        "canonical_module": pair["canonical_module"],
        "legacy_module": pair["legacy_module"],
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
