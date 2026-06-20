import csv
import json
import math
import os
from pathlib import Path

import numpy as np


APPLICATION_TIMESERIES_FIELDS = [
    "case",
    "reaction_transfer_mode",
    "step_index",
    "driver_lbm_step",
    "requested_phase",
    "selected_phase",
    "report_pass",
    "finite_pass",
    "cap_pass",
    "applied_cell_count",
    "max_applied_velocity_norm",
    "mean_applied_velocity_norm",
    "after_solid_vel_norm_max",
    "wall_velocity_cap_lbm",
    "lbm_population_update_count",
    "apply_to_lbm_solid_vel",
    "apply_to_lbm_populations",
    "modify_bounceback_formula",
]


def collect_wall_velocity_application_reports(case_dir) -> list[dict]:
    path = _resolve_path(case_dir) / "wall_velocity_application_timeseries.json"
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError(f"invalid wall velocity application timeseries payload: {path}")
    return rows


def reports_to_timeseries_rows(reports: list[dict], case: str, reaction_transfer_mode: str) -> list[dict]:
    rows = []
    for index, report in enumerate(reports):
        summary = report["summary"]
        rows.append(
            {
                "case": case,
                "reaction_transfer_mode": reaction_transfer_mode,
                "step_index": index,
                "driver_lbm_step": int(summary["driver_lbm_step"]),
                "requested_phase": float(summary["requested_phase"]),
                "selected_phase": float(summary["selected_phase"]),
                "report_pass": bool(summary["report_pass"]),
                "finite_pass": bool(summary["finite_pass"]),
                "cap_pass": bool(summary["cap_pass"]),
                "applied_cell_count": int(summary["applied_cell_count"]),
                "max_applied_velocity_norm": float(summary["max_applied_velocity_norm"]),
                "mean_applied_velocity_norm": float(summary["mean_applied_velocity_norm"]),
                "after_solid_vel_norm_max": float(summary["after_solid_vel_norm_max"]),
                "wall_velocity_cap_lbm": float(summary["wall_velocity_cap_lbm"]),
                "lbm_population_update_count": int(summary["lbm_population_update_count"]),
                "apply_to_lbm_solid_vel": bool(summary["apply_to_lbm_solid_vel"]),
                "apply_to_lbm_populations": bool(summary["apply_to_lbm_populations"]),
                "modify_bounceback_formula": bool(summary["modify_bounceback_formula"]),
            }
        )
    return rows


def summarize_application_envelope(rows: list[dict]) -> dict:
    if not rows:
        return _empty_application_summary()
    applied_counts = [_as_int(row["applied_cell_count"]) for row in rows]
    max_applied = [_as_float(row["max_applied_velocity_norm"]) for row in rows]
    mean_applied = [_as_float(row["mean_applied_velocity_norm"]) for row in rows]
    cap_values = [_as_float(row["wall_velocity_cap_lbm"]) for row in rows]
    selected_phases = [_as_float(row["selected_phase"]) for row in rows]
    summary = {
        "application_report_count": len(rows),
        "timeseries_row_count": len(rows),
        "applied_cell_count_min": min(applied_counts),
        "applied_cell_count_max": max(applied_counts),
        "max_applied_velocity_norm": max(max_applied),
        "mean_applied_velocity_norm_max": max(mean_applied),
        "wall_velocity_cap_lbm": max(cap_values),
        "lbm_population_update_count_max": max(_as_int(row["lbm_population_update_count"]) for row in rows),
        "report_pass_count": sum(1 for row in rows if _as_bool(row["report_pass"])),
        "finite_pass": all(_as_bool(row["finite_pass"]) for row in rows),
        "cap_pass": all(_as_bool(row["cap_pass"]) for row in rows),
        "apply_to_lbm_solid_vel_all": all(_as_bool(row["apply_to_lbm_solid_vel"]) for row in rows),
        "apply_to_lbm_populations_any": any(_as_bool(row["apply_to_lbm_populations"]) for row in rows),
        "modify_bounceback_formula_any": any(_as_bool(row["modify_bounceback_formula"]) for row in rows),
        "phase_sequence": selected_phases,
        "repeatable_phase_sequence": _repeatable_phase_sequence(selected_phases),
    }
    summary["application_envelope_pass"] = bool(
        summary["application_report_count"] >= 20
        and summary["applied_cell_count_min"] > 0
        and summary["applied_cell_count_max"] >= summary["applied_cell_count_min"]
        and math.isfinite(summary["max_applied_velocity_norm"])
        and summary["max_applied_velocity_norm"] <= summary["wall_velocity_cap_lbm"] + 1.0e-12
        and math.isfinite(summary["mean_applied_velocity_norm_max"])
        and summary["lbm_population_update_count_max"] == 0
        and summary["finite_pass"]
        and summary["cap_pass"]
        and summary["apply_to_lbm_solid_vel_all"]
        and not summary["apply_to_lbm_populations_any"]
        and not summary["modify_bounceback_formula_any"]
    )
    return summary


