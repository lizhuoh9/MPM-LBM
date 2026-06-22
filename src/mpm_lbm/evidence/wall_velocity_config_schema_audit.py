from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.config_schema_freeze_audit import schema_row
from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.wall_velocity.application_config import (
    WallVelocityApplicationConfig,
    validate_wall_velocity_application_config,
)
from src.mpm_lbm.sim.wall_velocity.config import (
    WallVelocityFieldConfig,
    step35_execution_flag_enabled_count,
    validate_wall_velocity_config,
)


def build_step73_wall_velocity_config_schema_audit(
    root: Path,
    policy_path: str = "configs/step73_wall_velocity_config_schema_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    frozen = read_json(root / policy["step70_config_schema_artifact_path"])
    current_rows = [schema_row(entry) for entry in policy["required_config_classes"]]
    rows: list[dict] = []
    for current, entry in zip(current_rows, policy["required_config_classes"]):
        previous = frozen_schema_row(frozen, entry)
        rows.extend(
            [
                bool_row(f"{entry['class_name']}_class_import_pass", current["class_import_pass"], True, "Required class imports"),
                bool_row(f"{entry['class_name']}_schema_hash_matches_step70", current["schema_hash"], previous.get("schema_hash", ""), "Step70 schema hash remains stable"),
                bool_row(f"{entry['class_name']}_schema_hash_matches_policy", current["schema_hash"], entry["expected_step70_schema_hash"], "Policy pins Step70 schema hash"),
                bool_row(f"{entry['class_name']}_from_json_available", current["from_json_available"], True, "Config remains JSON-loadable"),
                bool_row(f"{entry['class_name']}_to_dict_available", current["to_json_or_to_dict_available"], True, "Config remains serializable"),
            ]
        )

    field_schema = schema_by_class(current_rows, "WallVelocityFieldConfig")
    app_schema = schema_by_class(current_rows, "WallVelocityApplicationConfig")
    field_config = WallVelocityFieldConfig.from_json(root / policy["wall_velocity_field_config_path"])
    app_config = WallVelocityApplicationConfig.from_json(root / policy["wall_velocity_application_config_path"])

    field_validation = validate_wall_velocity_config(field_config, root=root)
    app_validation = validate_wall_velocity_application_config(app_config, root=root)
    rows.append(bool_row("wall_velocity_field_config_validation_pass", all(row["pass"] for row in field_validation), True, "Committed Step35 config validates"))
    rows.append(bool_row("wall_velocity_application_config_validation_pass", all(row["pass"] for row in app_validation), True, "Committed Step36 config validates"))

    rows.extend(
        bool_row(f"field_default_false_{field}", field_schema["default_values_repr"].get(field), "False", "Unsafe field execution default must be false")
        for field in policy["field_config_false_defaults"]
    )
    rows.extend(
        bool_row(f"field_default_true_{field}", field_schema["default_values_repr"].get(field), "True", "Required field default must be true")
        for field in policy["field_config_true_defaults"]
    )
    rows.extend(
        bool_row(f"field_config_false_{field}", getattr(field_config, field), False, "Committed field config must remain diagnostic-only")
        for field in policy["field_config_false_defaults"]
    )
    rows.extend(
        bool_row(f"app_default_false_{field}", app_schema["default_values_repr"].get(field), "False", "Unsafe application default must be false")
        for field in policy["application_config_false_defaults"]
    )
    rows.extend(
        bool_row(f"app_default_true_{field}", app_schema["default_values_repr"].get(field), "True", "Required application default must be true")
        for field in policy["application_config_true_defaults"]
    )
    rows.extend(
        bool_row(f"app_config_false_{field}", getattr(app_config, field), False, "Committed application config must remain safe")
        for field in policy["application_config_false_defaults"]
    )
    rows.extend(
        bool_row(f"app_config_true_{field}", getattr(app_config, field), True, "Committed application config must remain opt-in solid_vel only")
        for field in policy["application_config_true_defaults"]
    )

    all_required_fields = [
        *policy["field_config_false_defaults"],
        *policy["field_config_true_defaults"],
        *policy["application_config_false_defaults"],
        *policy["application_config_true_defaults"],
    ]
    missing_required_field_count = sum(
        1
        for field in all_required_fields
        if field not in field_schema["public_fields_or_constructor_params"]
        and field not in app_schema["public_fields_or_constructor_params"]
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "schema_hash_matches_step70_count": sum(
            1
            for row in rows
            if row["check"].endswith("_schema_hash_matches_step70") and row["pass"]
        ),
        "required_schema_hash_count": len(policy["required_config_classes"]),
        "unsafe_execution_flag_count": sum(1 for field in policy["field_config_false_defaults"] if getattr(field_config, field) is not False),
        "unsafe_application_flag_count": sum(1 for field in policy["application_config_false_defaults"] if getattr(app_config, field) is not False),
        "field_execution_flag_enabled_count": step35_execution_flag_enabled_count(field_config),
        "missing_required_field_count": missing_required_field_count,
        "wall_velocity_config_schema_audit_pass": False,
    }
    summary["wall_velocity_config_schema_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["schema_hash_matches_step70_count"] == summary["required_schema_hash_count"]
        and summary["unsafe_execution_flag_count"] == 0
        and summary["unsafe_application_flag_count"] == 0
        and summary["field_execution_flag_enabled_count"] == 0
        and summary["missing_required_field_count"] == 0
    )
    return rows, summary


def frozen_schema_row(payload: dict, entry: dict) -> dict:
    for row in payload["rows"]:
        if row["canonical_module"] == entry["canonical_module"] and row["class_name"] == entry["class_name"]:
            return row
    return {}


def schema_by_class(rows: list[dict], class_name: str) -> dict:
    for row in rows:
        if row["class_name"] == class_name:
            return row
    return {}


def bool_row(check: str, actual, expected, notes: str) -> dict:
    return {
        "check": check,
        "actual": actual,
        "expected": expected,
        "pass": actual == expected,
        "notes": notes,
    }
