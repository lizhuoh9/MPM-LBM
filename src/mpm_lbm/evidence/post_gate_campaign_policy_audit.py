from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import read_json


def build_step75_post_gate_campaign_policy_audit(
    root: Path,
    policy_path: str = "configs/step75_post_gate_campaign_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    rows = []
    for campaign in policy["allowed_campaigns"]:
        rows.extend(campaign_rows(campaign))
    rows.extend(
        {
            "actual": False,
            "campaign_id": "",
            "check": "forbidden_campaign_item_not_allowed",
            "expected": False,
            "item": item,
            "pass": True,
        }
        for item in policy["forbidden_campaign_items"]
    )
    first = policy["allowed_campaigns"][0]
    summary = {
        "activation_feature_count_in_first_campaign": len(first["activation_features"]),
        "allowed_campaign_count": len(policy["allowed_campaigns"]),
        "first_campaign_is_rebaseline_only": bool(first["first_campaign_is_rebaseline_only"]),
        "forbidden_campaign_count": len(policy["forbidden_campaign_items"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "post_gate_campaign_policy_audit_pass": False,
        "real_geometry_enabled": bool(first["real_geometry_enabled"]),
        "row_count": len(rows),
        "run_optional_32_3step": bool(first["run_optional_32_3step"]),
        "runtime_geometry_enabled": bool(first["runtime_geometry_enabled"]),
        "squid_proxy_enabled": bool(first["squid_proxy_enabled"]),
        "wall_velocity_enabled": bool(first["wall_velocity_enabled"]),
        "write_particles": bool(first["write_particles"]),
        "write_vtk": bool(first["write_vtk"]),
    }
    summary["post_gate_campaign_policy_audit_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["allowed_campaign_count"] >= 1
        and summary["forbidden_campaign_count"] >= 1
        and summary["first_campaign_is_rebaseline_only"]
        and summary["activation_feature_count_in_first_campaign"] == 0
        and summary["runtime_geometry_enabled"] is False
        and summary["wall_velocity_enabled"] is False
        and summary["real_geometry_enabled"] is False
        and summary["squid_proxy_enabled"] is False
        and summary["write_vtk"] is False
        and summary["write_particles"] is False
    )
    return rows, summary


def campaign_rows(campaign: dict) -> list[dict]:
    checks = [
        ("first_campaign_is_rebaseline_only", campaign["first_campaign_is_rebaseline_only"], True),
        ("run_optional_32_3step", campaign["run_optional_32_3step"], False),
        ("runtime_geometry_enabled", campaign["runtime_geometry_enabled"], False),
        ("wall_velocity_enabled", campaign["wall_velocity_enabled"], False),
        ("real_geometry_enabled", campaign["real_geometry_enabled"], False),
        ("squid_proxy_enabled", campaign["squid_proxy_enabled"], False),
        ("write_vtk", campaign["write_vtk"], False),
        ("write_particles", campaign["write_particles"], False),
        ("activation_feature_count", len(campaign["activation_features"]), 0),
    ]
    return [
        {
            "actual": actual,
            "campaign_id": campaign["campaign_id"],
            "check": check,
            "expected": expected,
            "item": "",
            "pass": actual == expected,
        }
        for check, actual, expected in checks
    ]
