from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json
from src.mpm_lbm.evidence.full_activation_gate_coverage_audit import build_step73_full_activation_gate_coverage_audit
from src.mpm_lbm.evidence.wall_velocity_api_audit import build_step73_wall_velocity_api_audit
from src.mpm_lbm.evidence.wall_velocity_application_safety_audit import build_step73_wall_velocity_application_safety_audit
from src.mpm_lbm.evidence.wall_velocity_config_schema_audit import build_step73_wall_velocity_config_schema_audit
from src.mpm_lbm.evidence.wall_velocity_driver_gate_audit import build_step73_wall_velocity_driver_gate_audit
from src.mpm_lbm.evidence.wall_velocity_output_policy_audit import build_step73_wall_velocity_output_policy_audit


AUDIT_BUILDERS = {
    "wall_velocity_api_audit": build_step73_wall_velocity_api_audit,
    "wall_velocity_config_schema_audit": build_step73_wall_velocity_config_schema_audit,
    "wall_velocity_driver_gate_audit": build_step73_wall_velocity_driver_gate_audit,
    "wall_velocity_application_safety_audit": build_step73_wall_velocity_application_safety_audit,
    "wall_velocity_output_policy_audit": build_step73_wall_velocity_output_policy_audit,
    "full_activation_gate_coverage_audit": build_step73_full_activation_gate_coverage_audit,
}


def build_step73_wall_velocity_readiness_audit(
    root: Path,
    policy_path: str = "configs/step73_wall_velocity_readiness_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
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
                "notes": "Step73 wall velocity readiness component must be green",
            }
        )
    rows.append(
        {
            "check": "activation_allowed_after_step73",
            "name": "wall_velocity_activation_allowed",
            "summary_key": "",
            "actual": policy["activation_allowed_after_step73"],
            "expected": False,
            "pass": policy["activation_allowed_after_step73"] is False,
            "notes": policy["readiness_claim"],
        }
    )
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "required_audit_count": len(policy["required_audits"]),
        "required_audit_pass_count": audit_pass_count,
        "activation_allowed_after_step73": bool(policy["activation_allowed_after_step73"]),
        "readiness_claim": policy["readiness_claim"],
        "wall_velocity_readiness_audit_pass": False,
    }
    summary["wall_velocity_readiness_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["required_audit_pass_count"] == summary["required_audit_count"]
        and summary["activation_allowed_after_step73"] is False
    )
    return rows, summary
