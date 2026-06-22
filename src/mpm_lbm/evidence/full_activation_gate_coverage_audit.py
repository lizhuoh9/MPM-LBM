from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step73_full_activation_gate_coverage_audit(
    root: Path,
    policy_path: str = "configs/step73_full_activation_gate_coverage_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    activation_policy = read_json(root / policy["step70_activation_policy_path"])
    rows = []
    for gate in policy["required_closed_activation_gates"]:
        actual = activation_policy["activation_gates"].get(gate)
        rows.append(
            {
                "check": "activation_gate_closed",
                "gate": gate,
                "actual": actual,
                "expected": False,
                "pass": actual is False,
                "notes": "Step73 full gate coverage keeps Step70 gate closed",
            }
        )
    extra_gates = sorted(set(activation_policy["activation_gates"]) - set(policy["required_closed_activation_gates"]))
    missing_gates = sorted(set(policy["required_closed_activation_gates"]) - set(activation_policy["activation_gates"]))
    rows.extend(
        {
            "check": "unexpected_extra_activation_gate",
            "gate": gate,
            "actual": True,
            "expected": False,
            "pass": False,
            "notes": "Step73 policy must cover every Step70 gate",
        }
        for gate in extra_gates
    )
    rows.extend(
        {
            "check": "missing_activation_gate",
            "gate": gate,
            "actual": False,
            "expected": True,
            "pass": False,
            "notes": "Step70 activation gate missing from artifact",
        }
        for gate in missing_gates
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_gate_count": len(policy["required_closed_activation_gates"]),
        "step70_gate_count": len(activation_policy["activation_gates"]),
        "expected_gate_count": int(policy["expected_gate_count"]),
        "closed_gate_count": sum(1 for row in rows if row["check"] == "activation_gate_closed" and row["actual"] is False),
        "activation_allowed_count": sum(1 for value in activation_policy["activation_gates"].values() if bool(value)),
        "extra_gate_count": len(extra_gates),
        "missing_gate_count": len(missing_gates),
        "full_activation_gate_coverage_audit_pass": False,
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
