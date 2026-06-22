from __future__ import annotations

import json
from pathlib import Path


PLAN_SUMMARY_CHECKS = {
    "driver_run_required": "expected_driver_run_required",
    "fsidriver_run_allowed": "expected_fsidriver_run_allowed",
    "simulation_run_allowed": "expected_simulation_run_allowed",
    "runtime_geometry_planned_for_step84": "expected_runtime_geometry_planned_for_step84",
    "geometry_motion_application_mode_allowed_for_step84": "expected_geometry_motion_application_mode_for_step84",
    "geometry_mutation_allowed": "expected_geometry_mutation_allowed_for_step84",
    "wall_velocity_planned_for_step84": "expected_wall_velocity_planned_for_step84",
    "wall_velocity_application_mode_allowed_for_step84": "expected_wall_velocity_application_mode_for_step84",
    "target_lbm_field_planned_for_step84": "expected_target_lbm_field_for_step84",
    "combined_runtime_geometry_wall_velocity_planned_for_step84": (
        "expected_combined_runtime_geometry_wall_velocity_for_step84"
    ),
    "step83_activation_feature_count": "expected_step83_activation_feature_count",
    "planned_step84_activation_feature_count": "expected_planned_activation_feature_count_for_step84",
    "real_geometry_allowed": "expected_real_geometry_for_step84",
    "squid_proxy_allowed": "expected_squid_proxy_for_step84",
    "link_area_allowed": "expected_link_area_for_step84",
    "grid_48_allowed": "expected_grid_48_for_step84",
    "grid_64_allowed": "expected_grid_64_for_step84",
    "vtr_output_allowed": "expected_vtr_for_step84",
    "particle_npy_output_allowed": "expected_particle_npy_for_step84",
}


APPLICATION_CONFIG_CHECKS = {
    "application_mode": "expected_wall_velocity_application_mode_for_step84",
    "target_lbm_field": "expected_target_lbm_field_for_step84",
    "boundary_motion_config_path": "expected_boundary_motion_config_path_for_step84",
    "apply_to_lbm_solid_vel": "expected_apply_to_lbm_solid_vel_for_step84",
    "apply_to_lbm_populations": "expected_apply_to_lbm_populations_for_step84",
    "apply_to_mpm": "expected_apply_to_mpm_for_step84",
    "apply_to_projector": "expected_apply_to_projector_for_step84",
    "modify_bounceback_formula": "expected_modify_bounceback_formula_for_step84",
    "jet_model_enabled": "expected_jet_model_enabled_for_step84",
    "actuation_claim_enabled": "expected_actuation_claim_enabled_for_step84",
}


GEOMETRY_CONFIG_CHECKS = {
    "geometry_motion_mode": "expected_geometry_motion_mode_for_step84",
    "application_mode": "expected_geometry_motion_application_mode_for_step84",
    "diagnostic_only": "expected_runtime_geometry_planned_for_step84",
    "mutate_geometry_state": "expected_geometry_mutation_allowed_for_step84",
}


