import csv
import json
import math
import os
from pathlib import Path

from .jet_cycle_parameter_sensitivity import (
    force_impulse_parameter_response_row,
    parse_wall_velocity_scale_from_case,
    summarize_parameter_driver_rows,
    summarize_response_rows,
)
from .jet_cycle_proxy_diagnostics import (
    compute_cavity_volume_cycle_proxy,
    compute_cycle_phase_alignment,
    compute_funnel_aperture_cycle_proxy,
    estimate_cavity_rest_volume,
    load_schedule_config,
    load_step32_schedule,
    wall_velocity_cycle_quality_row,
)


SELECTED_SCALE = 0.05
SELECTED_CAP = 0.01
N_GRID = 64
N_LBM_STEPS = 40
MPM_SUBSTEPS_PER_LBM_STEP = 5
SCALE_TOL = 1.0e-12


def summarize_selected_parameter_driver_rows(rows: list[dict]) -> dict:
    summary = summarize_parameter_driver_rows(rows)
    experimental = [row for row in rows if row["mode_class"] == "experimental"]
    summary["selected_scale"] = SELECTED_SCALE
    summary["n_grid"] = N_GRID
    summary["scale_values"] = sorted({round(_as_float(row["wall_velocity_scale"]), 12) for row in experimental})
    summary["scale_count"] = len(summary["scale_values"])
    summary["driver_pass"] = bool(
        summary["row_count"] == 4
        and summary["static_row_count"] == 2
        and summary["experimental_row_count"] == 2
        and summary["engineering_row_count"] == 2
        and summary["link_area_row_count"] == 2
        and summary["stable_count"] == 4
        and summary["quality_pass_count"] == 4
        and summary["scale_values"] == [SELECTED_SCALE]
        and summary["min_completed_lbm_steps"] >= N_LBM_STEPS
        and summary["min_total_mpm_substeps"] >= N_LBM_STEPS * MPM_SUBSTEPS_PER_LBM_STEP
        and summary["min_rho_min_global"] > 0.95
        and summary["max_rho_max_global"] < 1.05
        and summary["max_lbm_max_v_global"] < 0.1
        and summary["min_mpm_min_J_global"] > 0.0
        and summary["min_projected_mass_min"] > 0.0
        and summary["min_active_cell_count"] > 0
        and summary["min_bb_link_count_max"] > 0
        and summary["max_lbm_population_update_count"] == 0
        and summary["max_applied_velocity_norm"] <= SELECTED_CAP + SCALE_TOL
        and finite_values(summary)
    )
    summary["scope_note"] = "Step 41 controlled selected-parameter 64^3 feasibility; tethered proxy diagnostics only."
    return summary


def assert_selected_parameter_driver_summary(summary: dict) -> None:
    if not _as_bool(summary["driver_pass"]):
        raise RuntimeError(f"Step 41 selected-parameter driver summary failed: {summary}")


def summarize_selected_parameter_feasibility(rows: list[dict]) -> dict:
    driver = summarize_selected_parameter_driver_rows(rows)
    summary = {
        "driver_row_count": int(driver["row_count"]),
        "stable_count": int(driver["stable_count"]),
        "quality_pass_count": int(driver["quality_pass_count"]),
        "selected_scale": SELECTED_SCALE,
        "n_grid": N_GRID,
        "min_completed_lbm_steps": int(driver["min_completed_lbm_steps"]),
        "min_total_mpm_substeps": int(driver["min_total_mpm_substeps"]),
        "min_rho_min_global": float(driver["min_rho_min_global"]),
        "max_rho_max_global": float(driver["max_rho_max_global"]),
        "max_lbm_max_v_global": float(driver["max_lbm_max_v_global"]),
        "min_mpm_min_J_global": float(driver["min_mpm_min_J_global"]),
        "min_projected_mass_min": float(driver["min_projected_mass_min"]),
        "min_active_cell_count": int(driver["min_active_cell_count"]),
        "max_applied_velocity_norm": float(driver["max_applied_velocity_norm"]),
        "one_cycle_pass": bool(
            int(driver["min_completed_lbm_steps"]) >= N_LBM_STEPS
            and int(driver["min_total_mpm_substeps"]) >= N_LBM_STEPS * MPM_SUBSTEPS_PER_LBM_STEP
        ),
    }
    summary["feasibility_pass"] = bool(
        int(summary["driver_row_count"]) == 4
        and int(summary["stable_count"]) == 4
        and int(summary["quality_pass_count"]) == 4
        and summary["one_cycle_pass"]
        and float(summary["min_rho_min_global"]) > 0.95
        and float(summary["max_rho_max_global"]) < 1.05
        and float(summary["max_lbm_max_v_global"]) < 0.1
        and float(summary["min_mpm_min_J_global"]) > 0.0
        and float(summary["min_projected_mass_min"]) > 0.0
        and int(summary["min_active_cell_count"]) > 0
        and float(summary["max_applied_velocity_norm"]) <= SELECTED_CAP + SCALE_TOL
        and finite_values(summary)
    )
    return summary


