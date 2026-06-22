from __future__ import annotations

import json
from pathlib import Path


def build_step80_runtime_geometry_diagnostic_only_activation_guard(
    root: Path,
    policy_path: str = "configs/step80_activation_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / policy["matrix_artifact_path"])
    step79_guard = read_json(root / policy["step79_activation_guard_artifact_path"])
    rows = []
    for row in matrix["rows"]:
        rows.extend(row_activation_checks(row, policy))
    rows.extend(matrix_summary_checks(matrix["summary"], policy))
    rows.extend(step79_summary_checks(step79_guard["summary"], policy))
    summary = {
        "activation_feature_count": matrix["summary"]["activation_feature_count"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "planned_step80_activation_feature_count": step79_guard["summary"]["planned_step80_activation_feature_count"],
        "row_count": len(rows),
        "runtime_geometry_enabled_count": matrix["summary"]["runtime_geometry_enabled_count"],
        "step80_activation_guard_pass": False,
        "step80_runtime_geometry_diagnostic_only_activation_guard_pass": False,
        "wall_velocity_enabled_count": matrix["summary"]["wall_velocity_enabled_count"],
    }
    summary["step80_runtime_geometry_diagnostic_only_activation_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["activation_feature_count"] == int(policy["expected_activation_feature_count"])
        and summary["runtime_geometry_enabled_count"] == 1
        and summary["wall_velocity_enabled_count"] == 0
        and summary["planned_step80_activation_feature_count"] == int(
            policy["expected_step79_planned_step80_activation_feature_count"]
        )
    )
    summary["step80_activation_guard_pass"] = summary["step80_runtime_geometry_diagnostic_only_activation_guard_pass"]
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
            "geometry_motion_mode",
            row["geometry_motion_mode"],
            policy["expected_geometry_motion_mode"],
        ),
        literal_row(
            row["row_name"],
            "geometry_motion_application_mode",
            row["geometry_motion_application_mode"],
            policy["expected_geometry_motion_application_mode"],
        ),
        literal_row(row["row_name"], "geometry_motion_interface_report_pass", row["geometry_motion_interface_report_pass"], True),
        literal_row(row["row_name"], "mutation_flag_enabled_count", int(row["mutation_flag_enabled_count"]), 0),
    ]
    for flag in policy["activation_features_must_be_false"]:
        rows.append(literal_row(row["row_name"], flag, bool(row[flag]), False))
    return rows


def matrix_summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step80_runtime_geometry_diagnostic_only_smoke_matrix_pass", True),
        ("required_row_count", 1),
        ("optional_row_count", 0),
        ("required_stable_count", 1),
        ("activation_feature_count", int(policy["expected_activation_feature_count"])),
        ("runtime_geometry_enabled_count", 1),
        ("wall_velocity_enabled_count", 0),
        ("combined_runtime_geometry_wall_velocity_enabled_count", 0),
        ("real_geometry_enabled_count", 0),
        ("squid_proxy_enabled_count", 0),
        ("link_area_enabled_count", 0),
        ("grid_48_enabled_count", 0),
        ("grid_64_enabled_count", 0),
        ("runtime_code_changed", False),
        ("solver_behavior_changed", False),
        ("physics_feature_expansion", "diagnostic_only_only"),
    ]
    return [literal_row("", check, summary[check], expected) for check, expected in checks]


def step79_summary_checks(summary: dict, policy: dict) -> list[dict]:
    return [
        literal_row("step79_guard", "step79_activation_guard_pass", summary["step79_runtime_geometry_diagnostic_only_activation_guard_pass"], True),
        literal_row(
            "step79_guard",
            "planned_step80_activation_feature_count",
            summary["planned_step80_activation_feature_count"],
            policy["expected_step79_planned_step80_activation_feature_count"],
        ),
        literal_row("step79_guard", "step79_activation_feature_count", summary["step79_activation_feature_count"], 0),
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
