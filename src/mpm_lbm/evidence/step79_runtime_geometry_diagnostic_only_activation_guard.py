from __future__ import annotations

import json
from pathlib import Path


PLAN_SUMMARY_CHECKS = {
    "driver_run_required": "expected_step79_driver_run_required",
    "fsidriver_run_allowed": "expected_step79_fsidriver_run_allowed",
    "simulation_run_allowed": "expected_step79_simulation_run_allowed",
    "runtime_geometry_activation_planned": "expected_runtime_geometry_activation_planned",
    "runtime_geometry_application_mode_planned_for_step80": (
        "expected_runtime_geometry_application_mode_for_step80"
    ),
    "geometry_mutation_allowed": "expected_geometry_mutation_allowed",
    "solver_formula_change_allowed": "expected_solver_formula_change_allowed",
    "wall_velocity_allowed": "expected_wall_velocity_allowed",
    "combined_runtime_geometry_wall_velocity_allowed": (
        "expected_combined_runtime_geometry_wall_velocity_allowed"
    ),
    "real_geometry_allowed": "expected_real_geometry_allowed",
    "squid_proxy_allowed": "expected_squid_proxy_allowed",
    "link_area_allowed": "expected_link_area_allowed",
    "grid_48_allowed": "expected_grid_48_allowed",
    "grid_64_allowed": "expected_grid_64_allowed",
    "vtr_output_allowed": "expected_vtr_output_allowed",
    "particle_npy_output_allowed": "expected_particle_npy_output_allowed",
    "step79_activation_feature_count": "expected_activation_feature_count_in_step79",
    "planned_step80_activation_feature_count": "expected_planned_activation_feature_count_for_step80",
}


def build_step79_runtime_geometry_diagnostic_only_activation_guard(
    root: Path,
    policy_path: str = "configs/step79_runtime_geometry_diagnostic_only_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_payload = read_json(root / policy["plan_artifact_path"])
    plan_summary = plan_payload["summary"]

    rows = [plan_summary_row(plan_summary, policy, summary_key, policy_key) for summary_key, policy_key in PLAN_SUMMARY_CHECKS.items()]
    rows.extend(step78_artifact_rows(root, policy))
    rows.extend(
        [
            literal_row(
                "previous_step",
                plan_summary["previous_step"],
                policy["required_previous_step"],
                "step79_plan",
            ),
            literal_row(
                "previous_commit",
                plan_summary["previous_commit"],
                policy["required_step78_commit"],
                "step79_plan",
            ),
            literal_row(
                "step80_allowed_row_name",
                plan_summary["step80_allowed_row_name"],
                "canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke",
                "step80_plan",
            ),
            literal_row("step80_allowed_n_grid", plan_summary["step80_allowed_n_grid"], 32, "step80_plan"),
            literal_row("step80_allowed_n_particles", plan_summary["step80_allowed_n_particles"], 1024, "step80_plan"),
            literal_row("step80_allowed_n_lbm_steps", plan_summary["step80_allowed_n_lbm_steps"], 3, "step80_plan"),
            literal_row(
                "step80_allowed_mpm_substeps_per_lbm_step",
                plan_summary["step80_allowed_mpm_substeps_per_lbm_step"],
                1,
                "step80_plan",
            ),
            literal_row(
                "step80_allowed_coupling_mode",
                plan_summary["step80_allowed_coupling_mode"],
                "moving_boundary",
                "step80_plan",
            ),
            literal_row(
                "step80_allowed_reaction_transfer_mode",
                plan_summary["step80_allowed_reaction_transfer_mode"],
                "engineering",
                "step80_plan",
            ),
            literal_row(
                "geometry_motion_mode_allowed_for_step80",
                plan_summary["geometry_motion_mode_allowed_for_step80"],
                "prescribed_kinematic",
                "step80_plan",
            ),
        ]
    )

    summary = {
        "combined_runtime_geometry_wall_velocity_planned_for_step80": False,
        "geometry_mutation_allowed": plan_summary["geometry_mutation_allowed"],
        "grid_48_planned_for_step80": False,
        "grid_64_planned_for_step80": False,
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "link_area_planned_for_step80": False,
        "planned_step80_activation_feature_count": plan_summary["planned_step80_activation_feature_count"],
        "real_geometry_planned_for_step80": False,
        "row_count": len(rows),
        "runtime_geometry_application_mode_planned_for_step80": plan_summary[
            "runtime_geometry_application_mode_planned_for_step80"
        ],
        "runtime_geometry_planned_for_step80": plan_summary["runtime_geometry_activation_planned"],
        "squid_proxy_planned_for_step80": False,
        "step79_activation_feature_count": plan_summary["step79_activation_feature_count"],
        "step79_runtime_geometry_diagnostic_only_activation_guard_pass": False,
        "wall_velocity_planned_for_step80": False,
        "write_particles_planned_for_step80": False,
        "write_vtk_planned_for_step80": False,
    }
    summary["step79_runtime_geometry_diagnostic_only_activation_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step79_activation_feature_count"] == 0
        and summary["planned_step80_activation_feature_count"] == 1
        and summary["runtime_geometry_planned_for_step80"] is True
        and summary["runtime_geometry_application_mode_planned_for_step80"] == "diagnostic_only"
        and summary["geometry_mutation_allowed"] is False
    )
    return rows, summary


def plan_summary_row(plan_summary: dict, policy: dict, summary_key: str, policy_key: str) -> dict:
    return literal_row(summary_key, plan_summary.get(summary_key), policy[policy_key], "step79_plan")


def step78_artifact_rows(root: Path, policy: dict) -> list[dict]:
    rows = []
    for check in policy["artifact_checks"]:
        payload = read_json(root / check["artifact_path"])
        actual = payload.get("summary", payload).get(check["summary_key"])
        rows.append(
            {
                "actual": actual,
                "check": check["check"],
                "expected": check["expected"],
                "pass": actual == check["expected"],
                "row_name": "step78_regression_evidence",
            }
        )
    return rows


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