def compare_static_experimental_64_rows(static_rows: list[dict], experimental_rows: list[dict]) -> list[dict]:
    by_transfer = {row["reaction_transfer_mode"]: row for row in static_rows}
    rows = []
    for experimental in sorted(experimental_rows, key=lambda row: row["reaction_transfer_mode"]):
        static = by_transfer[experimental["reaction_transfer_mode"]]
        row = {
            "comparison": f"static_vs_experimental_64_{experimental['reaction_transfer_mode']}",
            "static_case": static["case"],
            "experimental_case": experimental["case"],
            "reaction_transfer_mode": experimental["reaction_transfer_mode"],
            "wall_velocity_scale": _as_float(experimental["wall_velocity_scale"]),
            "both_stable": _as_bool(static["stable"]) and _as_bool(experimental["stable"]),
            "rho_min_delta": _as_float(experimental["rho_min_global"]) - _as_float(static["rho_min_global"]),
            "rho_max_delta": _as_float(experimental["rho_max_global"]) - _as_float(static["rho_max_global"]),
            "lbm_max_v_delta": _as_float(experimental["lbm_max_v_global"]) - _as_float(static["lbm_max_v_global"]),
            "mpm_min_J_delta": _as_float(experimental["mpm_min_J_global"]) - _as_float(static["mpm_min_J_global"]),
            "projected_mass_delta": _as_float(experimental["projected_mass_max"]) - _as_float(static["projected_mass_max"]),
            "active_cell_count_delta": _as_int(experimental["active_cell_count"]) - _as_int(static["active_cell_count"]),
            "bb_link_count_delta": _as_int(experimental["bb_link_count_max"]) - _as_int(static["bb_link_count_max"]),
            "experimental_applied_velocity_max": _as_float(experimental["max_applied_velocity_norm"]),
            "notes": "bounded static vs experimental 64^3 proxy comparison",
        }
        row["comparison_pass"] = bool(
            row["both_stable"]
            and finite_values(row)
            and abs(row["rho_min_delta"]) <= 0.05
            and abs(row["rho_max_delta"]) <= 0.05
            and abs(row["lbm_max_v_delta"]) <= 0.08
            and abs(row["mpm_min_J_delta"]) <= 0.05
            and abs(row["projected_mass_delta"]) <= 2.0e-3
            and abs(row["active_cell_count_delta"]) <= 800
            and abs(row["bb_link_count_delta"]) <= 800
            and row["experimental_applied_velocity_max"] > 0.0
        )
        rows.append(row)
    return rows


def compare_engineering_link_area_64_rows(experimental_rows: list[dict]) -> list[dict]:
    by_transfer = {row["reaction_transfer_mode"]: row for row in experimental_rows}
    engineering = by_transfer["engineering"]
    link_area = by_transfer["link_area_experimental"]
    row = {
        "comparison": "engineering_vs_link_area_64_scale_0050",
        "engineering_case": engineering["case"],
        "link_area_case": link_area["case"],
        "wall_velocity_scale": _as_float(link_area["wall_velocity_scale"]),
        "both_stable": _as_bool(engineering["stable"]) and _as_bool(link_area["stable"]),
        "link_area_scale_final": _as_float(link_area["area_scale_final"]),
        "rho_min_delta": _as_float(link_area["rho_min_global"]) - _as_float(engineering["rho_min_global"]),
        "rho_max_delta": _as_float(link_area["rho_max_global"]) - _as_float(engineering["rho_max_global"]),
        "lbm_max_v_delta": _as_float(link_area["lbm_max_v_global"]) - _as_float(engineering["lbm_max_v_global"]),
        "mpm_min_J_delta": _as_float(link_area["mpm_min_J_global"]) - _as_float(engineering["mpm_min_J_global"]),
        "projected_mass_delta": _as_float(link_area["projected_mass_max"]) - _as_float(engineering["projected_mass_max"]),
        "max_applied_velocity_norm_delta": _as_float(link_area["max_applied_velocity_norm"]) - _as_float(engineering["max_applied_velocity_norm"]),
        "notes": "bounded engineering vs link-area 64^3 proxy comparison",
    }
    row["comparison_pass"] = bool(
        row["both_stable"]
        and finite_values(row)
        and 0.25 <= row["link_area_scale_final"] <= 2.0
        and abs(row["projected_mass_delta"]) <= 2.0e-3
        and abs(row["rho_min_delta"]) <= 0.05
        and abs(row["rho_max_delta"]) <= 0.05
        and abs(row["lbm_max_v_delta"]) <= 0.08
        and abs(row["mpm_min_J_delta"]) <= 0.05
    )
    return [row]


