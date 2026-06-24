from __future__ import annotations

import json
import math
from pathlib import Path


QUALITY_CHECKS = [
    ("rho_min_min", ">", "min_rho_min"),
    ("rho_max_max", "<", "max_rho_max"),
    ("lbm_max_v_max", "<", "max_lbm_max_v"),
    ("mpm_min_J_min", ">", "min_mpm_min_J"),
    ("mpm_max_speed_max", "<", "max_mpm_max_speed"),
    ("projected_mass_final", ">", "min_projected_mass_final"),
    ("active_cell_count_final", ">=", "min_active_cell_count_final"),
    ("bb_link_count_max", ">", 0),
    ("bb_max_correction_max", ">=", 0.0),
    ("active_reaction_particle_count_final", ">=", 0),
    ("applied_cell_count", ">=", "min_applied_cell_count"),
    ("ggui_screenshot_size_bytes", ">=", "min_screenshot_size_bytes"),
]


def build_step96_taichi_ggui_10step_visualization_quality_audit(
    root: Path,
    matrix_artifact_path: str = (
        "outputs/step96_taichi_ggui_10step_visualization_run_matrix/"
        "taichi_ggui_10step_visualization_run_matrix.json"
    ),
    acceptance_policy_path: str = "configs/step96_taichi_ggui_10step_visualization_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    payload = read_json(root / matrix_artifact_path)
    policy = read_json(root / acceptance_policy_path)
    rows = []
    for matrix_row in payload["rows"]:
        rows.extend(quality_rows(matrix_row, policy))
    summary = {
        "boundary_motion_interface_report_pass_count": sum(
            1 for row in payload["rows"] if row["boundary_motion_interface_report_pass"]
        ),
        "capped_wall_velocity_report_count": sum(1 for row in payload["rows"] if row["cap_pass"]),
        "finite_max_grid_reaction_norm_count": sum(
            1 for row in payload["rows"] if math.isfinite(float(row["max_grid_reaction_norm_max"]))
        ),
        "finite_wall_velocity_report_count": sum(1 for row in payload["rows"] if row["finite_pass"]),
        "from_step92_adds_ggui_visualization_count": sum(
            1 for row in payload["rows"] if row["from_step92_adds_ggui_visualization"]
        ),
        "from_step94_duration_expansion_count": sum(
            1 for row in payload["rows"] if row["from_step94_duration_expansion"]
        ),
        "geometry_motion_interface_report_pass_count": sum(
            1 for row in payload["rows"] if row["geometry_motion_interface_report_pass"]
        ),
        "geometry_quality_report_pass_count": sum(1 for row in payload["rows"] if row["geometry_quality_report_pass"]),
        "ggui_render_report_pass_count": sum(1 for row in payload["rows"] if row["ggui_render_report_pass"]),
        "ggui_screenshot_exists_count": sum(1 for row in payload["rows"] if row["ggui_screenshot_exists"]),
        "mutation_flag_enabled_count_max": max(int(row["mutation_flag_enabled_count"]) for row in payload["rows"]),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "source_matrix_row_count": len(payload["rows"]),
        "squid_proxy_enabled_count": sum(1 for row in payload["rows"] if row["squid_proxy_enabled"]),
        "step96_taichi_ggui_10step_visualization_quality_pass": False,
        "wall_velocity_application_report_pass_count": sum(
            1 for row in payload["rows"] if row["wall_velocity_application_report_pass"]
        ),
    }
    summary["step96_taichi_ggui_10step_visualization_quality_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["geometry_quality_report_pass_count"] == summary["source_matrix_row_count"]
        and summary["geometry_motion_interface_report_pass_count"] == summary["source_matrix_row_count"]
        and summary["wall_velocity_application_report_pass_count"] == summary["source_matrix_row_count"]
        and summary["boundary_motion_interface_report_pass_count"] == summary["source_matrix_row_count"]
        and summary["ggui_render_report_pass_count"] == summary["source_matrix_row_count"]
        and summary["ggui_screenshot_exists_count"] == summary["source_matrix_row_count"]
        and summary["finite_wall_velocity_report_count"] == summary["source_matrix_row_count"]
        and summary["capped_wall_velocity_report_count"] == summary["source_matrix_row_count"]
        and summary["finite_max_grid_reaction_norm_count"] == summary["source_matrix_row_count"]
        and summary["squid_proxy_enabled_count"] == summary["source_matrix_row_count"]
        and summary["from_step94_duration_expansion_count"] == summary["source_matrix_row_count"]
        and summary["from_step92_adds_ggui_visualization_count"] == summary["source_matrix_row_count"]
        and summary["mutation_flag_enabled_count_max"] == 0
    )
    return rows, summary


def quality_rows(matrix_row: dict, policy: dict) -> list[dict]:
    rows = []
    for metric, op, expected_key in QUALITY_CHECKS:
        expected = policy[expected_key] if isinstance(expected_key, str) else expected_key
        actual = matrix_row[metric]
        rows.append(
            {
                "actual": actual,
                "check": metric,
                "expected": expected,
                "operator": op,
                "pass": compare(actual, op, expected),
                "row_name": matrix_row["row_name"],
            }
        )
    rows.extend(
        [
            literal_row(matrix_row, "has_nan", False),
            literal_row(matrix_row, "has_inf", False),
            literal_row(matrix_row, "stable", True),
            literal_row(matrix_row, "diagnostics_csv_exists", True),
            literal_row(matrix_row, "diagnostics_npz_exists", True),
            literal_row(matrix_row, "driver_config_exists", True),
            literal_row(matrix_row, "driver_timing_exists", True),
            literal_row(matrix_row, "geo_path_name", "geo_all_fluid_32.dat"),
            literal_row(matrix_row, "runtime_hard_fail", False),
            literal_row(matrix_row, "previous_step", "Step95"),
            literal_row(matrix_row, "from_step94_duration_expansion", True),
            literal_row(matrix_row, "from_step92_adds_ggui_visualization", True),
            literal_row(matrix_row, "previous_step92_n_lbm_steps", 10),
            literal_row(matrix_row, "previous_step94_n_lbm_steps", 1),
            literal_row(matrix_row, "step96_n_lbm_steps", 10),
            literal_row(matrix_row, "geometry_type", "squid_proxy"),
            literal_row(matrix_row, "squid_proxy_enabled", True),
            literal_row(matrix_row, "procedural_geometry_enabled", True),
            literal_row(matrix_row, "real_geometry_candidate_enabled", False),
            literal_row(matrix_row, "real_geometry_enabled", False),
            literal_row(matrix_row, "runtime_geometry_enabled", True),
            literal_row(matrix_row, "wall_velocity_enabled", True),
            literal_row(matrix_row, "combined_runtime_geometry_wall_velocity_enabled", True),
            literal_row(matrix_row, "ggui_visualization_enabled", True),
            literal_row(matrix_row, "ggui_renderer_called", True),
            literal_row(matrix_row, "ggui_window_created", True),
            literal_row(matrix_row, "ggui_scene_created", True),
            literal_row(matrix_row, "ggui_camera_configured", True),
            literal_row(matrix_row, "ggui_screenshot_enabled", True),
            literal_row(matrix_row, "ggui_screenshot_exists", True),
            literal_row(matrix_row, "ggui_screenshot_file_count", 1),
            literal_row(matrix_row, "ggui_video_enabled", False),
            literal_row(matrix_row, "ggui_video_file_count", 0),
            literal_row(matrix_row, "ggui_render_report_exists", True),
            literal_row(matrix_row, "ggui_render_report_pass", True),
            literal_row(matrix_row, "link_area_enabled", False),
            literal_row(matrix_row, "geometry_quality_report_exists", True),
            literal_row(matrix_row, "geometry_quality_report_pass", True),
            literal_row(matrix_row, "geometry_quality_strict", False),
            literal_row(matrix_row, "quality_report_geometry_type", "squid_proxy"),
            literal_row(matrix_row, "quality_report_empty", False),
            min_row(matrix_row, "quality_report_occupied_count", 1),
            min_row(matrix_row, "quality_report_surface_voxel_count", 1),
            literal_row(matrix_row, "quality_report_touches_domain_boundary", False),
            literal_row(matrix_row, "sampling_stats_exist", True),
            literal_row(matrix_row, "sampling_geometry_type", "squid_proxy"),
            literal_row(matrix_row, "sampling_particle_count", policy["required_n_particles"]),
            min_row(matrix_row, "mantle_particle_count", 1),
            min_row(matrix_row, "head_particle_count", 1),
            min_row(matrix_row, "arms_particle_count", 1),
            literal_row(matrix_row, "geometry_motion_interface_report_exists", True),
            literal_row(matrix_row, "geometry_motion_interface_report_pass", True),
            literal_row(matrix_row, "diagnostic_only", True),
            literal_row(matrix_row, "no_op_pass", True),
            literal_row(matrix_row, "config_validation_pass", True),
            literal_row(matrix_row, "mutation_flag_enabled_count", 0),
            literal_row(matrix_row, "apply_to_driver", False),
            literal_row(matrix_row, "apply_to_mpm_particles", False),
            literal_row(matrix_row, "apply_to_lbm_solid_phi", False),
            literal_row(matrix_row, "apply_to_lbm_solid_vel", False),
            literal_row(matrix_row, "apply_to_projection", False),
            literal_row(matrix_row, "update_dynamic_solid", False),
            literal_row(matrix_row, "recompute_boundary_links", False),
            literal_row(matrix_row, "mutate_geometry_state", False),
            literal_row(matrix_row, "wall_velocity_application_report_exists", True),
            literal_row(matrix_row, "wall_velocity_application_report_pass", True),
            literal_row(matrix_row, "target_lbm_field", "solid_vel"),
            literal_row(matrix_row, "application_policy", "additive_capped"),
            literal_row(matrix_row, "apply_to_lbm_solid_vel_wall_velocity", True),
            literal_row(matrix_row, "apply_to_lbm_populations", False),
            literal_row(matrix_row, "apply_to_mpm", False),
            literal_row(matrix_row, "apply_to_projector", False),
            literal_row(matrix_row, "modify_bounceback_formula", False),
            literal_row(matrix_row, "jet_model_enabled", False),
            literal_row(matrix_row, "actuation_claim_enabled", False),
            literal_row(matrix_row, "finite_pass", True),
            literal_row(matrix_row, "cap_pass", True),
            literal_row(matrix_row, "boundary_motion_interface_report_exists", True),
            literal_row(matrix_row, "boundary_motion_interface_report_pass", True),
            literal_row(matrix_row, "boundary_motion_diagnostic_only", True),
            int_equal_row(matrix_row, "lbm_population_update_count", 0),
            int_equal_row(matrix_row, "completed_lbm_steps", policy["required_n_lbm_steps"]),
            finite_row(matrix_row, "max_grid_reaction_norm_max"),
        ]
    )
    return rows


def literal_row(matrix_row: dict, metric: str, expected) -> dict:
    actual = matrix_row[metric]
    return {
        "actual": actual,
        "check": metric,
        "expected": expected,
        "operator": "==",
        "pass": actual == expected,
        "row_name": matrix_row["row_name"],
    }


def min_row(matrix_row: dict, metric: str, expected_min: int) -> dict:
    actual = int(matrix_row[metric])
    return {
        "actual": actual,
        "check": metric,
        "expected": expected_min,
        "operator": ">=",
        "pass": actual >= int(expected_min),
        "row_name": matrix_row["row_name"],
    }


def int_equal_row(matrix_row: dict, metric: str, expected: int) -> dict:
    actual = int(matrix_row[metric])
    return {
        "actual": actual,
        "check": metric,
        "expected": expected,
        "operator": "==",
        "pass": actual == int(expected),
        "row_name": matrix_row["row_name"],
    }


def finite_row(matrix_row: dict, metric: str) -> dict:
    actual = float(matrix_row[metric])
    return {
        "actual": actual,
        "check": f"{metric}_finite",
        "expected": True,
        "operator": "is_finite",
        "pass": math.isfinite(actual),
        "row_name": matrix_row["row_name"],
    }


def compare(actual, op: str, expected) -> bool:
    actual_value = float(actual)
    expected_value = float(expected)
    if op == ">":
        return actual_value > expected_value
    if op == "<":
        return actual_value < expected_value
    if op == ">=":
        return actual_value >= expected_value
    raise ValueError(f"unsupported comparison operator: {op}")


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
