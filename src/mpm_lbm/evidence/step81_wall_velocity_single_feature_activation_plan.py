from __future__ import annotations

import json
from pathlib import Path


EXPECTED_PLAN_VALUES = {
    "step": "Step81",
    "previous_step": "Step80",
    "previous_required_commit": "a2fbdfa6a9af0f02901e16e92b276c2055755fe1",
    "activation_kind": "single_feature_plan_only",
    "feature_under_plan": "wall_velocity",
    "wall_velocity_activation_planned": True,
    "wall_velocity_application_mode_planned_for_step82": "solid_vel_experimental",
    "target_lbm_field_planned_for_step82": "solid_vel",
    "driver_run_required": False,
    "fsidriver_run_allowed": False,
    "simulation_run_allowed": False,
    "step82_allowed": True,
    "step82_allowed_row_name": "canonical_driver_wall_velocity_solid_vel_32_3step_smoke",
    "step82_allowed_n_grid": 32,
    "step82_allowed_n_particles": 1024,
    "step82_allowed_n_lbm_steps": 3,
    "step82_allowed_mpm_substeps_per_lbm_step": 1,
    "step82_allowed_coupling_mode": "moving_boundary",
    "step82_allowed_reaction_transfer_mode": "engineering",
    "step82_allowed_geometry_type": "box",
    "boundary_motion_mode_allowed_for_step82": "prescribed_kinematic",
    "boundary_motion_config_path_allowed_for_step82": (
        "configs/step34_boundary_motion_interface_prescribed_kinematic.json"
    ),
    "wall_velocity_application_mode_allowed_for_step82": "solid_vel_experimental",
    "wall_velocity_application_config_path_allowed_for_step82": (
        "configs/step36_wall_velocity_application_solid_vel_experimental.json"
    ),
    "wall_velocity_application_report_required_for_step82": True,
    "apply_to_lbm_solid_vel_allowed": True,
    "apply_to_lbm_populations_allowed": False,
    "apply_to_mpm_allowed": False,
    "apply_to_projector_allowed": False,
    "modify_bounceback_formula_allowed": False,
    "jet_model_allowed": False,
    "actuation_claim_allowed": False,
    "runtime_geometry_allowed": False,
    "combined_runtime_geometry_wall_velocity_allowed": False,
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


def build_step81_wall_velocity_single_feature_activation_plan(
    root: Path,
    plan_path: str = "configs/step81_wall_velocity_single_feature_activation_plan.json",
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
        "boundary_motion_config_path_allowed_for_step82": plan[
            "boundary_motion_config_path_allowed_for_step82"
        ],
        "boundary_motion_mode_allowed_for_step82": plan["boundary_motion_mode_allowed_for_step82"],
        "combined_runtime_geometry_wall_velocity_allowed": plan[
            "combined_runtime_geometry_wall_velocity_allowed"
        ],
        "driver_run_required": plan["driver_run_required"],
        "fsidriver_run_allowed": plan["fsidriver_run_allowed"],
        "grid_48_allowed": plan["grid_48_allowed"],
        "grid_64_allowed": plan["grid_64_allowed"],
        "jet_model_allowed": plan["jet_model_allowed"],
        "link_area_allowed": plan["link_area_allowed"],
        "modify_bounceback_formula_allowed": plan["modify_bounceback_formula_allowed"],
        "particle_npy_output_allowed": plan["particle_npy_output_allowed"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "physical_validation_claim_allowed": plan["physical_validation_claim_allowed"],
        "planned_step82_activation_feature_count": int(plan["wall_velocity_activation_planned"]),
        "previous_commit": plan["previous_required_commit"],
        "previous_step": plan["previous_step"],
        "production_readiness_claim_allowed": plan["production_readiness_claim_allowed"],
        "real_geometry_allowed": plan["real_geometry_allowed"],
        "real_squid_validation_claim_allowed": plan["real_squid_validation_claim_allowed"],
        "row_count": len(rows),
        "runtime_code_changed": plan["runtime_code_changed"],
        "runtime_geometry_allowed": plan["runtime_geometry_allowed"],
        "simulation_run_allowed": plan["simulation_run_allowed"],
        "solver_behavior_changed": plan["solver_behavior_changed"],
        "solver_formula_change_allowed": plan["solver_formula_change_allowed"],
        "squid_proxy_allowed": plan["squid_proxy_allowed"],
        "step81_activation_feature_count": 0,
        "step81_wall_velocity_single_feature_activation_plan_pass": False,
        "step82_allowed": plan["step82_allowed"],
        "step82_allowed_coupling_mode": plan["step82_allowed_coupling_mode"],
        "step82_allowed_geometry_type": plan["step82_allowed_geometry_type"],
        "step82_allowed_mpm_substeps_per_lbm_step": plan["step82_allowed_mpm_substeps_per_lbm_step"],
        "step82_allowed_n_grid": plan["step82_allowed_n_grid"],
        "step82_allowed_n_lbm_steps": plan["step82_allowed_n_lbm_steps"],
        "step82_allowed_n_particles": plan["step82_allowed_n_particles"],
        "step82_allowed_reaction_transfer_mode": plan["step82_allowed_reaction_transfer_mode"],
        "step82_allowed_row_count": int(plan["step82_allowed"]),
        "step82_allowed_row_name": plan["step82_allowed_row_name"],
        "target_lbm_field_planned_for_step82": plan["target_lbm_field_planned_for_step82"],
        "tau_migration_allowed": plan["tau_migration_allowed"],
        "vtr_output_allowed": plan["vtr_output_allowed"],
        "wall_velocity_activation_planned": plan["wall_velocity_activation_planned"],
        "wall_velocity_application_config_path_allowed_for_step82": plan[
            "wall_velocity_application_config_path_allowed_for_step82"
        ],
        "wall_velocity_application_mode_allowed_for_step82": plan[
            "wall_velocity_application_mode_allowed_for_step82"
        ],
        "wall_velocity_application_mode_planned_for_step82": plan[
            "wall_velocity_application_mode_planned_for_step82"
        ],
        "wall_velocity_application_report_required_for_step82": plan[
            "wall_velocity_application_report_required_for_step82"
        ],
    }
    summary["step81_wall_velocity_single_feature_activation_plan_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["step81_activation_feature_count"] == 0
        and summary["planned_step82_activation_feature_count"] == 1
        and summary["driver_run_required"] is False
        and summary["fsidriver_run_allowed"] is False
        and summary["simulation_run_allowed"] is False
        and summary["runtime_geometry_allowed"] is False
        and summary["combined_runtime_geometry_wall_velocity_allowed"] is False
        and summary["solver_formula_change_allowed"] is False
    )
    return rows, summary


def plan_row(plan: dict, key: str, expected) -> dict:
    row_name = plan.get("step82_allowed_row_name", "") if key.startswith("step82_") else ""
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
