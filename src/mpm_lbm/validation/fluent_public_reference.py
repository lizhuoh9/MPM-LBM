from __future__ import annotations

import csv
from pathlib import Path


REFERENCE_DISPLACEMENT_KEY = "fluent_public_digitized_total_displacement_m"
SOLVER_DISPLACEMENT_KEY = "solver_total_displacement_m"


def load_public_fluent_reference_curve(path: str | Path) -> list[dict]:
    rows = []
    for row in _read_csv(path):
        rows.append(
            {
                "digitization_method": row.get("digitization_method", ""),
                "digitization_uncertainty_m": _float(row["digitization_uncertainty_m"], "digitization_uncertainty_m"),
                REFERENCE_DISPLACEMENT_KEY: _float(row[REFERENCE_DISPLACEMENT_KEY], REFERENCE_DISPLACEMENT_KEY),
                "source_figure": row.get("source_figure", ""),
                "time_s": _float(row["time_s"], "time_s"),
            }
        )
    _require_monotone_time(rows, "reference")
    return rows


def load_solver_displacement_curve(
    path: str | Path,
    monitor_name: str,
    time_column: str = "time_s",
    displacement_column: str = "flap_tip_total_displacement_m",
) -> list[dict]:
    rows = []
    for row in _read_csv(path):
        rows.append(
            {
                "monitor_equivalence": False,
                "monitor_used": monitor_name,
                SOLVER_DISPLACEMENT_KEY: _float(row[displacement_column], displacement_column),
                "time_s": _float(row[time_column], time_column),
            }
        )
    _require_monotone_time(rows, "solver")
    return rows


def resample_to_common_time_grid(reference_rows: list[dict], solver_rows: list[dict]) -> tuple[list[dict], list[dict]]:
    if not reference_rows:
        raise ValueError("reference_rows must not be empty")
    if not solver_rows:
        raise ValueError("solver_rows must not be empty")
    solver_times = [float(row["time_s"]) for row in solver_rows]
    solver_values = [float(row[SOLVER_DISPLACEMENT_KEY]) for row in solver_rows]
    aligned_reference = []
    aligned_solver = []
    for row in reference_rows:
        time_s = float(row["time_s"])
        aligned_reference.append(
            {
                REFERENCE_DISPLACEMENT_KEY: float(row[REFERENCE_DISPLACEMENT_KEY]),
                "time_s": time_s,
            }
        )
        aligned_solver.append(
            {
                "monitor_equivalence": bool(solver_rows[0].get("monitor_equivalence", False)),
                "monitor_used": solver_rows[0].get("monitor_used", ""),
                SOLVER_DISPLACEMENT_KEY: _interpolate_with_endpoint_hold(solver_times, solver_values, time_s),
                "time_s": time_s,
            }
        )
    return aligned_reference, aligned_solver


def write_reference_csv(path: str | Path, rows: list[dict]) -> None:
    fields = [
        "time_s",
        REFERENCE_DISPLACEMENT_KEY,
        "digitization_uncertainty_m",
        "source_figure",
        "digitization_method",
    ]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def _read_csv(path: str | Path) -> list[dict]:
    path = Path(path)
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _float(value, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric: {value!r}") from exc
    if number != number or number in (float("inf"), float("-inf")):
        raise ValueError(f"{name} must be finite: {value!r}")
    return number


def _require_monotone_time(rows: list[dict], label: str) -> None:
    if not rows:
        raise ValueError(f"{label} curve must not be empty")
    prev = float("-inf")
    for row in rows:
        time_s = float(row["time_s"])
        if time_s < prev:
            raise ValueError(f"{label} curve time_s must be monotone")
        prev = time_s


def _interpolate_with_endpoint_hold(times: list[float], values: list[float], query_time: float) -> float:
    if query_time <= times[0]:
        return values[0]
    if query_time >= times[-1]:
        return values[-1]
    for index in range(1, len(times)):
        left_t = times[index - 1]
        right_t = times[index]
        if left_t <= query_time <= right_t:
            if right_t == left_t:
                return values[index]
            alpha = (query_time - left_t) / (right_t - left_t)
            return values[index - 1] + alpha * (values[index] - values[index - 1])
    return values[-1]
