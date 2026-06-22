from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step75_activation_gate_closure_audit(
    root: Path,
    policy_path: str = "configs/step75_activation_gate_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    activation_policy = read_json(root / policy["gate_source_policy"])
    rows = []
    for gate in policy["required_closed_activation_gates"]:
        actual = activation_policy["activation_gates"].get(gate)
        rows.append(
            {
                "actual": actual,
                "check": "activation_gate_closed",
                "expected": False,
                "gate": gate,
                "latest_step_checked": policy["latest_step_checked"],
                "pass": actual is False,
            }
        )
    extra_gates = sorted(set(activation_policy["activation_gates"]) - set(policy["required_closed_activation_gates"]))
    missing_gates = sorted(set(policy["required_closed_activation_gates"]) - set(activation_policy["activation_gates"]))
    rows.extend(extra_gate_row(gate, policy) for gate in extra_gates)
    rows.extend(missing_gate_row(gate, policy) for gate in missing_gates)
    summary = {
        "activation_allowed_count": sum(1 for value in activation_policy["activation_gates"].values() if bool(value)),
        "activation_gate_closure_audit_pass": False,
        "closed_gate_count": sum(
            1 for row in rows if row["check"] == "activation_gate_closed" and row["actual"] is False
        ),
        "expected_gate_count": int(policy["expected_gate_count"]),
        "extra_gate_count": len(extra_gates),
        "gate_source_policy": policy["gate_source_policy"],
        "latest_step_checked": policy["latest_step_checked"],
        "missing_gate_count": len(missing_gates),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_gate_count": len(policy["required_closed_activation_gates"]),
        "row_count": len(rows),
    }
    summary["activation_gate_closure_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["required_gate_count"] == summary["expected_gate_count"]
        and summary["closed_gate_count"] == summary["expected_gate_count"]
        and summary["activation_allowed_count"] == 0
        and summary["extra_gate_count"] == 0
        and summary["missing_gate_count"] == 0
    )
    return rows, summary


def extra_gate_row(gate: str, policy: dict) -> dict:
    return {
        "actual": True,
        "check": "unexpected_extra_activation_gate",
        "expected": False,
        "gate": gate,
        "latest_step_checked": policy["latest_step_checked"],
        "pass": False,
    }


def missing_gate_row(gate: str, policy: dict) -> dict:
    return {
        "actual": False,
        "check": "missing_activation_gate",
        "expected": True,
        "gate": gate,
        "latest_step_checked": policy["latest_step_checked"],
        "pass": False,
    }
