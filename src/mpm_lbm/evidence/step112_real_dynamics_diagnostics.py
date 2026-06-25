from __future__ import annotations

import math
from pathlib import Path

from src.mpm_lbm.evidence.step112_common import (
    max_numeric,
    numeric_values_finite,
    read_csv_rows,
    reset_output_dir,
    safe_ratio,
    summary_rows,
    write_csv_rows,
    write_json,
)


COMPONENT_FIELDS = [
    "diagnostics_source",
    "nearest_monitor_peak_total_m",
    "nearest_monitor_peak_x_m",
    "nearest_monitor_peak_y_m",
    "nearest_monitor_peak_z_m",
    "z_to_total_peak_ratio",
    "y_to_total_peak_ratio",
    "final_total_m",
    "final_x_m",
    "final_y_m",
    "final_z_m",
    "time_of_peak_total_s",
    "time_of_peak_x_s",
    "time_of_peak_y_s",
    "time_of_peak_z_s",
    "monotonic_increasing_fraction",
    "all_metrics_finite",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
]

FORCE_FIELDS = [
    "diagnostics_source",
    "force_to_displacement_lag_s",
    "hydro_force_max_norm_max",
    "max_grid_reaction_norm_max",
    "time_of_hydro_force_peak_s",
    "time_of_peak_total_s",
    "all_metrics_finite",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
]

STRUCTURAL_FIELDS = [
    "diagnostics_source",
    "mpm_min_J_min",
    "mpm_max_speed_max",
    "solid_mean_velocity_norm_max",
    "all_metrics_finite",
    "validation_claim_allowed",
    "direct_quantitative_equivalence_allowed",
]


def build_step112_real_dynamics_diagnostics(
    root: Path,
    solver_dir: str = "outputs/step111_real_solver_candidate",
) -> tuple[dict, dict, dict]:
    root = Path(root)
    out_dir = root / "outputs" / "step112_real_dynamics_diagnostics"
    reset_output_dir(out_dir, root / "outputs")
    monitor_rows = coerce_monitor_rows(read_csv_rows(root / solver_dir / "monitor_timeseries_nearest_public_monitor_point.csv"))
    diagnostics_rows = coerce_diagnostics_rows(read_csv_rows(root / solver_dir / "diagnostics_timeseries.csv"))

    component_row = component_diagnostics_row(monitor_rows)
    force_row = force_phase_row(monitor_rows, diagnostics_rows)
    structural_row = structural_state_row(diagnostics_rows)
    component_summary = {
        "real_dynamics_diagnostics_pass": bool(component_row["all_metrics_finite"]),
        "row_count": 1,
        "validation_claim_allowed": False,
        "direct_quantitative_equivalence_allowed": False,
    }
    force_summary = {
        "force_displacement_phase_pass": bool(force_row["all_metrics_finite"]),
        "row_count": 1,
        "validation_claim_allowed": False,
        "direct_quantitative_equivalence_allowed": False,
    }
    structural_summary = {
        "structural_state_pass": bool(structural_row["all_metrics_finite"]),
        "row_count": 1,
        "validation_claim_allowed": False,
        "direct_quantitative_equivalence_allowed": False,
    }
    write_json(out_dir / "component_monitor_report.json", {"summary": component_summary, "rows": [component_row]})
    write_json(out_dir / "force_displacement_phase_report.json", {"summary": force_summary, "rows": [force_row]})
    write_json(out_dir / "structural_state_report.json", {"summary": structural_summary, "rows": [structural_row]})
    write_csv_rows(out_dir / "component_monitor_report.csv", [component_row], COMPONENT_FIELDS)
    write_csv_rows(out_dir / "force_displacement_phase_report.csv", [force_row], FORCE_FIELDS)
    write_csv_rows(out_dir / "structural_state_report.csv", [structural_row], STRUCTURAL_FIELDS)
    write_csv_rows(out_dir / "component_monitor_summary.csv", summary_rows(component_summary), ["metric", "value"])
    return component_summary, force_summary, structural_summary


