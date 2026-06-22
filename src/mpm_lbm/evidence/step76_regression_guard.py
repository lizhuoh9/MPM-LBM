from __future__ import annotations

import json
from pathlib import Path


def build_step76_step75_regression_guard(
    root: Path,
    policy_path: str = "configs/step76_step75_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [artifact_row(root, check) for check in policy["artifact_checks"]]
    rows.extend(artifact_row(root, check) for check in policy["gate_checks"])
    summary = {
        "artifact_check_count": len(policy["artifact_checks"]),
        "artifact_pass_count": sum(1 for row in rows[: len(policy["artifact_checks"])] if row["pass"]),
        "gate_check_count": len(policy["gate_checks"]),
        "gate_pass_count": sum(1 for row in rows[len(policy["artifact_checks"]) :] if row["pass"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "step76_step75_regression_guard_pass": False,
    }
    summary["step76_step75_regression_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["artifact_pass_count"] == summary["artifact_check_count"]
        and summary["gate_pass_count"] == summary["gate_check_count"]
    )
    return rows, summary


def artifact_row(root: Path, check: dict) -> dict:
    payload = read_json(root / check["artifact_path"])
    actual = payload.get("summary", payload).get(check["summary_key"])
    return {
        "actual": actual,
        "artifact_path": check["artifact_path"],
        "check": check["check"],
        "expected": check["expected"],
        "pass": actual == check["expected"],
        "summary_key": check["summary_key"],
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
