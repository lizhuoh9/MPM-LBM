from __future__ import annotations

import math
from pathlib import Path

from src.mpm_lbm.evidence.step111_common import (
    numeric_values_finite,
    read_json,
    reset_output_dir,
    summary_rows,
    write_csv_rows,
    write_json,
    write_markdown_table,
)
from src.mpm_lbm.validation.error_metrics import compute_displacement_error_metrics
from src.mpm_lbm.validation.fluent_public_reference import (
    load_public_fluent_reference_curve,
    load_solver_displacement_curve,
    resample_to_common_time_grid,
)


ERROR_FIELDS = [
    "error_source",
    "reference_loaded",
    "solver_curve_loaded",
    "monitor_used",
    "monitor_equivalence",
    "sample_count",
    "solver_curve_time_start_s",
    "solver_curve_time_end_s",
    "peak_reference_m",
    "peak_solver_m",
    "peak_abs_error_m",
    "peak_relative_error",
    "rms_abs_error_m",
    "normalized_rms_error",
    "peak_time_error_s",
    "shape_correlation",
    "all_metrics_finite",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
    "stable",
]


def build_step111_error_comparison(root: Path, policy_path: str = "configs/step111_error_policy.json") -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    reference_rows = load_public_fluent_reference_curve(root / policy["reference_curve_path"])
    solver_rows = load_solver_displacement_curve(
        root / policy["solver_curve_path"],
        monitor_name=policy["monitor_used"],
        time_column=policy["solver_time_column"],
        displacement_column=policy["solver_displacement_column"],
    )
    reference_aligned, solver_aligned = resample_to_common_time_grid(reference_rows, solver_rows)
    row = compute_displacement_error_metrics(reference_aligned, solver_aligned, policy)
    row["error_source"] = "real_solver_monitor_timeseries"
    row["solver_curve_time_start_s"] = float(solver_rows[0]["time_s"])
    row["solver_curve_time_end_s"] = float(solver_rows[-1]["time_s"])
    row["all_metrics_finite"] = bool(row["all_metrics_finite"] and numeric_values_finite(row))
    row["stable"] = error_row_pass(row, policy)
    rows = [row]
    summary = {
        "direct_quantitative_equivalence_allowed": False,
        "error_source": "real_solver_monitor_timeseries",
        "normalized_rms_beats_step108": bool(row["normalized_rms_error"] < float(policy["step108_normalized_rms_error"])),
        "peak_solver_above_minimum": bool(abs(float(row["peak_solver_m"])) > float(policy["min_peak_solver_m"])),
        "row_count": 1,
        "shape_correlation_beats_step108": bool(row["shape_correlation"] > float(policy["step108_shape_correlation"])),
        "step111_error_comparison_pass": bool(row["stable"]),
        "validation_claim_allowed": False,
    }
    out_dir = root / "outputs" / "step111_error_comparison"
    reset_output_dir(out_dir, root / "outputs")
    write_error_artifacts(out_dir, rows, summary)
    return rows, summary


def error_row_pass(row: dict, policy: dict) -> bool:
    return bool(
        row["error_source"] == "real_solver_monitor_timeseries"
        and row["reference_loaded"]
        and row["solver_curve_loaded"]
        and int(row["sample_count"]) == int(policy["expected_solver_curve_rows"])
        and math.isclose(float(row["solver_curve_time_end_s"]), float(policy["time_end_s"]), rel_tol=0.0, abs_tol=1.0e-15)
        and abs(float(row["peak_solver_m"])) > float(policy["min_peak_solver_m"])
        and float(row["normalized_rms_error"]) < float(policy["max_normalized_rms_error"])
        and float(row["shape_correlation"]) > float(policy["min_shape_correlation"])
        and not row["monitor_equivalence"]
        and row["all_metrics_finite"]
        and not row["validation_claim_allowed"]
        and not row["direct_quantitative_equivalence_allowed"]
        and numeric_values_finite(row)
    )


def write_error_artifacts(out_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(out_dir / "error_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "error_report.csv", rows, ERROR_FIELDS)
    write_csv_rows(out_dir / "error_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "error_report.md",
        "Step111 Real Solver Public-Plot Error Comparison",
        rows,
        ERROR_FIELDS,
        note="The solver curve comes from real solver particles and is compared to the Step107 public-plot digitization.",
    )
