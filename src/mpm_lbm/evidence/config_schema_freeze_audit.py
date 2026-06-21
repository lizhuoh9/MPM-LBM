from __future__ import annotations

import dataclasses
import hashlib
import importlib
import inspect
import json
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step70_config_schema_freeze_audit(
    root: Path,
    policy_path: str = "configs/step70_config_schema_freeze_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [schema_row(entry) for entry in policy["required_config_classes"]]
    summary = {
        "row_count": len(rows),
        "schema_row_count": len(rows),
        "required_config_class_count": len(policy["required_config_classes"]),
        "missing_config_class_count": sum(1 for row in rows if not row["class_import_pass"]),
        "schema_hash_count": sum(1 for row in rows if bool(row["schema_hash"])),
        "from_json_available_count": sum(1 for row in rows if row["from_json_available"]),
        "to_json_or_to_dict_available_count": sum(1 for row in rows if row["to_json_or_to_dict_available"]),
        "config_schema_freeze_audit_pass": False,
    }
    summary["config_schema_freeze_audit_pass"] = bool(
        rows
        and summary["missing_config_class_count"] == 0
        and summary["schema_hash_count"] == summary["schema_row_count"]
        and all(row["pass"] for row in rows)
    )
    return rows, summary


def schema_row(entry: dict) -> dict:
    error = ""
    cls = None
    class_import_pass = False
    try:
        module = importlib.import_module(entry["canonical_module"])
        cls = getattr(module, entry["class_name"])
        class_import_pass = True
    except Exception as exc:  # pragma: no cover - artifact row captures details
        error = f"{type(exc).__name__}: {exc}"
    is_dataclass = bool(cls is not None and dataclasses.is_dataclass(cls))
    init_signature = ""
    fields_or_params: list[str] = []
    default_values: dict[str, str] = {}
    from_json_available = False
    to_json_or_to_dict_available = False
    if cls is not None:
        init_signature = str(inspect.signature(cls))
        if is_dataclass:
            for field in dataclasses.fields(cls):
                fields_or_params.append(field.name)
                default_values[field.name] = default_repr(field)
        else:
            params = inspect.signature(cls).parameters
            fields_or_params = [name for name in params if name != "self"]
            default_values = {
                name: repr(param.default)
                for name, param in params.items()
                if name != "self" and param.default is not inspect._empty
            }
        from_json_available = hasattr(cls, "from_json")
        to_json_or_to_dict_available = any(hasattr(cls, name) for name in ("to_json", "to_dict"))
    hash_payload = {
        "class_name": entry["class_name"],
        "canonical_module": entry["canonical_module"],
        "is_dataclass": is_dataclass,
        "init_signature": init_signature,
        "public_fields_or_constructor_params": fields_or_params,
        "default_values_repr": default_values,
        "from_json_available": from_json_available,
        "to_json_or_to_dict_available": to_json_or_to_dict_available,
    }
    schema_hash = hashlib.sha256(json.dumps(hash_payload, sort_keys=True).encode("utf-8")).hexdigest() if class_import_pass else ""
    passed = bool(class_import_pass and schema_hash and fields_or_params)
    return {
        **hash_payload,
        "class_import_pass": class_import_pass,
        "schema_hash": schema_hash,
        "pass": passed,
        "error": error,
    }


def default_repr(field) -> str:
    if field.default is not dataclasses.MISSING:
        return repr(field.default)
    if field.default_factory is not dataclasses.MISSING:  # type: ignore[attr-defined]
        return "<default_factory>"
    return "<required>"


def write_config_schema_docs(rows: list[dict], summary: dict) -> str:
    lines = [
        "# Config Schema Freeze",
        "",
        "Step70 records constructor/dataclass schema fingerprints for required config classes.",
        "",
        "```text",
        f"config_schema_freeze_audit_pass = {summary['config_schema_freeze_audit_pass']}",
        f"schema_row_count = {summary['schema_row_count']}",
        f"missing_config_class_count = {summary['missing_config_class_count']}",
        "```",
        "",
        "| Class | Module | Dataclass | Schema Hash |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['class_name']}` | `{row['canonical_module']}` | `{row['is_dataclass']}` | `{row['schema_hash']}` |"
        )
    return "\n".join(lines).rstrip() + "\n"
