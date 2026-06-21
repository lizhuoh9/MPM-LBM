from __future__ import annotations

import ast
import importlib
import json
from pathlib import Path


def build_src_init_export_audit(
    root: Path,
    policy_path: str = "configs/step57_src_init_export_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    src_init_path = root / policy["src_init_path"]
    src_init_text = src_init_path.read_text(encoding="utf-8") if src_init_path.is_file() else ""
    export_modules = parse_export_modules(src_init_text)
    rows = [export_row(symbol, module_name) for symbol, module_name in sorted(export_modules.items())]
    target_rows = [
        migrated_target_row(symbol, expected_module, export_modules)
        for symbol, expected_module in sorted(policy["migrated_symbol_targets"].items())
    ]
    calibration_rows = [
        calibration_export_row(root, symbol, export_modules)
        for symbol in policy["calibration_symbols"]
    ]
    all_rows = rows + target_rows + calibration_rows
    lazy_import_enabled = "__getattr__" in src_init_text and "import_module" in src_init_text
    solver_object_constructed = contains_solver_construction(src_init_text)
    summary = {
        "export_count": len(rows),
        "row_count": len(all_rows),
        "pass_count": sum(1 for row in all_rows if row["pass"]),
        "missing_module_count": sum(1 for row in rows if row["check"] == "export_resolves" and not row["module_import_pass"]),
        "missing_symbol_count": sum(1 for row in rows if row["check"] == "export_resolves" and not row["symbol_resolve_pass"]),
        "migrated_target_mismatch_count": sum(1 for row in target_rows if not row["pass"]),
        "calibration_export_issue_count": sum(1 for row in calibration_rows if not row["pass"]),
        "lazy_import_enabled": lazy_import_enabled,
        "solver_object_constructed": solver_object_constructed,
        "src_init_export_audit_pass": False,
    }
    summary["src_init_export_audit_pass"] = bool(
        summary["export_count"] > 0
        and summary["row_count"] == summary["pass_count"]
        and lazy_import_enabled == bool(policy["lazy_import_required"])
        and not solver_object_constructed
    )
    return all_rows, summary


def parse_export_modules(src_init_text: str) -> dict:
    module_ast = ast.parse(src_init_text)
    for node in module_ast.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "_EXPORT_MODULES" for target in node.targets):
                value = ast.literal_eval(node.value)
                return dict(value)
    return {}


def export_row(symbol: str, module_name: str) -> dict:
    error = ""
    module_import_pass = False
    symbol_resolve_pass = False
    try:
        module = importlib.import_module(module_name)
        module_import_pass = True
        getattr(module, symbol)
        symbol_resolve_pass = True
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        error = f"{type(exc).__name__}: {exc}"
    return {
        "check": "export_resolves",
        "symbol": symbol,
        "expected_module": module_name,
        "actual_module": module_name,
        "module_import_pass": module_import_pass,
        "symbol_resolve_pass": symbol_resolve_pass,
        "pass": bool(module_import_pass and symbol_resolve_pass),
        "error": error,
    }


def migrated_target_row(symbol: str, expected_module: str, export_modules: dict) -> dict:
    actual_module = export_modules.get(symbol, "")
    return {
        "check": "migrated_symbol_target",
        "symbol": symbol,
        "expected_module": expected_module,
        "actual_module": actual_module,
        "module_import_pass": actual_module == expected_module,
        "symbol_resolve_pass": actual_module == expected_module,
        "pass": actual_module == expected_module,
        "error": "" if actual_module == expected_module else "migrated symbol target mismatch",
    }


def calibration_export_row(root: Path, symbol: str, export_modules: dict) -> dict:
    actual_module = export_modules.get(symbol, "")
    expected_module = "src.calibration"
    calibration_exists = (root / "src" / "calibration.py").is_file()
    base = {
        "check": "calibration_export",
        "symbol": symbol,
        "expected_module": expected_module,
        "actual_module": actual_module,
    }
    if not calibration_exists:
        return {
            **base,
            "module_import_pass": False,
            "symbol_resolve_pass": False,
            "pass": False,
            "error": "src/calibration.py is missing",
        }
    row = export_row(symbol, actual_module)
    return {
        **base,
        "module_import_pass": row["module_import_pass"] and actual_module == expected_module,
        "symbol_resolve_pass": row["symbol_resolve_pass"],
        "pass": bool(actual_module == expected_module and row["pass"]),
        "error": row["error"] if actual_module == expected_module else "calibration export target mismatch",
    }


def contains_solver_construction(src_init_text: str) -> bool:
    construction_tokens = [
        "LBMFluid3D(",
        "MPMSolid3D(",
        "FSIDriver3D(",
        "PenaltyFSICoupler3D(",
        "MovingBoundaryFSICoupler3D(",
        "LinkAreaMovingBoundaryCoupler3D(",
    ]
    return any(token in src_init_text for token in construction_tokens)


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
