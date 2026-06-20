import csv
import json
import math
import os
from pathlib import Path

from .jet_cycle_proxy_diagnostics import (
    compute_cavity_volume_cycle_proxy,
    compute_funnel_aperture_cycle_proxy,
    compute_impulse_norm_proxy,
    estimate_cavity_rest_volume,
)


def assign_cycle_index(step: int, cycle_period_steps: int) -> int:
    step_int = int(step)
    if step_int <= 0:
        return 0
    return ((step_int - 1) // int(cycle_period_steps)) + 1


def assign_application_cycle_index(driver_lbm_step: int, cycle_period_steps: int) -> int:
    return (int(driver_lbm_step) // int(cycle_period_steps)) + 1


def split_rows_by_cycle(diagnostics_rows: list[dict], cycle_period_steps: int) -> dict[int, list[dict]]:
    by_cycle: dict[int, list[dict]] = {}
    for row in diagnostics_rows:
        cycle_index = assign_cycle_index(int(row["step"]), cycle_period_steps)
        if cycle_index <= 0:
            continue
        by_cycle.setdefault(cycle_index, []).append(row)
    return dict(sorted(by_cycle.items()))


def split_application_rows_by_cycle(application_rows: list[dict], cycle_period_steps: int) -> dict[int, list[dict]]:
    by_cycle: dict[int, list[dict]] = {}
    for row in application_rows:
        cycle_index = assign_application_cycle_index(int(row["driver_lbm_step"]), cycle_period_steps)
        by_cycle.setdefault(cycle_index, []).append(row)
    return dict(sorted(by_cycle.items()))


def summarize_cycle_stability(driver_row: dict, diagnostics_rows: list[dict], cycle_period_steps: int) -> list[dict]:
    rows = []
    for cycle_index, cycle_rows in split_rows_by_cycle(diagnostics_rows, cycle_period_steps).items():
        row = cycle_stability_row(driver_row, cycle_index, cycle_rows)
        rows.append(row)
    return rows


def cycle_stability_row(driver_row: dict, cycle_index: int, cycle_rows: list[dict]) -> dict:
    steps = [_as_int(row["step"]) for row in cycle_rows]
    projected = [_as_float(row["projected_mass"]) for row in cycle_rows]
    row = {
        "case": driver_row["case"],
        "mode_class": driver_row["mode_class"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "cycle_index": int(cycle_index),
        "step_min": min(steps),
        "step_max": max(steps),
        "row_count": len(cycle_rows),
        "rho_min": min(_as_float(row["rho_min"]) for row in cycle_rows),
        "rho_max": max(_as_float(row["rho_max"]) for row in cycle_rows),
        "lbm_max_v": max(_as_float(row["lbm_max_v"]) for row in cycle_rows),
        "mpm_min_J": min(_as_float(row["mpm_min_J"]) for row in cycle_rows),
        "mpm_max_speed": max(_as_float(row["mpm_max_speed"]) for row in cycle_rows),
        "projected_mass_min": min(projected),
        "projected_mass_max": max(projected),
        "bb_link_count_min": min(_as_int(row["bb_link_count"]) for row in cycle_rows),
        "bb_link_count_max": max(_as_int(row["bb_link_count"]) for row in cycle_rows),
        "bb_max_correction_max": max(_as_float(row["bb_max_correction"]) for row in cycle_rows),
        "hydro_force_max_norm": max(_as_float(row["hydro_force_max_norm"]) for row in cycle_rows),
    }
    row["cycle_stable"] = bool(
        row["row_count"] > 0
        and _finite_values(row.values())
        and row["rho_min"] > 0.95
        and row["rho_max"] < 1.05
        and row["lbm_max_v"] < 0.1
        and row["mpm_min_J"] > 0.0
        and row["projected_mass_min"] > 0.0
        and row["projected_mass_max"] > 0.0
        and row["bb_link_count_max"] > 0
    )
    return row


def summarize_cycle_to_cycle_drift(cycle_summaries: list[dict]) -> dict:
    by_cycle = {int(row["cycle_index"]): row for row in cycle_summaries}
    if 1 not in by_cycle or 2 not in by_cycle:
        raise ValueError("cycle drift requires cycle 1 and cycle 2 summaries")
    first = by_cycle[1]
    second = by_cycle[2]
    row = {
        "case": first["case"],
        "mode_class": first["mode_class"],
        "reaction_transfer_mode": first["reaction_transfer_mode"],
        "rho_min_drift_cycle2_minus_cycle1": _as_float(second["rho_min"]) - _as_float(first["rho_min"]),
        "rho_max_drift_cycle2_minus_cycle1": _as_float(second["rho_max"]) - _as_float(first["rho_max"]),
        "lbm_max_v_drift": _as_float(second["lbm_max_v"]) - _as_float(first["lbm_max_v"]),
        "mpm_min_J_drift": _as_float(second["mpm_min_J"]) - _as_float(first["mpm_min_J"]),
        "projected_mass_drift": _as_float(second["projected_mass_max"]) - _as_float(first["projected_mass_max"]),
        "hydro_force_max_norm_drift": _as_float(second["hydro_force_max_norm"]) - _as_float(first["hydro_force_max_norm"]),
        "bb_max_correction_drift": _as_float(second["bb_max_correction_max"]) - _as_float(first["bb_max_correction_max"]),
    }
    row["drift_pass"] = bool(
        _finite_values(row.values())
        and abs(row["projected_mass_drift"]) <= 1.0e-3
        and abs(row["lbm_max_v_drift"]) <= 5.0e-3
        and abs(row["rho_min_drift_cycle2_minus_cycle1"]) <= 5.0e-3
        and abs(row["rho_max_drift_cycle2_minus_cycle1"]) <= 5.0e-3
    )
    return row


def summarize_cavity_proxy_by_cycle(schedule_rows: list[dict], cycle_count: int, cycle_period_steps: int, geometry_config_path) -> list[dict]:
    cavity_rest_volume, source = estimate_cavity_rest_volume(geometry_config_path)
    rows = []
    for cycle_index in range(1, int(cycle_count) + 1):
        summary = compute_cavity_volume_cycle_proxy(schedule_rows, cavity_rest_volume)
        summary.update(
            {
                "metric_kind": "cavity_proxy",
                "case": "schedule_proxy",
                "cycle_index": cycle_index,
                "cycle_period_steps": int(cycle_period_steps),
                "cavity_rest_volume_source": source,
                "phase_alignment_pass": True,
                "cycle_pass": bool(summary["cavity_volume_cycle_pass"]),
                "notes": "schedule-derived cavity proxy only; no internal-fluid volume solve",
            }
        )
        rows.append(summary)
    return rows


def summarize_funnel_proxy_by_cycle(schedule_rows: list[dict], cycle_count: int, cycle_period_steps: int) -> list[dict]:
    rows = []
    for cycle_index in range(1, int(cycle_count) + 1):
        summary = compute_funnel_aperture_cycle_proxy(schedule_rows)
        summary.update(
            {
                "metric_kind": "funnel_proxy",
                "case": "schedule_proxy",
                "cycle_index": cycle_index,
                "cycle_period_steps": int(cycle_period_steps),
                "phase_alignment_pass": True,
                "cycle_pass": bool(summary["funnel_aperture_cycle_pass"]),
                "notes": "schedule-derived funnel aperture proxy only",
            }
        )
        rows.append(summary)
    return rows


def wall_velocity_proxy_by_cycle(driver_row: dict, application_rows: list[dict], cycle_period_steps: int, cycle_count: int) -> list[dict]:
    rows = []
    by_cycle = split_application_rows_by_cycle(application_rows, cycle_period_steps)
    for cycle_index in range(1, int(cycle_count) + 1):
        cycle_rows = by_cycle.get(cycle_index, [])
        rows.append(wall_velocity_cycle_row(driver_row, cycle_index, cycle_rows, cycle_period_steps))
    return rows


def wall_velocity_cycle_row(driver_row: dict, cycle_index: int, rows: list[dict], cycle_period_steps: int) -> dict:
    if not rows:
        return {
            "metric_kind": "wall_velocity_proxy",
            "case": driver_row["case"],
            "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
            "cycle_index": int(cycle_index),
            "cycle_period_steps": int(cycle_period_steps),
            "timeseries_row_count": 0,
            "cycle_pass": False,
        }
    requested = [_as_float(row["requested_phase"]) for row in rows]
    expected_last = (int(cycle_period_steps) - 1) / float(cycle_period_steps)
    applied = [_as_int(row["applied_cell_count"]) for row in rows]
    max_velocity = [_as_float(row["max_applied_velocity_norm"]) for row in rows]
    cap_values = [_as_float(row["wall_velocity_cap_lbm"]) for row in rows]
    row = {
        "metric_kind": "wall_velocity_proxy",
        "case": driver_row["case"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "cycle_index": int(cycle_index),
        "cycle_period_steps": int(cycle_period_steps),
        "timeseries_row_count": len(rows),
        "requested_phase_min": min(requested),
        "requested_phase_max": max(requested),
        "requested_phase_unique_count": len({round(value, 12) for value in requested}),
        "phase_alignment_pass": bool(min(requested) == 0.0 and max(requested) >= expected_last - 1.0e-12 and len(rows) >= int(cycle_period_steps)),
        "applied_cell_count_min": min(applied),
        "applied_cell_count_max": max(applied),
        "max_applied_velocity_norm": max(max_velocity),
        "wall_velocity_cap_lbm": max(cap_values),
        "cap_pass": all(_as_bool(row["cap_pass"]) for row in rows),
        "finite_pass": all(_as_bool(row["finite_pass"]) for row in rows) and _finite_values(requested + max_velocity),
        "lbm_population_update_count_max": max(_as_int(row["lbm_population_update_count"]) for row in rows),
        "modify_bounceback_formula_any": any(_as_bool(row["modify_bounceback_formula"]) for row in rows),
    }
    row["cycle_pass"] = bool(
        row["phase_alignment_pass"]
        and row["applied_cell_count_min"] > 0
        and row["max_applied_velocity_norm"] <= row["wall_velocity_cap_lbm"] + 1.0e-12
        and row["cap_pass"]
        and row["finite_pass"]
        and row["lbm_population_update_count_max"] == 0
        and not row["modify_bounceback_formula_any"]
    )
    return row


def wall_velocity_multicycle_quality_row(driver_row: dict, application_rows: list[dict], cycle_period_steps: int, cycle_count: int) -> dict:
    per_cycle = wall_velocity_proxy_by_cycle(driver_row, application_rows, cycle_period_steps, cycle_count)
    requested = [_as_float(row["requested_phase"]) for row in application_rows]
    row = {
        "case": driver_row["case"],
        "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
        "timeseries_row_count": len(application_rows),
        "cycle_count": int(cycle_count),
        "phase_sequence_repeats": _phase_sequence_repeats(requested, cycle_period_steps, cycle_count),
        "applied_cell_count_min": min(_as_int(row["applied_cell_count"]) for row in application_rows) if application_rows else 0,
        "applied_cell_count_max": max(_as_int(row["applied_cell_count"]) for row in application_rows) if application_rows else 0,
        "max_applied_velocity_norm": max(_as_float(row["max_applied_velocity_norm"]) for row in application_rows) if application_rows else 0.0,
        "wall_velocity_cap_lbm": max(_as_float(row["wall_velocity_cap_lbm"]) for row in application_rows) if application_rows else 0.0,
        "cap_pass": all(_as_bool(row["cap_pass"]) for row in application_rows),
        "finite_pass": all(_as_bool(row["finite_pass"]) for row in application_rows),
        "lbm_population_update_count_max": max(_as_int(row["lbm_population_update_count"]) for row in application_rows) if application_rows else 0,
        "modify_bounceback_formula_any": any(_as_bool(row["modify_bounceback_formula"]) for row in application_rows),
        "cycle_pass_count": sum(1 for row in per_cycle if _as_bool(row["cycle_pass"])),
    }
    row["quality_pass"] = bool(
        row["timeseries_row_count"] >= int(cycle_count) * int(cycle_period_steps)
        and row["cycle_pass_count"] == int(cycle_count)
        and row["phase_sequence_repeats"]
        and row["applied_cell_count_min"] > 0
        and row["max_applied_velocity_norm"] <= row["wall_velocity_cap_lbm"] + 1.0e-12
        and row["cap_pass"]
        and row["finite_pass"]
        and row["lbm_population_update_count_max"] == 0
        and not row["modify_bounceback_formula_any"]
    )
    return row


def force_impulse_proxy_rows_by_cycle(driver_row: dict, diagnostics_rows: list[dict], cycle_period_steps: int) -> list[dict]:
    rows = []
    for cycle_index, cycle_rows in split_rows_by_cycle(diagnostics_rows, cycle_period_steps).items():
        summary = compute_impulse_norm_proxy(cycle_rows)
        summary.update(
            {
                "case": driver_row["case"],
                "mode_class": driver_row["mode_class"],
                "reaction_transfer_mode": driver_row["reaction_transfer_mode"],
                "cycle_index": int(cycle_index),
                "notes": "existing-diagnostics multicycle force and bounce-back proxy only; no real impulse validation claim",
            }
        )
        rows.append(summary)
    return rows


def summarize_impulse_drift(rows: list[dict]) -> dict:
    by_case: dict[str, dict[int, dict]] = {}
    for row in rows:
        by_case.setdefault(row["case"], {})[int(row["cycle_index"])] = row
    drift_values = []
    for case_rows in by_case.values():
        if 1 in case_rows and 2 in case_rows:
            drift_values.append(
                _as_float(case_rows[2]["hydro_force_max_norm_integral_proxy"])
                - _as_float(case_rows[1]["hydro_force_max_norm_integral_proxy"])
            )
    return {
        "max_cycle_to_cycle_impulse_proxy_drift": max(abs(value) for value in drift_values) if drift_values else 0.0,
        "cycle_to_cycle_impulse_proxy_drift_finite": _finite_values(drift_values),
    }


def write_multicycle_summary(rows: list[dict], csv_path, json_path, summary: dict) -> None:
    write_csv_rows(csv_path, rows)
    write_json(json_path, {"summary": summary, "rows": rows})


def write_csv_rows(path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    fields = _fieldnames(rows) if fieldnames is None else fieldnames
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fields})


def write_json(path, data) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _phase_sequence_repeats(phases: list[float], cycle_period_steps: int, cycle_count: int) -> bool:
    if len(phases) < int(cycle_period_steps) * int(cycle_count):
        return False
    expected = [index / float(cycle_period_steps) for index in range(int(cycle_period_steps))]
    for cycle_index in range(int(cycle_count)):
        start = cycle_index * int(cycle_period_steps)
        cycle_phases = phases[start : start + int(cycle_period_steps)]
        for observed, expected_value in zip(cycle_phases, expected):
            if not math.isclose(observed, expected_value, abs_tol=1.0e-12):
                return False
    return True


def _fieldnames(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _as_float(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite value: {value}")
    return number


def _as_int(value) -> int:
    return int(float(value))


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _finite_values(values) -> bool:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                continue
        if isinstance(value, (int, float)) and not math.isfinite(float(value)):
            return False
    return True
