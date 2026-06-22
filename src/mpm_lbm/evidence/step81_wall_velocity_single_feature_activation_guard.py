from __future__ import annotations

import json
from pathlib import Path


PLAN_SUMMARY_CHECKS = {
    "driver_run_required": "expected_driver_run_required",
    "fsidriver_run_allowed": "expected_fsidriver_run_allowed",
    "simulation_run_allowed": "expected_simulation_run_allowed",
    "wall_velocity_activation_planned": "expected_wall_velocity_planned_for_step82",
    "wall_velocity_application_mode_planned_for_step82": "expected_wall_velocity_application_mode_for_step82",
    "target_lbm_field_planned_for_step82": "expected_target_lbm_field_for_step82",
    "step81_activation_feature_count": "expected_activation_feature_count_in_step81",
    "planned_step82_activation_feature_count": "expected_planned_activation_feature_count_for_step82",
    "runtime_geometry_allowed": "expected_runtime_geometry_planned_for_step82",
    "combined_runtime_geometry_wall_velocity_allowed": (
        "expected_combined_runtime_geometry_wall_velocity_for_step82"
    ),
    "real_geometry_allowed": "expected_real_geometry_for_step82",
    "squid_proxy_allowed": "expected_squid_proxy_for_step82",
    "link_area_allowed": "expected_link_area_for_step82",
    "grid_48_allowed": "expected_grid_48_for_step82",
    "grid_64_allowed": "expected_grid_64_for_step82",
    "vtr_output_allowed": "expected_vtr_for_step82",
    "particle_npy_output_allowed": "expected_particle_npy_for_step82",
}


APPLICATION_CONFIG_CHECKS = {
    "application_mode": "expected_wall_velocity_application_mode_for_step82",
    "target_lbm_field": "expected_target_lbm_field_for_step82",
    "boundary_motion_config_path": "expected_boundary_motion_config_path_for_step82",
    "apply_to_lbm_solid_vel": "expected_apply_to_lbm_solid_vel_for_step82",
    "apply_to_lbm_populations": "expected_apply_to_lbm_populations_for_step82",
    "apply_to_mpm": "expected_apply_to_mpm_for_step82",
    "apply_to_projector": "expected_apply_to_projector_for_step82",
    "modify_bounceback_formula": "expected_modify_bounceback_formula_for_step82",
    "jet_model_enabled": "expected_jet_model_enabled_for_step82",
    "actuation_claim_enabled": "expected_actuation_claim_enabled_for_step82",
}


def build_step81_wall_velocity_single_feature_activation_guard(
    root: Path,
    policy_path: str = "configs/step81_wall_velocity_single_feature_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_payload = read_json(root / policy["plan_artifact_path"])
    plan_summary = plan_payload["summary"]
    application_config = read_json(root / policy["application_config_path"])

    rows = [
        plan_summary_row(plan_summary, policy, summary_key, policy_key)
        for summary_key, policy_key in PLAN_SUMMARY_CHECKS.items()
    ]
    rows.extend(
        [
            literal_row(
                "previous_commit",
                plan_summary["previous_commit"],
                policy["expected_step80_commit"],
                "step81_plan",
            ),
            literal_row(
                "step82_allowed_row_name",
                plan_summary["step82_allowed_row_name"],
                policy["expected_step82_allowed_row_name"],
                "step82_plan",
            ),
            literal_row("step82_allowed_n_grid", plan_summary["step82_allowed_n_grid"], 32, "step82_plan"),
            literal_row("step82_allowed_n_particles", plan_summary["step82_allowed_n_particles"], 1024, "step82_plan"),
            literal_row("step82_allowed_n_lbm_steps", plan_summary["step82_allowed_n_lbm_steps"], 3, "step82_plan"),
            literal_row(
                "step82_allowed_mpm_substeps_per_lbm_step",
                plan_summary["step82_allowed_mpm_substeps_per_lbm_step"],
                1,
                "step82_plan",
            ),
            literal_row(
                "step82_allowed_coupling_mode",
                plan_summary["step82_allowed_coupling_mode"],
                "moving_boundary",
                "step82_plan",
            ),
            literal_row(
                "step82_allowed_reaction_transfer_mode",
                plan_summary["step82_allowed_reaction_transfer_mode"],
                "engineering",
                "step82_plan",
            ),
            literal_row(
                "boundary_motion_mode_allowed_for_step82",
                plan_summary["boundary_motion_mode_allowed_for_step82"],
                policy["expected_boundary_motion_mode_for_step82"],
                "step82_plan",
            ),
        ]
    )
    rows.extend(
        [
            literal_row(key, application_config[key], policy[policy_key], "step36_wall_velocity_application")
            for key, policy_key in APPLICATION_CONFIG_CHECKS.items()
        ]
    )

    summary = {
        "actuation_claim_planned_for_step82": application_config["actuation_claim_enabled"],
        "apply_to_lbm_populations_planned_for_step82": application_config["apply_to_lbm_populations"],
        "apply_to_lbm_solid_vel_planned_for_step82": application_config["apply_to_lbm_solid_vel"],
        "apply_to_mpm_planned_for_step82": application_config["apply_to_mpm"],
        "apply_to_projector_planned_for_step82": application_config["apply_to_projector"],
        "combined_runtime_geometry_wall_velocity_planned_for_step82": plan_summary[
            "combined_runtime_geometry_wall_velocity_allowed"
        ],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "jet_model_planned_for_step82": application_config["jet_model_enabled"],
        "link_area_planned_for_step82": plan_summary["link_area_allowed"],
        "modify_bounceback_formula_planned_for_step82": application_config["modify_bounceback_formula"],
        "planned_step82_activation_feature_count": plan_summary["planned_step82_activation_feature_count"],
        "real_geometry_planned_for_step82": plan_summary["real_geometry_allowed"],
        "row_count": len(rows),
        "runtime_geometry_planned_for_step82": plan_summary["runtime_geometry_allowed"],
        "squid_proxy_planned_for_step82": plan_summary["squid_proxy_allowed"],
        "step81_activation_feature_count": plan_summary["step81_activation_feature_count"],
        "step81_wall_velocity_single_feature_activation_guard_pass": False,
        "target_lbm_field_planned_for_step82": plan_summary["target_lbm_field_planned_for_step82"],
        "wall_velocity_application_mode_planned_for_step82": plan_summary[
            "wall_velocity_application_mode_planned_for_step82"
        ],
        "wall_velocity_planned_for_step82": plan_summary["wall_velocity_activation_planned"],
        "write_particles_planned_for_step82": plan_summary["particle_npy_output_allowed"],
        "write_vtk_planned_for_step82": plan_summary["vtr_output_allowed"],
    }
    summary["step81_wall_velocity_single_feature_activation_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step81_activation_feature_count"] == 0
        and summary["planned_step82_activation_feature_count"] == 1
        and summary["wall_velocity_planned_for_step82"] is True
        and summary["wall_velocity_application_mode_planned_for_step82"] == "solid_vel_experimental"
        and summary["target_lbm_field_planned_for_step82"] == "solid_vel"
        and summary["apply_to_lbm_solid_vel_planned_for_step82"] is True
        and summary["apply_to_lbm_populations_planned_for_step82"] is False
        and summary["modify_bounceback_formula_planned_for_step82"] is False
        and summary["runtime_geometry_planned_for_step82"] is False
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step82"] is False
    )
    return rows, summary


def plan_summary_row(plan_summary: dict, policy: dict, summary_key: str, policy_key: str) -> dict:
    return literal_row(summary_key, plan_summary.get(summary_key), policy[policy_key], "step81_plan")


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
