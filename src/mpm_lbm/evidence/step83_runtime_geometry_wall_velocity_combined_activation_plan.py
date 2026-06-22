from __future__ import annotations

import json
from pathlib import Path


EXPECTED_PLAN_VALUES = {
    "step": "Step83",
    "previous_step": "Step82",
    "previous_required_commit": "3df6bb25b32d74f16300b8ba603c843eecc725c2",
    "activation_kind": "combined_feature_plan_only",
    "features_under_plan": ["runtime_geometry_diagnostic_only", "wall_velocity_solid_vel"],
    "driver_run_required": False,
    "fsidriver_run_allowed": False,
    "simulation_run_allowed": False,
    "step84_allowed": True,
    "step84_allowed_row_name": "canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke",
    "step84_allowed_n_grid": 32,
    "step84_allowed_n_particles": 1024,
    "step84_allowed_n_lbm_steps": 3,
    "step84_allowed_mpm_substeps_per_lbm_step": 1,
    "step84_allowed_coupling_mode": "moving_boundary",
    "step84_allowed_reaction_transfer_mode": "engineering",
    "step84_allowed_geometry_type": "box",
    "runtime_geometry_planned_for_step84": True,
    "geometry_motion_mode_allowed_for_step84": "prescribed_kinematic",
    "geometry_motion_application_mode_allowed_for_step84": "diagnostic_only",
    "geometry_motion_config_path_allowed_for_step84": (
        "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json"
    ),
    "geometry_motion_application_config_path_allowed_for_step84": (
        "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json"
    ),
    "geometry_motion_interface_report_required_for_step84": True,
    "geometry_mutation_allowed": False,
    "wall_velocity_planned_for_step84": True,
    "boundary_motion_mode_allowed_for_step84": "prescribed_kinematic",
    "boundary_motion_config_path_allowed_for_step84": (
        "configs/step34_boundary_motion_interface_prescribed_kinematic.json"
    ),
    "wall_velocity_application_mode_allowed_for_step84": "solid_vel_experimental",
    "wall_velocity_application_config_path_allowed_for_step84": (
        "configs/step36_wall_velocity_application_solid_vel_experimental.json"
    ),
    "wall_velocity_application_report_required_for_step84": True,
    "target_lbm_field_planned_for_step84": "solid_vel",
    "combined_runtime_geometry_wall_velocity_planned_for_step84": True,
    "planned_step84_activation_feature_count": 2,
    "step83_activation_feature_count": 0,
    "apply_to_lbm_solid_vel_allowed": True,
    "apply_to_lbm_populations_allowed": False,
    "apply_to_mpm_allowed": False,
    "apply_to_projector_allowed": False,
    "modify_bounceback_formula_allowed": False,
    "jet_model_allowed": False,
    "actuation_claim_allowed": False,
    "real_geometry_allowed": False,
    "squid_proxy_allowed": False,
    "link_area_allowed": False,
    "grid_48_allowed": False,
    "grid_64_allowed": False,
    "vtr_output_allowed": False,
    "particle_npy_output_allowed": False,
    "runtime_code_changed": False,
    "solver_behavior_changed": False,
    "solver_formula_change_allowed": False,
    "tau_migration_allowed": False,
    "physical_validation_claim_allowed": False,
    "production_readiness_claim_allowed": False,
    "real_squid_validation_claim_allowed": False,
}


