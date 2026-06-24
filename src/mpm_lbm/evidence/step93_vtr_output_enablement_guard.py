from __future__ import annotations

import json
from pathlib import Path


def build_step93_vtr_output_enablement_guard(
    root: Path,
    policy_path: str = "configs/step93_vtr_output_enablement_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_summary = read_json(root / policy["plan_artifact_path"])["summary"]
    rows = []
    rows.extend(summary_checks(plan_summary, policy))
    for flag in policy["plan_summary_flags_must_be_false"]:
        rows.append(literal_row("step94_vtr_smoke_plan", flag, bool(plan_summary[flag]), False))

    summary = {
        "combined_runtime_geometry_wall_velocity_planned_for_step94": plan_summary[
            "combined_runtime_geometry_wall_velocity_planned_for_step94"
        ],
        "duration_reduction_for_output_isolation": plan_summary["duration_reduction_for_output_isolation"],
        "geometry_motion_application_mode_planned_for_step94": plan_summary[
            "geometry_motion_application_mode_allowed_for_step94"
        ],
        "geometry_mutation_allowed": plan_summary["geometry_mutation_allowed"],
        "geometry_type_planned_for_step94": plan_summary["geometry_type_allowed_for_step94"],
        "grid_48_planned_for_step94": plan_summary["grid_48_allowed"],
        "grid_64_planned_for_step94": plan_summary["grid_64_allowed"],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "link_area_planned_for_step94": plan_summary["link_area_allowed"],
        "only_new_feature_from_step92": plan_summary["only_new_feature_from_step92"],
        "particle_npy_output_allowed": plan_summary["particle_npy_output_allowed"],
        "planned_step94_activation_feature_count": plan_summary["planned_step94_activation_feature_count"],
        "planned_step94_duration_lbm_steps": plan_summary["step94_allowed_n_lbm_steps"],
        "previous_step92_n_lbm_steps": plan_summary["previous_step92_n_lbm_steps"],
        "real_geometry_candidate_data_planned_for_step94": plan_summary["real_geometry_candidate_data_allowed"],
        "real_geometry_planned_for_step94": plan_summary["real_geometry_allowed"],
        "row_count": len(rows),
        "runtime_geometry_planned_for_step94": plan_summary["runtime_geometry_planned_for_step94"],
        "squid_proxy_planned_for_step94": plan_summary["squid_proxy_planned_for_step94"],
        "step93_activation_feature_count": plan_summary["step93_activation_feature_count"],
        "step93_vtr_output_enablement_guard_pass": False,
        "target_lbm_field_planned_for_step94": plan_summary["target_lbm_field_planned_for_step94"],
        "target_u_lbm_planned_for_step94": plan_summary["target_u_lbm_allowed_for_step94"],
        "vtr_output_planned_for_step94": plan_summary["vtr_output_planned_for_step94"],
        "vtr_output_smoke_isolation": plan_summary["vtr_output_smoke_isolation"],
        "wall_velocity_application_mode_planned_for_step94": plan_summary[
            "wall_velocity_application_mode_allowed_for_step94"
        ],
        "wall_velocity_planned_for_step94": plan_summary["wall_velocity_planned_for_step94"],
        "write_particles_allowed_for_step94": plan_summary["write_particles_allowed_for_step94"],
        "write_vtk_allowed_for_step94": plan_summary["write_vtk_allowed_for_step94"],
    }
    summary["step93_vtr_output_enablement_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step93_activation_feature_count"] == int(policy["expected_step93_activation_feature_count"])
        and summary["planned_step94_activation_feature_count"]
        == int(policy["expected_planned_step94_activation_feature_count"])
        and summary["planned_step94_duration_lbm_steps"] == int(policy["expected_planned_step94_n_lbm_steps"])
        and summary["previous_step92_n_lbm_steps"] == int(policy["expected_previous_step92_n_lbm_steps"])
        and summary["duration_reduction_for_output_isolation"] is True
        and summary["vtr_output_smoke_isolation"] is True
        and summary["only_new_feature_from_step92"] == policy["expected_only_new_feature_from_step92"]
        and summary["vtr_output_planned_for_step94"] is True
        and summary["write_vtk_allowed_for_step94"] is True
        and summary["write_particles_allowed_for_step94"] is False
        and summary["particle_npy_output_allowed"] is False
        and summary["squid_proxy_planned_for_step94"] is True
        and summary["runtime_geometry_planned_for_step94"] is True
        and summary["wall_velocity_planned_for_step94"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step94"] is True
        and summary["geometry_motion_application_mode_planned_for_step94"]
        == policy["expected_geometry_motion_application_mode"]
        and summary["wall_velocity_application_mode_planned_for_step94"]
        == policy["expected_wall_velocity_application_mode"]
        and summary["target_lbm_field_planned_for_step94"] == policy["expected_target_lbm_field"]
        and summary["target_u_lbm_planned_for_step94"] == policy["expected_target_u_lbm"]
        and summary["real_geometry_planned_for_step94"] is False
        and summary["real_geometry_candidate_data_planned_for_step94"] is False
        and summary["link_area_planned_for_step94"] is False
        and summary["grid_48_planned_for_step94"] is False
        and summary["grid_64_planned_for_step94"] is False
    )
    return rows, summary


def summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step93_vtr_output_enablement_plan_pass", True),
        ("step94_allowed_row_name", policy["step94_allowed_row_name"]),
        ("step93_activation_feature_count", int(policy["expected_step93_activation_feature_count"])),
        ("planned_step94_activation_feature_count", int(policy["expected_planned_step94_activation_feature_count"])),
        ("step94_allowed_n_lbm_steps", int(policy["expected_planned_step94_n_lbm_steps"])),
        ("previous_step92_n_lbm_steps", int(policy["expected_previous_step92_n_lbm_steps"])),
        ("planned_step94_n_lbm_steps", int(policy["expected_planned_step94_n_lbm_steps"])),
        ("duration_reduction_for_output_isolation", True),
        ("vtr_output_smoke_isolation", True),
        ("only_new_feature_from_step92", policy["expected_only_new_feature_from_step92"]),
        ("geometry_type_allowed_for_step94", policy["expected_geometry_type"]),
        ("geometry_config_path_allowed_for_step94", policy["expected_geometry_config_path"]),
        ("geometry_motion_application_mode_allowed_for_step94", policy["expected_geometry_motion_application_mode"]),
        ("wall_velocity_application_mode_allowed_for_step94", policy["expected_wall_velocity_application_mode"]),
        ("target_lbm_field_planned_for_step94", policy["expected_target_lbm_field"]),
        ("target_u_lbm_allowed_for_step94", policy["expected_target_u_lbm"]),
        ("vtr_output_planned_for_step94", True),
        ("write_vtk_allowed_for_step94", True),
        ("write_particles_allowed_for_step94", False),
        ("squid_proxy_planned_for_step94", True),
        ("runtime_geometry_planned_for_step94", True),
        ("wall_velocity_planned_for_step94", True),
        ("combined_runtime_geometry_wall_velocity_planned_for_step94", True),
    ]
    return [literal_row("step94_vtr_smoke_plan", check, summary[check], expected) for check, expected in checks]


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
