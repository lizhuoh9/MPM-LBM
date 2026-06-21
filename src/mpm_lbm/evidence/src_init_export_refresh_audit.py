from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import public_symbol_names, read_json


def build_step69_src_init_export_audit(
    root: Path,
    policy_path: str = "configs/step69_src_init_export_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    exports = extract_export_modules(root / policy["src_init_path"])
    heavy_loaded = imported_heavy_modules(root, policy["heavy_import_modules"])
    rows = []
    for symbol, expected_module in policy["required_exports"].items():
        actual_module = exports.get(symbol, "")
        rows.append(
            {
                "check": "required_export",
                "symbol": symbol,
                "expected_module": expected_module,
                "actual_module": actual_module,
                "symbol_present_in_target_source": symbol_present_in_module_source(root, expected_module, symbol),
                "pass": bool(actual_module == expected_module and symbol_present_in_module_source(root, expected_module, symbol)),
            }
        )
    for symbol, module in sorted(exports.items()):
        stale = module in policy["forbidden_export_targets"]
        rows.append(
            {
                "check": "forbidden_stale_export_target",
                "symbol": symbol,
                "expected_module": "",
                "actual_module": module,
                "symbol_present_in_target_source": "",
                "pass": not stale,
            }
        )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_export_count": len(policy["required_exports"]),
        "required_export_pass_count": sum(1 for row in rows if row["check"] == "required_export" and row["pass"]),
        "no_stale_export_count": sum(1 for row in rows if row["check"] == "forbidden_stale_export_target" and not row["pass"]),
        "heavy_import_during_src_import": bool(heavy_loaded),
        "heavy_import_loaded_modules": heavy_loaded,
        "src_init_export_audit_pass": False,
    }
    summary["src_init_export_audit_pass"] = bool(
        summary["required_export_pass_count"] == summary["required_export_count"]
        and summary["no_stale_export_count"] == 0
        and not summary["heavy_import_during_src_import"]
        and all(row["pass"] for row in rows)
    )
    return rows, summary


def extract_export_modules(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_EXPORT_MODULES":
                    value = ast.literal_eval(node.value)
                    return {str(key): str(module) for key, module in value.items()}
    raise RuntimeError(f"_EXPORT_MODULES not found in {path}")


def symbol_present_in_module_source(root: Path, module: str, symbol: str) -> bool:
    module_path = root / (module.replace(".", "/") + ".py")
    return symbol in public_symbol_names(module_path)


def imported_heavy_modules(root: Path, heavy_modules: list[str]) -> list[str]:
    script = (
        "import json, sys\n"
        "import src\n"
        f"heavy = {json.dumps(heavy_modules)}\n"
        "print(json.dumps(sorted([name for name in heavy if name in sys.modules])))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout.strip() or "[]")