def summarize_driver_stability_envelope(diagnostics_rows: list[dict]) -> dict:
    if not diagnostics_rows:
        return {"diagnostics_row_count": 0, "stable": False}
    post_rows = [row for row in diagnostics_rows if _as_int(row["step"]) > 0]
    if not post_rows:
        raise ValueError("driver diagnostics missing post-step rows")
    summary = {
        "diagnostics_row_count": len(diagnostics_rows),
        "completed_lbm_steps": max(_as_int(row["step"]) for row in diagnostics_rows),
        "total_mpm_substeps": max(_as_int(row["total_mpm_substeps"]) for row in diagnostics_rows),
        "rho_min_global": min(_as_float(row["rho_min"]) for row in diagnostics_rows),
        "rho_max_global": max(_as_float(row["rho_max"]) for row in diagnostics_rows),
        "lbm_max_v_global": max(_as_float(row["lbm_max_v"]) for row in diagnostics_rows),
        "mpm_min_J_global": min(_as_float(row["mpm_min_J"]) for row in diagnostics_rows),
        "mpm_max_speed_global": max(_as_float(row["mpm_max_speed"]) for row in diagnostics_rows),
        "projected_mass_min": min(_as_float(row["projected_mass"]) for row in post_rows),
        "projected_mass_max": max(_as_float(row["projected_mass"]) for row in post_rows),
        "active_cell_count": max(_as_int(row["active_cell_count"]) for row in diagnostics_rows),
        "cell_force_max_norm": max(_as_float(row["cell_force_max_norm"]) for row in diagnostics_rows),
        "hydro_force_max_norm": max(_as_float(row["hydro_force_max_norm"]) for row in diagnostics_rows),
        "bb_link_count_min": min(_as_int(row["bb_link_count"]) for row in post_rows),
        "bb_link_count_max": max(_as_int(row["bb_link_count"]) for row in post_rows),
        "bb_max_correction_max": max(_as_float(row["bb_max_correction"]) for row in diagnostics_rows),
        "active_reaction_particle_count_max": max(_as_int(row["active_reaction_particle_count"]) for row in post_rows),
        "max_grid_reaction_norm": max(_as_float(row["max_grid_reaction_norm"]) for row in diagnostics_rows),
        "has_nan": not _rows_are_finite(diagnostics_rows),
        "has_inf": not _rows_are_finite(diagnostics_rows),
    }
    summary["stable"] = bool(
        not summary["has_nan"]
        and not summary["has_inf"]
        and summary["completed_lbm_steps"] >= 20
        and summary["total_mpm_substeps"] >= 100
        and summary["rho_min_global"] > 0.95
        and summary["rho_max_global"] < 1.05
        and summary["lbm_max_v_global"] < 0.1
        and summary["mpm_min_J_global"] > 0.0
        and summary["projected_mass_min"] > 0.0
        and summary["projected_mass_max"] > 0.0
        and summary["active_cell_count"] > 0
        and summary["bb_link_count_max"] > 0
        and math.isfinite(summary["hydro_force_max_norm"])
        and math.isfinite(summary["bb_max_correction_max"])
        and math.isfinite(summary["max_grid_reaction_norm"])
    )
    return summary


def compare_static_experimental_envelopes(static_row: dict, experimental_row: dict) -> dict:
    row = {
        "comparison": f"static_vs_experimental_{experimental_row['reaction_transfer_mode']}",
        "static_case": static_row["case"],
        "experimental_case": experimental_row["case"],
        "reaction_transfer_mode": experimental_row["reaction_transfer_mode"],
        "both_stable": _as_bool(static_row["stable"]) and _as_bool(experimental_row["stable"]),
        "rho_min_delta": _as_float(experimental_row["rho_min_global"]) - _as_float(static_row["rho_min_global"]),
        "rho_max_delta": _as_float(experimental_row["rho_max_global"]) - _as_float(static_row["rho_max_global"]),
        "lbm_max_v_delta": _as_float(experimental_row["lbm_max_v_global"]) - _as_float(static_row["lbm_max_v_global"]),
        "mpm_min_J_delta": _as_float(experimental_row["mpm_min_J_global"]) - _as_float(static_row["mpm_min_J_global"]),
        "projected_mass_delta": _as_float(experimental_row["projected_mass_max"]) - _as_float(static_row["projected_mass_max"]),
        "active_cell_count_delta": _as_int(experimental_row["active_cell_count"]) - _as_int(static_row["active_cell_count"]),
        "bb_link_count_delta": _as_int(experimental_row["bb_link_count_max"]) - _as_int(static_row["bb_link_count_max"]),
        "experimental_applied_velocity_max": _as_float(experimental_row["max_applied_velocity_norm"]),
        "notes": "bounded Step 37 static-vs-experimental short-window envelope comparison",
    }
    row["comparison_pass"] = bool(
        row["both_stable"]
        and _finite_row(row)
        and abs(row["rho_min_delta"]) <= 0.05
        and abs(row["rho_max_delta"]) <= 0.05
        and abs(row["lbm_max_v_delta"]) <= 0.08
        and abs(row["mpm_min_J_delta"]) <= 0.05
        and abs(row["projected_mass_delta"]) <= 1.0e-3
        and abs(row["active_cell_count_delta"]) <= 500
        and abs(row["bb_link_count_delta"]) <= 500
        and row["experimental_applied_velocity_max"] > 0.0
    )
    return row


