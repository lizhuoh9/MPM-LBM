from __future__ import annotations

import json
from pathlib import Path


def build_step95_taichi_ggui_10step_visualization_guard(
    root: Path,
    policy_path: str = "configs/step95_taichi_ggui_10step_visualization_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_summary = read_json(root / policy["plan_artifact_path"])["summary"]
    rows = []
    rows.extend(summary_checks(plan_summary, policy))
    for flag in policy["plan_summary_flags_must_be_false"]:
        rows.append(literal_row("step96_ggui_10step_visual_run_plan", flag, bool(plan_summary[flag]), False))

    summary = {
        "combined_runtime_geometry_wall_velocity_planned_for_step96": plan_summary[
            "combined_runtime_geometry_wall_velocity_planned_for_step96"
        ],
        "from_step92_adds_ggui_visualization": plan_summary["from_step92_adds_ggui_visualization"],
        "from_step94_duration_expansion": plan_summary["from_step94_duration_expansion"],
        "geometry_motion_application_mode_planned_for_step96": plan_summary[
            "geometry_motion_application_mode_allowed_for_step96"
        ],
        "geometry_mutation_allowed": plan_summary["geometry_mutation_allowed"],
        "geometry_type_planned_for_step96": plan_summary["geometry_type_allowed_for_step96"],
        "ggui_interactive_window_allowed_for_step96": plan_summary["ggui_interactive_window_allowed_for_step96"],
        "ggui_screenshot_allowed_for_step96": plan_summary["ggui_screenshot_allowed_for_step96"],
        "ggui_video_allowed_for_step96": plan_summary["ggui_video_allowed_for_step96"],
        "ggui_visualization_planned_for_step96": plan_summary["ggui_visualization_planned_for_step96"],
        "grid_48_planned_for_step96": plan_summary["grid_48_allowed"],
        "grid_64_planned_for_step96": plan_summary["grid_64_allowed"],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "link_area_planned_for_step96": plan_summary["link_area_allowed"],
        "particle_npy_output_planned_for_step96": plan_summary["particle_npy_output_allowed"],
        "planned_step96_activation_feature_count": plan_summary["planned_step96_activation_feature_count"],
        "planned_step96_duration_lbm_steps": plan_summary["step96_allowed_n_lbm_steps"],
        "previous_step92_n_lbm_steps": plan_summary["previous_step92_n_lbm_steps"],
        "previous_step94_n_lbm_steps": plan_summary["previous_step94_n_lbm_steps"],
        "real_geometry_candidate_data_planned_for_step96": plan_summary["real_geometry_candidate_data_allowed"],
        "real_geometry_planned_for_step96": plan_summary["real_geometry_allowed"],
        "row_count": len(rows),
        "runtime_geometry_planned_for_step96": plan_summary["runtime_geometry_planned_for_step96"],
        "squid_proxy_planned_for_step96": plan_summary["squid_proxy_planned_for_step96"],
        "step95_activation_feature_count": plan_summary["step95_activation_feature_count"],
        "step95_taichi_ggui_10step_visualization_guard_pass": False,
        "target_lbm_field_planned_for_step96": plan_summary["target_lbm_field_planned_for_step96"],
        "target_u_lbm_planned_for_step96": plan_summary["target_u_lbm_allowed_for_step96"],
        "vtr_route_allowed_for_step96": plan_summary["vtr_output_allowed"],
        "wall_velocity_application_mode_planned_for_step96": plan_summary[
            "wall_velocity_application_mode_allowed_for_step96"
        ],
        "wall_velocity_planned_for_step96": plan_summary["wall_velocity_planned_for_step96"],
        "write_particles_allowed_for_step96": plan_summary["write_particles_allowed"],
        "write_vtk_planned_for_step96": plan_summary["write_vtk_allowed"],
    }
    summary["step95_taichi_ggui_10step_visualization_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step95_activation_feature_count"] == int(policy["expected_step95_activation_feature_count"])
        and summary["planned_step96_activation_feature_count"]
        == int(policy["expected_planned_step96_activation_feature_count"])
        and summary["planned_step96_duration_lbm_steps"] == int(policy["expected_planned_step96_n_lbm_steps"])
        and summary["previous_step94_n_lbm_steps"] == int(policy["expected_previous_step94_n_lbm_steps"])
        and summary["previous_step92_n_lbm_steps"] == int(policy["expected_previous_step92_n_lbm_steps"])
        and summary["from_step94_duration_expansion"] is True
        and summary["from_step92_adds_ggui_visualization"] is True
        and summary["ggui_visualization_planned_for_step96"] is True
        and summary["ggui_interactive_window_allowed_for_step96"] is True
        and summary["ggui_screenshot_allowed_for_step96"] is True
        and summary["ggui_video_allowed_for_step96"] is False
        and summary["write_vtk_planned_for_step96"] is False
        and summary["write_particles_allowed_for_step96"] is False
        and summary["vtr_route_allowed_for_step96"] is False
        and summary["particle_npy_output_planned_for_step96"] is False
        and summary["squid_proxy_planned_for_step96"] is True
        and summary["runtime_geometry_planned_for_step96"] is True
        and summary["wall_velocity_planned_for_step96"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step96"] is True
        and summary["geometry_motion_application_mode_planned_for_step96"]
        == policy["expected_geometry_motion_application_mode"]
        and summary["wall_velocity_application_mode_planned_for_step96"]
        == policy["expected_wall_velocity_application_mode"]
        and summary["target_lbm_field_planned_for_step96"] == policy["expected_target_lbm_field"]
        and summary["target_u_lbm_planned_for_step96"] == policy["expected_target_u_lbm"]
        and summary["real_geometry_planned_for_step96"] is False
        and summary["real_geometry_candidate_data_planned_for_step96"] is False
        and summary["link_area_planned_for_step96"] is False
        and summary["grid_48_planned_for_step96"] is False
        and summary["grid_64_planned_for_step96"] is False
    )
    return rows, summary


def summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step95_taichi_ggui_10step_visualization_plan_pass", True),
        ("step96_allowed_row_name", policy["step96_allowed_row_name"]),
        ("step95_activation_feature_count", int(policy["expected_step95_activation_feature_count"])),
        ("planned_step96_activation_feature_count", int(policy["expected_planned_step96_activation_feature_count"])),
        ("step96_allowed_n_lbm_steps", int(policy["expected_planned_step96_n_lbm_steps"])),
        ("previous_step94_n_lbm_steps", int(policy["expected_previous_step94_n_lbm_steps"])),
        ("previous_step92_n_lbm_steps", int(policy["expected_previous_step92_n_lbm_steps"])),
        ("planned_step96_n_lbm_steps", int(policy["expected_planned_step96_n_lbm_steps"])),
        ("from_step94_duration_expansion", True),
        ("from_step92_adds_ggui_visualization", True),
        ("geometry_type_allowed_for_step96", policy["expected_geometry_type"]),
        ("geometry_config_path_allowed_for_step96", policy["expected_geometry_config_path"]),
        ("geometry_motion_application_mode_allowed_for_step96", policy["expected_geometry_motion_application_mode"]),
        ("wall_velocity_application_mode_allowed_for_step96", policy["expected_wall_velocity_application_mode"]),
        ("target_lbm_field_planned_for_step96", policy["expected_target_lbm_field"]),
        ("target_u_lbm_allowed_for_step96", policy["expected_target_u_lbm"]),
        ("ggui_visualization_planned_for_step96", True),
        ("ggui_interactive_window_allowed_for_step96", True),
        ("ggui_screenshot_allowed_for_step96", True),
        ("ggui_video_allowed_for_step96", False),
        ("write_vtk_allowed", False),
        ("write_particles_allowed", False),
        ("vtr_output_allowed", False),
        ("particle_npy_output_allowed", False),
        ("video_output_allowed", False),
        ("squid_proxy_planned_for_step96", True),
        ("runtime_geometry_planned_for_step96", True),
        ("wall_velocity_planned_for_step96", True),
        ("combined_runtime_geometry_wall_velocity_planned_for_step96", True),
    ]
    return [literal_row("step96_ggui_10step_visual_run_plan", check, summary[check], expected) for check, expected in checks]


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
