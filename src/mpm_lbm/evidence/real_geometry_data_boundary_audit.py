from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step74_real_geometry_data_boundary_audit(
    root: Path,
    policy_path: str = "configs/step74_real_geometry_data_boundary_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = [required_audit_row(root, audit) for audit in policy["required_audits"]]
    activation_policy = read_json(root / policy["step70_activation_policy_path"])
    activation_allowed = activation_policy["activation_gates"].get(policy["activation_gate"])
    rows.append(
        {
            "actual": activation_allowed,
            "check": "activation_allowed_after_step74",
            "expected": False,
            "name": policy["activation_gate"],
            "notes": policy["readiness_claim"],
            "pass": activation_allowed is False,
            "summary_key": "",
        }
    )
    summary = {
        "activation_allowed_after_step74": bool(activation_allowed),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "readiness_claim": policy["readiness_claim"],
        "real_geometry_data_boundary_audit_pass": False,
        "required_audit_count": len(policy["required_audits"]),
        "required_audit_pass_count": sum(
            1 for row in rows if row["check"] == "required_audit_pass" and row["pass"]
        ),
        "row_count": len(rows),
    }
    summary["real_geometry_data_boundary_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["required_audit_pass_count"] == summary["required_audit_count"]
        and summary["activation_allowed_after_step74"] is False
    )
    return rows, summary


def required_audit_row(root: Path, audit: dict) -> dict:
    payload = read_json(root / audit["artifact_path"])
    actual = payload["summary"].get(audit["summary_key"])
    return {
        "actual": actual,
        "check": "required_audit_pass",
        "expected": True,
        "name": audit["audit_name"],
        "notes": "Step74 real geometry data boundary component must be green",
        "pass": actual is True,
        "summary_key": audit["summary_key"],
    }
