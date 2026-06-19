"""Calibration helpers for Step 15 moving-boundary parameter sweeps."""

import json
import math
import os

import numpy as np

from .run_utils import save_csv_rows


def _as_float(row, key, default=0.0):
    value = row.get(key, default)
    if value == "":
        return float(default)
    return float(value)


def _as_bool(row, key, default=False):
    value = row.get(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _finite_values(row):
    values = []
    for key, value in row.items():
        if key in {
            "label",
            "mode",
            "geometry_type",
            "stable",
            "well_behaved",
            "over_damped",
            "sign_reversed",
            "recommended",
            "classification_reason",
            "reason",
            "recommendation",
            "notes",
        }:
            continue
        if value == "":
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    return values


def classify_calibration_row(row: dict) -> dict:
    values = _finite_values(row)
    finite = bool(values) and bool(np.all(np.isfinite(values)))
    rho_min = _as_float(row, "rho_min", 0.0)
    rho_max = _as_float(row, "rho_max", 1.0e9)
    lbm_max_v = _as_float(row, "lbm_max_v", 1.0e9)
    mpm_min_J = _as_float(row, "mpm_min_J", -1.0)
    mpm_max_speed = _as_float(row, "mpm_max_speed", 1.0e9)
    final_solid_vx = _as_float(row, "final_solid_vx", _as_float(row, "final_solid_vx_norm", 0.0))
    sign_reversed = _as_bool(row, "sign_reversed", final_solid_vx < 0.0)

    stable = (
        finite
        and rho_min > 0.95
        and rho_max < 1.05
        and lbm_max_v < 0.1
        and mpm_min_J > 0.0
        and mpm_max_speed < 10.0
    )
    well_behaved = (
        stable
        and rho_min > 0.98
        and rho_max < 1.02
        and mpm_min_J > 0.90
        and mpm_max_speed < 1.0
        and not sign_reversed
        and final_solid_vx > 0.0
    )
    over_damped = stable and (sign_reversed or final_solid_vx < 0.0)

    rho_span = rho_max - rho_min if math.isfinite(rho_max - rho_min) else 1.0e9
    slowdown = max(_as_float(row, "solid_slowdown", 0.0), 0.0)
    cap = _as_float(row, "force_cap_norm", _as_float(row, "mb_force_cap_norm", 0.0))
    reaction_scale = _as_float(row, "reaction_scale", _as_float(row, "mb_reaction_scale", 1.0))
    score = 0.0
    if stable:
        score += 1000.0
    if well_behaved:
        score += 1000.0
    if over_damped:
        score -= 500.0
    score -= 10000.0 * max(rho_span, 0.0)
    score -= 0.1 * mpm_max_speed
    score += 10.0 * min(slowdown, 1.0)
    score -= 100.0 * cap
    score -= 0.01 * abs(reaction_scale - 1.0)

    reasons = []
    if not finite:
        reasons.append("nonfinite")
    if not stable:
        reasons.append("unstable")
    if well_behaved:
        reasons.append("well_behaved")
    if over_damped:
        reasons.append("over_damped")
    if sign_reversed:
        reasons.append("sign_reversed")
    if not reasons:
        reasons.append("stable")

    result = dict(row)
    result.update(
        {
            "stable": bool(stable),
            "well_behaved": bool(well_behaved),
            "over_damped": bool(over_damped),
            "sign_reversed": bool(sign_reversed),
            "reason": ";".join(reasons),
            "classification_reason": ";".join(reasons),
            "score": float(score),
            "recommended": False,
        }
    )
    return result


def choose_recommended_row(rows: list[dict]) -> dict:
    classified = [classify_calibration_row(row) for row in rows]
    stable_rows = [row for row in classified if row["stable"]]
    if not stable_rows:
        raise ValueError("cannot choose a recommended row because no stable rows are available")

    well_behaved_rows = [row for row in stable_rows if row["well_behaved"] and not row["over_damped"]]
    candidates = well_behaved_rows if well_behaved_rows else [row for row in stable_rows if not row["over_damped"]]
    if not candidates:
        candidates = stable_rows

    def key(row):
        rho_span = _as_float(row, "rho_max") - _as_float(row, "rho_min")
        cap = _as_float(row, "force_cap_norm", _as_float(row, "mb_force_cap_norm", 0.0))
        sign_penalty = 1 if row["sign_reversed"] else 0
        fallback_penalty = 0 if row["well_behaved"] else 1
        return (
            fallback_penalty,
            sign_penalty,
            rho_span,
            cap,
            -_as_float(row, "solid_slowdown", 0.0),
            -_as_float(row, "score", 0.0),
        )

    chosen = dict(sorted(candidates, key=key)[0])
    chosen["recommended"] = True
    if not chosen["well_behaved"]:
        chosen["classification_reason"] = f"{chosen['classification_reason']};conservative_fallback"
        chosen["reason"] = chosen["classification_reason"]
    return chosen


def write_calibration_summary(rows, csv_path: str, json_path: str) -> dict:
    classified_rows = [classify_calibration_row(row) for row in rows]
    recommended = choose_recommended_row(classified_rows)
    output_rows = []
    for row in classified_rows:
        row_out = dict(row)
        if row is not recommended:
            same_force_cap = _as_float(row_out, "force_cap_norm", -1.0) == _as_float(recommended, "force_cap_norm", -2.0)
            same_scale = _as_float(row_out, "reaction_scale", -1.0) == _as_float(recommended, "reaction_scale", -2.0)
            row_out["recommended"] = same_force_cap and same_scale
        output_rows.append(row_out)

    fieldnames = list(output_rows[0].keys()) if output_rows else []
    save_csv_rows(output_rows, csv_path, fieldnames=fieldnames)

    summary = {
        "row_count": len(output_rows),
        "stable_count": sum(1 for row in output_rows if bool(row["stable"])),
        "well_behaved_count": sum(1 for row in output_rows if bool(row["well_behaved"])),
        "recommended": recommended,
    }
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    return summary