def build_step83_runtime_geometry_wall_velocity_combined_activation_guard(
    root: Path,
    policy_path: str = "configs/step83_runtime_geometry_wall_velocity_combined_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_payload = read_json(root / policy["plan_artifact_path"])
    plan_summary = plan_payload["summary"]
    application_config = read_json(root / policy["application_config_path"])
    geometry_config = read_json(root / policy["geometry_motion_application_config_path"])

    rows = [
        plan_summary_row(plan_summary, policy, summary_key, policy_key)
        for summary_key, policy_key in PLAN_SUMMARY_CHECKS.items()
    ]
    rows.extend(
        [
            literal_row(
                "previous_commit",
                plan_summary["previous_commit"],
                policy["expected_step82_commit"],
                "step83_plan",
            ),
            literal_row(
                "step84_allowed_row_name",
                plan_summary["step84_allowed_row_name"],
                policy["expected_step84_allowed_row_name"],
                "step84_plan",
            ),
            literal_row("step84_allowed_n_grid", plan_summary["step84_allowed_n_grid"], 32, "step84_plan"),
            literal_row("step84_allowed_n_particles", plan_summary["step84_allowed_n_particles"], 1024, "step84_plan"),
            literal_row("step84_allowed_n_lbm_steps", plan_summary["step84_allowed_n_lbm_steps"], 3, "step84_plan"),
            literal_row(
                "step84_allowed_mpm_substeps_per_lbm_step",
                plan_summary["step84_allowed_mpm_substeps_per_lbm_step"],
                1,
                "step84_plan",
            ),
            literal_row(
                "step84_allowed_coupling_mode",
                plan_summary["step84_allowed_coupling_mode"],
                "moving_boundary",
                "step84_plan",
            ),
            literal_row(
                "step84_allowed_reaction_transfer_mode",
                plan_summary["step84_allowed_reaction_transfer_mode"],
                "engineering",
                "step84_plan",
            ),
            literal_row(
                "boundary_motion_mode_allowed_for_step84",
                plan_summary["boundary_motion_mode_allowed_for_step84"],
                policy["expected_boundary_motion_mode_for_step84"],
                "step84_plan",
            ),
            literal_row(
                "geometry_motion_config_path_allowed_for_step84",
                plan_summary["geometry_motion_config_path_allowed_for_step84"],
                policy["expected_geometry_motion_config_path_for_step84"],
                "step84_plan",
            ),
            literal_row(
                "geometry_motion_application_config_path_allowed_for_step84",
                plan_summary["geometry_motion_application_config_path_allowed_for_step84"],
                policy["expected_geometry_motion_application_config_path_for_step84"],
                "step84_plan",
            ),
        ]
    )
    rows.extend(
        [
            literal_row(key, application_config[key], policy[policy_key], "step36_wall_velocity_application")
            for key, policy_key in APPLICATION_CONFIG_CHECKS.items()
        ]
    )
    rows.extend(
        [
            literal_row(key, geometry_config[key], policy[policy_key], "step80_runtime_geometry_diagnostic_only")
            for key, policy_key in GEOMETRY_CONFIG_CHECKS.items()
        ]
    )

    summary = {
        "actuation_claim_planned_for_step84": application_config["actuation_claim_enabled"],
        "apply_to_lbm_populations_planned_for_step84": application_config["apply_to_lbm_populations"],
        "apply_to_lbm_solid_vel_planned_for_step84": application_config["apply_to_lbm_solid_vel"],
        "apply_to_mpm_planned_for_step84": application_config["apply_to_mpm"],
        "apply_to_projector_planned_for_step84": application_config["apply_to_projector"],
        "combined_runtime_geometry_wall_velocity_planned_for_step84": plan_summary[
            "combined_runtime_geometry_wall_velocity_planned_for_step84"
        ],
        "geometry_mutation_allowed": plan_summary["geometry_mutation_allowed"],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "jet_model_planned_for_step84": application_config["jet_model_enabled"],
        "link_area_planned_for_step84": plan_summary["link_area_allowed"],
        "modify_bounceback_formula_planned_for_step84": application_config["modify_bounceback_formula"],
        "planned_step84_activation_feature_count": plan_summary["planned_step84_activation_feature_count"],
        "real_geometry_planned_for_step84": plan_summary["real_geometry_allowed"],
        "row_count": len(rows),
        "runtime_geometry_application_mode_planned_for_step84": plan_summary[
            "geometry_motion_application_mode_allowed_for_step84"
        ],
        "runtime_geometry_planned_for_step84": plan_summary["runtime_geometry_planned_for_step84"],
        "squid_proxy_planned_for_step84": plan_summary["squid_proxy_allowed"],
        "step83_activation_feature_count": plan_summary["step83_activation_feature_count"],
        "step83_runtime_geometry_wall_velocity_combined_activation_guard_pass": False,
        "target_lbm_field_planned_for_step84": plan_summary["target_lbm_field_planned_for_step84"],
        "wall_velocity_application_mode_planned_for_step84": plan_summary[
            "wall_velocity_application_mode_allowed_for_step84"
        ],
        "wall_velocity_planned_for_step84": plan_summary["wall_velocity_planned_for_step84"],
        "write_particles_planned_for_step84": plan_summary["particle_npy_output_allowed"],
        "write_vtk_planned_for_step84": plan_summary["vtr_output_allowed"],
    }
    summary["step83_runtime_geometry_wall_velocity_combined_activation_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step83_activation_feature_count"] == 0
        and summary["planned_step84_activation_feature_count"] == 2
        and summary["runtime_geometry_planned_for_step84"] is True
        and summary["runtime_geometry_application_mode_planned_for_step84"] == "diagnostic_only"
        and summary["geometry_mutation_allowed"] is False
        and summary["wall_velocity_planned_for_step84"] is True
        and summary["wall_velocity_application_mode_planned_for_step84"] == "solid_vel_experimental"
        and summary["apply_to_lbm_solid_vel_planned_for_step84"] is True
        and summary["apply_to_lbm_populations_planned_for_step84"] is False
        and summary["modify_bounceback_formula_planned_for_step84"] is False
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step84"] is True
        and summary["real_geometry_planned_for_step84"] is False
        and summary["squid_proxy_planned_for_step84"] is False
    )
    return rows, summary


def plan_summary_row(plan_summary: dict, policy: dict, summary_key: str, policy_key: str) -> dict:
    return literal_row(summary_key, plan_summary.get(summary_key), policy[policy_key], "step83_plan")


def literal_row(check: str, actual, expected, row_name: str) -> dict:
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
