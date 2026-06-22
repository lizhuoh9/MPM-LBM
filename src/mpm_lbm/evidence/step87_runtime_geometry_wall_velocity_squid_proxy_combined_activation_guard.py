from __future__ import annotations

import json
from pathlib import Path


def build_step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard(
    root: Path,
    policy_path: str = "configs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_guard_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    plan_artifact = read_json(root / policy["activation_plan_artifact_path"])
    plan_summary = plan_artifact["summary"]
    rows = []
    rows.extend(summary_checks(plan_summary, policy))
    for flag in policy["plan_summary_flags_must_be_false"]:
        rows.append(literal_row("activation_plan", flag, bool(plan_summary[flag]), False))

    summary = {
        "apply_to_lbm_populations_planned_for_step88": plan_summary["apply_to_lbm_populations_allowed"],
        "apply_to_lbm_solid_vel_planned_for_step88": plan_summary["apply_to_lbm_solid_vel_allowed"],
        "combined_runtime_geometry_wall_velocity_planned_for_step88": plan_summary[
            "combined_runtime_geometry_wall_velocity_planned_for_step88"
        ],
        "geometry_mutation_allowed": plan_summary["geometry_mutation_allowed"],
        "geometry_quality_report_required_for_step88": plan_summary["geometry_quality_report_required_for_step88"],
        "geometry_type_planned_for_step88": plan_summary["geometry_type_allowed_for_step88"],
        "guard_pass_count": sum(1 for row in rows if row["pass"]),
        "guard_row_count": len(rows),
        "link_area_planned_for_step88": plan_summary["link_area_allowed"],
        "modify_bounceback_formula_planned_for_step88": plan_summary["modify_bounceback_formula_allowed"],
        "planned_step88_activation_feature_count": plan_summary["planned_step88_activation_feature_count"],
        "real_geometry_candidate_data_planned_for_step88": plan_summary["real_geometry_candidate_data_allowed"],
        "real_geometry_planned_for_step88": plan_summary["real_geometry_allowed"],
        "row_count": len(rows),
        "runtime_geometry_application_mode_planned_for_step88": plan_summary[
            "geometry_motion_application_mode_allowed_for_step88"
        ],
        "runtime_geometry_planned_for_step88": plan_summary["runtime_geometry_planned_for_step88"],
        "squid_proxy_planned_for_step88": plan_summary["squid_proxy_planned_for_step88"],
        "step87_activation_feature_count": plan_summary["step87_activation_feature_count"],
        "step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass": False,
        "wall_velocity_application_mode_planned_for_step88": plan_summary[
            "wall_velocity_application_mode_allowed_for_step88"
        ],
        "wall_velocity_planned_for_step88": plan_summary["wall_velocity_planned_for_step88"],
        "write_particles_planned_for_step88": plan_summary["particle_npy_output_allowed"],
        "write_vtk_planned_for_step88": plan_summary["vtr_output_allowed"],
    }
    summary["step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass"] = bool(
        rows
        and summary["guard_pass_count"] == summary["guard_row_count"]
        and summary["step87_activation_feature_count"] == int(policy["expected_step87_activation_feature_count"])
        and summary["planned_step88_activation_feature_count"]
        == int(policy["expected_planned_step88_activation_feature_count"])
        and summary["squid_proxy_planned_for_step88"] is True
        and summary["runtime_geometry_planned_for_step88"] is True
        and summary["wall_velocity_planned_for_step88"] is True
        and summary["combined_runtime_geometry_wall_velocity_planned_for_step88"] is True
        and summary["geometry_type_planned_for_step88"] == policy["expected_geometry_type"]
        and summary["runtime_geometry_application_mode_planned_for_step88"]
        == policy["expected_geometry_motion_application_mode"]
        and summary["wall_velocity_application_mode_planned_for_step88"]
        == policy["expected_wall_velocity_application_mode"]
        and summary["apply_to_lbm_solid_vel_planned_for_step88"] is True
        and summary["apply_to_lbm_populations_planned_for_step88"] is False
        and summary["modify_bounceback_formula_planned_for_step88"] is False
        and summary["real_geometry_planned_for_step88"] is False
        and summary["real_geometry_candidate_data_planned_for_step88"] is False
        and summary["write_vtk_planned_for_step88"] is False
        and summary["write_particles_planned_for_step88"] is False
    )
    return rows, summary


def summary_checks(summary: dict, policy: dict) -> list[dict]:
    checks = [
        ("step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass", True),
        ("step88_allowed_row_name", policy["allowed_required_row_name"]),
        ("step87_activation_feature_count", int(policy["expected_step87_activation_feature_count"])),
        ("planned_step88_activation_feature_count", int(policy["expected_planned_step88_activation_feature_count"])),
        ("geometry_type_allowed_for_step88", policy["expected_geometry_type"]),
        ("geometry_config_path_allowed_for_step88", policy["expected_geometry_config_path"]),
        ("geometry_motion_application_mode_allowed_for_step88", policy["expected_geometry_motion_application_mode"]),
        ("wall_velocity_application_mode_allowed_for_step88", policy["expected_wall_velocity_application_mode"]),
        ("target_lbm_field_planned_for_step88", policy["expected_target_lbm_field"]),
        ("geometry_quality_report_required_for_step88", True),
        ("squid_proxy_planned_for_step88", True),
        ("runtime_geometry_planned_for_step88", True),
        ("wall_velocity_planned_for_step88", True),
        ("combined_runtime_geometry_wall_velocity_planned_for_step88", True),
        ("apply_to_lbm_solid_vel_allowed", True),
    ]
    return [literal_row("activation_plan", check, summary[check], expected) for check, expected in checks]


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
