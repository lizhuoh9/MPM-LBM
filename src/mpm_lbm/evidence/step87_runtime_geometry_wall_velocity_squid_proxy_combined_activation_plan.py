from __future__ import annotations

import json
from pathlib import Path


EXPECTED_PLAN_VALUES = {
    "step": "Step87",
    "previous_step": "Step86",
    "previous_required_commit": "e69e11971728a370465e54f753988d2b9ab228b5",
    "activation_kind": "combined_feature_plan_only",
    "features_under_plan": [
        "squid_proxy_static_geometry",
        "runtime_geometry_diagnostic_only",
        "wall_velocity_solid_vel",
    ],
    "driver_run_required": False,
    "fsidriver_run_allowed": False,
    "simulation_run_allowed": False,
    "step88_allowed": True,
    "step88_allowed_row_name": "canonical_driver_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke",
    "step88_allowed_n_grid": 32,
    "step88_allowed_n_particles": 1024,
    "step88_allowed_n_lbm_steps": 3,
    "step88_allowed_mpm_substeps_per_lbm_step": 1,
    "step88_allowed_coupling_mode": "moving_boundary",
    "step88_allowed_reaction_transfer_mode": "engineering",
    "squid_proxy_planned_for_step88": True,
    "geometry_type_allowed_for_step88": "squid_proxy",
    "geometry_config_path_allowed_for_step88": "configs/step85_squid_proxy_geometry_1024.json",
    "quality_check_enabled_allowed_for_step88": True,
    "quality_check_strict_allowed_for_step88": False,
    "geometry_quality_report_required_for_step88": True,
    "runtime_geometry_planned_for_step88": True,
    "geometry_motion_mode_allowed_for_step88": "prescribed_kinematic",
    "geometry_motion_application_mode_allowed_for_step88": "diagnostic_only",
    "geometry_motion_config_path_allowed_for_step88": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
    "geometry_motion_application_config_path_allowed_for_step88": "configs/step80_geometry_motion_interface_prescribed_diagnostic_only.json",
    "geometry_motion_interface_report_required_for_step88": True,
    "geometry_motion_application_report_required_for_step88": True,
    "geometry_mutation_allowed": False,
    "wall_velocity_planned_for_step88": True,
    "boundary_motion_mode_allowed_for_step88": "prescribed_kinematic",
    "boundary_motion_config_path_allowed_for_step88": "configs/step34_boundary_motion_interface_prescribed_kinematic.json",
    "boundary_motion_report_required_for_step88": True,
    "wall_velocity_application_mode_allowed_for_step88": "solid_vel_experimental",
    "wall_velocity_application_config_path_allowed_for_step88": "configs/step36_wall_velocity_application_solid_vel_experimental.json",
    "wall_velocity_application_report_required_for_step88": True,
    "target_lbm_field_planned_for_step88": "solid_vel",
    "combined_runtime_geometry_wall_velocity_planned_for_step88": True,
    "planned_step88_activation_feature_count": 3,
    "step87_activation_feature_count": 0,
    "apply_to_lbm_solid_vel_allowed": True,
    "apply_to_lbm_populations_allowed": False,
    "apply_to_mpm_allowed": False,
    "apply_to_projector_allowed": False,
    "modify_bounceback_formula_allowed": False,
    "jet_model_allowed": False,
    "actuation_claim_allowed": False,
    "real_geometry_allowed": False,
    "real_geometry_candidate_data_allowed": False,
    "link_area_allowed": False,
    "grid_48_allowed": False,
    "grid_64_allowed": False,
    "vtr_output_allowed": False,
    "particle_npy_output_allowed": False,
    "write_vtk_allowed_for_step88": False,
    "write_particles_allowed_for_step88": False,
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


def build_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan(
    root: Path,
    plan_path: str = "configs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.json",
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
            "step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass": False,
        }
    )
    summary["step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["driver_run_required"] is False
        and summary["fsidriver_run_allowed"] is False
        and summary["simulation_run_allowed"] is False
        and summary["squid_proxy_planned_for_step88"] is True
        and summary["runtime_geometry_planned_for_step88"] is True
        and summary["wall_velocity_planned_for_step88"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step88"] is True
        and summary["step87_activation_feature_count"] == 0
        and summary["planned_step88_activation_feature_count"] == 3
        and summary["real_geometry_allowed"] is False
        and summary["real_geometry_candidate_data_allowed"] is False
        and summary["link_area_allowed"] is False
        and summary["vtr_output_allowed"] is False
        and summary["particle_npy_output_allowed"] is False
    )
    return rows, summary


def plan_row(plan: dict, key: str, expected) -> dict:
    actual = plan.get(key)
    row_name = plan.get("step88_allowed_row_name", "") if "step88" in key else ""
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
