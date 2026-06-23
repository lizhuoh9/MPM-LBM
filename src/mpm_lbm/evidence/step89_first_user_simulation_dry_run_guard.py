from __future__ import annotations

import json
from pathlib import Path


def build_step89_first_user_simulation_dry_run_guard(
    root: Path,
    policy_path: str = "configs/step89_first_user_simulation_dry_run_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_summary = read_json(root / policy["plan_artifact_path"])["summary"]
    rows = []
    rows.extend(summary_checks(plan_summary, policy))
    for flag in policy["plan_summary_flags_must_be_false"]:
        rows.append(literal_row("dry_run_plan", flag, bool(plan_summary[flag]), False))

    summary = {
        "combined_runtime_geometry_wall_velocity_planned_for_step90": plan_summary[
            "combined_runtime_geometry_wall_velocity_planned_for_step90"
        ],
        "geometry_motion_application_mode_planned_for_step90": plan_summary[
            "geometry_motion_application_mode_allowed_for_step90"
        ],
        "geometry_mutation_allowed": plan_summary["geometry_mutation_allowed"],
        "geometry_type_planned_for_step90": plan_summary["geometry_type_allowed_for_step90"],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "link_area_planned_for_step90": plan_summary["link_area_allowed"],
        "planned_step90_activation_feature_count": plan_summary["planned_step90_activation_feature_count"],
        "planned_step90_duration_lbm_steps": plan_summary["step90_allowed_n_lbm_steps"],
        "real_geometry_candidate_data_planned_for_step90": plan_summary["real_geometry_candidate_data_allowed"],
        "real_geometry_planned_for_step90": plan_summary["real_geometry_allowed"],
        "row_count": len(rows),
        "runtime_geometry_planned_for_step90": plan_summary["runtime_geometry_planned_for_step90"],
        "squid_proxy_planned_for_step90": plan_summary["squid_proxy_planned_for_step90"],
        "step89_activation_feature_count": plan_summary["step89_activation_feature_count"],
        "step89_first_user_simulation_dry_run_guard_pass": False,
        "target_lbm_field_planned_for_step90": plan_summary["target_lbm_field_planned_for_step90"],
        "target_u_lbm_planned_for_step90": plan_summary["target_u_lbm_allowed_for_step90"],
        "wall_velocity_application_mode_planned_for_step90": plan_summary[
            "wall_velocity_application_mode_allowed_for_step90"
        ],
        "wall_velocity_planned_for_step90": plan_summary["wall_velocity_planned_for_step90"],
        "write_particles_planned_for_step90": plan_summary["write_particles_allowed"],
        "write_vtk_planned_for_step90": plan_summary["write_vtk_allowed"],
    }
    summary["step89_first_user_simulation_dry_run_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step89_activation_feature_count"] == int(policy["expected_step89_activation_feature_count"])
        and summary["planned_step90_activation_feature_count"]
        == int(policy["expected_planned_step90_activation_feature_count"])
        and summary["planned_step90_duration_lbm_steps"] == int(policy["expected_step90_duration_lbm_steps"])
        and summary["squid_proxy_planned_for_step90"] is True
        and summary["runtime_geometry_planned_for_step90"] is True
        and summary["wall_velocity_planned_for_step90"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step90"] is True
        and summary["geometry_motion_application_mode_planned_for_step90"]
        == policy["expected_geometry_motion_application_mode"]
        and summary["wall_velocity_application_mode_planned_for_step90"]
        == policy["expected_wall_velocity_application_mode"]
        and summary["target_lbm_field_planned_for_step90"] == policy["expected_target_lbm_field"]
        and summary["target_u_lbm_planned_for_step90"] == policy["expected_target_u_lbm"]
        and summary["real_geometry_planned_for_step90"] is False
        and summary["real_geometry_candidate_data_planned_for_step90"] is False
        and summary["link_area_planned_for_step90"] is False
        and summary["write_vtk_planned_for_step90"] is False
        and summary["write_particles_planned_for_step90"] is False
    )
    return rows, summary


def summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step89_first_user_simulation_dry_run_plan_pass", True),
        ("step90_allowed_row_name", policy["step90_allowed_row_name"]),
        ("step89_activation_feature_count", int(policy["expected_step89_activation_feature_count"])),
        ("planned_step90_activation_feature_count", int(policy["expected_planned_step90_activation_feature_count"])),
        ("step90_allowed_n_lbm_steps", int(policy["expected_step90_duration_lbm_steps"])),
        ("geometry_type_allowed_for_step90", policy["expected_geometry_type"]),
        ("geometry_config_path_allowed_for_step90", policy["expected_geometry_config_path"]),
        ("geometry_motion_application_mode_allowed_for_step90", policy["expected_geometry_motion_application_mode"]),
        ("wall_velocity_application_mode_allowed_for_step90", policy["expected_wall_velocity_application_mode"]),
        ("target_lbm_field_planned_for_step90", policy["expected_target_lbm_field"]),
        ("target_u_lbm_allowed_for_step90", policy["expected_target_u_lbm"]),
        ("squid_proxy_planned_for_step90", True),
        ("runtime_geometry_planned_for_step90", True),
        ("wall_velocity_planned_for_step90", True),
        ("combined_runtime_geometry_wall_velocity_planned_for_step90", True),
    ]
    return [literal_row("dry_run_plan", check, summary[check], expected) for check, expected in checks]


def literal_row(row_name: str, check: str, actual, expected) -> dict:
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
