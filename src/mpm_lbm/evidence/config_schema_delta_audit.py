from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.config_schema_freeze_audit import schema_row
from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step71_config_schema_delta_audit(
    root: Path,
    policy_path: str = "configs/step71_config_schema_delta_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    step70_policy = read_json(root / policy["step70_config_schema_policy_path"])
    step70_artifact = read_json(root / policy["step70_schema_freeze_artifact_path"])
    previous_rows = {row["class_name"]: row for row in step70_artifact["rows"]}
    current_rows = [schema_row(entry) for entry in step70_policy["required_config_classes"]]
    expected_changed = set(policy["expected_changed_schema_classes"])
    expected_unchanged = set(policy["expected_unchanged_schema_classes"])
    rows = [
        delta_row(row, previous_rows.get(row["class_name"], {}), expected_changed, expected_unchanged, policy)
        for row in current_rows
    ]
    changed_schema_classes = sorted(row["class_name"] for row in rows if row["schema_hash_changed"])
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "changed_schema_classes": changed_schema_classes,
        "expected_changed_schema_classes": sorted(expected_changed),
        "unexpected_changed_schema_count": sum(1 for row in rows if row["schema_hash_changed"] and not row["expected_changed"]),
        "missing_expected_changed_schema_count": len(expected_changed.difference(changed_schema_classes)),
        "unchanged_schema_classes_checked": sorted(expected_unchanged),
        "fsidriver_write_vtk_default_previous": previous_rows.get("FSIDriverConfig", {}).get("default_values_repr", {}).get("write_vtk", ""),
        "fsidriver_write_vtk_default_current": next_default(current_rows, "FSIDriverConfig", "write_vtk"),
        "fsidriver_write_particles_default_previous": previous_rows.get("FSIDriverConfig", {}).get("default_values_repr", {}).get("write_particles", ""),
        "fsidriver_write_particles_default_current": next_default(current_rows, "FSIDriverConfig", "write_particles"),
        "config_schema_delta_audit_pass": False,
    }
    summary["config_schema_delta_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["changed_schema_classes"] == summary["expected_changed_schema_classes"]
        and summary["unexpected_changed_schema_count"] == 0
        and summary["missing_expected_changed_schema_count"] == 0
        and summary["fsidriver_write_vtk_default_previous"] == "True"
        and summary["fsidriver_write_vtk_default_current"] == "False"
        and summary["fsidriver_write_particles_default_previous"] == "True"
        and summary["fsidriver_write_particles_default_current"] == "False"
    )
    return rows, summary


def delta_row(current: dict, previous: dict, expected_changed: set[str], expected_unchanged: set[str], policy: dict) -> dict:
    class_name = current["class_name"]
    previous_hash = previous.get("schema_hash", "")
    current_hash = current.get("schema_hash", "")
    schema_hash_changed = bool(previous_hash and current_hash and previous_hash != current_hash)
    previous_defaults = previous.get("default_values_repr", {})
    current_defaults = current.get("default_values_repr", {})
    changed_default_fields = sorted(
        field
        for field in set(previous_defaults).union(current_defaults)
        if previous_defaults.get(field) != current_defaults.get(field)
    )
    expected_field_deltas = policy["expected_field_default_deltas"].get(class_name, {})
    field_delta_pass = True
    for field, expected in expected_field_deltas.items():
        field_delta_pass = field_delta_pass and previous_defaults.get(field) == expected["previous"]
        field_delta_pass = field_delta_pass and current_defaults.get(field) == expected["current"]
    expected_changed_class = class_name in expected_changed
    expected_unchanged_class = class_name in expected_unchanged
    passed = bool(
        previous
        and current["pass"]
        and schema_hash_changed is expected_changed_class
        and field_delta_pass
        and (expected_changed_class or expected_unchanged_class)
    )
    return {
        "class_name": class_name,
        "canonical_module": current["canonical_module"],
        "previous_schema_hash": previous_hash,
        "current_schema_hash": current_hash,
        "schema_hash_changed": schema_hash_changed,
        "expected_changed": expected_changed_class,
        "expected_unchanged": expected_unchanged_class,
        "changed_default_fields": changed_default_fields,
        "field_delta_pass": field_delta_pass,
        "pass": passed,
    }


def next_default(rows: list[dict], class_name: str, field: str) -> str:
    for row in rows:
        if row["class_name"] == class_name:
            return row["default_values_repr"].get(field, "")
    return ""
