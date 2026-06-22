from __future__ import annotations

import importlib
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import output_snapshot, read_json


def build_step74_real_geometry_api_audit(
    root: Path,
    policy_path: str = "configs/step74_real_geometry_api_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before = output_snapshot(root)
    rows = [symbol_row(entry) for entry in policy["required_symbols"]]
    after = output_snapshot(root)
    projection_imported = any(
        row["check"] == "canonical_symbol_import"
        and row["canonical_module"] == "src.mpm_lbm.sim.geometry.intake"
        and row["symbol"] == "run_candidate_projection_smoke"
        and row["pass"]
        for row in rows
    )
    rows.append(
        {
            "actual_kind": "",
            "canonical_module": "src.mpm_lbm.sim.geometry.intake",
            "check": "projection_smoke_imported_but_not_executed",
            "error": "",
            "expected_kind": "",
            "pass": projection_imported,
            "symbol": "run_candidate_projection_smoke",
        }
    )
    rows.append(
        {
            "actual_kind": "",
            "canonical_module": "",
            "check": "output_snapshot_unchanged_after_imports",
            "error": "",
            "expected_kind": "",
            "pass": before == after,
            "symbol": "",
        }
    )
    summary = {
        "canonical_import_pass_count": sum(
            1 for row in rows if row["check"] == "canonical_symbol_import" and row["pass"]
        ),
        "driver_constructed": False,
        "missing_symbol_count": sum(
            1 for row in rows if row["check"] == "canonical_symbol_import" and not row["pass"]
        ),
        "output_snapshot_unchanged": before == after,
        "projection_smoke_imported_but_not_executed": projection_imported,
        "real_geometry_api_audit_pass": False,
        "required_symbol_count": len(policy["required_symbols"]),
        "row_count": len(rows),
        "solver_run": False,
    }
    summary["real_geometry_api_audit_pass"] = bool(
        summary["canonical_import_pass_count"] == summary["required_symbol_count"]
        and summary["missing_symbol_count"] == 0
        and summary["output_snapshot_unchanged"]
        and summary["projection_smoke_imported_but_not_executed"]
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
        "actual_kind": actual_kind,
        "canonical_module": entry["canonical_module"],
        "check": "canonical_symbol_import",
        "error": error,
        "expected_kind": entry["kind"],
        "pass": passed,
        "symbol": entry["symbol"],
    }


def classify_symbol(symbol, name: str) -> str:
    if isinstance(symbol, type):
        return "class"
    if callable(symbol):
        return "function"
    if name.isupper() or name.endswith("_FIELDS"):
        return "constant"
    return "value"
