from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step75_step74_regression_guard(
    root: Path,
    policy_path: str = "configs/step75_step74_regression_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    artifact_check_names = {check["check"] for check in policy["step74_artifact_checks"]}
    rows = [artifact_row(root, check) for check in policy["step74_artifact_checks"]]
    activation_policy = read_json(root / policy["step70_activation_policy_path"])
    for gate in policy["required_closed_activation_gates"]:
        actual = activation_policy["activation_gates"].get(gate)
        rows.append(
            {
                "actual": actual,
                "check": f"{gate}_still_closed",
                "expected": False,
                "pass": actual is False,
                "summary_key": gate,
            }
        )
    summary = {
        "closed_gate_pass_count": sum(
            1 for row in rows if row["summary_key"] in policy["required_closed_activation_gates"] and row["pass"]
        ),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_closed_gate_count": len(policy["required_closed_activation_gates"]),
        "row_count": len(rows),
        "step74_artifact_check_count": len(policy["step74_artifact_checks"]),
        "step74_artifact_pass_count": sum(1 for row in rows if row["check"] in artifact_check_names and row["pass"]),
        "step75_step74_regression_guard_pass": False,
    }
    summary["step75_step74_regression_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["step74_artifact_pass_count"] == summary["step74_artifact_check_count"]
        and summary["closed_gate_pass_count"] == summary["required_closed_gate_count"]
    )
    return rows, summary


def artifact_row(root: Path, check: dict) -> dict:
    payload = read_json(root / check["artifact_path"])
    actual = payload.get("summary", payload).get(check["summary_key"])
    return {
        "actual": actual,
        "check": check["check"],
        "expected": check["expected"],
        "pass": actual == check["expected"],
        "summary_key": check["summary_key"],
    }
