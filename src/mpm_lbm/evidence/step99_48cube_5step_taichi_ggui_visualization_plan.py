from __future__ import annotations

import json
from pathlib import Path


STEP100_ROW = "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_48_5step_ggui_visual_run"

EXPECTED_PLAN_VALUES = {
    "step": "Step99",
    "previous_step": "Step98",
    "previous_required_commit": "3142aea8361fd67c4799143ee56f95b8a09b3286",
    "activation_kind": "48cube_5step_taichi_ggui_visualization_plan_only",
    "driver_run_required": False,
    "fsidriver_run_allowed": False,
    "simulation_run_allowed": False,
    "ggui_run_allowed": False,
    "screenshot_output_allowed_in_step99": False,
    "step100_allowed": True,
    "step100_allowed_row_name": STEP100_ROW,
    "step100_allowed_n_grid": 48,
    "step100_allowed_n_particles": 1024,
    "step100_allowed_n_lbm_steps": 5,
    "step100_allowed_mpm_substeps_per_lbm_step": 1,
    "step100_allowed_coupling_mode": "moving_boundary",
    "step100_allowed_reaction_transfer_mode": "engineering",
    "step100_allowed_output_interval": 1,
    "from_step98_duration_expansion": True,
    "previous_step98_n_grid": 48,
    "previous_step98_n_lbm_steps": 1,
    "planned_step100_n_grid": 48,
    "planned_step100_n_lbm_steps": 5,
    "only_new_dimension_from_step98": "n_lbm_steps_5",
    "ggui_visualization_planned_for_step100": True,
    "ggui_interactive_window_allowed_for_step100": True,
    "ggui_screenshot_allowed_for_step100": True,
    "ggui_screenshot_count_allowed_for_step100": 1,
    "ggui_video_allowed_for_step100": False,
    "ggui_required_backend_policy": "local_desktop_taichi_environment",
    "squid_proxy_planned_for_step100": True,
    "geometry_type_allowed_for_step100": "squid_proxy",
    "geometry_config_path_allowed_for_step100": "configs/step85_squid_proxy_geometry_1024.json",
    "quality_check_enabled_allowed_for_step100": True,
    "quality_check_strict_allowed_for_step100": False,
    "geometry_quality_report_required_for_step100": True,
    "runtime_geometry_planned_for_step100": True,
    "geometry_motion_mode_allowed_for_step100": "prescribed_kinematic",
    "geometry_motion_application_mode_allowed_for_step100": "diagnostic_only",
    "geometry_motion_config_path_allowed_for_step100": (
        "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json"
    ),
    "geometry_motion_application_config_path_allowed_for_step100": (
        "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json"
    ),
    "geometry_motion_interface_report_required_for_step100": True,
    "geometry_motion_application_report_required_for_step100": True,
    "geometry_mutation_allowed": False,
    "wall_velocity_planned_for_step100": True,
    "boundary_motion_mode_allowed_for_step100": "prescribed_kinematic",
    "boundary_motion_config_path_allowed_for_step100": (
        "configs/step34_boundary_motion_interface_prescribed_kinematic.json"
    ),
    "boundary_motion_report_required_for_step100": True,
    "wall_velocity_application_mode_allowed_for_step100": "solid_vel_experimental",
    "wall_velocity_application_config_path_allowed_for_step100": (
        "configs/step36_wall_velocity_application_solid_vel_experimental.json"
    ),
    "wall_velocity_application_report_required_for_step100": True,
    "target_lbm_field_planned_for_step100": "solid_vel",
    "target_u_lbm_allowed_for_step100": [0.0, 0.0, 0.0],
    "target_u_lbm_policy": "same_zero_background_flow_as_step90_step92_step94_step96_step98",
    "combined_runtime_geometry_wall_velocity_planned_for_step100": True,
    "planned_step100_activation_feature_count": 5,
    "step99_activation_feature_count": 0,
    "write_vtk_allowed": False,
    "write_particles_allowed": False,
    "vtr_output_allowed": False,
    "particle_npy_output_allowed": False,
    "video_output_allowed": False,
    "real_geometry_allowed": False,
    "real_geometry_candidate_data_allowed": False,
    "link_area_allowed": False,
    "grid_64_allowed": False,
    "dense_wall_velocity_output_allowed": False,
    "dense_displacement_output_allowed": False,
    "runtime_code_changed": False,
    "solver_behavior_changed": False,
    "solver_formula_change_allowed": False,
    "tau_migration_allowed": False,
    "physical_validation_claim_allowed": False,
    "production_readiness_claim_allowed": False,
    "real_squid_validation_claim_allowed": False,
    "squid_swimming_claim_allowed": False,
    "squid_actuation_claim_allowed": False,
}


