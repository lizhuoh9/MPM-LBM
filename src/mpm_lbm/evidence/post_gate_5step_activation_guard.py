from __future__ import annotations

import json
from pathlib import Path


def build_step78_post_gate_5step_activation_guard(
    root: Path,
    policy_path: str = "configs/step78_activation_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / policy["matrix_artifact_path"])
    previous_matrix = read_json(root / policy["previous_matrix_artifact_path"])
    rows = []
    for row in matrix["rows"]:
        rows.extend(row_activation_checks(row, policy))
    rows.extend(matrix_summary_checks(matrix["summary"], policy))
    rows.extend(previous_matrix_summary_checks(previous_matrix["summary"]))
    summary = {
        "activation_feature_count": sum(int(row.get("actual", 0)) for row in rows if row["check"] == "activation_feature_count"),
        "optional_row_count": matrix["summary"]["optional_row_count"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "post_gate_5step_activation_guard_pass": False,
        "previous_activation_feature_count": previous_matrix["summary"]["activation_feature_count"],
        "row_count": len(rows),
    }
    summary["post_gate_5step_activation_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["activation_feature_count"] == int(policy["expected_activation_feature_count"])
        and summary["previous_activation_feature_count"] == 0
        and summary["optional_row_count"] == 0
    )
    return rows, summary


def row_activation_checks(row: dict, policy: dict) -> list[dict]:
    rows = [
        {
            "actual": row["row_name"],
            "check": "allowed_required_row_name",
            "expected": policy["allowed_required_row_name"],
            "pass": row["row_name"] == policy["allowed_required_row_name"],
            "row_name": row["row_name"],
        },
        {
            "actual": int(row["activation_feature_count"]),
            "check": "activation_feature_count",
            "expected": int(policy["expected_activation_feature_count"]),
            "pass": int(row["activation_feature_count"]) == int(policy["expected_activation_feature_count"]),
            "row_name": row["row_name"],
        },
    ]
    for flag in policy["activation_features_must_be_false"]:
        rows.append(
            {
                "actual": bool(row[flag]),
                "check": flag,
                "expected": False,
                "pass": row[flag] is False,
                "row_name": row["row_name"],
            }
        )
    return rows


def matrix_summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("post_gate_5step_rebaseline_matrix_pass", summary["post_gate_5step_rebaseline_matrix_pass"], True),
        ("allowed_next_step", summary["allowed_next_step"], "Step78"),
        (
            "allowed_next_step_scope",
            summary["allowed_next_step_scope"],
            "minimal post-gate canonical driver 5-step rebaseline only",
        ),
        ("previous_rebaseline_step", summary["previous_rebaseline_step"], "Step77"),
        ("optional_row_count", summary["optional_row_count"], 0),
        ("runtime_hard_fail_count", summary["runtime_hard_fail_count"], 0),
        ("required_rows_present", summary["required_rows_present"], [policy["allowed_required_row_name"]]),
    ]
    return [
        {
            "actual": actual,
            "check": check,
            "expected": expected,
            "pass": actual == expected,
            "row_name": "",
        }
        for check, actual, expected in checks
    ]


def previous_matrix_summary_checks(summary: dict) -> list[dict]:
    checks = [
        ("step77_matrix_pass", summary["post_gate_3step_rebaseline_matrix_pass"], True),
        ("step77_activation_feature_count", summary["activation_feature_count"], 0),
        ("step77_optional_row_count", summary["optional_row_count"], 0),
    ]
    return [
        {
            "actual": actual,
            "check": check,
            "expected": expected,
            "pass": actual == expected,
            "row_name": "",
        }
        for check, actual, expected in checks
    ]


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
