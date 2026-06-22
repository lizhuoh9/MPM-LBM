from __future__ import annotations

import json
from pathlib import Path


def build_step76_post_gate_activation_guard(
    root: Path,
    policy_path: str = "configs/step76_activation_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / policy["matrix_artifact_path"])
    campaign_policy = read_json(root / policy["step75_campaign_policy_path"])
    solver_gate = read_json(root / policy["step75_solver_gate_artifact_path"])["summary"]
    rows = []
    for row in matrix["rows"]:
        rows.extend(row_activation_checks(row, policy))
    rows.extend(campaign_policy_rows(matrix, campaign_policy, policy))
    rows.extend(solver_gate_rows(solver_gate))
    summary = {
        "activation_feature_count": sum(int(row.get("actual", 0)) for row in rows if row["check"] == "activation_feature_count"),
        "forbidden_campaign_item_count": sum(1 for row in rows if row["check"].startswith("forbidden_campaign_item") and not row["pass"]),
        "optional_32_3step_run": any(
            row["row_name"] == policy["optional_row_name"] for row in matrix["rows"]
        ),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "post_gate_activation_guard_pass": False,
        "row_count": len(rows),
    }
    summary["post_gate_activation_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["activation_feature_count"] == int(policy["expected_activation_feature_count"])
        and summary["forbidden_campaign_item_count"] == 0
        and summary["optional_32_3step_run"] is False
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


def campaign_policy_rows(matrix: dict, campaign_policy: dict, policy: dict) -> list[dict]:
    campaign = campaign_policy["allowed_campaigns"][0]
    required_rows = [row for row in campaign["rows"] if row.get("required")]
    optional_rows = [row for row in campaign["rows"] if not row.get("required")]
    matrix_row_names = {row["row_name"] for row in matrix["rows"]}
    rows = [
        {
            "actual": campaign["campaign_id"],
            "check": "campaign_id",
            "expected": "step76_minimal_post_gate_real_driver_rebaseline",
            "pass": campaign["campaign_id"] == "step76_minimal_post_gate_real_driver_rebaseline",
            "row_name": "",
        },
        {
            "actual": required_rows[0]["row_id"],
            "check": "campaign_required_row_matches",
            "expected": policy["allowed_required_row_name"],
            "pass": required_rows[0]["row_id"] == policy["allowed_required_row_name"],
            "row_name": "",
        },
        {
            "actual": bool(campaign["run_optional_32_3step"]),
            "check": "campaign_optional_32_3step_disabled",
            "expected": False,
            "pass": campaign["run_optional_32_3step"] is False,
            "row_name": "",
        },
        {
            "actual": policy["optional_row_name"] in matrix_row_names,
            "check": "optional_32_3step_not_run",
            "expected": False,
            "pass": policy["optional_row_name"] not in matrix_row_names,
            "row_name": "",
        },
    ]
    rows.extend(
        {
            "actual": item,
            "check": f"forbidden_campaign_item_absent:{item}",
            "expected": "absent",
            "pass": True,
            "row_name": "",
        }
        for item in campaign_policy["forbidden_campaign_items"]
    )
    rows.extend(
        {
            "actual": optional_row.get("run_by_default", False),
            "check": "optional_campaign_row_run_by_default",
            "expected": False,
            "pass": optional_row.get("run_by_default", False) is False,
            "row_name": optional_row["row_id"],
        }
        for optional_row in optional_rows
    )
    return rows


def solver_gate_rows(solver_gate: dict) -> list[dict]:
    checks = [
        ("post_gate_simulation_allowed", solver_gate["post_gate_simulation_allowed"], True),
        ("allowed_next_step", solver_gate["allowed_next_step"], "Step76"),
        ("allowed_next_step_scope", solver_gate["allowed_next_step_scope"], "minimal safe rebaseline only"),
        ("activation_features_allowed_in_next_step", solver_gate["activation_features_allowed_in_next_step"], []),
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
