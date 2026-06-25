from __future__ import annotations

import math


def composite_error_score(row: dict, peak_reference_m: float, time_end_s: float) -> float:
    peak_solver = max(abs(float(row["peak_solver_m"])), 1.0e-30)
    peak_reference = max(abs(float(peak_reference_m)), 1.0e-30)
    normalized_peak_time_error = abs(float(row["peak_time_error_s"])) / max(float(time_end_s), 1.0e-30)
    return (
        0.45 * float(row["normalized_rms_error"])
        + 0.25 * abs(math.log(peak_solver / peak_reference))
        + 0.20 * normalized_peak_time_error
        + 0.10 * (1.0 - max(float(row["shape_correlation"]), 0.0))
    )


def rank_candidate_rows(rows: list[dict], peak_reference_m: float, time_end_s: float) -> list[dict]:
    ranked = []
    for row in rows:
        updated = dict(row)
        updated["normalized_peak_time_error"] = abs(float(row["peak_time_error_s"])) / max(float(time_end_s), 1.0e-30)
        updated["composite_error_score"] = composite_error_score(row, peak_reference_m, time_end_s)
        ranked.append(updated)
    return sorted(
        ranked,
        key=lambda row: (
            float(row["composite_error_score"]),
            float(row["normalized_rms_error"]),
            float(row["peak_time_error_s"]),
        ),
    )

