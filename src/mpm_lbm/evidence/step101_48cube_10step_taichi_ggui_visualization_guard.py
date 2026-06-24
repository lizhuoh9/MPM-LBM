from __future__ import annotations

import json
from pathlib import Path


def build_step101_48cube_10step_taichi_ggui_visualization_guard(
    root: Path,
    policy_path: str = "configs/step101_48cube_10step_taichi_ggui_visualization_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_summary = read_json(root / policy["plan_artifact_path"])["summary"]
    rows = []
    rows.extend(summary_checks(plan_summary, policy))
    for flag in policy["plan_summary_flags_must_be_false"]:
        rows.append(literal_row("step102_48cube_10step_ggui_visual_run_plan", flag, bool(plan_summary[flag]), False))

    duration_expansion = bool(
        plan_summary["from_step100_duration_expansion"]
        and plan_summary["previous_step100_n_lbm_steps"] == 5
        and plan_summary["planned_step102_n_lbm_steps"] == 10
    )
    summary = {
        "combined_runtime_geometry_wall_velocity_planned_for_step102": plan_summary[
            "combined_runtime_geometry_wall_velocity_planned_for_step102"
        ],
        "duration_expansion_from_step100": duration_expansion,
        "from_step100_duration_expansion": plan_summary["from_step100_duration_expansion"],
        "geometry_motion_application_mode_planned_for_step102": plan_summary[
            "geometry_motion_application_mode_allowed_for_step102"
        ],
        "geometry_mutation_allowed": plan_summary["geometry_mutation_allowed"],
        "geometry_type_planned_for_step102": plan_summary["geometry_type_allowed_for_step102"],
        "ggui_interactive_window_allowed_for_step102": plan_summary["ggui_interactive_window_allowed_for_step102"],
        "ggui_screenshot_allowed_for_step102": plan_summary["ggui_screenshot_allowed_for_step102"],
        "ggui_video_allowed_for_step102": plan_summary["ggui_video_allowed_for_step102"],
        "ggui_visualization_planned_for_step102": plan_summary["ggui_visualization_planned_for_step102"],
        "grid_64_planned_for_step102": plan_summary["grid_64_allowed"],
        "grid_convergence_claim_allowed": plan_summary["grid_convergence_claim_allowed"],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "link_area_planned_for_step102": plan_summary["link_area_allowed"],
        "particle_npy_output_planned_for_step102": plan_summary["particle_npy_output_allowed"],
        "planned_step102_activation_feature_count": plan_summary["planned_step102_activation_feature_count"],
        "planned_step102_n_grid": plan_summary["planned_step102_n_grid"],
        "planned_step102_n_lbm_steps": plan_summary["planned_step102_n_lbm_steps"],
        "previous_step100_n_grid": plan_summary["previous_step100_n_grid"],
        "previous_step100_n_lbm_steps": plan_summary["previous_step100_n_lbm_steps"],
        "real_geometry_candidate_data_planned_for_step102": plan_summary["real_geometry_candidate_data_allowed"],
        "real_geometry_planned_for_step102": plan_summary["real_geometry_allowed"],
        "row_count": len(rows),
        "runtime_geometry_planned_for_step102": plan_summary["runtime_geometry_planned_for_step102"],
        "squid_proxy_planned_for_step102": plan_summary["squid_proxy_planned_for_step102"],
        "step101_activation_feature_count": plan_summary["step101_activation_feature_count"],
        "step101_48cube_10step_taichi_ggui_visualization_guard_pass": False,
        "step102_allowed_row_name": plan_summary["step102_allowed_row_name"],
        "target_lbm_field_planned_for_step102": plan_summary["target_lbm_field_planned_for_step102"],
        "target_u_lbm_planned_for_step102": plan_summary["target_u_lbm_allowed_for_step102"],
        "video_output_planned_for_step102": plan_summary["video_output_allowed"],
        "vtr_output_planned_for_step102": plan_summary["vtr_output_allowed"],
        "wall_velocity_application_mode_planned_for_step102": plan_summary[
            "wall_velocity_application_mode_allowed_for_step102"
        ],
        "wall_velocity_planned_for_step102": plan_summary["wall_velocity_planned_for_step102"],
        "write_particles_allowed_for_step102": plan_summary["write_particles_allowed"],
        "write_vtk_planned_for_step102": plan_summary["write_vtk_allowed"],
    }
    summary["step101_48cube_10step_taichi_ggui_visualization_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step101_activation_feature_count"] == int(policy["expected_step101_activation_feature_count"])
        and summary["planned_step102_activation_feature_count"]
        == int(policy["expected_planned_step102_activation_feature_count"])
        and summary["planned_step102_n_grid"] == int(policy["expected_planned_step102_n_grid"])
        and summary["planned_step102_n_lbm_steps"] == int(policy["expected_planned_step102_n_lbm_steps"])
        and summary["previous_step100_n_grid"] == int(policy["expected_previous_step100_n_grid"])
        and summary["previous_step100_n_lbm_steps"] == int(policy["expected_previous_step100_n_lbm_steps"])
        and summary["from_step100_duration_expansion"] is True
        and summary["duration_expansion_from_step100"] is True
        and summary["ggui_visualization_planned_for_step102"] is True
        and summary["ggui_interactive_window_allowed_for_step102"] is True
        and summary["ggui_screenshot_allowed_for_step102"] is True
        and summary["ggui_video_allowed_for_step102"] is False
        and summary["write_vtk_planned_for_step102"] is False
        and summary["write_particles_allowed_for_step102"] is False
        and summary["vtr_output_planned_for_step102"] is False
        and summary["particle_npy_output_planned_for_step102"] is False
        and summary["video_output_planned_for_step102"] is False
        and summary["squid_proxy_planned_for_step102"] is True
        and summary["runtime_geometry_planned_for_step102"] is True
        and summary["wall_velocity_planned_for_step102"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step102"] is True
        and summary["geometry_motion_application_mode_planned_for_step102"]
        == policy["expected_geometry_motion_application_mode"]
        and summary["wall_velocity_application_mode_planned_for_step102"]
        == policy["expected_wall_velocity_application_mode"]
        and summary["target_lbm_field_planned_for_step102"] == policy["expected_target_lbm_field"]
        and summary["target_u_lbm_planned_for_step102"] == policy["expected_target_u_lbm"]
        and summary["grid_64_planned_for_step102"] is False
        and summary["grid_convergence_claim_allowed"] is False
        and summary["real_geometry_planned_for_step102"] is False
        and summary["real_geometry_candidate_data_planned_for_step102"] is False
        and summary["link_area_planned_for_step102"] is False
    )
    return rows, summary


def summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step101_48cube_10step_taichi_ggui_visualization_plan_pass", True),
        ("step102_allowed_row_name", policy["step102_allowed_row_name"]),
        ("step101_activation_feature_count", int(policy["expected_step101_activation_feature_count"])),
        ("planned_step102_activation_feature_count", int(policy["expected_planned_step102_activation_feature_count"])),
        ("step102_allowed_n_grid", int(policy["expected_planned_step102_n_grid"])),
        ("planned_step102_n_grid", int(policy["expected_planned_step102_n_grid"])),
        ("step102_allowed_n_lbm_steps", int(policy["expected_planned_step102_n_lbm_steps"])),
        ("planned_step102_n_lbm_steps", int(policy["expected_planned_step102_n_lbm_steps"])),
        ("previous_step100_n_grid", int(policy["expected_previous_step100_n_grid"])),
        ("previous_step100_n_lbm_steps", int(policy["expected_previous_step100_n_lbm_steps"])),
        ("from_step100_duration_expansion", True),
        ("geometry_type_allowed_for_step102", policy["expected_geometry_type"]),
        ("geometry_config_path_allowed_for_step102", policy["expected_geometry_config_path"]),
        ("geometry_motion_application_mode_allowed_for_step102", policy["expected_geometry_motion_application_mode"]),
        ("wall_velocity_application_mode_allowed_for_step102", policy["expected_wall_velocity_application_mode"]),
        ("target_lbm_field_planned_for_step102", policy["expected_target_lbm_field"]),
        ("target_u_lbm_allowed_for_step102", policy["expected_target_u_lbm"]),
        ("ggui_visualization_planned_for_step102", True),
        ("ggui_interactive_window_allowed_for_step102", True),
        ("ggui_screenshot_allowed_for_step102", True),
        ("ggui_video_allowed_for_step102", False),
        ("write_vtk_allowed", False),
        ("write_particles_allowed", False),
        ("vtr_output_allowed", False),
        ("particle_npy_output_allowed", False),
        ("video_output_allowed", False),
        ("squid_proxy_planned_for_step102", True),
        ("runtime_geometry_planned_for_step102", True),
        ("wall_velocity_planned_for_step102", True),
        ("combined_runtime_geometry_wall_velocity_planned_for_step102", True),
    ]
    return [literal_row("step102_48cube_10step_ggui_visual_run_plan", check, summary[check], expected) for check, expected in checks]


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