def build_step83_runtime_geometry_wall_velocity_combined_activation_plan(
    root: Path,
    plan_path: str = "configs/step83_runtime_geometry_wall_velocity_combined_activation_plan.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    plan = read_json(root / plan_path)
    rows = [plan_row(plan, key, expected) for key, expected in EXPECTED_PLAN_VALUES.items()]
    summary = {
        "actuation_claim_allowed": plan["actuation_claim_allowed"],
        "apply_to_lbm_populations_allowed": plan["apply_to_lbm_populations_allowed"],
        "apply_to_lbm_solid_vel_allowed": plan["apply_to_lbm_solid_vel_allowed"],
        "apply_to_mpm_allowed": plan["apply_to_mpm_allowed"],
        "apply_to_projector_allowed": plan["apply_to_projector_allowed"],
        "boundary_motion_config_path_allowed_for_step84": plan[
            "boundary_motion_config_path_allowed_for_step84"
        ],
        "boundary_motion_mode_allowed_for_step84": plan["boundary_motion_mode_allowed_for_step84"],
        "combined_runtime_geometry_wall_velocity_planned_for_step84": plan[
            "combined_runtime_geometry_wall_velocity_planned_for_step84"
        ],
        "driver_run_required": plan["driver_run_required"],
        "features_under_plan": plan["features_under_plan"],
        "fsidriver_run_allowed": plan["fsidriver_run_allowed"],
        "geometry_motion_application_config_path_allowed_for_step84": plan[
            "geometry_motion_application_config_path_allowed_for_step84"
        ],
        "geometry_motion_application_mode_allowed_for_step84": plan[
            "geometry_motion_application_mode_allowed_for_step84"
        ],
        "geometry_motion_config_path_allowed_for_step84": plan["geometry_motion_config_path_allowed_for_step84"],
        "geometry_motion_interface_report_required_for_step84": plan[
            "geometry_motion_interface_report_required_for_step84"
        ],
        "geometry_motion_mode_allowed_for_step84": plan["geometry_motion_mode_allowed_for_step84"],
        "geometry_mutation_allowed": plan["geometry_mutation_allowed"],
        "grid_48_allowed": plan["grid_48_allowed"],
        "grid_64_allowed": plan["grid_64_allowed"],
        "jet_model_allowed": plan["jet_model_allowed"],
        "link_area_allowed": plan["link_area_allowed"],
        "modify_bounceback_formula_allowed": plan["modify_bounceback_formula_allowed"],
        "particle_npy_output_allowed": plan["particle_npy_output_allowed"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "physical_validation_claim_allowed": plan["physical_validation_claim_allowed"],
        "planned_step84_activation_feature_count": plan["planned_step84_activation_feature_count"],
        "previous_commit": plan["previous_required_commit"],
        "previous_step": plan["previous_step"],
        "production_readiness_claim_allowed": plan["production_readiness_claim_allowed"],
        "real_geometry_allowed": plan["real_geometry_allowed"],
        "real_squid_validation_claim_allowed": plan["real_squid_validation_claim_allowed"],
        "row_count": len(rows),
        "runtime_code_changed": plan["runtime_code_changed"],
        "runtime_geometry_planned_for_step84": plan["runtime_geometry_planned_for_step84"],
        "simulation_run_allowed": plan["simulation_run_allowed"],
        "solver_behavior_changed": plan["solver_behavior_changed"],
        "solver_formula_change_allowed": plan["solver_formula_change_allowed"],
        "squid_proxy_allowed": plan["squid_proxy_allowed"],
        "step83_activation_feature_count": plan["step83_activation_feature_count"],
        "step83_runtime_geometry_wall_velocity_combined_activation_plan_pass": False,
        "step84_allowed": plan["step84_allowed"],
        "step84_allowed_coupling_mode": plan["step84_allowed_coupling_mode"],
        "step84_allowed_geometry_type": plan["step84_allowed_geometry_type"],
        "step84_allowed_mpm_substeps_per_lbm_step": plan["step84_allowed_mpm_substeps_per_lbm_step"],
        "step84_allowed_n_grid": plan["step84_allowed_n_grid"],
        "step84_allowed_n_lbm_steps": plan["step84_allowed_n_lbm_steps"],
        "step84_allowed_n_particles": plan["step84_allowed_n_particles"],
        "step84_allowed_reaction_transfer_mode": plan["step84_allowed_reaction_transfer_mode"],
        "step84_allowed_row_count": int(plan["step84_allowed"]),
        "step84_allowed_row_name": plan["step84_allowed_row_name"],
        "target_lbm_field_planned_for_step84": plan["target_lbm_field_planned_for_step84"],
        "tau_migration_allowed": plan["tau_migration_allowed"],
        "vtr_output_allowed": plan["vtr_output_allowed"],
        "wall_velocity_application_config_path_allowed_for_step84": plan[
            "wall_velocity_application_config_path_allowed_for_step84"
        ],
        "wall_velocity_application_mode_allowed_for_step84": plan[
            "wall_velocity_application_mode_allowed_for_step84"
        ],
        "wall_velocity_application_report_required_for_step84": plan[
            "wall_velocity_application_report_required_for_step84"
        ],
        "wall_velocity_planned_for_step84": plan["wall_velocity_planned_for_step84"],
    }
    summary["step83_runtime_geometry_wall_velocity_combined_activation_plan_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["step83_activation_feature_count"] == 0
        and summary["planned_step84_activation_feature_count"] == 2
        and summary["driver_run_required"] is False
        and summary["fsidriver_run_allowed"] is False
        and summary["simulation_run_allowed"] is False
        and summary["runtime_geometry_planned_for_step84"] is True
        and summary["wall_velocity_planned_for_step84"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step84"] is True
        and summary["geometry_mutation_allowed"] is False
        and summary["solver_formula_change_allowed"] is False
    )
    return rows, summary


def plan_row(plan: dict, key: str, expected) -> dict:
    row_name = plan.get("step84_allowed_row_name", "") if "step84" in key else ""
    actual = plan.get(key)
    return {
        "actual": actual,
        "check": key,
        "expected": expected,
        "pass": actual == expected,
        "row_name": row_name,
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
