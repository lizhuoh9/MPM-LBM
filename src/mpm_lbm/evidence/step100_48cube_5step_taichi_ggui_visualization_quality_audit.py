from __future__ import annotations

import json
import math
from pathlib import Path


def build_step100_48cube_5step_taichi_ggui_visualization_quality_audit(
    root: Path,
    matrix_artifact_path: str = (
        "outputs/step100_48cube_5step_taichi_ggui_visualization_run_matrix/"
        "48cube_5step_taichi_ggui_visualization_run_matrix.json"
    ),
) -> tuple[list[dict], dict]:
    root = Path(root)
    matrix = read_json(root / matrix_artifact_path)
    matrix_rows = matrix["rows"]
    rows = [row for matrix_row in matrix_rows for row in quality_rows(matrix_row)]
    summary = {
        "boundary_motion_interface_report_pass_count": sum(
            1 for row in matrix_rows if row["boundary_motion_interface_report_pass"]
        ),
        "capped_wall_velocity_report_count": sum(1 for row in matrix_rows if row["cap_pass"]),
        "finite_max_grid_reaction_norm_count": sum(
            1 for row in matrix_rows if math.isfinite(float(row["max_grid_reaction_norm_max"]))
        ),
        "finite_wall_velocity_report_count": sum(1 for row in matrix_rows if row["finite_pass"]),
        "from_step98_duration_expansion_count": sum(1 for row in matrix_rows if row["from_step98_duration_expansion"]),
        "geometry_motion_interface_report_pass_count": sum(
            1 for row in matrix_rows if row["geometry_motion_interface_report_pass"]
        ),
        "geometry_quality_report_pass_count": sum(1 for row in matrix_rows if row["geometry_quality_report_pass"]),
        "ggui_render_report_pass_count": sum(1 for row in matrix_rows if row["ggui_render_report_pass"]),
        "ggui_screenshot_exists_count": sum(1 for row in matrix_rows if row["ggui_screenshot_exists"]),
        "mutation_flag_enabled_count_max": max(
            (int(row["mutation_flag_enabled_count"]) for row in matrix_rows),
            default=0,
        ),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "quality_row_count": len(rows),
        "row_count": len(rows),
        "source_matrix_row_count": len(matrix_rows),
        "squid_proxy_enabled_count": sum(1 for row in matrix_rows if row["squid_proxy_enabled"]),
        "step100_48cube_5step_taichi_ggui_visualization_quality_pass": False,
        "wall_velocity_application_report_pass_count": sum(
            1 for row in matrix_rows if row["wall_velocity_application_report_pass"]
        ),
    }
    summary["step100_48cube_5step_taichi_ggui_visualization_quality_pass"] = bool(
        rows
        and summary["pass_count"] == summary["quality_row_count"]
        and summary["source_matrix_row_count"] == 1
        and summary["geometry_quality_report_pass_count"] == 1
        and summary["geometry_motion_interface_report_pass_count"] == 1
        and summary["wall_velocity_application_report_pass_count"] == 1
        and summary["boundary_motion_interface_report_pass_count"] == 1
        and summary["ggui_render_report_pass_count"] == 1
        and summary["ggui_screenshot_exists_count"] == 1
        and summary["finite_wall_velocity_report_count"] == 1
        and summary["capped_wall_velocity_report_count"] == 1
        and summary["finite_max_grid_reaction_norm_count"] == 1
        and summary["squid_proxy_enabled_count"] == 1
        and summary["from_step98_duration_expansion_count"] == 1
        and summary["mutation_flag_enabled_count_max"] == 0
    )
    return rows, summary


def quality_rows(matrix_row: dict) -> list[dict]:
    return [
        literal_row(matrix_row, "row_name", matrix_row["row_name"]),
        literal_row(matrix_row, "stable", True),
        literal_row(matrix_row, "n_grid", 48),
        literal_row(matrix_row, "n_lbm_steps", 5),
        literal_row(matrix_row, "completed_lbm_steps", 5),
        literal_row(matrix_row, "from_step98_duration_expansion", True),
        literal_row(matrix_row, "previous_step98_n_grid", 48),
        literal_row(matrix_row, "previous_step98_n_lbm_steps", 1),
        literal_row(matrix_row, "only_new_dimension_from_step98", "n_lbm_steps_5"),
        literal_row(matrix_row, "grid_48_enabled", True),
        literal_row(matrix_row, "grid_64_enabled", False),
        literal_row(matrix_row, "geometry_quality_report_pass", True),
        literal_row(matrix_row, "geometry_motion_interface_report_pass", True),
        literal_row(matrix_row, "wall_velocity_application_report_pass", True),
        literal_row(matrix_row, "boundary_motion_interface_report_pass", True),
        literal_row(matrix_row, "ggui_render_report_pass", True),
        literal_row(matrix_row, "ggui_screenshot_exists", True),
        literal_row(matrix_row, "finite_pass", True),
        literal_row(matrix_row, "cap_pass", True),
        min_row(matrix_row, "ggui_screenshot_size_bytes", 1),
        min_row(matrix_row, "ggui_rendered_frame_count", 1),
        int_equal_row(matrix_row, "mutation_flag_enabled_count", 0),
        int_equal_row(matrix_row, "vtr_output_count", 0),
        int_equal_row(matrix_row, "particle_npy_output_count", 0),
        finite_row(matrix_row, "max_grid_reaction_norm_max"),
        finite_row(matrix_row, "max_applied_velocity_norm"),
    ]


def literal_row(matrix_row: dict, metric: str, expected) -> dict:
    actual = matrix_row[metric]
    return {
        "actual": actual,
        "expected": expected,
        "metric": metric,
        "pass": actual == expected,
        "row_name": matrix_row["row_name"],
    }


def min_row(matrix_row: dict, metric: str, expected_min: int) -> dict:
    actual = matrix_row[metric]
    return {
        "actual": actual,
        "expected": expected_min,
        "metric": metric,
        "pass": int(actual) >= int(expected_min),
        "row_name": matrix_row["row_name"],
    }


def int_equal_row(matrix_row: dict, metric: str, expected: int) -> dict:
    actual = matrix_row[metric]
    return {
        "actual": actual,
        "expected": expected,
        "metric": metric,
        "pass": int(actual) == int(expected),
        "row_name": matrix_row["row_name"],
    }


def finite_row(matrix_row: dict, metric: str) -> dict:
    actual = float(matrix_row[metric])
    return {
        "actual": actual,
        "expected": "finite",
        "metric": metric,
        "pass": math.isfinite(actual),
        "row_name": matrix_row["row_name"],
    }


def read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
