from __future__ import annotations

import json
from pathlib import Path


EXPECTED_PLAN_VALUES = {
    "step": "Step89",
    "previous_step": "Step88",
    "previous_required_commit": "f83ddcd1a0979ed6dbe41c6a9763d891e9c66b9f",
    "activation_kind": "first_user_simulation_dry_run_plan_only",
    "features_under_plan": [
        "squid_proxy_static_geometry",
        "runtime_geometry_diagnostic_only",
        "wall_velocity_solid_vel",
    ],
    "driver_run_required": False,
    "fsidriver_run_allowed": False,
    "simulation_run_allowed": False,
    "step90_allowed": True,
    "step90_allowed_row_name": "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run",
    "step90_allowed_n_grid": 32,
    "step90_allowed_n_particles": 1024,
    "step90_allowed_n_lbm_steps": 5,
    "step90_allowed_mpm_substeps_per_lbm_step": 1,
    "step90_allowed_coupling_mode": "moving_boundary",
    "step90_allowed_reaction_transfer_mode": "engineering",
    "step90_allowed_output_interval": 1,
    "squid_proxy_planned_for_step90": True,
    "geometry_type_allowed_for_step90": "squid_proxy",
    "geometry_config_path_allowed_for_step90": "configs/step85_squid_proxy_geometry_1024.json",
    "quality_check_enabled_allowed_for_step90": True,
    "quality_check_strict_allowed_for_step90": False,
    "geometry_quality_report_required_for_step90": True,
    "runtime_geometry_planned_for_step90": True,
    "geometry_motion_mode_allowed_for_step90": "prescribed_kinematic",
    "geometry_motion_application_mode_allowed_for_step90": "diagnostic_only",
    "geometry_motion_config_path_allowed_for_step90": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
    "geometry_motion_application_config_path_allowed_for_step90": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
    "geometry_motion_interface_report_required_for_step90": True,
    "geometry_motion_application_report_required_for_step90": True,
    "geometry_mutation_allowed": False,
    "wall_velocity_planned_for_step90": True,
    "boundary_motion_mode_allowed_for_step90": "prescribed_kinematic",
    "boundary_motion_config_path_allowed_for_step90": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
    "boundary_motion_report_required_for_step90": True,
    "wall_velocity_application_mode_allowed_for_step90": "solid_vel_experimental",
    "wall_velocity_application_config_path_allowed_for_step90": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
    "wall_velocity_application_report_required_for_step90": True,
    "target_lbm_field_planned_for_step90": "solid_vel",
    "target_u_lbm_allowed_for_step90": [0.0, 0.0, 0.0],
    "target_u_lbm_policy": "row_local_zero_background_flow_for_first_user_dry_run",
    "combined_runtime_geometry_wall_velocity_planned_for_step90": True,
    "planned_step90_activation_feature_count": 3,
    "step89_activation_feature_count": 0,
    "write_vtk_allowed": False,
    "write_particles_allowed": False,
    "real_geometry_allowed": False,
    "real_geometry_candidate_data_allowed": False,
    "link_area_allowed": False,
    "grid_48_allowed": False,
    "grid_64_allowed": False,
    "vtr_output_allowed": False,
    "particle_npy_output_allowed": False,
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


def build_step89_first_user_simulation_dry_run_plan(
    root: Path,
    plan_path: str = "configs/step89_first_user_simulation_dry_run_plan.json",
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
            "step89_first_user_simulation_dry_run_plan_pass": False,
        }
    )
    summary["step89_first_user_simulation_dry_run_plan_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["driver_run_required"] is False
        and summary["fsidriver_run_allowed"] is False
        and summary["simulation_run_allowed"] is False
        and summary["step90_allowed"] is True
        and summary["step90_allowed_n_grid"] == 32
        and summary["step90_allowed_n_particles"] == 1024
        and summary["step90_allowed_n_lbm_steps"] == 5
        and summary["step89_activation_feature_count"] == 0
        and summary["planned_step90_activation_feature_count"] == 3
        and summary["squid_proxy_planned_for_step90"] is True
        and summary["runtime_geometry_planned_for_step90"] is True
        and summary["wall_velocity_planned_for_step90"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step90"] is True
        and summary["target_u_lbm_allowed_for_step90"] == [0.0, 0.0, 0.0]
        and summary["real_geometry_allowed"] is False
        and summary["real_geometry_candidate_data_allowed"] is False
        and summary["link_area_allowed"] is False
        and summary["vtr_output_allowed"] is False
        and summary["particle_npy_output_allowed"] is False
    )
    return rows, summary


def plan_row(plan: dict, key: str, expected) -> dict:
    actual = plan.get(key)
    return {
        "actual": actual,
        "check": key,
        "expected": expected,
        "pass": actual == expected,
        "row_name": plan.get("step90_allowed_row_name", ""),
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
