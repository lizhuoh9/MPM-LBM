from __future__ import annotations

import importlib
import json
from pathlib import Path


def build_fsidriver_import_execution_audit(
    root: Path,
    policy_path: str = "configs/step58_driver_import_execution_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    before_outputs = output_snapshot(root)
    rows = [symbol_import_row(pair) for pair in policy["symbol_pairs"]]
    rows.extend(bridge_import_row(item) for item in policy["bridge_imports"])
    after_outputs = output_snapshot(root)
    output_snapshot_unchanged = before_outputs == after_outputs
    pair_rows = [row for row in rows if row["row_kind"] == "symbol_pair"]
    bridge_rows = [row for row in rows if row["row_kind"] == "bridge_import"]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "symbol_pair_row_count": len(pair_rows),
        "symbol_pair_pass_count": sum(1 for row in pair_rows if row["pass"]),
        "bridge_import_row_count": len(bridge_rows),
        "bridge_import_pass_count": sum(1 for row in bridge_rows if row["pass"]),
        "canonical_import_pass_count": sum(1 for row in rows if row["canonical_import_pass"]),
        "legacy_import_pass_count": sum(1 for row in pair_rows if row["legacy_import_pass"]),
        "identity_pair_count": sum(1 for row in pair_rows if row["comparison"] == "identity"),
        "same_object_count": sum(1 for row in pair_rows if row["same_object"] is True),
        "equality_pair_count": sum(1 for row in pair_rows if row["comparison"] == "equality"),
        "equal_value_count": sum(1 for row in pair_rows if row["equal_value"] is True),
        "output_snapshot_unchanged": output_snapshot_unchanged,
        "solver_run": False,
        "runtime_object_construction_required": False,
        "no_output_writes": output_snapshot_unchanged,
        "fsidriver_import_execution_audit_pass": False,
    }
    summary["fsidriver_import_execution_audit_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["symbol_pair_row_count"] == 2
        and summary["bridge_import_row_count"] == 4
        and output_snapshot_unchanged
        and not summary["solver_run"]
        and not summary["runtime_object_construction_required"]
    )
    return rows, summary


def symbol_import_row(pair: dict) -> dict:
    error = ""
    canonical_obj = None
    legacy_obj = None
    canonical_import_pass = False
    legacy_import_pass = False
    try:
        canonical_module = importlib.import_module(pair["canonical_module"])
        canonical_obj = getattr(canonical_module, pair["symbol"])
        canonical_import_pass = True
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        error = f"canonical_import_error={type(exc).__name__}: {exc}"
    try:
        legacy_module = importlib.import_module(pair["legacy_module"])
        legacy_obj = getattr(legacy_module, pair["symbol"])
        legacy_import_pass = True
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        error = join_error(error, f"legacy_import_error={type(exc).__name__}: {exc}")
    same_object = bool(canonical_import_pass and legacy_import_pass and canonical_obj is legacy_obj)
    equal_value = bool(canonical_import_pass and legacy_import_pass and canonical_obj == legacy_obj)
    if pair["comparison"] == "identity":
        passed = same_object
    elif pair["comparison"] == "equality":
        passed = equal_value
    else:
        passed = False
        error = join_error(error, f"unsupported_comparison={pair['comparison']}")
    return {
        "row_kind": "symbol_pair",
        "canonical_module": pair["canonical_module"],
        "legacy_module": pair["legacy_module"],
        "symbol": pair["symbol"],
        "comparison": pair["comparison"],
        "canonical_import_pass": canonical_import_pass,
        "legacy_import_pass": legacy_import_pass,
        "same_object": same_object,
        "equal_value": equal_value,
        "pass": bool(canonical_import_pass and legacy_import_pass and passed),
        "error": error,
    }


def bridge_import_row(item: dict) -> dict:
    error = ""
    canonical_import_pass = False
    canonical_obj = None
    try:
        canonical_module = importlib.import_module(item["canonical_module"])
        canonical_obj = getattr(canonical_module, item["symbol"])
        canonical_import_pass = callable(canonical_obj)
    except Exception as exc:  # pragma: no cover - surfaced in audit artifacts
        error = f"bridge_import_error={type(exc).__name__}: {exc}"
    return {
        "row_kind": "bridge_import",
        "canonical_module": item["canonical_module"],
        "legacy_module": "",
        "symbol": item["symbol"],
        "comparison": "import_only",
        "canonical_import_pass": canonical_import_pass,
        "legacy_import_pass": "",
        "same_object": "",
        "equal_value": "",
        "pass": canonical_import_pass,
        "error": error,
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


def join_error(existing: str, new: str) -> str:
    if existing:
        return f"{existing}; {new}"
    return new


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
