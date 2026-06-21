from __future__ import annotations

import importlib
import json
from pathlib import Path


def build_optional_bridge_audit(
    root: Path,
    policy_path: str = "configs/step58_optional_bridge_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before_outputs = output_snapshot(root)
    rows = [bridge_row(root, bridge) for bridge in policy["bridges"]]
    after_outputs = output_snapshot(root)
    output_snapshot_unchanged = before_outputs == after_outputs
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "bridge_file_count": sum(1 for row in rows if row["bridge_file_exists"]),
        "temporary_marker_count": sum(1 for row in rows if row["temporary_marker_present"]),
        "legacy_getattr_bridge_count": sum(1 for row in rows if row["uses_legacy_getattr"]),
        "bridge_retired_count": sum(1 for row in rows if row["bridge_retired"]),
        "active_temporary_bridge_count": sum(1 for row in rows if row["temporary_bridge_active"]),
        "same_object_symbol_count": sum(int(row["same_object_symbol_count"]) for row in rows),
        "symbol_count": sum(int(row["symbol_count"]) for row in rows),
        "output_snapshot_unchanged": output_snapshot_unchanged,
        "bridge_is_temporary_until_step59": bool(policy["bridge_is_temporary_until_step59"]),
        "solver_run": False,
        "optional_bridge_audit_pass": False,
    }
    summary["optional_bridge_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["same_object_symbol_count"] == summary["symbol_count"]
        and output_snapshot_unchanged
        and summary["bridge_is_temporary_until_step59"]
        and not summary["solver_run"]
    )
    return rows, summary


def bridge_row(root: Path, bridge: dict) -> dict:
    path = root / bridge["canonical_path"]
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    errors: list[str] = []
    canonical_module_obj = None
    legacy_module_obj = None
    canonical_import_pass = False
    legacy_import_pass = False
    try:
        canonical_module_obj = importlib.import_module(bridge["canonical_module"])
        canonical_import_pass = True
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        errors.append(f"canonical_import_error={type(exc).__name__}: {exc}")
    try:
        legacy_module_obj = importlib.import_module(bridge["legacy_module"])
        legacy_import_pass = True
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        errors.append(f"legacy_import_error={type(exc).__name__}: {exc}")

    same_object_symbol_count = 0
    resolved_symbol_count = 0
    for symbol in bridge["symbols"]:
        try:
            canonical_obj = getattr(canonical_module_obj, symbol) if canonical_module_obj is not None else None
            legacy_obj = getattr(legacy_module_obj, symbol) if legacy_module_obj is not None else None
            resolved = canonical_obj is not None and legacy_obj is not None
            resolved_symbol_count += int(resolved)
            same_object_symbol_count += int(resolved and canonical_obj is legacy_obj)
        except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
            errors.append(f"{symbol}_error={type(exc).__name__}: {exc}")

    temporary_marker_present = bool(
        "Implementation remains legacy until Step 59" in text
        and "BRIDGE_IS_TEMPORARY_UNTIL_STEP59 = True" in text
    )
    all_symbols_listed = all(f'"{symbol}"' in text for symbol in bridge["symbols"])
    uses_legacy_getattr = "legacy_getattr" in text and "_LEGACY_MODULE" in text
    legacy_module_declared = bridge["legacy_module"] in text
    temporary_bridge_active = bool(
        path.is_file()
        and temporary_marker_present
        and all_symbols_listed
        and uses_legacy_getattr
        and legacy_module_declared
        and canonical_import_pass
        and legacy_import_pass
        and resolved_symbol_count == len(bridge["symbols"])
        and same_object_symbol_count == len(bridge["symbols"])
    )
    bridge_retired = bool(
        path.is_file()
        and not temporary_marker_present
        and not uses_legacy_getattr
        and canonical_import_pass
        and legacy_import_pass
        and resolved_symbol_count == len(bridge["symbols"])
        and same_object_symbol_count == len(bridge["symbols"])
    )
    passed = bool(temporary_bridge_active or bridge_retired)
    return {
        "canonical_path": bridge["canonical_path"],
        "canonical_module": bridge["canonical_module"],
        "legacy_module": bridge["legacy_module"],
        "symbol_count": len(bridge["symbols"]),
        "bridge_file_exists": path.is_file(),
        "temporary_marker_present": temporary_marker_present,
        "uses_legacy_getattr": uses_legacy_getattr,
        "temporary_bridge_active": temporary_bridge_active,
        "bridge_retired": bridge_retired,
        "legacy_module_declared": legacy_module_declared,
        "all_symbols_listed": all_symbols_listed,
        "canonical_import_pass": canonical_import_pass,
        "legacy_import_pass": legacy_import_pass,
        "resolved_symbol_count": resolved_symbol_count,
        "same_object_symbol_count": same_object_symbol_count,
        "pass": passed,
        "error": "; ".join(errors),
    }


def output_snapshot(root: Path) -> list[tuple[str, int]]:
    output_root = root / "outputs"
    if not output_root.exists():
        return []
    return sorted(
        (path.relative_to(root).as_posix(), int(path.stat().st_size))
        for path in output_root.rglob("*")
        if path.is_file()
    )


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
