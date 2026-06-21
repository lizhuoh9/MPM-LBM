from __future__ import annotations

import json
from pathlib import Path


def build_compatibility_shim_audit(root: Path, policy_path: str = "configs/step55_compatibility_shim_policy.json") -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = []
    for surface in policy["surfaces"]:
        old_path = root / surface["old_path"]
        new_path = root / surface["new_path"]
        symbol = surface["symbol"]
        old_text = old_path.read_text(encoding="utf-8") if old_path.is_file() else ""
        new_text = new_path.read_text(encoding="utf-8") if new_path.is_file() else ""
        old_symbol_present = symbol in old_text
        new_symbol_present = symbol in new_text
        new_lazy_surface_present = "_LEGACY_MODULE" in new_text and "__getattr__" in new_text
        rows.append(
            {
                "old_path": surface["old_path"],
                "new_path": surface["new_path"],
                "symbol": symbol,
                "old_path_exists": old_path.is_file(),
                "new_path_exists": new_path.is_file(),
                "old_symbol_present": old_symbol_present,
                "new_symbol_or_lazy_export_present": new_symbol_present or new_lazy_surface_present,
                "source_text_check_only": bool(policy["source_text_check_only"]),
                "pass": bool(
                    old_path.is_file()
                    and new_path.is_file()
                    and old_symbol_present
                    and (new_symbol_present or new_lazy_surface_present)
                ),
            }
        )
    summary = {
        "surface_count": len(rows),
        "pass_count": sum(1 for item in rows if item["pass"]),
        "source_text_check_only": bool(policy["source_text_check_only"]),
        "avoid_heavy_runtime_imports_in_hook": bool(policy["avoid_heavy_runtime_imports_in_hook"]),
        "compatibility_shim_audit_pass": False,
    }
    summary["compatibility_shim_audit_pass"] = bool(summary["surface_count"] == summary["pass_count"] and summary["surface_count"] > 0)
    return rows, summary


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
