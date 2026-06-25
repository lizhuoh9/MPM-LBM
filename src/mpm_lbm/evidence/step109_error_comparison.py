from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step109_common import numeric_values_finite, read_json
from src.mpm_lbm.validation.error_metrics import compute_displacement_error_metrics
from src.mpm_lbm.validation.fluent_public_reference import (
    load_public_fluent_reference_curve,
    load_solver_displacement_curve,
    resample_to_common_time_grid,
)


def evaluate_solver_curve_against_step107_public_reference(
    root: Path,
    solver_curve_path: Path,
    monitor_name: str,
    policy: dict | None = None,
    policy_path: str = "configs/step109_response_matrix_policy.json",
) -> dict:
    root = Path(root)
    policy = dict(policy or read_json(root / policy_path))
    reference_rows = load_public_fluent_reference_curve(root / policy["reference_curve_path"])
    solver_rows = load_solver_displacement_curve(
        solver_curve_path,
        monitor_name=monitor_name,
        time_column=policy["solver_time_column"],
        displacement_column=policy["solver_displacement_column"],
    )
    reference_aligned, solver_aligned = resample_to_common_time_grid(reference_rows, solver_rows)
    row = compute_displacement_error_metrics(reference_aligned, solver_aligned, policy)
    row["solver_curve_time_start_s"] = float(solver_rows[0]["time_s"])
    row["solver_curve_time_end_s"] = float(solver_rows[-1]["time_s"])
    row["all_metrics_finite"] = bool(row["all_metrics_finite"] and numeric_values_finite(row))
    return row
