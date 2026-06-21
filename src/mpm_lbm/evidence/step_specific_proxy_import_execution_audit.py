from __future__ import annotations

import importlib
import json
from pathlib import Path


def build_step68_import_execution_audit(
    root: Path,
    policy_path: str = "configs/step68_import_execution_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    migration_policy = read_json(root / policy["migration_policy_path"])
    before_outputs = output_snapshot(root)
    rows = [symbol_import_row(migration, symbol) for migration in migration_policy["migrations"] for symbol in migration["public_symbols"]]
    after_outputs = output_snapshot(root)
    summary = {
        "row_count": len(rows),
        "symbol_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "experiment_import_pass_count": sum(1 for row in rows if row["experiment_import_pass"]),
        "legacy_import_pass_count": sum(1 for row in rows if row["legacy_import_pass"]),
        "same_object_count": sum(1 for row in rows if row["same_object"]),
        "output_snapshot_unchanged": before_outputs == after_outputs,
        "solver_run": False,
        "step68_import_execution_audit_pass": False,
    }
    summary["step68_import_execution_audit_pass"] = bool(
        summary["row_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and summary["same_object_count"] == summary["symbol_count"]
        and summary["output_snapshot_unchanged"]
        and not summary["solver_run"]
    )
    return rows, summary


def symbol_import_row(migration: dict, symbol: str) -> dict:
    error = ""
    experiment_obj = None
    legacy_obj = None
    experiment_import_pass = False
    legacy_import_pass = False
    try:
        experiment_module = importlib.import_module(migration["experiment_module"])
        experiment_obj = getattr(experiment_module, symbol)
        experiment_import_pass = True
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = join_error(error, f"experiment_import_error={type(exc).__name__}: {exc}")
    try:
        legacy_module = importlib.import_module(migration["legacy_module"])
        legacy_obj = getattr(legacy_module, symbol)
        legacy_import_pass = True
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = join_error(error, f"legacy_import_error={type(exc).__name__}: {exc}")
    same_object = bool(experiment_import_pass and legacy_import_pass and experiment_obj is legacy_obj)
    return {
        "symbol": symbol,
        "experiment_module": migration["experiment_module"],
        "legacy_module": migration["legacy_module"],
        "experiment_import_pass": experiment_import_pass,
        "legacy_import_pass": legacy_import_pass,
        "same_object": same_object,
        "pass": bool(experiment_import_pass and legacy_import_pass and same_object),
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
