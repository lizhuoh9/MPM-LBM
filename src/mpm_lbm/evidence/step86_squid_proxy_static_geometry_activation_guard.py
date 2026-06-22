from __future__ import annotations

import json
from pathlib import Path


def build_step86_squid_proxy_static_geometry_activation_guard(
    root: Path,
    policy_path: str = "configs/step86_activation_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / policy["matrix_artifact_path"])
    summary_rows = [
        literal_row("", "step86_squid_proxy_static_geometry_smoke_matrix_pass", matrix["summary"]["step86_squid_proxy_static_geometry_smoke_matrix_pass"], True),
        literal_row("", "activation_feature_count", matrix["summary"]["activation_feature_count"], policy["expected_activation_feature_count"]),
        literal_row("", "procedural_geometry_enabled_count", matrix["summary"]["procedural_geometry_enabled_count"], policy["expected_procedural_geometry_enabled_count"]),
        literal_row("", "squid_proxy_enabled_count", matrix["summary"]["squid_proxy_enabled_count"], policy["expected_squid_proxy_enabled_count"]),
    ]
    for key in policy["summary_zero_counts"]:
        summary_rows.append(literal_row("", key, matrix["summary"][key], 0))
    row_checks = []
    for row in matrix["rows"]:
        row_checks.extend(
            [
                literal_row(row["row_name"], "row_name", row["row_name"], policy["required_row_name"]),
                literal_row(row["row_name"], "activation_feature_count", row["activation_feature_count"], 1),
                literal_row(row["row_name"], "squid_proxy_enabled", row["squid_proxy_enabled"], True),
                literal_row(row["row_name"], "procedural_geometry_enabled", row["procedural_geometry_enabled"], True),
                literal_row(row["row_name"], "real_geometry_candidate_enabled", row["real_geometry_candidate_enabled"], False),
                literal_row(row["row_name"], "runtime_geometry_enabled", row["runtime_geometry_enabled"], False),
                literal_row(row["row_name"], "wall_velocity_enabled", row["wall_velocity_enabled"], False),
                literal_row(row["row_name"], "link_area_enabled", row["link_area_enabled"], False),
                literal_row(row["row_name"], "write_vtk", row["write_vtk"], False),
                literal_row(row["row_name"], "write_particles", row["write_particles"], False),
            ]
        )
    rows = summary_rows + row_checks
    summary = {
        "activation_feature_count": matrix["summary"]["activation_feature_count"],
        "combined_runtime_geometry_wall_velocity_enabled_count": matrix["summary"][
            "combined_runtime_geometry_wall_velocity_enabled_count"
        ],
        "link_area_enabled_count": matrix["summary"]["link_area_enabled_count"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "procedural_geometry_enabled_count": matrix["summary"]["procedural_geometry_enabled_count"],
        "real_geometry_candidate_enabled_count": matrix["summary"]["real_geometry_candidate_enabled_count"],
        "real_geometry_enabled_count": matrix["summary"]["real_geometry_enabled_count"],
        "row_count": len(rows),
        "runtime_geometry_enabled_count": matrix["summary"]["runtime_geometry_enabled_count"],
        "squid_proxy_enabled_count": matrix["summary"]["squid_proxy_enabled_count"],
        "step86_activation_guard_pass": False,
        "wall_velocity_enabled_count": matrix["summary"]["wall_velocity_enabled_count"],
        "write_particles_count": matrix["summary"]["write_particles_count"],
        "write_vtk_count": matrix["summary"]["write_vtk_count"],
    }
    summary["step86_activation_guard_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["activation_feature_count"] == 1
        and summary["squid_proxy_enabled_count"] == 1
        and summary["procedural_geometry_enabled_count"] == 1
        and summary["real_geometry_candidate_enabled_count"] == 0
        and summary["real_geometry_enabled_count"] == 0
        and summary["runtime_geometry_enabled_count"] == 0
        and summary["wall_velocity_enabled_count"] == 0
        and summary["combined_runtime_geometry_wall_velocity_enabled_count"] == 0
        and summary["link_area_enabled_count"] == 0
        and summary["write_vtk_count"] == 0
        and summary["write_particles_count"] == 0
    )
    return rows, summary


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