def summarize_wall_velocity_64_quality(application_rows_by_case: dict[str, list[dict]], driver_rows: list[dict]) -> tuple[list[dict], dict]:
    rows = []
    for driver_row in sorted([row for row in driver_rows if row["mode_class"] == "experimental"], key=lambda row: row["reaction_transfer_mode"]):
        row = wall_velocity_cycle_quality_row(driver_row, application_rows_by_case.get(driver_row["case"], []), N_LBM_STEPS)
        row["selected_scale"] = _as_float(driver_row["wall_velocity_scale"])
        row["cap_value"] = _as_float(driver_row["wall_velocity_cap_lbm"])
        rows.append(row)
    summary = {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if _as_bool(row["quality_pass"])),
        "selected_scale": SELECTED_SCALE,
        "cap_value": SELECTED_CAP,
        "min_timeseries_row_count": min((_as_int(row["timeseries_row_count"]) for row in rows), default=0),
        "min_applied_cell_count": min((_as_int(row["applied_cell_count_min"]) for row in rows), default=0),
        "max_applied_velocity_norm": max((_as_float(row["max_applied_velocity_norm"]) for row in rows), default=0.0),
        "max_lbm_population_update_count": max((_as_int(row["lbm_population_update_count_max"]) for row in rows), default=0),
        "quality_pass": bool(len(rows) == 2 and all(_as_bool(row["quality_pass"]) for row in rows)),
    }
    return rows, summary


def summarize_cycle_proxy_64(schedule_config_path, schedule_rows_path, driver_rows: list[dict], application_rows: list[dict], geometry_config_path) -> tuple[list[dict], dict]:
    schedule_config = load_schedule_config(schedule_config_path)
    schedule_rows = load_step32_schedule(schedule_rows_path)
    cycle_period = int(schedule_config["cycle_period_steps"])
    cavity_rest_volume, rest_volume_source = estimate_cavity_rest_volume(geometry_config_path)
    summary = {
        "metric_scope": "Step 41 controlled selected-parameter 64^3 cycle proxy diagnostics only",
        "cycle_period_steps": cycle_period,
        "cycle_count": int(N_LBM_STEPS / cycle_period),
        "schedule_row_count": len(schedule_rows),
        "driver_row_count": len(driver_rows),
        "experimental_row_count": sum(1 for row in driver_rows if row.get("mode_class") == "experimental"),
        "cavity_rest_volume_source": rest_volume_source,
        "net_cycle_tolerance": max(1.0e-8, 1.0e-6 * float(cavity_rest_volume)),
    }
    summary.update(compute_cavity_volume_cycle_proxy(schedule_rows, cavity_rest_volume))
    summary.update(compute_funnel_aperture_cycle_proxy(schedule_rows))
    summary.update(compute_cycle_phase_alignment(application_rows, schedule_rows, cycle_period))
    summary["cycle_proxy_64_pass"] = bool(
        summary["cycle_period_steps"] == N_LBM_STEPS
        and summary["cycle_count"] == 1
        and summary["phase_alignment_pass"]
        and summary["cavity_volume_cycle_pass"]
        and summary["funnel_aperture_cycle_pass"]
        and summary["expelled_volume_proxy"] > 0.0
        and summary["refill_volume_proxy"] > 0.0
        and abs(summary["net_cycle_volume_proxy"]) <= summary["net_cycle_tolerance"]
        and finite_values(summary)
    )
    summary["notes"] = "schedule-derived 64^3 proxy diagnostics; no internal-fluid volume solve and no propulsion claim"
    return [summary], summary


def force_impulse_64_row(driver_row: dict, diagnostics_rows: list[dict]) -> dict:
    row = force_impulse_parameter_response_row(driver_row, diagnostics_rows)
    row["notes"] = "Step 41 force and bounce-back proxy only; no real impulse validation claim"
    return row


def summarize_force_impulse_64_rows(rows: list[dict]) -> dict:
    summary = summarize_response_rows(rows, "response_finite_pass")
    summary["force_impulse_64_pass"] = bool(int(summary["row_count"]) == 4 and int(summary["response_finite_pass_count"]) == 4)
    return summary


def write_selected_parameter_outputs(rows: list[dict], csv_path, json_path, summary: dict) -> None:
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


def read_json(path):
    with _resolve_path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def finite_values(row, excluded=()) -> bool:
    values = row.values() if isinstance(row, dict) else row
    if isinstance(row, dict):
        iterable = ((key, value) for key, value in row.items() if key not in excluded)
    else:
        iterable = ((None, value) for value in values)
    for _, value in iterable:
        if isinstance(value, bool) or value == "":
            continue
        if isinstance(value, (list, tuple)):
            if not finite_values(value):
                return False
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def scale_from_config_path(config_path) -> float:
    return parse_wall_velocity_scale_from_case(config_path)


def _fieldnames(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return Path(__file__).resolve().parents[1] / path_obj


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _as_int(value) -> int:
    return int(float(value))


def _as_float(value) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite value: {value}")
    return number
