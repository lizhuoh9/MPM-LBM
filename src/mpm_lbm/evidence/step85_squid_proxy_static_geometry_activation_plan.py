from __future__ import annotations

import json
from pathlib import Path


EXPECTED_PLAN_VALUES = {
    "step": "Step85",
    "previous_step": "Step84",
    "previous_required_commit": "29a130ccef93f095deeaa941b44003720f2291c5",
    "activation_kind": "single_feature_plan_only",
    "feature_under_plan": "squid_proxy_static_geometry",
    "driver_run_required": False,
    "fsidriver_run_allowed": False,
    "simulation_run_allowed": False,
    "step86_allowed": True,
    "step86_allowed_row_name": "canonical_driver_squid_proxy_static_geometry_32_3step_smoke",
    "step86_allowed_n_grid": 32,
    "step86_allowed_n_particles": 1024,
    "step86_allowed_n_lbm_steps": 3,
    "step86_allowed_mpm_substeps_per_lbm_step": 1,
    "step86_allowed_coupling_mode": "moving_boundary",
    "step86_allowed_reaction_transfer_mode": "engineering",
    "step86_allowed_geometry_type": "squid_proxy",
    "squid_proxy_planned_for_step86": True,
    "geometry_type_allowed_for_step86": "squid_proxy",
    "geometry_config_path_allowed_for_step86": "configs/step85_squid_proxy_geometry_1024.json",
    "quality_check_enabled_allowed_for_step86": True,
    "quality_check_strict_allowed_for_step86": False,
    "geometry_quality_report_required_for_step86": True,
    "runtime_geometry_allowed": False,
    "geometry_motion_mode_allowed_for_step86": "static",
    "geometry_motion_application_mode_allowed_for_step86": "disabled",
    "geometry_mutation_allowed": False,
    "wall_velocity_allowed": False,
    "boundary_motion_mode_allowed_for_step86": "static",
    "wall_velocity_application_mode_allowed_for_step86": "disabled",
    "combined_runtime_geometry_wall_velocity_allowed": False,
    "real_geometry_allowed": False,
    "real_geometry_candidate_data_allowed": False,
    "link_area_allowed": False,
    "grid_48_allowed": False,
    "grid_64_allowed": False,
    "vtr_output_allowed": False,
    "particle_npy_output_allowed": False,
    "write_vtk_allowed_for_step86": False,
    "write_particles_allowed_for_step86": False,
    "planned_step86_activation_feature_count": 1,
    "step85_activation_feature_count": 0,
    "runtime_code_changed": False,
    "solver_behavior_changed": False,
    "solver_formula_change_allowed": False,
    "tau_migration_allowed": False,
    "physical_validation_claim_allowed": False,
    "production_readiness_claim_allowed": False,
    "real_squid_validation_claim_allowed": False,
    "squid_swimming_claim_allowed": False,
    "squid_actuation_claim_allowed": False,
    "actuation_claim_allowed": False,
    "jet_model_allowed": False,
}


