from __future__ import annotations

import math

from src.mpm_lbm.validation.fluent_public_reference import REFERENCE_DISPLACEMENT_KEY, SOLVER_DISPLACEMENT_KEY


def compute_displacement_error_metrics(reference_rows: list[dict], solver_rows: list[dict], policy: dict) -> dict:
    if len(reference_rows) != len(solver_rows):
        raise ValueError("reference_rows and solver_rows must have the same length")
    if not reference_rows:
        raise ValueError("at least one sample is required")

    ref_values = [float(row[REFERENCE_DISPLACEMENT_KEY]) for row in reference_rows]
    solver_values = [float(row[SOLVER_DISPLACEMENT_KEY]) for row in solver_rows]
    times = [float(row["time_s"]) for row in reference_rows]
    eps = float(policy.get("relative_error_epsilon_m", policy.get("relative_error_epsilon", 1.0e-12)))

    peak_ref_index = max(range(len(ref_values)), key=lambda index: abs(ref_values[index]))
    peak_solver_index = max(range(len(solver_values)), key=lambda index: abs(solver_values[index]))
    peak_ref = ref_values[peak_ref_index]
    peak_solver = solver_values[peak_solver_index]
    errors = [solver - ref for ref, solver in zip(ref_values, solver_values)]
    abs_errors = [abs(value) for value in errors]
    rms_abs_error = math.sqrt(sum(value * value for value in abs_errors) / len(abs_errors))
    final_ref = ref_values[-1]
    final_solver = solver_values[-1]
    metrics = {
        "all_metrics_finite": False,
        "direct_quantitative_equivalence_allowed": bool(policy.get("direct_quantitative_equivalence_allowed", False)),
        "final_abs_error_m": abs(final_solver - final_ref),
        "final_reference_m": final_ref,
        "final_relative_error": abs(final_solver - final_ref) / max(abs(final_ref), eps),
        "final_solver_m": final_solver,
        "monitor_equivalence": bool(policy.get("monitor_equivalence", False)),
        "monitor_used": policy.get("monitor_used", ""),
        "normalized_rms_error": rms_abs_error / max(abs(peak_ref), eps),
        "peak_abs_error_m": abs(peak_solver - peak_ref),
        "peak_reference_m": peak_ref,
        "peak_relative_error": abs(peak_solver - peak_ref) / max(abs(peak_ref), eps),
        "peak_solver_m": peak_solver,
        "peak_time_error_s": abs(times[peak_solver_index] - times[peak_ref_index]),
        "reference_loaded": True,
        "rms_abs_error_m": rms_abs_error,
        "sample_count": len(reference_rows),
        "shape_correlation": shape_correlation(ref_values, solver_values),
        "sign_consistency": sign_consistency(ref_values, solver_values),
        "solver_curve_loaded": True,
        "time_of_peak_reference_s": times[peak_ref_index],
        "time_of_peak_solver_s": times[peak_solver_index],
        "validation_claim_allowed": bool(policy.get("validation_claim_allowed", False)),
    }
    metrics["all_metrics_finite"] = finite_metric_row(metrics)
    return metrics


def shape_correlation(reference_values: list[float], solver_values: list[float]) -> float:
    if len(reference_values) != len(solver_values) or not reference_values:
        raise ValueError("shape_correlation requires equal non-empty vectors")
    ref_mean = sum(reference_values) / len(reference_values)
    solver_mean = sum(solver_values) / len(solver_values)
    ref_centered = [value - ref_mean for value in reference_values]
    solver_centered = [value - solver_mean for value in solver_values]
    numerator = sum(a * b for a, b in zip(ref_centered, solver_centered))
    ref_norm = math.sqrt(sum(value * value for value in ref_centered))
    solver_norm = math.sqrt(sum(value * value for value in solver_centered))
    if ref_norm <= 1.0e-30 or solver_norm <= 1.0e-30:
        return 0.0
    return max(-1.0, min(1.0, numerator / (ref_norm * solver_norm)))


def sign_consistency(reference_values: list[float], solver_values: list[float]) -> bool:
    for ref, solver in zip(reference_values, solver_values):
        if abs(ref) <= 1.0e-30 or abs(solver) <= 1.0e-30:
            continue
        if (ref > 0.0) != (solver > 0.0):
            return False
    return True


def finite_metric_row(metrics: dict) -> bool:
    for value in metrics.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True
