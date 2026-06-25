from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step107_common import (
    ALLOWED_CLAIM,
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


def build_step107_error_comparison(
    root: Path,
    policy_path: str = "configs/step107_error_metric_policy.json",
) -> tuple[list[dict], dict]:
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
    rows = [row]
    summary = step107_error_summary(rows, policy)
    if not summary["step107_error_comparison_pass"]:
        raise RuntimeError(f"Step107 error comparison failed: {summary}")
    out_dir = root / "outputs" / "step107_error_comparison"
    reset_output_dir(out_dir, root / "outputs")
    write_step107_error_artifacts(out_dir, rows, summary)
    return rows, summary


def step107_error_summary(rows: list[dict], policy: dict) -> dict:
    summary = {
        "all_metrics_finite_count": sum(1 for row in rows if row["all_metrics_finite"]),
        "direct_quantitative_equivalence_allowed": False,
        "min_sample_count": int(policy["min_sample_count"]),
        "row_count": len(rows),
        "step107_error_comparison_pass": False,
        "validation_claim_allowed": False,
    }
    summary["step107_error_comparison_pass"] = bool(
        rows
        and all(row["reference_loaded"] for row in rows)
        and all(row["solver_curve_loaded"] for row in rows)
        and all(int(row["sample_count"]) >= int(policy["min_sample_count"]) for row in rows)
        and all(not row["monitor_equivalence"] for row in rows)
        and all(row["all_metrics_finite"] for row in rows)
        and all(numeric_values_finite(row) for row in rows)
        and all(not row["validation_claim_allowed"] for row in rows)
        and all(not row["direct_quantitative_equivalence_allowed"] for row in rows)
        and not summary["validation_claim_allowed"]
        and not summary["direct_quantitative_equivalence_allowed"]
    )
    return summary


def write_step107_error_artifacts(out_dir: Path, rows: list[dict], summary: dict) -> None:
    write_json(out_dir / "error_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "error_report.csv", rows, ERROR_FIELDS)
    write_csv_rows(out_dir / "error_summary.csv", summary_rows(summary), ["metric", "value"])
    write_markdown_table(
        out_dir / "error_report.md",
        "Step107 Public Fluent Plot Error Comparison",
        rows,
        ERROR_FIELDS,
        note=(
            "This is not Fluent validation. It compares the current proxy solver displacement curve "
            "against an approximate public-plot digitization with explicit uncertainty."
        ),
    )