def component_diagnostics_row(rows: list[dict]) -> dict:
    peak_total_row = max(rows, key=lambda row: abs(float(row["total_displacement_m"])))
    peak_x_row = max(rows, key=lambda row: abs(float(row["x_displacement_m"])))
    peak_y_row = max(rows, key=lambda row: abs(float(row["y_displacement_m"])))
    peak_z_row = max(rows, key=lambda row: abs(float(row["z_displacement_m"])))
    final = rows[-1]
    total_peak = abs(float(peak_total_row["total_displacement_m"]))
    row = {
        "diagnostics_source": "real_solver_particles",
        "nearest_monitor_peak_total_m": total_peak,
        "nearest_monitor_peak_x_m": abs(float(peak_x_row["x_displacement_m"])),
        "nearest_monitor_peak_y_m": abs(float(peak_y_row["y_displacement_m"])),
        "nearest_monitor_peak_z_m": abs(float(peak_z_row["z_displacement_m"])),
        "z_to_total_peak_ratio": safe_ratio(abs(float(peak_total_row["z_displacement_m"])), total_peak),
        "y_to_total_peak_ratio": safe_ratio(abs(float(peak_total_row["y_displacement_m"])), total_peak),
        "final_total_m": abs(float(final["total_displacement_m"])),
        "final_x_m": float(final["x_displacement_m"]),
        "final_y_m": float(final["y_displacement_m"]),
        "final_z_m": float(final["z_displacement_m"]),
        "time_of_peak_total_s": float(peak_total_row["time_s"]),
        "time_of_peak_x_s": float(peak_x_row["time_s"]),
        "time_of_peak_y_s": float(peak_y_row["time_s"]),
        "time_of_peak_z_s": float(peak_z_row["time_s"]),
        "monotonic_increasing_fraction": monotonic_fraction([float(row["total_displacement_m"]) for row in rows]),
        "validation_claim_allowed": False,
        "direct_quantitative_equivalence_allowed": False,
    }
    row["all_metrics_finite"] = numeric_values_finite(row)
    return row


def force_phase_row(monitor_rows: list[dict], diagnostics_rows: list[dict]) -> dict:
    displacement_peak = max(monitor_rows, key=lambda row: abs(float(row["total_displacement_m"])))
    force_peak = max(diagnostics_rows, key=lambda row: abs(float(row["hydro_force_max_norm"])))
    row = {
        "diagnostics_source": "real_solver_particles",
        "force_to_displacement_lag_s": float(displacement_peak["time_s"]) - step_time(force_peak),
        "hydro_force_max_norm_max": max_numeric(diagnostics_rows, "hydro_force_max_norm"),
        "max_grid_reaction_norm_max": max_numeric(diagnostics_rows, "max_grid_reaction_norm"),
        "time_of_hydro_force_peak_s": step_time(force_peak),
        "time_of_peak_total_s": float(displacement_peak["time_s"]),
        "validation_claim_allowed": False,
        "direct_quantitative_equivalence_allowed": False,
    }
    row["all_metrics_finite"] = numeric_values_finite(row)
    return row


def structural_state_row(diagnostics_rows: list[dict]) -> dict:
    row = {
        "diagnostics_source": "real_solver_particles",
        "mpm_min_J_min": min(float(item["mpm_min_J"]) for item in diagnostics_rows),
        "mpm_max_speed_max": max_numeric(diagnostics_rows, "mpm_max_speed"),
        "solid_mean_velocity_norm_max": max_numeric(diagnostics_rows, "solid_mean_vx_norm"),
        "validation_claim_allowed": False,
        "direct_quantitative_equivalence_allowed": False,
    }
    row["all_metrics_finite"] = numeric_values_finite(row)
    return row


def monotonic_fraction(values: list[float]) -> float:
    if len(values) < 2:
        return 1.0
    increasing = sum(1 for left, right in zip(values, values[1:]) if right >= left)
    return increasing / float(len(values) - 1)


def step_time(row: dict) -> float:
    return float(row["step"]) * 0.0005


def coerce_monitor_rows(rows: list[dict]) -> list[dict]:
    return [{key: (int(value) if key == "step" else float(value)) for key, value in row.items()} for row in rows]


def coerce_diagnostics_rows(rows: list[dict]) -> list[dict]:
    numeric = []
    for row in rows:
        converted = {}
        for key, value in row.items():
            if key == "coupling_mode":
                converted[key] = value
            elif key in {"step", "total_mpm_substeps", "active_cell_count", "bb_link_count", "active_reaction_particle_count"}:
                converted[key] = int(float(value))
            else:
                converted[key] = float(value)
        numeric.append(converted)
    return numeric
