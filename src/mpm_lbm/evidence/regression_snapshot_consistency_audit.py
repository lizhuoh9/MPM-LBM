from __future__ import annotations

import json
from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import read_json
from src.mpm_lbm.evidence.step63_67_regression_guard import build_step63_67_step62_regression_guard


def build_regression_snapshot_consistency_audit(
    root: Path,
    policy_path: str = "configs/step63_regression_snapshot_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    guard_rows, guard_summary = build_step63_67_step62_regression_guard(root)
    rows = [source_artifact_row(root, path) for path in policy["source_artifacts"]]
    rows.append(
        {
            "check": "step63_67_guard_uses_stable_fields",
            "pass": not contains_volatile_key(guard_summary, policy["volatile_keys_not_embedded"]),
            "source_artifact_path": "build_step63_67_step62_regression_guard",
            "stable_field_count": len(guard_summary),
        }
    )
    rows.append(
        {
            "check": "step63_67_guard_rows_pass",
            "pass": all(row["pass"] for row in guard_rows) and guard_summary["step63_67_regression_guard_pass"],
            "source_artifact_path": "build_step63_67_step62_regression_guard",
            "stable_field_count": len(guard_rows),
        }
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "volatile_size_snapshot_embedded": contains_volatile_key(
            guard_summary, policy["volatile_keys_not_embedded"]
        ),
        "regression_snapshot_consistency_pass": False,
    }
    summary["regression_snapshot_consistency_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and not summary["volatile_size_snapshot_embedded"]
    )
    return rows, summary


def source_artifact_row(root: Path, path: str) -> dict:
    artifact_path = root / path
    loaded = False
    stable_field_count = 0
    if artifact_path.is_file():
        payload = read_json(artifact_path)
        loaded = True
        stable_field_count = len(json.dumps(payload, sort_keys=True))
    return {
        "check": "source_artifact_available",
        "pass": loaded,
        "source_artifact_path": path,
        "stable_field_count": stable_field_count,
    }


def contains_volatile_key(payload, volatile_keys: list[str]) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in volatile_keys or contains_volatile_key(value, volatile_keys):
                return True
    if isinstance(payload, list):
        return any(contains_volatile_key(item, volatile_keys) for item in payload)
    return False
