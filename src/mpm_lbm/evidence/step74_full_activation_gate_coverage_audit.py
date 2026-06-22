from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step74_full_activation_gate_coverage_audit(
    root: Path,
    policy_path: str = "configs/step74_full_activation_gate_coverage_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    activation_policy = read_json(root / policy["step70_activation_policy_path"])
    rows = []
    for gate in policy["required_closed_activation_gates"]:
        actual = activation_policy["activation_gates"].get(gate)
        rows.append(
            {
                "actual": actual,
                "check": "activation_gate_closed",
                "expected": False,
                "gate": gate,
                "notes": "Step74 keeps every Step70 activation gate closed",
                "pass": actual is False,
            }
        )
    extra_gates = sorted(set(activation_policy["activation_gates"]) - set(policy["required_closed_activation_gates"]))
    missing_gates = sorted(set(policy["required_closed_activation_gates"]) - set(activation_policy["activation_gates"]))
    rows.extend(extra_gate_row(gate) for gate in extra_gates)
    rows.extend(missing_gate_row(gate) for gate in missing_gates)
    summary = {
        "activation_allowed_count": sum(1 for value in activation_policy["activation_gates"].values() if bool(value)),
        "closed_gate_count": sum(
            1 for row in rows if row["check"] == "activation_gate_closed" and row["actual"] is False
        ),
        "expected_gate_count": int(policy["expected_gate_count"]),
        "extra_gate_count": len(extra_gates),
        "full_activation_gate_coverage_audit_pass": False,
        "missing_gate_count": len(missing_gates),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_gate_count": len(policy["required_closed_activation_gates"]),
        "row_count": len(rows),
        "step70_gate_count": len(activation_policy["activation_gates"]),
    }
    summary["full_activation_gate_coverage_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["required_gate_count"] == summary["expected_gate_count"]
        and summary["step70_gate_count"] == summary["expected_gate_count"]
        and summary["closed_gate_count"] == summary["expected_gate_count"]
        and summary["activation_allowed_count"] == 0
        and summary["extra_gate_count"] == 0
        and summary["missing_gate_count"] == 0
    )
    return rows, summary


def extra_gate_row(gate: str) -> dict:
    return {
        "actual": True,
        "check": "unexpected_extra_activation_gate",
        "expected": False,
        "gate": gate,
        "notes": "Step74 policy must cover every Step70 gate",
        "pass": False,
    }


def missing_gate_row(gate: str) -> dict:
    return {
        "actual": False,
        "check": "missing_activation_gate",
        "expected": True,
        "gate": gate,
        "notes": "Step70 activation gate missing from artifact",
        "pass": False,
    }