def build_step99_48cube_5step_taichi_ggui_visualization_plan(
    root: Path,
    plan_path: str = "configs/step99_48cube_5step_taichi_ggui_visualization_plan.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    plan = read_json(root / plan_path)
    rows = [plan_row(plan, key, expected) for key, expected in EXPECTED_PLAN_VALUES.items()]
    summary = {key: plan[key] for key in EXPECTED_PLAN_VALUES}
    summary.update(
        {
            "pass_count": sum(1 for row in rows if row["pass"]),
            "previous_commit": plan["previous_required_commit"],
            "row_count": len(rows),
            "step99_48cube_5step_taichi_ggui_visualization_plan_pass": False,
        }
    )
    summary["step99_48cube_5step_taichi_ggui_visualization_plan_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["driver_run_required"] is False
        and summary["fsidriver_run_allowed"] is False
        and summary["simulation_run_allowed"] is False
        and summary["ggui_run_allowed"] is False
        and summary["screenshot_output_allowed_in_step99"] is False
        and summary["step100_allowed"] is True
        and summary["step100_allowed_row_name"] == STEP100_ROW
        and summary["step100_allowed_n_grid"] == 48
        and summary["step100_allowed_n_particles"] == 1024
        and summary["step100_allowed_n_lbm_steps"] == 5
        and summary["step100_allowed_mpm_substeps_per_lbm_step"] == 1
        and summary["from_step98_duration_expansion"] is True
        and summary["previous_step98_n_grid"] == 48
        and summary["previous_step98_n_lbm_steps"] == 1
        and summary["planned_step100_n_grid"] == 48
        and summary["planned_step100_n_lbm_steps"] == 5
        and summary["only_new_dimension_from_step98"] == "n_lbm_steps_5"
        and summary["ggui_visualization_planned_for_step100"] is True
        and summary["ggui_screenshot_allowed_for_step100"] is True
        and summary["ggui_video_allowed_for_step100"] is False
        and summary["step99_activation_feature_count"] == 0
        and summary["planned_step100_activation_feature_count"] == 5
        and summary["write_vtk_allowed"] is False
        and summary["write_particles_allowed"] is False
        and summary["vtr_output_allowed"] is False
        and summary["particle_npy_output_allowed"] is False
        and summary["video_output_allowed"] is False
        and summary["squid_proxy_planned_for_step100"] is True
        and summary["runtime_geometry_planned_for_step100"] is True
        and summary["wall_velocity_planned_for_step100"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step100"] is True
        and summary["target_u_lbm_allowed_for_step100"] == [0.0, 0.0, 0.0]
        and summary["real_geometry_allowed"] is False
        and summary["real_geometry_candidate_data_allowed"] is False
        and summary["link_area_allowed"] is False
        and summary["grid_64_allowed"] is False
        and summary["solver_behavior_changed"] is False
        and summary["physical_validation_claim_allowed"] is False
    )
    return rows, summary


def plan_row(plan: dict, key: str, expected) -> dict:
    actual = plan.get(key)
    return {
        "actual": actual,
        "check": key,
        "expected": expected,
        "pass": actual == expected,
        "row_name": plan.get("step100_allowed_row_name", ""),
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
