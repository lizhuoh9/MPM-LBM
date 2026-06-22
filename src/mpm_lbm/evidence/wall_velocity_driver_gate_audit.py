from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig


def build_step73_wall_velocity_driver_gate_audit(
    root: Path,
    policy_path: str = "configs/step73_wall_velocity_driver_gate_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    default_config = FSIDriverConfig()
    rows = [
        default_row(field, getattr(default_config, field), expected)
        for field, expected in policy["required_defaults"].items()
    ]
    rows.extend(invalid_combination_row(entry) for entry in policy["invalid_combinations"])
    rows.extend(
        [
            bool_row("driver_constructed", False, False, "Audit only constructs config dataclasses"),
            bool_row("driver_initialized", False, False, "Audit does not initialize FSIDriver3D"),
            bool_row("solver_run", False, False, "Audit does not step or run solver"),
        ]
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "default_gate_closed": all(
            getattr(default_config, field) == expected for field, expected in policy["required_defaults"].items()
        ),
        "invalid_combination_count": len(policy["invalid_combinations"]),
        "invalid_combination_rejected_count": sum(1 for row in rows if row["check"] == "invalid_combination_rejected" and row["pass"]),
        "safe_output_defaults_preserved": bool(default_config.write_vtk is False and default_config.write_particles is False),
        "activation_constructed": False,
        "driver_run": False,
        "wall_velocity_driver_gate_audit_pass": False,
    }
    summary["wall_velocity_driver_gate_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["default_gate_closed"]
        and summary["invalid_combination_rejected_count"] == summary["invalid_combination_count"]
        and summary["safe_output_defaults_preserved"]
        and summary["activation_constructed"] is False
        and summary["driver_run"] is False
    )
    return rows, summary


def default_row(field: str, actual, expected) -> dict:
    return {
        "check": "default_gate_closed",
        "field": field,
        "actual": actual,
        "expected": expected,
        "pass": actual == expected,
        "error": "",
    }


def invalid_combination_row(entry: dict) -> dict:
    error = ""
    rejected = False
    try:
        FSIDriverConfig(**entry["kwargs"])
    except ValueError as exc:
        rejected = True
        error = str(exc)
    return {
        "check": "invalid_combination_rejected",
        "field": entry["case"],
        "actual": "rejected" if rejected else "accepted",
        "expected": "rejected",
        "pass": rejected,
        "error": error,
    }


def bool_row(check: str, actual, expected, notes: str) -> dict:
    return {
        "check": check,
        "field": "",
        "actual": actual,
        "expected": expected,
        "pass": actual is expected,
        "error": notes,
    }
