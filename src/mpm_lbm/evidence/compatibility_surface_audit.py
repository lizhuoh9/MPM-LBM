from __future__ import annotations

import ast
import importlib
import json
import subprocess
import sys
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import is_compatibility_shim, output_snapshot, read_json, read_text


def build_step70_compatibility_surface_audit(
    root: Path,
    policy_path: str = "configs/step70_compatibility_surface_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    exports = extract_export_modules(root / policy["src_init_path"])
    before_outputs = output_snapshot(root)
    rows = [compatibility_row(root, policy, symbol, module) for symbol, module in sorted(exports.items())]
    after_outputs = output_snapshot(root)
    heavy_loaded = imported_heavy_modules(root, policy["heavy_import_modules"])
    legacy_rows = [row for row in rows if row["classification"] == "legacy_shim_target_allowed"]
    expected_count = len(policy["export_rules"])
    summary = {
        "row_count": len(rows),
        "expected_count": expected_count,
        "src_init_export_count": len(exports),
        "src_init_export_audit_pass": False,
        "stale_export_count": sum(1 for row in rows if row["stale_export"]),
        "forbidden_target_count": sum(1 for row in rows if row["forbidden_target"]),
        "legacy_shim_target_count": len(legacy_rows),
        "legacy_shim_targets_are_shims": all(row["legacy_target_is_shim"] for row in legacy_rows),
        "same_object_count": sum(1 for row in rows if row["same_object"]),
        "heavy_import_during_src_import": bool(heavy_loaded),
        "heavy_import_loaded_modules": heavy_loaded,
        "output_snapshot_unchanged": before_outputs == after_outputs,
        "compatibility_surface_audit_pass": False,
    }
    summary["src_init_export_audit_pass"] = bool(
        summary["src_init_export_count"] == expected_count
        and summary["stale_export_count"] == 0
        and summary["forbidden_target_count"] == 0
        and not summary["heavy_import_during_src_import"]
    )
    summary["compatibility_surface_audit_pass"] = bool(
        rows
        and summary["src_init_export_audit_pass"]
        and summary["same_object_count"] == expected_count
        and summary["legacy_shim_targets_are_shims"]
        and summary["output_snapshot_unchanged"]
        and all(row["pass"] for row in rows)
    )
    return rows, summary


def compatibility_row(root: Path, policy: dict, symbol: str, actual_module: str) -> dict:
    rule = policy["export_rules"].get(symbol)
    classification = rule.get("classification", "missing_policy_rule") if rule else "missing_policy_rule"
    expected_module = rule.get("module", "") if rule else ""
    forbidden_target = any(actual_module.startswith(prefix) for prefix in policy["forbidden_target_prefixes"])
    stale_export = bool(not rule or actual_module != expected_module)
    legacy_target_is_shim = False
    same_object = False
    import_pass = False
    error = ""
    try:
        actual_obj = getattr(importlib.import_module(actual_module), symbol)
        export_obj = getattr(importlib.import_module("src"), symbol)
        if classification == "legacy_shim_target_allowed":
            legacy_target_is_shim = is_compatibility_shim(read_text(root / (actual_module.replace(".", "/") + ".py")))
            canonical_obj = getattr(importlib.import_module(rule["canonical_module"]), symbol)
            same_object = bool(export_obj is canonical_obj and actual_obj is canonical_obj)
        elif classification in {"canonical_target_required", "approved_legacy_tooling_allowed"}:
            same_object = bool(export_obj is actual_obj)
        import_pass = True
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = f"{type(exc).__name__}: {exc}"
    passed = bool(
        rule
        and import_pass
        and not stale_export
        and not forbidden_target
        and same_object
        and (classification != "legacy_shim_target_allowed" or legacy_target_is_shim)
    )
    return {
        "symbol": symbol,
        "classification": classification,
        "actual_module": actual_module,
        "expected_module": expected_module,
        "canonical_module": rule.get("canonical_module", "") if rule else "",
        "import_pass": import_pass,
        "same_object": same_object,
        "legacy_target_is_shim": legacy_target_is_shim,
        "stale_export": stale_export,
        "forbidden_target": forbidden_target,
        "heavy_import_during_src_import": False,
        "pass": passed,
        "error": error,
    }


def extract_export_modules(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "_EXPORT_MODULES":
                    return {str(key): str(value) for key, value in ast.literal_eval(node.value).items()}
    raise RuntimeError(f"_EXPORT_MODULES not found in {path}")


def imported_heavy_modules(root: Path, heavy_modules: list[str]) -> list[str]:
    script = (
        "import json, sys\n"
        "import src\n"
        f"heavy = {json.dumps(heavy_modules)}\n"
        "print(json.dumps(sorted([name for name in heavy if name in sys.modules])))\n"
    )
    result = subprocess.run([sys.executable, "-c", script], cwd=root, text=True, capture_output=True, check=True)
    return json.loads(result.stdout.strip() or "[]")


def write_compatibility_docs(summary: dict, rows: list[dict]) -> str:
    lines = [
        "# Compatibility And Deprecation Policy",
        "",
        "Step70 freezes the root `src` compatibility surface.",
        "",
        "```text",
        f"compatibility_surface_audit_pass = {summary['compatibility_surface_audit_pass']}",
        f"src_init_export_count = {summary['src_init_export_count']}",
        f"legacy_shim_target_count = {summary['legacy_shim_target_count']}",
        f"forbidden_target_count = {summary['forbidden_target_count']}",
        "```",
        "",
        "| Symbol | Classification | Module |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| `{row['symbol']}` | `{row['classification']}` | `{row['actual_module']}` |")
    return "\n".join(lines).rstrip() + "\n"
