from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.config_schema_freeze_audit import schema_row
from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.sim.runtime_geometry.projection_config import (
    RuntimeGeometryProjectionIntegrationConfig,
    mutation_flag_enabled_count,
    mutation_flags,
)


def build_step72_runtime_geometry_config_schema_audit(
    root: Path,
    policy_path: str = "configs/step72_runtime_geometry_config_schema_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    current = schema_row(policy["required_config_class"])
    frozen = frozen_schema_row(root, policy)
    config = RuntimeGeometryProjectionIntegrationConfig.from_json(root / policy["runtime_projection_config_path"])
    rows: list[dict] = [
        bool_row("class_import_pass", current["class_import_pass"], True, "Runtime geometry projection config imports"),
        bool_row("schema_hash_matches_step70", current["schema_hash"], frozen.get("schema_hash", ""), "Step70 schema hash remains stable"),
        bool_row("schema_hash_matches_policy", current["schema_hash"], policy["expected_step70_schema_hash"], "Policy pins Step70 schema hash"),
        bool_row("from_json_available", current["from_json_available"], True, "Config remains loadable from JSON"),
        bool_row("to_json_or_to_dict_available", current["to_json_or_to_dict_available"], True, "Config remains serializable"),
        bool_row("integration_mode", config.integration_mode, policy["expected_integration_mode"], "Runtime projection remains transient only"),
        bool_row("diagnostic_only_config", config.diagnostic_only, policy["expected_diagnostic_only"], "Runtime projection config remains diagnostic-only"),
        bool_row("mutation_flag_enabled_count", mutation_flag_enabled_count(config), 0, "No mutation or persistence flag enabled"),
    ]
    defaults = current["default_values_repr"]
    rows.extend(
        bool_row(f"default_false_{field}", defaults.get(field), "False", "Runtime geometry unsafe default must remain false")
        for field in policy["required_false_defaults"]
    )
    rows.extend(
        bool_row(f"default_true_{field}", defaults.get(field), "True", "Required diagnostic default must remain true")
        for field in policy["required_true_defaults"]
    )
    flags = mutation_flags(config)
    rows.extend(
        bool_row(f"config_flag_false_{field}", flags.get(field), False, "Committed Step45 runtime projection config must remain non-mutating")
        for field in policy["required_false_defaults"]
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "current_schema_hash": current["schema_hash"],
        "step70_schema_hash": frozen.get("schema_hash", ""),
        "schema_hash_matches_step70": current["schema_hash"] == frozen.get("schema_hash", ""),
        "required_false_default_count": len(policy["required_false_defaults"]),
        "unsafe_default_true_count": sum(1 for field in policy["required_false_defaults"] if defaults.get(field) != "False"),
        "required_true_default_count": len(policy["required_true_defaults"]),
        "missing_required_field_count": sum(
            1
            for field in [*policy["required_false_defaults"], *policy["required_true_defaults"]]
            if field not in current["public_fields_or_constructor_params"]
        ),
        "config_mutation_flag_enabled_count": mutation_flag_enabled_count(config),
        "runtime_geometry_config_schema_audit_pass": False,
    }
    summary["runtime_geometry_config_schema_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["schema_hash_matches_step70"]
        and summary["unsafe_default_true_count"] == 0
        and summary["missing_required_field_count"] == 0
        and summary["config_mutation_flag_enabled_count"] == 0
    )
    return rows, summary


def frozen_schema_row(root: Path, policy: dict) -> dict:
    payload = read_json(root / policy["step70_config_schema_artifact_path"])
    expected = policy["required_config_class"]
    for row in payload["rows"]:
        if row["canonical_module"] == expected["canonical_module"] and row["class_name"] == expected["class_name"]:
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