def compare_engineering_link_area_envelopes(engineering_row: dict, link_area_row: dict) -> dict:
    row = {
        "comparison": "experimental_engineering_vs_link_area",
        "engineering_case": engineering_row["case"],
        "link_area_case": link_area_row["case"],
        "both_stable": _as_bool(engineering_row["stable"]) and _as_bool(link_area_row["stable"]),
        "link_area_scale_final": _as_float(link_area_row["area_scale_final"]),
        "rho_min_delta": _as_float(link_area_row["rho_min_global"]) - _as_float(engineering_row["rho_min_global"]),
        "rho_max_delta": _as_float(link_area_row["rho_max_global"]) - _as_float(engineering_row["rho_max_global"]),
        "lbm_max_v_delta": _as_float(link_area_row["lbm_max_v_global"]) - _as_float(engineering_row["lbm_max_v_global"]),
        "mpm_min_J_delta": _as_float(link_area_row["mpm_min_J_global"]) - _as_float(engineering_row["mpm_min_J_global"]),
        "projected_mass_delta": _as_float(link_area_row["projected_mass_max"]) - _as_float(engineering_row["projected_mass_max"]),
        "notes": "bounded Step 37 experimental engineering-vs-link-area short-window envelope comparison",
    }
    row["comparison_pass"] = bool(
        row["both_stable"]
        and _finite_row(row)
        and 0.25 <= row["link_area_scale_final"] <= 2.0
        and abs(row["projected_mass_delta"]) <= 1.0e-3
        and abs(row["rho_min_delta"]) <= 0.05
        and abs(row["rho_max_delta"]) <= 0.05
        and abs(row["lbm_max_v_delta"]) <= 0.08
        and abs(row["mpm_min_J_delta"]) <= 0.05
    )
    return row


def write_envelope_rows(rows: list[dict], csv_path, json_path, summary=None) -> None:
    fields = _fieldnames(rows)
    _write_csv(csv_path, rows, fields)
    payload = {"summary": _summary(rows) if summary is None else summary, "rows": rows}
    _write_json(json_path, payload)


def write_timeseries(rows: list[dict], csv_path, json_path, summary=None) -> None:
    _write_csv(csv_path, rows, APPLICATION_TIMESERIES_FIELDS)
    payload = {"summary": summarize_application_envelope(rows) if summary is None else summary, "rows": rows}
    _write_json(json_path, payload)


def _empty_application_summary() -> dict:
    return {
        "application_report_count": 0,
        "timeseries_row_count": 0,
        "applied_cell_count_min": 0,
        "applied_cell_count_max": 0,
        "max_applied_velocity_norm": 0.0,
        "mean_applied_velocity_norm_max": 0.0,
        "wall_velocity_cap_lbm": 0.0,
        "lbm_population_update_count_max": 0,
        "report_pass_count": 0,
        "finite_pass": False,
        "cap_pass": False,
        "apply_to_lbm_solid_vel_all": False,
        "apply_to_lbm_populations_any": False,
        "modify_bounceback_formula_any": False,
        "phase_sequence": [],
        "repeatable_phase_sequence": False,
        "application_envelope_pass": False,
    }


def _repeatable_phase_sequence(phases) -> bool:
    if not phases:
        return False
    if not all(math.isfinite(float(value)) for value in phases):
        return False
    return all(float(value) >= 0.0 for value in phases)


def _rows_are_finite(rows: list[dict]) -> bool:
    for row in rows:
        for value in row.values():
            if isinstance(value, bool):
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(number):
                return False
    return True


def _finite_row(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool):
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(number):
            return False
    return True


def _summary(rows):
    return {
        "row_count": len(rows),
        "pass_count": sum(1 for row in rows if _as_bool(row.get("comparison_pass", row.get("stable", False)))),
    }


def _fieldnames(rows: list[dict]) -> list[str]:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _write_csv(path, rows: list[dict], fieldnames: list[str]) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: _csv_value(row.get(field, "")) for field in fieldnames})


def _write_json(path, payload) -> None:
    resolved = _resolve_path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _csv_value(value):
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True)
    return value


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _as_int(value) -> int:
    return int(float(value))


def _as_float(value) -> float:
    return float(value)


def _resolve_path(path) -> Path:
    path_obj = Path(os.fspath(path))
    if path_obj.is_absolute():
        return path_obj
    return _repo_root() / path_obj


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]
