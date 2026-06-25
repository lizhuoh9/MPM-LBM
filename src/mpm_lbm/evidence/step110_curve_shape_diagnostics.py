from __future__ import annotations

from pathlib import Path

from src.mpm_lbm.evidence.step110_common import read_csv_rows, read_json, reset_output_dir, summary_rows, window_rms, write_csv_rows, write_json
from src.mpm_lbm.validation.fluent_public_reference import REFERENCE_DISPLACEMENT_KEY, SOLVER_DISPLACEMENT_KEY, load_public_fluent_reference_curve


DIAGNOSTIC_FIELDS = [
    "row_name",
    "first_peak_time_s",
    "first_peak_m",
    "final_displacement_m",
    "monotonic_increasing_fraction",
    "reference_peak_time_s",
    "solver_peak_time_s",
    "peak_time_error_s",
    "early_window_rms_error_0_to_0p008",
    "mid_window_rms_error_0p008_to_0p017",
    "late_window_rms_error_0p017_to_0p025",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
]


def build_step110_curve_shape_diagnostics(root: Path, policy_path: str = "configs/step110_candidate_matrix_policy.json") -> tuple[list[dict], dict]:
    root = Path(root)
    policy = read_json(root / policy_path)
    matrix = read_json(root / "outputs" / "step110_error_minimized_candidate_matrix" / "candidate_matrix_report.json")
    out_dir = root / "outputs" / "step110_curve_shape_diagnostics"
    reset_output_dir(out_dir, root / "outputs")
    reference_rows = load_public_fluent_reference_curve(root / policy["reference_curve_path"])
    rows = []
    for candidate in matrix["rows"]:
        curve = read_csv_rows(
            root
            / "outputs"
            / "step110_error_minimized_candidate_matrix"
            / "curves"
            / f"{candidate['row_name']}_monitor_timeseries.csv"
        )
        rows.append(diagnostic_row(candidate["row_name"], reference_rows, curve))
    summary = {
        "curve_shape_diagnostics_pass": bool(
            len(rows) == len(matrix["rows"])
            and all(row["validation_claim_allowed"] is False for row in rows)
            and all(row["direct_quantitative_equivalence_allowed"] is False for row in rows)
        ),
        "diagnostic_row_count": len(rows),
        "validation_claim_allowed": False,
        "direct_quantitative_equivalence_allowed": False,
    }
    write_json(out_dir / "curve_shape_diagnostics_report.json", {"summary": summary, "rows": rows})
    write_csv_rows(out_dir / "curve_shape_diagnostics_report.csv", rows, DIAGNOSTIC_FIELDS)
    write_csv_rows(out_dir / "curve_shape_diagnostics_summary.csv", summary_rows(summary), ["metric", "value"])
    if not summary["curve_shape_diagnostics_pass"]:
        raise RuntimeError(f"Step110 curve shape diagnostics failed: {summary}")
    return rows, summary


def diagnostic_row(row_name: str, reference_rows: list[dict], curve: list[dict]) -> dict:
    solver_values = [float(row["total_displacement_m"]) for row in curve]
    solver_rows = [
        {SOLVER_DISPLACEMENT_KEY: value, "time_s": float(row["time_s"])}
        for value, row in zip(solver_values, curve)
    ]
    reference_values = [float(row[REFERENCE_DISPLACEMENT_KEY]) for row in reference_rows]
    solver_peak_index = max(range(len(solver_values)), key=lambda index: abs(solver_values[index]))
    reference_peak_index = max(range(len(reference_values)), key=lambda index: abs(reference_values[index]))
    increasing = 0
    for left, right in zip(solver_values, solver_values[1:]):
        if abs(right) >= abs(left):
            increasing += 1
    return {
        "direct_quantitative_equivalence_allowed": False,
        "early_window_rms_error_0_to_0p008": window_rms(reference_rows, solver_rows, 0.0, 0.008),
        "final_displacement_m": solver_values[-1],
        "first_peak_m": solver_values[solver_peak_index],
        "first_peak_time_s": float(curve[solver_peak_index]["time_s"]),
        "late_window_rms_error_0p017_to_0p025": window_rms(reference_rows, solver_rows, 0.017, 0.025),
        "mid_window_rms_error_0p008_to_0p017": window_rms(reference_rows, solver_rows, 0.008, 0.017),
        "monotonic_increasing_fraction": increasing / max(len(solver_values) - 1, 1),
        "peak_time_error_s": abs(float(curve[solver_peak_index]["time_s"]) - float(reference_rows[reference_peak_index]["time_s"])),
        "reference_peak_time_s": float(reference_rows[reference_peak_index]["time_s"]),
        "row_name": row_name,
        "solver_peak_time_s": float(curve[solver_peak_index]["time_s"]),
        "validation_claim_allowed": False,
    }

