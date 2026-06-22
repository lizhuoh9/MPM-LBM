from __future__ import annotations

import json
from pathlib import Path


EXPECTED_PLAN_VALUES = {
    "step": "Step79",
    "previous_step": "Step78",
    "previous_required_commit": "d226b1fc679f7d5592629a359c56f0b83372a393",
    "activation_kind": "single_feature_plan_only",
    "feature_under_plan": "runtime_geometry",
    "runtime_geometry_activation_planned": True,
    "runtime_geometry_application_mode_planned_for_step80": "diagnostic_only",
    "driver_run_required": False,
    "fsidriver_run_allowed": False,
    "simulation_run_allowed": False,
    "step80_allowed": True,
    "step80_allowed_row_name": "canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke",
    "step80_allowed_n_grid": 32,
    "step80_allowed_n_particles": 1024,
    "step80_allowed_n_lbm_steps": 3,
    "step80_allowed_mpm_substeps_per_lbm_step": 1,
    "step80_allowed_coupling_mode": "moving_boundary",
    "step80_allowed_reaction_transfer_mode": "engineering",
    "step80_allowed_geometry_type": "box",
    "geometry_motion_mode_allowed_for_step80": "prescribed_kinematic",
    "geometry_motion_application_mode_allowed_for_step80": "diagnostic_only",
    "geometry_motion_report_required_for_step80": True,
    "geometry_motion_interface_report_required_for_step80": True,
    "geometry_mutation_allowed": False,
    "runtime_code_changed": False,
    "solver_behavior_changed": False,
    "solver_formula_change_allowed": False,
    "tau_migration_allowed": False,
    "wall_velocity_allowed": False,
    "combined_runtime_geometry_wall_velocity_allowed": False,
    "real_geometry_allowed": False,
    "squid_proxy_allowed": False,
    "link_area_allowed": False,
    "grid_48_allowed": False,
    "grid_64_allowed": False,
    "vtr_output_allowed": False,
    "particle_npy_output_allowed": False,
    "physical_validation_claim_allowed": False,
    "production_readiness_claim_allowed": False,
    "real_squid_validation_claim_allowed": False,
}


def build_step79_runtime_geometry_diagnostic_only_activation_plan(
    root: Path,
    plan_path: str = "configs/step79_runtime_geometry_diagnostic_only_activation_plan.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    plan = read_json(root / plan_path)
    rows = [plan_row(plan, key, expected) for key, expected in EXPECTED_PLAN_VALUES.items()]

    summary = {
        "combined_runtime_geometry_wall_velocity_allowed": plan["combined_runtime_geometry_wall_velocity_allowed"],
        "driver_run_required": plan["driver_run_required"],
        "fsidriver_run_allowed": plan["fsidriver_run_allowed"],
        "geometry_motion_application_mode_allowed_for_step80": plan[
            "geometry_motion_application_mode_allowed_for_step80"
        ],
        "geometry_motion_interface_report_required_for_step80": plan[
            "geometry_motion_interface_report_required_for_step80"
        ],
        "geometry_motion_mode_allowed_for_step80": plan["geometry_motion_mode_allowed_for_step80"],
        "geometry_motion_report_required_for_step80": plan["geometry_motion_report_required_for_step80"],
        "geometry_mutation_allowed": plan["geometry_mutation_allowed"],
        "grid_48_allowed": plan["grid_48_allowed"],
        "grid_64_allowed": plan["grid_64_allowed"],
        "link_area_allowed": plan["link_area_allowed"],
        "particle_npy_output_allowed": plan["particle_npy_output_allowed"],
        "pass_count": sum(1 for row in rows if row["pass"]),
        "physical_validation_claim_allowed": plan["physical_validation_claim_allowed"],
        "planned_step80_activation_feature_count": int(plan["runtime_geometry_activation_planned"]),
        "previous_commit": plan["previous_required_commit"],
        "previous_step": plan["previous_step"],
        "production_readiness_claim_allowed": plan["production_readiness_claim_allowed"],
        "real_geometry_allowed": plan["real_geometry_allowed"],
        "real_squid_validation_claim_allowed": plan["real_squid_validation_claim_allowed"],
        "row_count": len(rows),
        "runtime_code_changed": plan["runtime_code_changed"],
        "runtime_geometry_activation_planned": plan["runtime_geometry_activation_planned"],
        "runtime_geometry_application_mode_planned_for_step80": plan[
            "runtime_geometry_application_mode_planned_for_step80"
        ],
        "simulation_run_allowed": plan["simulation_run_allowed"],
        "solver_behavior_changed": plan["solver_behavior_changed"],
        "solver_formula_change_allowed": plan["solver_formula_change_allowed"],
        "squid_proxy_allowed": plan["squid_proxy_allowed"],
        "step79_activation_feature_count": 0,
        "step79_runtime_geometry_diagnostic_only_activation_plan_pass": False,
        "step80_allowed": plan["step80_allowed"],
        "step80_allowed_coupling_mode": plan["step80_allowed_coupling_mode"],
        "step80_allowed_geometry_type": plan["step80_allowed_geometry_type"],
        "step80_allowed_mpm_substeps_per_lbm_step": plan["step80_allowed_mpm_substeps_per_lbm_step"],
        "step80_allowed_n_grid": plan["step80_allowed_n_grid"],
        "step80_allowed_n_lbm_steps": plan["step80_allowed_n_lbm_steps"],
        "step80_allowed_n_particles": plan["step80_allowed_n_particles"],
        "step80_allowed_reaction_transfer_mode": plan["step80_allowed_reaction_transfer_mode"],
        "step80_allowed_row_count": int(plan["step80_allowed"]),
        "step80_allowed_row_name": plan["step80_allowed_row_name"],
        "tau_migration_allowed": plan["tau_migration_allowed"],
        "vtr_output_allowed": plan["vtr_output_allowed"],
        "wall_velocity_allowed": plan["wall_velocity_allowed"],
    }
    summary["step79_runtime_geometry_diagnostic_only_activation_plan_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["step79_activation_feature_count"] == 0
        and summary["planned_step80_activation_feature_count"] == 1
        and summary["driver_run_required"] is False
        and summary["fsidriver_run_allowed"] is False
        and summary["simulation_run_allowed"] is False
        and summary["geometry_mutation_allowed"] is False
        and summary["solver_formula_change_allowed"] is False
    )
    return rows, summary


def plan_row(plan: dict, key: str, expected) -> dict:
    row_name = plan.get("step80_allowed_row_name", "") if key.startswith("step80_") else ""
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
