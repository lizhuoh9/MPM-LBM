from __future__ import annotations

import json
from pathlib import Path


def build_step85_squid_proxy_static_geometry_activation_guard(
    root: Path,
    policy_path: str = "configs/step85_squid_proxy_static_geometry_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_artifact = read_json(root / policy["activation_plan_artifact_path"])
    plan_summary = plan_artifact["summary"]
    geometry_config = read_json(root / policy["expected_geometry_config_path"])
    rows = []
    rows.extend(summary_checks(plan_summary, policy))
    rows.extend(geometry_config_checks(geometry_config, policy))
    for flag in policy["plan_summary_flags_must_be_false"]:
        rows.append(literal_row("activation_plan", flag, bool(plan_summary[flag]), False))

    summary = {
        "geometry_config_path_allowed_for_step86": plan_summary["geometry_config_path_allowed_for_step86"],
        "geometry_quality_report_required_for_step86": plan_summary["geometry_quality_report_required_for_step86"],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "planned_step86_activation_feature_count": plan_summary["planned_step86_activation_feature_count"],
        "planned_step86_feature": plan_summary["feature_under_plan"],
        "planned_step86_row_name": plan_summary["step86_allowed_row_name"],
        "row_count": len(rows),
        "step85_activation_feature_count": plan_summary["step85_activation_feature_count"],
        "step85_squid_proxy_static_geometry_activation_guard_pass": False,
        "squid_proxy_planned_for_step86": plan_summary["squid_proxy_planned_for_step86"],
    }
    summary["step85_squid_proxy_static_geometry_activation_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step85_activation_feature_count"] == int(policy["expected_step85_activation_feature_count"])
        and summary["planned_step86_activation_feature_count"]
        == int(policy["expected_planned_step86_activation_feature_count"])
        and summary["planned_step86_feature"] == policy["expected_feature_under_plan"]
        and summary["geometry_config_path_allowed_for_step86"] == policy["expected_geometry_config_path"]
        and summary["geometry_quality_report_required_for_step86"] is True
        and summary["squid_proxy_planned_for_step86"] is True
    )
    return rows, summary


def summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step85_squid_proxy_static_geometry_activation_plan_pass", True),
        ("step86_allowed_row_name", policy["allowed_required_row_name"]),
        ("feature_under_plan", policy["expected_feature_under_plan"]),
        ("step85_activation_feature_count", int(policy["expected_step85_activation_feature_count"])),
        ("planned_step86_activation_feature_count", int(policy["expected_planned_step86_activation_feature_count"])),
        ("geometry_type_allowed_for_step86", policy["expected_geometry_type"]),
        ("geometry_config_path_allowed_for_step86", policy["expected_geometry_config_path"]),
        ("geometry_motion_mode_allowed_for_step86", policy["expected_geometry_motion_mode"]),
        ("geometry_motion_application_mode_allowed_for_step86", policy["expected_geometry_motion_application_mode"]),
        ("boundary_motion_mode_allowed_for_step86", policy["expected_boundary_motion_mode"]),
        ("wall_velocity_application_mode_allowed_for_step86", policy["expected_wall_velocity_application_mode"]),
        ("geometry_quality_report_required_for_step86", bool(policy["geometry_quality_report_required"])),
        ("write_vtk_allowed_for_step86", False),
        ("write_particles_allowed_for_step86", False),
        ("driver_run_required", False),
        ("fsidriver_run_allowed", False),
        ("simulation_run_allowed", False),
    ]
    return [literal_row("activation_plan", check, summary[check], expected) for check, expected in checks]


def geometry_config_checks(config: dict, policy: dict) -> list[dict]:
    rows = []
    for key, expected in policy["planned_geometry_required_values"].items():
        rows.append(literal_row("planned_geometry_config", key, config.get(key), expected))
    rows.append(literal_row("planned_geometry_config", "mantle_center_len", len(config["mantle_center"]), 3))
    rows.append(literal_row("planned_geometry_config", "mantle_radii_len", len(config["mantle_radii"]), 3))
    rows.append(literal_row("planned_geometry_config", "head_center_len", len(config["head_center"]), 3))
    rows.append(literal_row("planned_geometry_config", "head_radii_len", len(config["head_radii"]), 3))
    return rows


def literal_row(row_name: str, check: str, actual, expected) -> dict:
    return {
        "actual": actual,
        "check": check,
        "expected": expected,
        "pass": actual == expected,
        "row_name": row_name,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
