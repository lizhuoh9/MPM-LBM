from __future__ import annotations

import importlib
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import output_snapshot, read_json


def build_step72_runtime_geometry_api_audit(
    root: Path,
    policy_path: str = "configs/step72_runtime_geometry_api_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before = output_snapshot(root)
    rows = [symbol_row(entry) for entry in policy["required_symbols"]]
    after = output_snapshot(root)
    rows.append(
        {
            "check": "output_snapshot_unchanged_after_imports",
            "canonical_module": "",
            "symbol": "",
            "expected_kind": "",
            "actual_kind": "",
            "pass": before == after,
            "error": "",
        }
    )
    summary = {
        "row_count": len(rows),
        "required_symbol_count": len(policy["required_symbols"]),
        "canonical_import_pass_count": sum(1 for row in rows if row["check"] == "canonical_symbol_import" and row["pass"]),
        "missing_symbol_count": sum(1 for row in rows if row["check"] == "canonical_symbol_import" and not row["pass"]),
        "output_snapshot_unchanged": before == after,
        "driver_constructed": False,
        "solver_run": False,
        "runtime_geometry_api_audit_pass": False,
    }
    summary["runtime_geometry_api_audit_pass"] = bool(
        summary["canonical_import_pass_count"] == summary["required_symbol_count"]
        and summary["missing_symbol_count"] == 0
        and summary["output_snapshot_unchanged"]
        and summary["driver_constructed"] is False
        and summary["solver_run"] is False
    )
    return rows, summary


def symbol_row(entry: dict) -> dict:
    error = ""
    actual_kind = ""
    passed = False
    try:
        module = importlib.import_module(entry["canonical_module"])
        symbol = getattr(module, entry["symbol"])
        actual_kind = classify_symbol(symbol, entry["symbol"])
        passed = actual_kind == entry["kind"]
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = f"{type(exc).__name__}: {exc}"
    return {
        "check": "canonical_symbol_import",
        "canonical_module": entry["canonical_module"],
        "symbol": entry["symbol"],
        "expected_kind": entry["kind"],
        "actual_kind": actual_kind,
        "pass": passed,
        "error": error,
    }


def classify_symbol(symbol, name: str) -> str:
    if isinstance(symbol, type):
        return "class"
    if callable(symbol):
        return "function"
    if name.isupper() or name.endswith("_FIELDS"):
        return "constant"
    return "value"
