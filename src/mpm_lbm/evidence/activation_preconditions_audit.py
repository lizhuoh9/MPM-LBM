from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step70_activation_preconditions_audit(
    root: Path,
    policy_path: str = "configs/step70_activation_preconditions_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [
        {
            "check": "activation_gate_closed",
            "gate": gate,
            "allowed": bool(value),
            "pass": value is False,
            "notes": "Step70 freeze keeps activation closed",
        }
        for gate, value in sorted(policy["activation_gates"].items())
    ]
    rows.extend(
        {
            "check": "pending_gate_reason_recorded",
            "gate": "",
            "allowed": "",
            "pass": bool(reason),
            "notes": reason,
        }
        for reason in policy["pending_gate_reasons"]
    )
    summary = {
        "row_count": len(rows),
        "activation_gate_count": len(policy["activation_gates"]),
        "activation_allowed_count": sum(1 for value in policy["activation_gates"].values() if bool(value)),
        "pending_gate_count": len(policy["pending_gate_reasons"]),
        "activation_preconditions_audit_pass": False,
    }
    summary["activation_preconditions_audit_pass"] = bool(
        summary["activation_allowed_count"] == 0
        and summary["pending_gate_count"] >= 5
        and all(row["pass"] for row in rows)
    )
    return rows, summary


def write_activation_docs(rows: list[dict], summary: dict) -> str:
    lines = [
        "# Activation Preconditions",
        "",
        "Step70 keeps every activation gate closed before later readiness steps.",
        "",
        "```text",
        f"activation_preconditions_audit_pass = {summary['activation_preconditions_audit_pass']}",
        f"activation_allowed_count = {summary['activation_allowed_count']}",
        f"pending_gate_count = {summary['pending_gate_count']}",
        "```",
        "",
    ]
    for row in rows:
        if row["check"] == "activation_gate_closed":
            lines.append(f"- `{row['gate']}` = `{row['allowed']}`")
        else:
            lines.append(f"- {row['notes']}")
    return "\n".join(lines).rstrip() + "\n"
