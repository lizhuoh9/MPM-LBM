from __future__ import annotations

import json
from pathlib import Path


def build_step103_activation_guard(
    root: Path,
    policy_path: str = "configs/step103_activation_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / policy["matrix_artifact_path"])
    summary = matrix["summary"]
    row = matrix["rows"][0]
    rows = [
        literal_row("matrix_summary", "matrix_pass", summary["step103_fluent_inspired_duct_flap_proxy_smoke_matrix_pass"], True),
        literal_row("matrix_summary", "duct_flap_proxy_enabled_count", summary["duct_flap_proxy_enabled_count"], policy["expected_duct_flap_proxy_enabled_count"]),
        literal_row("matrix_summary", "runtime_geometry_enabled_count", summary["runtime_geometry_enabled_count"], policy["expected_runtime_geometry_enabled_count"]),
        literal_row("matrix_summary", "wall_velocity_enabled_count", summary["wall_velocity_enabled_count"], policy["expected_wall_velocity_enabled_count"]),
        literal_row("matrix_summary", "combined_runtime_geometry_wall_velocity_enabled_count", summary["combined_runtime_geometry_wall_velocity_enabled_count"], policy["expected_combined_runtime_geometry_wall_velocity_enabled_count"]),
        literal_row("matrix_summary", "ggui_visualization_enabled_count", summary["ggui_visualization_enabled_count"], policy["expected_ggui_visualization_enabled_count"]),
        literal_row("matrix_summary", "grid_48_enabled_count", summary["grid_48_enabled_count"], policy["expected_grid_48_enabled_count"]),
        literal_row("matrix_summary", "grid_64_enabled_count", summary["grid_64_enabled_count"], policy["expected_grid_64_enabled_count"]),
        literal_row("matrix_summary", "ggui_renderer_called_count", summary["ggui_renderer_called_count"], policy["expected_ggui_renderer_called_count"]),
        literal_row("matrix_summary", "ggui_screenshot_count", summary["ggui_screenshot_count"], policy["expected_ggui_screenshot_count"]),
        literal_row("matrix_row", "row_name", row["row_name"], policy["expected_required_row_name"]),
        literal_row("matrix_row", "geometry_type", row["geometry_type"], policy["expected_geometry_type"]),
        literal_row("matrix_row", "geometry_config_path", row["geometry_config_path"], policy["expected_geometry_config_path"]),
        literal_row("matrix_row", "geometry_motion_application_mode", row["geometry_motion_application_mode"], policy["expected_geometry_motion_application_mode"]),
        literal_row("matrix_row", "wall_velocity_application_mode", row["wall_velocity_application_mode"], policy["expected_wall_velocity_application_mode"]),
        literal_row("matrix_row", "target_lbm_field", row["target_lbm_field"], policy["expected_target_lbm_field"]),
        literal_row("matrix_row", "direct_quantitative_equivalence_allowed", row["direct_quantitative_equivalence_allowed"], False),
        literal_row("matrix_row", "validation_claim_allowed", row["validation_claim_allowed"], False),
    ]
    for flag in policy["summary_flags_must_be_zero"]:
        rows.append(literal_row("matrix_summary", flag, summary[flag], 0))
    guard_summary = {
        "direct_quantitative_equivalence_allowed": bool(row["direct_quantitative_equivalence_allowed"]),
        "combined_runtime_geometry_wall_velocity_enabled_count": summary[
            "combined_runtime_geometry_wall_velocity_enabled_count"
        ],
        "duct_flap_proxy_enabled_count": summary["duct_flap_proxy_enabled_count"],
        "geometry_type": row["geometry_type"],
        "ggui_screenshot_count": summary["ggui_screenshot_count"],
        "ggui_visualization_enabled_count": summary["ggui_visualization_enabled_count"],
        "grid_48_enabled_count": summary["grid_48_enabled_count"],
        "grid_64_enabled_count": summary["grid_64_enabled_count"],
        "guard_pass_count": sum(1 for item in rows if item["pass"]),
        "guard_row_count": len(rows),
        "link_area_enabled_count": summary["link_area_enabled_count"],
        "real_geometry_candidate_enabled_count": summary["real_geometry_candidate_enabled_count"],
        "real_geometry_enabled_count": summary["real_geometry_enabled_count"],
        "required_row_name": row["row_name"],
        "row_count": len(rows),
        "runtime_geometry_enabled_count": summary["runtime_geometry_enabled_count"],
        "step103_activation_guard_pass": False,
        "validation_claim_allowed": bool(row["validation_claim_allowed"]),
        "wall_velocity_enabled_count": summary["wall_velocity_enabled_count"],
        "write_particles_count": summary["write_particles_count"],
        "write_vtk_count": summary["write_vtk_count"],
    }
    guard_summary["step103_activation_guard_pass"] = bool(
        rows
        and guard_summary["guard_pass_count"] == guard_summary["guard_row_count"]
        and guard_summary["required_row_name"] == policy["expected_required_row_name"]
        and guard_summary["geometry_type"] == policy["expected_geometry_type"]
        and guard_summary["duct_flap_proxy_enabled_count"] == int(policy["expected_duct_flap_proxy_enabled_count"])
        and guard_summary["wall_velocity_enabled_count"] == int(policy["expected_wall_velocity_enabled_count"])
        and guard_summary["combined_runtime_geometry_wall_velocity_enabled_count"]
        == int(policy["expected_combined_runtime_geometry_wall_velocity_enabled_count"])
        and guard_summary["ggui_visualization_enabled_count"] == int(policy["expected_ggui_visualization_enabled_count"])
        and guard_summary["grid_48_enabled_count"] == int(policy["expected_grid_48_enabled_count"])
        and guard_summary["grid_64_enabled_count"] == 0
        and guard_summary["real_geometry_candidate_enabled_count"] == 0
        and guard_summary["real_geometry_enabled_count"] == 0
        and guard_summary["link_area_enabled_count"] == 0
        and guard_summary["write_vtk_count"] == 0
        and guard_summary["write_particles_count"] == 0
        and guard_summary["validation_claim_allowed"] is False
        and guard_summary["direct_quantitative_equivalence_allowed"] is False
    )
    return rows, guard_summary


def literal_row(row_name: str, check: str, actual, expected) -> dict:
    return {"actual": actual, "check": check, "expected": expected, "pass": actual == expected, "row_name": row_name}


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
