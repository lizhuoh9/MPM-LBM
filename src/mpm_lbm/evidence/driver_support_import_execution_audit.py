from __future__ import annotations

import importlib
import json
from pathlib import Path


def build_driver_support_import_execution_audit(
    root: Path,
    policy_path: str = "configs/step57_import_execution_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before_outputs = output_snapshot(root)
    rows = [symbol_import_row(pair) for pair in policy["symbol_pairs"]]
    after_outputs = output_snapshot(root)
    output_snapshot_unchanged = before_outputs == after_outputs
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "canonical_import_pass_count": sum(1 for row in rows if row["canonical_import_pass"]),
        "legacy_import_pass_count": sum(1 for row in rows if row["legacy_import_pass"]),
        "same_object_count": sum(1 for row in rows if row["same_object"]),
        "output_snapshot_unchanged": output_snapshot_unchanged,
        "solver_run": False,
        "runtime_object_construction_required": False,
        "driver_support_import_execution_audit_pass": False,
    }
    summary["driver_support_import_execution_audit_pass"] = bool(
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
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        error = f"canonical_import_error={type(exc).__name__}: {exc}"
    try:
        legacy_module = importlib.import_module(pair["legacy_module"])
        legacy_obj = getattr(legacy_module, pair["symbol"])
        legacy_import_pass = True
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        error = join_error(error, f"legacy_import_error={type(exc).__name__}: {exc}")
    same_object = bool(canonical_import_pass and legacy_import_pass and canonical_obj is legacy_obj)
    passed = bool(canonical_import_pass and legacy_import_pass and same_object)
    return {
        "canonical_module": pair["canonical_module"],
        "legacy_module": pair["legacy_module"],
        "symbol": pair["symbol"],
        "canonical_import_pass": canonical_import_pass,
        "legacy_import_pass": legacy_import_pass,
        "same_object": same_object,
        "pass": passed,
        "error": error,
    }


def output_snapshot(root: Path) -> list[tuple[str, int]]:
    output_root = root / "outputs"
    if not output_root.exists():
        return []
    return sorted(
        (path.relative_to(root).as_posix(), int(path.stat().st_size))
        for path in output_root.rglob("*")
        if path.is_file()
    )


def join_error(existing: str, new: str) -> str:
    if existing:
        return f"{existing}; {new}"
    return new


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
