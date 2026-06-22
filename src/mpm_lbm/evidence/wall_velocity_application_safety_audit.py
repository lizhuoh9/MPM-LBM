from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json, read_text
from src.mpm_lbm.sim.wall_velocity.application_config import (
    WallVelocityApplicationConfig,
    validate_wall_velocity_application_config,
)


def build_step73_wall_velocity_application_safety_audit(
    root: Path,
    policy_path: str = "configs/step73_wall_velocity_application_safety_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    config = WallVelocityApplicationConfig.from_json(root / policy["wall_velocity_application_config_path"])
    validation_rows = validate_wall_velocity_application_config(config, root=root)
    source = read_text(root / policy["wall_velocity_application_source_path"])
    rows: list[dict] = [
        bool_row("application_config_validation_pass", all(row["pass"] for row in validation_rows), True, "Committed Step36 application config validates"),
        bool_row("application_mode", config.application_mode, "solid_vel_experimental", "Wall velocity remains explicit opt-in mode"),
        bool_row("target_lbm_field", config.target_lbm_field, "solid_vel", "Only lbm.solid_vel is targeted"),
    ]
    rows.extend(
        bool_row(f"config_true_{field}", getattr(config, field), True, "Required opt-in/report flag remains true")
        for field in policy["required_true_config_fields"]
    )
    rows.extend(
        bool_row(f"config_false_{field}", getattr(config, field), False, "Unsafe application flag remains false")
        for field in policy["required_false_config_fields"]
    )
    rows.extend(
        bool_row(f"source_contains_{term}", term in source, True, "Application source retains safety/report term")
        for term in policy["required_source_terms"]
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "lbm_population_update_allowed": bool(config.apply_to_lbm_populations),
        "mpm_update_allowed": bool(config.apply_to_mpm),
        "projector_update_allowed": bool(config.apply_to_projector),
        "bounceback_formula_modification_allowed": bool(config.modify_bounceback_formula),
        "actuation_claim_allowed": bool(config.actuation_claim_enabled),
        "jet_model_allowed": bool(config.jet_model_enabled),
        "apply_to_lbm_solid_vel": bool(config.apply_to_lbm_solid_vel),
        "diagnostic_report_enabled": bool(config.diagnostic_report_enabled),
        "wall_velocity_application_safety_audit_pass": False,
    }
    summary["wall_velocity_application_safety_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["lbm_population_update_allowed"] is False
        and summary["mpm_update_allowed"] is False
        and summary["projector_update_allowed"] is False
        and summary["bounceback_formula_modification_allowed"] is False
        and summary["actuation_claim_allowed"] is False
        and summary["jet_model_allowed"] is False
        and summary["apply_to_lbm_solid_vel"] is True
        and summary["diagnostic_report_enabled"] is True
    )
    return rows, summary


def bool_row(check: str, actual, expected, notes: str) -> dict:
    return {
        "check": check,
        "actual": actual,
        "expected": expected,
        "pass": actual == expected,
        "notes": notes,
    }
