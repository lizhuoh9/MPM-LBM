from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.evidence.runtime_geometry_api_audit import build_step72_runtime_geometry_api_audit
from src.mpm_lbm.evidence.runtime_geometry_config_schema_audit import build_step72_runtime_geometry_config_schema_audit
from src.mpm_lbm.evidence.runtime_geometry_driver_gate_audit import build_step72_runtime_geometry_driver_gate_audit
from src.mpm_lbm.evidence.runtime_geometry_output_policy_audit import build_step72_runtime_geometry_output_policy_audit
from src.mpm_lbm.evidence.runtime_geometry_state_guard_audit import build_step72_runtime_geometry_state_guard_audit


AUDIT_BUILDERS = {
    "runtime_geometry_api_audit": build_step72_runtime_geometry_api_audit,
    "runtime_geometry_config_schema_audit": build_step72_runtime_geometry_config_schema_audit,
    "runtime_geometry_driver_gate_audit": build_step72_runtime_geometry_driver_gate_audit,
    "runtime_geometry_state_guard_audit": build_step72_runtime_geometry_state_guard_audit,
    "runtime_geometry_output_policy_audit": build_step72_runtime_geometry_output_policy_audit,
}


def build_step72_runtime_geometry_readiness_audit(
    root: Path,
    policy_path: str = "configs/step72_runtime_geometry_readiness_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    activation_policy = read_json(root / policy["step70_activation_policy_path"])
    rows = []
    audit_pass_count = 0
    for entry in policy["required_audits"]:
        summary = AUDIT_BUILDERS[entry["name"]](root)[1]
        actual = summary.get(entry["summary_key"])
        if actual is True:
            audit_pass_count += 1
        rows.append(
            {
                "check": "required_audit_pass",
                "name": entry["name"],
                "summary_key": entry["summary_key"],
                "actual": actual,
                "expected": True,
                "pass": actual is True,
                "notes": "Step72 readiness component must be green",
            }
        )
    closed_gate_count = 0
    for gate in policy["required_closed_activation_gates"]:
        actual = activation_policy["activation_gates"].get(gate)
        if actual is False:
            closed_gate_count += 1
        rows.append(
            {
                "check": "activation_gate_remains_closed",
                "name": gate,
                "summary_key": "",
                "actual": actual,
                "expected": False,
                "pass": actual is False,
                "notes": "Step72 readiness does not open activation gates",
            }
        )
    rows.append(
        {
            "check": "activation_allowed_after_step72",
            "name": "runtime_geometry_activation_allowed",
            "summary_key": "",
            "actual": policy["activation_allowed_after_step72"],
            "expected": False,
            "pass": policy["activation_allowed_after_step72"] is False,
            "notes": policy["readiness_claim"],
        }
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_audit_count": len(policy["required_audits"]),
        "required_audit_pass_count": audit_pass_count,
        "required_closed_gate_count": len(policy["required_closed_activation_gates"]),
        "closed_gate_pass_count": closed_gate_count,
        "activation_allowed_after_step72": bool(policy["activation_allowed_after_step72"]),
        "readiness_claim": policy["readiness_claim"],
        "runtime_geometry_readiness_audit_pass": False,
    }
    summary["runtime_geometry_readiness_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["required_audit_pass_count"] == summary["required_audit_count"]
        and summary["closed_gate_pass_count"] == summary["required_closed_gate_count"]
        and summary["activation_allowed_after_step72"] is False
    )
    return rows, summary
