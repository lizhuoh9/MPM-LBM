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
]


def build_step80_runtime_geometry_diagnostic_only_quality_audit(
    root: Path,
    matrix_artifact_path: str = "outputs/step80_runtime_geometry_diagnostic_only_smoke_matrix/runtime_geometry_diagnostic_only_smoke_matrix.json",
    acceptance_policy_path: str = "configs/step80_runtime_geometry_diagnostic_only_acceptance_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    payload = read_json(root / matrix_artifact_path)
    policy = read_json(root / acceptance_policy_path)
    rows = []
    for matrix_row in payload["rows"]:
        rows.extend(quality_rows(matrix_row, policy))
    summary = {
        "finite_max_grid_reaction_norm_count": sum(
            1 for row in payload["rows"] if math.isfinite(float(row["max_grid_reaction_norm_max"]))
        ),
        "geometry_motion_interface_report_pass_count": sum(
            1 for row in payload["rows"] if row["geometry_motion_interface_report_pass"]
        ),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "row_count": len(rows),
        "source_matrix_row_count": len(payload["rows"]),
        "step80_runtime_geometry_diagnostic_only_quality_pass": False,
    }
    summary["step80_runtime_geometry_diagnostic_only_quality_pass"] = bool(
        rows
        and summary["pass_count"] == summary["row_count"]
        and summary["finite_max_grid_reaction_norm_count"] == summary["source_matrix_row_count"]
        and summary["geometry_motion_interface_report_pass_count"] == summary["source_matrix_row_count"]
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
            bool_row(matrix_row, "has_nan", False),
            bool_row(matrix_row, "has_inf", False),
            bool_row(matrix_row, "stable", True),
            bool_row(matrix_row, "diagnostics_csv_exists", True),
            bool_row(matrix_row, "diagnostics_npz_exists", True),
            bool_row(matrix_row, "driver_config_exists", True),
            bool_row(matrix_row, "geo_path_name", "geo_all_fluid_32.dat"),
            bool_row(matrix_row, "runtime_hard_fail", False),
            bool_row(matrix_row, "previous_step", "Step79"),
            bool_row(matrix_row, "runtime_geometry_enabled", True),
            bool_row(matrix_row, "geometry_motion_interface_report_exists", True),
            bool_row(matrix_row, "geometry_motion_interface_report_pass", True),
            bool_row(matrix_row, "no_op_pass", True),
            bool_row(matrix_row, "config_validation_pass", True),
            bool_row(matrix_row, "diagnostic_only", True),
            {
                "actual": matrix_row["mutation_flag_enabled_count"],
                "check": "mutation_flag_enabled_count",
                "expected": 0,
                "operator": "==",
                "pass": int(matrix_row["mutation_flag_enabled_count"]) == 0,
                "row_name": matrix_row["row_name"],
            },
            {
                "actual": matrix_row["completed_lbm_steps"],
                "check": "completed_lbm_steps",
                "expected": policy["required_n_lbm_steps"],
                "operator": "==",
                "pass": int(matrix_row["completed_lbm_steps"]) == int(policy["required_n_lbm_steps"]),
                "row_name": matrix_row["row_name"],
            },
            {
                "actual": matrix_row["max_grid_reaction_norm_max"],
                "check": "max_grid_reaction_norm_max_finite",
                "expected": True,
                "operator": "is_finite",
                "pass": math.isfinite(float(matrix_row["max_grid_reaction_norm_max"])),
                "row_name": matrix_row["row_name"],
            },
        ]
    )
    return rows


def bool_row(matrix_row: dict, metric: str, expected) -> dict:
    actual = matrix_row[metric]
    return {
        "actual": actual,
        "check": metric,
        "expected": expected,
        "operator": "==",
        "pass": actual == expected,
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
