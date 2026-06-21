from __future__ import annotations

import json
from pathlib import Path


def build_step68_step63_67_regression_guard(
    root: Path,
    policy_path: str = "configs/step68_step63_67_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, path) for path in policy["required_artifacts"]]
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "step63_67_required_artifact_count": len(rows),
        "step63_67_pass_count": sum(1 for row in rows if row["pass"]),
        "volatile_size_snapshot_embedded": False,
        "step68_regression_guard_pass": False,
    }
    summary["step68_regression_guard_pass"] = bool(
        summary["row_count"] == summary["pass_count"]
        and summary["step63_67_required_artifact_count"] == summary["step63_67_pass_count"]
        and not summary["volatile_size_snapshot_embedded"]
    )
    return rows, summary


def artifact_row(root: Path, path: str) -> dict:
    artifact_path = root / path
    exists = artifact_path.is_file()
    pass_key = ""
    pass_value = False
    if exists:
        payload = read_json(artifact_path)
        summary = payload.get("summary", payload)
        pass_items = [(key, value) for key, value in summary.items() if key.endswith("_pass")]
        if pass_items:
            pass_key, pass_value = pass_items[-1]
        elif "artifact_budget_pass" in summary:
            pass_key, pass_value = "artifact_budget_pass", bool(summary["artifact_budget_pass"])
    return {
        "source_artifact_path": path,
        "artifact_exists": exists,
        "pass_key": pass_key,
        "pass_value": bool(pass_value),
        "pass": bool(exists and pass_value),
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
