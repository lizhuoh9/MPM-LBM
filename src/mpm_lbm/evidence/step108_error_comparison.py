from __future__ import annotations

import math
from pathlib import Path

from src.mpm_lbm.evidence.step108_common import (
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
    "final_reference_m",
    "final_solver_m",
    "final_abs_error_m",
    "final_relative_error",
    "time_of_peak_reference_s",
    "time_of_peak_solver_s",
    "peak_time_error_s",
    "shape_correlation",
    "sign_consistency",
    "all_metrics_finite",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
]


def build_step108_error_comparison(
    root: Path,
    policy_path: str = "configs/step108_low_mach_subcycling_policy.json",
) -> tuple[list[dict], dict]:
    root = Path(root)
    policy = dict(read_json(root / policy_path))
    policy["_step107_error_report_path"] = str(root / policy["step107_error_report_path"])
    reference_rows = load_public_fluent_reference_curve(root / policy["reference_curve_path"])
    solver_rows = load_solver_displacement_curve(
        root / policy["solver_curve_path"],
        monitor_name=policy["monitor_used"],
        time_column=policy["solver_time_column"],
        displacement_column=policy["solver_displacement_column"],
    )
    reference_aligned, solver_aligned = resample_to_common_time_grid(reference_rows, solver_rows)
    row = compute_displacement_error_metrics(reference_aligned, solver_aligned, policy)
    row["solver_curve_time_start_s"] = float(solver_rows[0]["time_s"])
    row["solver_curve_time_end_s"] = float(solver_rows[-1]["time_s"])
    row["all_metrics_finite"] = bool(row["all_metrics_finite"] and numeric_values_finite(row))
    rows = [row]
    summary = step108_error_summary(rows, policy)
    if not summary["step108_error_comparison_pass"]:
        raise RuntimeError(f"Step108 error comparison failed: {summary}")
    out_dir = root / "outputs" / "step108_error_comparison"
    reset_output_dir(out_dir, root / "outputs")
    write_step108_error_artifacts(out_dir, rows, summary)
    return rows, summary


def step108_error_summary(rows: list[dict], policy: dict) -> dict:
    step107_row = read_step107_baseline_row(Path(policy["_step107_error_report_path"]))
    row = rows[0] if rows else {}
    summary = {
        "all_metrics_finite_count": sum(1 for item in rows if item["all_metrics_finite"]),
        "direct_quantitative_equivalence_allowed": False,
        "min_sample_count": 10,
        "row_count": len(rows),
        "soft_goals_are_hard_gates": False,
        "solver_curve_time_end_s": row.get("solver_curve_time_end_s"),
        "step107_normalized_rms_error": step107_row["normalized_rms_error"],
        "step107_peak_solver_m": step107_row["peak_solver_m"],
        "step107_shape_correlation": step107_row["shape_correlation"],
        "step108_error_comparison_pass": False,
        "step108_normalized_rms_improved": False,
        "step108_peak_solver_improved": False,
        "step108_shape_correlation_improved": False,
        "validation_claim_allowed": False,
    }
    if rows:
        current = rows[0]
        summary["step108_peak_solver_improved"] = bool(abs(current["peak_solver_m"]) > abs(step107_row["peak_solver_m"]))
        summary["step108_normalized_rms_improved"] = bool(current["normalized_rms_error"] < step107_row["normalized_rms_error"])
        summary["step108_shape_correlation_improved"] = bool(current["shape_correlation"] > step107_row["shape_correlation"])

    summary["step108_error_comparison_pass"] = bool(
        rows
        and all(row["reference_loaded"] for row in rows)
        and all(row["solver_curve_loaded"] for row in rows)
        and all(int(row["sample_count"]) == int(policy["expected_solver_curve_rows"]) for row in rows)
        and all(math.isclose(float(row["solver_curve_time_end_s"]), float(policy["time_end_s"]), rel_tol=0.0, abs_tol=1.0e-15) for row in rows)
        and all(not row["monitor_equivalence"] for row in rows)
        and all(row["all_metrics_finite"] for row in rows)
        and all(numeric_values_finite(row) for row in rows)
        and all(not row["validation_claim_allowed"] for row in rows)
        and all(not row["direct_quantitative_equivalence_allowed"] for row in rows)
        and not summary["validation_claim_allowed"]
        and not summary["direct_quantitative_equivalence_allowed"]
    )
    return summary


def read_step107_baseline_row(path: Path) -> dict:
    payload = read_json(path)
    rows = payload.get("rows", [])
    if not rows:
        raise RuntimeError(f"missing Step107 baseline rows: {path}")
    return rows[0]


def write_step108_error_artifacts(out_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(out_dir / "error_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "error_report.csv", rows, ERROR_FIELDS)
    write_csv_rows(out_dir / "error_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "error_report.md",
        "Step108 Low-Mach Subcycling Error Comparison",
        rows,
        ERROR_FIELDS,
        note=(
            "This is not Fluent validation. It compares the Step108 low-Mach proxy solver curve "
            "against the Step107 approximate public-plot digitization."
        ),
    )