def build_step85_squid_proxy_static_geometry_activation_plan(
    root: Path,
    plan_path: str = "configs/step85_squid_proxy_static_geometry_activation_plan.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    plan = read_json(root / plan_path)
    rows = [plan_row(plan, key, expected) for key, expected in EXPECTED_PLAN_VALUES.items()]
    summary = {
        "actuation_claim_allowed": plan["actuation_claim_allowed"],
        "boundary_motion_mode_allowed_for_step86": plan["boundary_motion_mode_allowed_for_step86"],
        "combined_runtime_geometry_wall_velocity_allowed": plan["combined_runtime_geometry_wall_velocity_allowed"],
        "driver_run_required": plan["driver_run_required"],
        "feature_under_plan": plan["feature_under_plan"],
        "fsidriver_run_allowed": plan["fsidriver_run_allowed"],
        "geometry_config_path_allowed_for_step86": plan["geometry_config_path_allowed_for_step86"],
        "geometry_motion_application_mode_allowed_for_step86": plan[
            "geometry_motion_application_mode_allowed_for_step86"
        ],
        "geometry_motion_mode_allowed_for_step86": plan["geometry_motion_mode_allowed_for_step86"],
        "geometry_mutation_allowed": plan["geometry_mutation_allowed"],
        "geometry_quality_report_required_for_step86": plan["geometry_quality_report_required_for_step86"],
        "geometry_type_allowed_for_step86": plan["geometry_type_allowed_for_step86"],
        "grid_48_allowed": plan["grid_48_allowed"],
        "grid_64_allowed": plan["grid_64_allowed"],
        "jet_model_allowed": plan["jet_model_allowed"],
        "link_area_allowed": plan["link_area_allowed"],
        "particle_npy_output_allowed": plan["particle_npy_output_allowed"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "physical_validation_claim_allowed": plan["physical_validation_claim_allowed"],
        "planned_step86_activation_feature_count": plan["planned_step86_activation_feature_count"],
        "previous_commit": plan["previous_required_commit"],
        "previous_step": plan["previous_step"],
        "production_readiness_claim_allowed": plan["production_readiness_claim_allowed"],
        "quality_check_enabled_allowed_for_step86": plan["quality_check_enabled_allowed_for_step86"],
        "quality_check_strict_allowed_for_step86": plan["quality_check_strict_allowed_for_step86"],
        "real_geometry_allowed": plan["real_geometry_allowed"],
        "real_geometry_candidate_data_allowed": plan["real_geometry_candidate_data_allowed"],
        "real_squid_validation_claim_allowed": plan["real_squid_validation_claim_allowed"],
        "row_count": len(rows),
        "runtime_code_changed": plan["runtime_code_changed"],
        "runtime_geometry_allowed": plan["runtime_geometry_allowed"],
        "simulation_run_allowed": plan["simulation_run_allowed"],
        "solver_behavior_changed": plan["solver_behavior_changed"],
        "solver_formula_change_allowed": plan["solver_formula_change_allowed"],
        "squid_actuation_claim_allowed": plan["squid_actuation_claim_allowed"],
        "squid_proxy_planned_for_step86": plan["squid_proxy_planned_for_step86"],
        "squid_swimming_claim_allowed": plan["squid_swimming_claim_allowed"],
        "step85_activation_feature_count": plan["step85_activation_feature_count"],
        "step85_squid_proxy_static_geometry_activation_plan_pass": False,
        "step86_allowed": plan["step86_allowed"],
        "step86_allowed_coupling_mode": plan["step86_allowed_coupling_mode"],
        "step86_allowed_geometry_type": plan["step86_allowed_geometry_type"],
        "step86_allowed_mpm_substeps_per_lbm_step": plan["step86_allowed_mpm_substeps_per_lbm_step"],
        "step86_allowed_n_grid": plan["step86_allowed_n_grid"],
        "step86_allowed_n_lbm_steps": plan["step86_allowed_n_lbm_steps"],
        "step86_allowed_n_particles": plan["step86_allowed_n_particles"],
        "step86_allowed_reaction_transfer_mode": plan["step86_allowed_reaction_transfer_mode"],
        "step86_allowed_row_count": int(plan["step86_allowed"]),
        "step86_allowed_row_name": plan["step86_allowed_row_name"],
        "tau_migration_allowed": plan["tau_migration_allowed"],
        "vtr_output_allowed": plan["vtr_output_allowed"],
        "wall_velocity_allowed": plan["wall_velocity_allowed"],
        "wall_velocity_application_mode_allowed_for_step86": plan[
            "wall_velocity_application_mode_allowed_for_step86"
        ],
        "write_particles_allowed_for_step86": plan["write_particles_allowed_for_step86"],
        "write_vtk_allowed_for_step86": plan["write_vtk_allowed_for_step86"],
    }
    summary["step85_squid_proxy_static_geometry_activation_plan_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["step85_activation_feature_count"] == 0
        and summary["planned_step86_activation_feature_count"] == 1
        and summary["driver_run_required"] is False
        and summary["fsidriver_run_allowed"] is False
        and summary["simulation_run_allowed"] is False
        and summary["squid_proxy_planned_for_step86"] is True
        and summary["runtime_geometry_allowed"] is False
        and summary["wall_velocity_allowed"] is False
        and summary["combined_runtime_geometry_wall_velocity_allowed"] is False
        and summary["geometry_mutation_allowed"] is False
        and summary["real_geometry_allowed"] is False
        and summary["solver_formula_change_allowed"] is False
        and summary["tau_migration_allowed"] is False
        and summary["physical_validation_claim_allowed"] is False
    )
    return rows, summary


def plan_row(plan: dict, key: str, expected) -> dict:
    row_name = plan.get("step86_allowed_row_name", "") if "step86" in key else ""
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
