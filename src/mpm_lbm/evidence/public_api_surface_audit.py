from __future__ import annotations

import importlib
import json
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import output_snapshot, read_json


def build_step70_public_api_surface_audit(
    root: Path,
    policy_path: str = "configs/step70_public_api_surface_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before_outputs = output_snapshot(root)
    rows = [
        public_api_row(entry["api_group"], entry["canonical_module"], symbol)
        for entry in policy["entries"]
        for symbol in entry["symbols"]
    ]
    after_outputs = output_snapshot(root)
    expected_count = len(rows)
    summary = {
        "row_count": len(rows),
        "expected_count": expected_count,
        "canonical_import_pass_count": sum(1 for row in rows if row["canonical_import_pass"]),
        "missing_symbol_count": sum(1 for row in rows if not row["canonical_import_pass"]),
        "runtime_object_construction_required_count": sum(1 for row in rows if row["runtime_object_construction_required"]),
        "solver_run": False,
        "output_snapshot_unchanged": before_outputs == after_outputs,
        "api_group_count": len({row["api_group"] for row in rows}),
        "public_api_surface_audit_pass": False,
    }
    summary["public_api_surface_audit_pass"] = bool(
        expected_count > 0
        and summary["canonical_import_pass_count"] == expected_count
        and summary["missing_symbol_count"] == 0
        and summary["runtime_object_construction_required_count"] == 0
        and not summary["solver_run"]
        and summary["output_snapshot_unchanged"]
    )
    return rows, summary


def public_api_row(api_group: str, canonical_module: str, symbol: str) -> dict:
    error = ""
    object_type = ""
    canonical_import_pass = False
    try:
        module = importlib.import_module(canonical_module)
        obj = getattr(module, symbol)
        object_type = type(obj).__name__
        canonical_import_pass = True
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = f"{type(exc).__name__}: {exc}"
    return {
        "api_group": api_group,
        "symbol": symbol,
        "canonical_module": canonical_module,
        "canonical_import_pass": canonical_import_pass,
        "object_type": object_type,
        "runtime_object_construction_required": False,
        "solver_run": False,
        "output_snapshot_unchanged": True,
        "pass": canonical_import_pass,
        "error": error,
    }


def write_public_api_docs(root: Path, rows: list[dict], summary: dict) -> str:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["api_group"], []).append(row)
    lines = [
        "# Public API Surface",
        "",
        "Step70 freezes this import surface for later activation-readiness work.",
        "",
        "```text",
        f"public_api_surface_audit_pass = {summary['public_api_surface_audit_pass']}",
        f"canonical_import_pass_count = {summary['canonical_import_pass_count']}",
        f"expected_count = {summary['expected_count']}",
        "```",
        "",
    ]
    for group in sorted(grouped):
        lines.append(f"## {group}")
        lines.append("")
        for row in sorted(grouped[group], key=lambda item: (item["canonical_module"], item["symbol"])):
            lines.append(f"- `{row['canonical_module']}.{row['symbol']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
