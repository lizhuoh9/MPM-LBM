from __future__ import annotations

import importlib
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json, read_text
from src.mpm_lbm.sim.runtime_geometry.projection_config import (
    RuntimeGeometryProjectionIntegrationConfig,
    mutation_flag_enabled_count,
)


def build_step72_runtime_geometry_state_guard_audit(
    root: Path,
    policy_path: str = "configs/step72_runtime_geometry_state_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    module = importlib.import_module("src.mpm_lbm.sim.runtime_geometry.state_guard")
    source = read_text(root / policy["state_guard_module_path"])
    config = RuntimeGeometryProjectionIntegrationConfig.from_json(root / policy["runtime_projection_config_path"])
    rows: list[dict] = []
    rows.extend(symbol_row(module, symbol) for symbol in policy["required_guard_symbols"])
    rows.extend(source_contains_row("required_guard_check", term, source) for term in policy["required_guard_checks"])
    rows.extend(source_contains_row("required_source_term", term, source) for term in policy["required_source_terms"])
    rows.extend(config_zero_row(field, getattr(config, field)) for field in policy["required_zero_summary_fields"] if hasattr(config, field))
    rows.append(bool_row("runtime_projection_config_mutation_flags_zero", mutation_flag_enabled_count(config), 0, "Committed projection config remains guardable without persistence"))
    rows.append(bool_row("state_guard_driver_run", False, False, "State guard audit does not run FSIDriver3D"))
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_guard_symbol_count": len(policy["required_guard_symbols"]),
        "required_guard_check_count": len(policy["required_guard_checks"]),
        "required_source_term_count": len(policy["required_source_terms"]),
        "config_mutation_flag_enabled_count": mutation_flag_enabled_count(config),
        "driver_run": False,
        "runtime_geometry_state_guard_audit_pass": False,
    }
    summary["runtime_geometry_state_guard_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["config_mutation_flag_enabled_count"] == 0
        and summary["driver_run"] is False
    )
    return rows, summary


def symbol_row(module, symbol: str) -> dict:
    return {
        "check": "required_guard_symbol",
        "name": symbol,
        "actual": hasattr(module, symbol),
        "expected": True,
        "pass": hasattr(module, symbol),
        "notes": "State guard public surface must remain importable",
    }


def source_contains_row(check: str, term: str, source: str) -> dict:
    return {
        "check": check,
        "name": term,
        "actual": term in source,
        "expected": True,
        "pass": term in source,
        "notes": "State guard source must retain guard invariant",
    }


def config_zero_row(field: str, actual) -> dict:
    return {
        "check": "config_guard_field_zero",
        "name": field,
        "actual": actual,
        "expected": False,
        "pass": actual is False,
        "notes": "Committed runtime projection config must not request persistent state",
    }


def bool_row(check: str, actual, expected, notes: str) -> dict:
    return {
        "check": check,
        "name": "",
        "actual": actual,
        "expected": expected,
        "pass": actual == expected,
        "notes": notes,
    }
