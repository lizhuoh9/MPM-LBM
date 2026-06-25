from __future__ import annotations


def normalized_peak_time_error(peak_time_error_s: float, time_end_s: float) -> float:
    if abs(float(time_end_s)) <= 1.0e-30:
        return 0.0
    return abs(float(peak_time_error_s)) / float(time_end_s)


def real_candidate_score(row: dict, time_end_s: float) -> float:
    normalized_time = normalized_peak_time_error(float(row["peak_time_error_s"]), time_end_s)
    correlation_penalty = 1.0 - max(float(row["shape_correlation"]), 0.0)
    return (
        0.35 * float(row["normalized_rms_error"])
        + 0.25 * float(row["peak_relative_error"])
        + 0.25 * normalized_time
        + 0.15 * correlation_penalty
    )


def sort_real_candidate_rows(rows: list[dict], time_end_s: float) -> list[dict]:
    scored = []
    for row in rows:
        updated = dict(row)
        updated["normalized_peak_time_error"] = normalized_peak_time_error(float(row["peak_time_error_s"]), time_end_s)
        updated["composite_error_score"] = real_candidate_score(updated, time_end_s)
        scored.append(updated)
    return sorted(scored, key=lambda row: (not row.get("stable", False), float(row["composite_error_score"])))
