from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .fluent_duct_flap_io import display_path, parse_float, read_csv_rows, resolve_repo_path, write_json


SOLVER_SERIES_CANDIDATES = [
    "official_point_like_total_displacement_m",
    "flap_tip_total_displacement_m",
]
OFFICIAL_SERIES_CANDIDATES = [
    "flap_tip_total_displacement_m",
    "official_point_like_total_displacement_m",
    "total_displacement_m",
    "displacement_m",
]


def load_optional_official_monitor(path: Path) -> dict[str, Any]:
    resolved = resolve_repo_path(path)
    if not resolved.is_file():
        return {
            "status": "official_monitor_missing",
            "path": display_path(resolved),
            "official_monitor_loaded": False,
            "rows": [],
        }
    rows = read_csv_rows(resolved)
    return {
        "status": "official_monitor_loaded",
        "path": display_path(resolved),
        "official_monitor_loaded": True,
        "rows": rows,
        "row_count": len(rows),
    }


def build_official_comparison_report(
    official_monitor_path: Path,
    solver_monitor_csv: Path,
    output_path: Path,
) -> dict[str, Any]:
    official = load_optional_official_monitor(official_monitor_path)
    if not official["official_monitor_loaded"]:
        report = {
            "step": 156,
            "status": "official_monitor_missing",
            "official_monitor_path": display_path(resolve_repo_path(official_monitor_path)),
            "official_monitor_loaded": False,
            "official_error_metrics_available": False,
            "comparison_scope": "solver_postprocess_only",
            "next_action": "provide_private_official_monitor_or_run_step150_intake",
            "validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
        }
        write_json(output_path, report)
        return report

    solver_rows = read_csv_rows(solver_monitor_csv)
    official_rows = official["rows"]
    solver_time, solver_values, solver_series = _extract_series(
        solver_rows,
        SOLVER_SERIES_CANDIDATES,
    )
    official_time, official_values, official_series = _extract_series(
        official_rows,
        OFFICIAL_SERIES_CANDIDATES,
    )
    if solver_time.size == 0 or official_time.size == 0:
        report = {
            "step": 156,
            "status": "official_monitor_schema_unusable",
            "official_monitor_path": display_path(resolve_repo_path(official_monitor_path)),
            "official_monitor_loaded": True,
            "official_error_metrics_available": False,
            "solver_series_used": solver_series,
            "official_series_used": official_series,
            "validation_claim_allowed": False,
            "figure_29_3_parity_claim_allowed": False,
        }
        write_json(output_path, report)
        return report

    order = np.argsort(official_time)
    official_time = official_time[order]
    official_values = official_values[order]
    valid = (solver_time >= official_time[0]) & (solver_time <= official_time[-1])
    aligned_solver_time = solver_time[valid]
    aligned_solver_values = solver_values[valid]
    aligned_official = np.interp(aligned_solver_time, official_time, official_values)
    diff = aligned_solver_values - aligned_official
    report = {
        "step": 156,
        "status": "official_monitor_comparison_metrics_written",
        "official_monitor_path": display_path(resolve_repo_path(official_monitor_path)),
        "official_monitor_loaded": True,
        "official_error_metrics_available": True,
        "aligned_sample_count": int(diff.size),
        "rmse_m": float(np.sqrt(np.mean(diff * diff))) if diff.size else 0.0,
        "max_abs_error_m": float(np.max(np.abs(diff))) if diff.size else 0.0,
        "solver_series_used": solver_series,
        "official_series_used": official_series,
        "validation_claim_allowed": False,
        "figure_29_3_parity_claim_allowed": False,
    }
    write_json(output_path, report)
    return report


def _extract_series(
    rows: list[dict[str, str]],
    candidates: list[str],
) -> tuple[np.ndarray, np.ndarray, str | None]:
    if not rows:
        return np.array([], dtype=float), np.array([], dtype=float), None
    series = next((name for name in candidates if name in rows[0]), None)
    if series is None or "time_s" not in rows[0]:
        return np.array([], dtype=float), np.array([], dtype=float), series
    times = np.array([parse_float(row.get("time_s")) for row in rows], dtype=float)
    values = np.array([parse_float(row.get(series)) for row in rows], dtype=float)
    finite = np.isfinite(times) & np.isfinite(values)
    return times[finite], values[finite], series
