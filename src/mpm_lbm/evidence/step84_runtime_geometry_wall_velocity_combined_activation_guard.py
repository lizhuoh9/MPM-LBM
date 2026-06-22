from __future__ import annotations

import json
from pathlib import Path


def build_step84_runtime_geometry_wall_velocity_combined_activation_guard(
    root: Path,
    policy_path: str = "configs/step84_activation_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / policy["matrix_artifact_path"])
    step83_guard = read_json(root / policy["step83_activation_guard_artifact_path"])
    rows = []
    for row in matrix["rows"]:
        rows.extend(row_activation_checks(row, policy))
    rows.extend(matrix_summary_checks(matrix["summary"], policy))
    rows.extend(step83_summary_checks(step83_guard["summary"], policy))
    summary = {
        "activation_feature_count": matrix["summary"]["activation_feature_count"],
        "combined_runtime_geometry_wall_velocity_enabled_count": matrix["summary"][
            "combined_runtime_geometry_wall_velocity_enabled_count"
        ],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step84_activation_feature_count": step83_guard["summary"]["planned_step84_activation_feature_count"],
        "row_count": len(rows),
        "runtime_geometry_enabled_count": matrix["summary"]["runtime_geometry_enabled_count"],
        "step84_activation_guard_pass": False,
        "wall_velocity_enabled_count": matrix["summary"]["wall_velocity_enabled_count"],
    }
    summary["step84_activation_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["activation_feature_count"] == int(policy["expected_activation_feature_count"])
        and summary["runtime_geometry_enabled_count"] == 1
        and summary["wall_velocity_enabled_count"] == 1
        and summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 1
        and summary["planned_step84_activation_feature_count"]
        == int(policy["expected_step83_planned_step84_activation_feature_count"])
    )
    return rows, summary


def row_activation_checks(row: dict, policy: dict) -> list[dict]:
    rows = [
        literal_row(row["row_name"], "allowed_required_row_name", row["row_name"], policy["allowed_required_row_name"]),
        literal_row(
            row["row_name"],
            "activation_feature_count",
            int(row["activation_feature_count"]),
            int(policy["expected_activation_feature_count"]),
        ),
        literal_row(
            row["row_name"],
            "runtime_geometry_enabled",
            bool(row["runtime_geometry_enabled"]),
            bool(policy["expected_runtime_geometry_enabled"]),
        ),
        literal_row(
            row["row_name"],
            "geometry_motion_application_mode",
            row["geometry_motion_application_mode"],
            policy["expected_geometry_motion_application_mode"],
        ),
        literal_row(
            row["row_name"],
            "wall_velocity_enabled",
            bool(row["wall_velocity_enabled"]),
            bool(policy["expected_wall_velocity_enabled"]),
        ),
        literal_row(
            row["row_name"],
            "wall_velocity_application_mode",
            row["wall_velocity_application_mode"],
            policy["expected_wall_velocity_application_mode"],
        ),
        literal_row(
            row["row_name"],
            "boundary_motion_mode",
            row["boundary_motion_mode"],
            policy["expected_boundary_motion_mode"],
        ),
        literal_row(row["row_name"], "geometry_motion_interface_report_pass", row["geometry_motion_interface_report_pass"], True),
        literal_row(row["row_name"], "wall_velocity_application_report_pass", row["wall_velocity_application_report_pass"], True),
        literal_row(row["row_name"], "boundary_motion_interface_report_pass", row["boundary_motion_interface_report_pass"], True),
    ]
    for flag in policy["activation_features_must_be_false"]:
        rows.append(literal_row(row["row_name"], flag, bool(row[flag]), False))
    return rows


def matrix_summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step84_runtime_geometry_wall_velocity_combined_smoke_matrix_pass", True),
        ("required_row_count", 1),
        ("optional_row_count", 0),
        ("required_stable_count", 1),
        ("activation_feature_count", int(policy["expected_activation_feature_count"])),
        ("runtime_geometry_enabled_count", 1),
        ("wall_velocity_enabled_count", 1),
        ("combined_runtime_geometry_wall_velocity_enabled_count", 1),
        ("real_geometry_enabled_count", 0),
        ("squid_proxy_enabled_count", 0),
        ("link_area_enabled_count", 0),
        ("grid_48_enabled_count", 0),
        ("grid_64_enabled_count", 0),
        ("runtime_code_changed", False),
        ("solver_behavior_changed", False),
        ("physics_feature_expansion", "runtime_geometry_diagnostic_only_wall_velocity_solid_vel_only"),
    ]
    return [literal_row("", check, summary[check], expected) for check, expected in checks]


def step83_summary_checks(summary: dict, policy: dict) -> list[dict]:
    return [
        literal_row(
            "step83_guard",
            "step83_activation_guard_pass",
            summary["step83_runtime_geometry_wall_velocity_combined_activation_guard_pass"],
            True,
        ),
        literal_row(
            "step83_guard",
            "planned_step84_activation_feature_count",
            summary["planned_step84_activation_feature_count"],
            policy["expected_step83_planned_step84_activation_feature_count"],
        ),
        literal_row("step83_guard", "step83_activation_feature_count", summary["step83_activation_feature_count"], 0),
    ]


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
