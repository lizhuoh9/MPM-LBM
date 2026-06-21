from __future__ import annotations

import math


def ratio(left, right) -> float:
    denominator = float(right)
    if abs(denominator) <= 1.0e-15:
        return 1.0 if abs(float(left)) <= 1.0e-15 else math.inf
    return float(left) / denominator


def finite_number(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def finite_values(row: dict, excluded: set[str] | None = None) -> bool:
    excluded = excluded or set()
    for key, value in row.items():
        if key in excluded or isinstance(value, bool) or value == "":
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def row_by_name(rows: list[dict], row_name: str) -> dict:
    return next(row for row in rows if row["row_name"] == row_name)


def step_by_phase(row: dict) -> dict[float, dict]:
    return {float(step["phase"]): step for step in row["step_records"]}


def max_step_value(row: dict, field: str) -> float:
    return max(float(step[field]) for step in row["step_records"])


def min_step_value(row: dict, field: str) -> float:
    return min(float(step[field]) for step in row["step_records"])


def bool_text(value: bool) -> str:
    return "true" if bool(value) else "false"


def all_ratio_fields_finite(row: dict) -> bool:
    return all(math.isfinite(float(value)) for key, value in row.items() if key.endswith("_ratio_48_vs_32") or key.endswith("_ratio"))
