from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


STEP = 149
DEFAULT_OFFICIAL_MONITOR = Path("benchmarks") / "private" / "fluent_fsi_2way" / "outputs" / "official_monitor.csv"
DEFAULT_SOLVER_MONITOR = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_monitor.csv"
DEFAULT_SOLVER_FORCE_MONITOR = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_force_monitor.csv"
DEFAULT_SOLVER_SUMMARY = Path("outputs") / "step148_our_solver_fluent_official_case" / "solver_reproduction_summary.json"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step149_fluent_official_vs_our_solver_error_localization"
BUG_CATEGORIES = [
    "geometry_mapping_error",
    "unit_mapping_error",
    "fluid_boundary_error",
    "structural_model_error",
    "coupling_force_transfer_error",
    "solid_to_fluid_motion_error",
    "time_integration_or_subcycling_error",
    "monitor_extraction_error",
    "numerical_stability_error",
]
DISPLACEMENT_ALIASES = [
    "flap_tip_total_displacement_m",
    "total_displacement_m",
    "displacement_m",
    "fluent_public_digitized_total_displacement_m",
    "solver_total_displacement_m",
]
FORCE_ALIASES = [
    "fluid_force_magnitude_n",
    "force_magnitude_n",
    "fluid_force_y_n",
    "force_y_n",
]
ALIGNED_FIELDS = [
    "time_s",
    "official_flap_tip_total_displacement_m",
    "solver_flap_tip_total_displacement_m",
    "displacement_error_m",
    "official_fluid_force_magnitude_n",
    "solver_fluid_force_magnitude_n",
    "force_error_n",
]


def run_step149_error_localization(
    official_monitor: Path | str = DEFAULT_OFFICIAL_MONITOR,
    solver_monitor: Path | str = DEFAULT_SOLVER_MONITOR,
    solver_force_monitor: Path | str = DEFAULT_SOLVER_FORCE_MONITOR,
    solver_summary: Path | str | None = DEFAULT_SOLVER_SUMMARY,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    del force
    official_monitor = Path(official_monitor)
    solver_monitor = Path(solver_monitor)
    solver_force_monitor = Path(solver_force_monitor)
    solver_summary_path = None if solver_summary is None else Path(solver_summary)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not official_monitor.is_file():
        return _write_missing_summary(
            output_dir,
            status="missing_official_monitor",
            missing_reason="official_reference_missing",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
        )
    if not solver_monitor.is_file():
        return _write_missing_summary(
            output_dir,
            status="missing_solver_monitor",
            missing_reason="solver_reference_missing",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
        )

    official_rows = _read_csv(official_monitor)
    solver_rows = _read_csv(solver_monitor)
    if not official_rows:
        return _write_missing_summary(
            output_dir,
            status="missing_official_monitor",
            missing_reason="official_reference_empty",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
        )
    if not solver_rows:
        return _write_missing_summary(
            output_dir,
            status="missing_solver_monitor",
            missing_reason="solver_reference_empty",
            official_monitor=official_monitor,
            solver_monitor=solver_monitor,
            solver_force_monitor=solver_force_monitor,
            solver_summary_path=solver_summary_path,
        )

    official_disp = _find_column(official_rows[0], DISPLACEMENT_ALIASES)
    solver_disp = _find_column(solver_rows[0], DISPLACEMENT_ALIASES)
    official_force = _find_column(official_rows[0], FORCE_ALIASES, required=False)
    solver_force = _find_column(solver_rows[0], FORCE_ALIASES, required=False)
    official = _series(official_rows, official_disp, official_force)
    solver = _series(solver_rows, solver_disp, solver_force)
    aligned = _align_series(official, solver)

    _write_csv(output_dir / "aligned_monitor_comparison.csv", aligned, ALIGNED_FIELDS)
    displacement_metrics = _displacement_metrics(official, solver, aligned, official_monitor, solver_monitor)
    force_metrics = _force_metrics(official, solver, aligned, official_force, solver_force)
    phase_metrics = _phase_lag_metrics(aligned, force_metrics)
    hypotheses = _bug_hypotheses(displacement_metrics, force_metrics, phase_metrics)
    summary = _comparison_summary(
        official_monitor=official_monitor,
        solver_monitor=solver_monitor,
        solver_force_monitor=solver_force_monitor,
        solver_summary_path=solver_summary_path,
        aligned=aligned,
        displacement_metrics=displacement_metrics,
        force_metrics=force_metrics,
        phase_metrics=phase_metrics,
        hypotheses=hypotheses,
    )

    _write_json(output_dir / "displacement_error_metrics.json", displacement_metrics)
    _write_json(output_dir / "force_error_metrics.json", force_metrics)
    _write_json(output_dir / "phase_lag_metrics.json", phase_metrics)
    _write_json(output_dir / "solver_bug_hypotheses.json", hypotheses)
    _write_json(output_dir / "error_localization_summary.json", summary)
    _write_report(output_dir, summary, hypotheses)
    return summary


def _write_missing_summary(
    output_dir: Path,
    status: str,
    missing_reason: str,
    official_monitor: Path,
    solver_monitor: Path,
    solver_force_monitor: Path,
    solver_summary_path: Path | None,
) -> dict[str, Any]:
    solver_loaded = solver_monitor.is_file()
    official_loaded = official_monitor.is_file()
    summary = {
        "step": STEP,
        "status": status,
        "missing_reason": missing_reason,
        "official_monitor": _display_path(official_monitor),
        "solver_monitor": _display_path(solver_monitor),
        "solver_force_monitor": _display_path(solver_force_monitor),
        "solver_summary": None if solver_summary_path is None else _display_path(solver_summary_path),
        "official_reference_loaded": official_loaded,
        "solver_monitor_loaded": solver_loaded,
        "error_metrics_present": False,
        "solver_bug_hypotheses_present": False,
        "next_code_fix_step_identified": False,
        "fabricated_metrics_used": False,
        "validation_claim_allowed": False,
    }
    _write_csv(output_dir / "aligned_monitor_comparison.csv", [], ALIGNED_FIELDS)
    _write_json(output_dir / "displacement_error_metrics.json", {"status": status, "missing_reason": missing_reason})
    _write_json(output_dir / "force_error_metrics.json", {"status": status, "missing_reason": missing_reason})
    _write_json(output_dir / "phase_lag_metrics.json", {"status": status, "missing_reason": missing_reason})
    _write_json(
        output_dir / "solver_bug_hypotheses.json",
        {
            "status": status,
            "hypotheses": [],
            "next_fix_step_recommended": None,
            "fabricated_metrics_used": False,
        },
    )
    _write_json(output_dir / "error_localization_summary.json", summary)
    _write_report(output_dir, summary, {"hypotheses": []})
    return summary


def _series(rows: list[dict[str, str]], displacement_column: str, force_column: str | None) -> list[dict[str, float]]:
    series = []
    for row in rows:
        item = {
            "time_s": float(row["time_s"]),
            "displacement_m": float(row[displacement_column]),
            "force_n": float(row[force_column]) if force_column is not None and row.get(force_column, "") != "" else math.nan,
        }
        if not math.isfinite(item["time_s"]) or not math.isfinite(item["displacement_m"]):
            raise ValueError("monitor rows must contain finite time and displacement")
        series.append(item)
    series.sort(key=lambda item: item["time_s"])
    return series


def _align_series(official: list[dict[str, float]], solver: list[dict[str, float]]) -> list[dict[str, Any]]:
    start = max(official[0]["time_s"], solver[0]["time_s"])
    end = min(official[-1]["time_s"], solver[-1]["time_s"])
    if start > end:
        raise ValueError("official and solver monitors have no overlapping time range")
    times = sorted(
        time
        for time in {item["time_s"] for item in official} | {item["time_s"] for item in solver}
        if start <= time <= end
    )
    if not times:
        times = [start]
    aligned = []
    for time_s in times:
        official_d = _interpolate(official, "displacement_m", time_s)
        solver_d = _interpolate(solver, "displacement_m", time_s)
        official_f = _interpolate(official, "force_n", time_s)
        solver_f = _interpolate(solver, "force_n", time_s)
        force_error = (
            solver_f - official_f
            if math.isfinite(official_f) and math.isfinite(solver_f)
            else ""
        )
        aligned.append(
            {
                "time_s": time_s,
                "official_flap_tip_total_displacement_m": official_d,
                "solver_flap_tip_total_displacement_m": solver_d,
                "displacement_error_m": solver_d - official_d,
                "official_fluid_force_magnitude_n": official_f if math.isfinite(official_f) else "",
                "solver_fluid_force_magnitude_n": solver_f if math.isfinite(solver_f) else "",
                "force_error_n": force_error,
            }
        )
    return aligned


def _displacement_metrics(
    official: list[dict[str, float]],
    solver: list[dict[str, float]],
    aligned: list[dict[str, Any]],
    official_monitor: Path,
    solver_monitor: Path,
) -> dict[str, Any]:
    official_values = [float(row["official_flap_tip_total_displacement_m"]) for row in aligned]
    solver_values = [float(row["solver_flap_tip_total_displacement_m"]) for row in aligned]
    times = [float(row["time_s"]) for row in aligned]
    errors = [solver_value - official_value for official_value, solver_value in zip(official_values, solver_values)]
    abs_errors = [abs(value) for value in errors]
    official_peak_index = _peak_index(official_values)
    solver_peak_index = _peak_index(solver_values)
    peak_official = official_values[official_peak_index]
    peak_solver = solver_values[solver_peak_index]
    eps = 1.0e-12
    metrics = {
        "status": "computed",
        "official_monitor": _display_path(official_monitor),
        "solver_monitor": _display_path(solver_monitor),
        "sample_count": len(aligned),
        "interpolation_method": "linear_time_overlap",
        "official_time_start_s": official[0]["time_s"],
        "official_time_end_s": official[-1]["time_s"],
        "solver_time_start_s": solver[0]["time_s"],
        "solver_time_end_s": solver[-1]["time_s"],
        "overlap_time_start_s": times[0],
        "overlap_time_end_s": times[-1],
        "rms_abs_error_m": _rms(errors),
        "normalized_rms_error": _rms(errors) / max(abs(peak_official), eps),
        "peak_official_m": peak_official,
        "peak_solver_m": peak_solver,
        "peak_abs_error_m": abs(peak_solver - peak_official),
        "official_peak_time_s": times[official_peak_index],
        "solver_peak_time_s": times[solver_peak_index],
        "peak_time_error_s": abs(times[solver_peak_index] - times[official_peak_index]),
        "final_official_m": official_values[-1],
        "final_solver_m": solver_values[-1],
        "final_abs_error_m": abs(solver_values[-1] - official_values[-1]),
        "shape_correlation": _correlation(official_values, solver_values),
        "sign_agreement_fraction": _sign_agreement_fraction(official_values, solver_values),
        "all_metrics_finite": True,
        "validation_claim_allowed": False,
    }
    metrics["all_metrics_finite"] = _finite_metrics(metrics)
    return metrics


def _force_metrics(
    official: list[dict[str, float]],
    solver: list[dict[str, float]],
    aligned: list[dict[str, Any]],
    official_force_column: str | None,
    solver_force_column: str | None,
) -> dict[str, Any]:
    if official_force_column is None or solver_force_column is None:
        return {
            "status": "force_columns_missing",
            "force_reference_loaded": official_force_column is not None,
            "solver_force_loaded": solver_force_column is not None,
            "validation_claim_allowed": False,
        }
    official_values = [_optional_float(row["official_fluid_force_magnitude_n"]) for row in aligned]
    solver_values = [_optional_float(row["solver_fluid_force_magnitude_n"]) for row in aligned]
    times = [float(row["time_s"]) for row in aligned]
    valid = [
        (time_s, official_force, solver_force)
        for time_s, official_force, solver_force in zip(times, official_values, solver_values)
        if math.isfinite(official_force) and math.isfinite(solver_force)
    ]
    if not valid:
        return {
            "status": "force_values_missing",
            "force_reference_loaded": False,
            "solver_force_loaded": False,
            "validation_claim_allowed": False,
        }
    valid_times = [item[0] for item in valid]
    official_force = [item[1] for item in valid]
    solver_force = [item[2] for item in valid]
    errors = [solver_value - official_value for official_value, solver_value in zip(official_force, solver_force)]
    official_peak_index = _peak_index(official_force)
    solver_peak_index = _peak_index(solver_force)
    eps = 1.0e-12
    metrics = {
        "status": "computed",
        "force_reference_loaded": True,
        "solver_force_loaded": True,
        "sample_count": len(valid),
        "rms_abs_error_n": _rms(errors),
        "normalized_rms_error": _rms(errors) / max(abs(official_force[official_peak_index]), eps),
        "peak_official_force_n": official_force[official_peak_index],
        "peak_solver_force_n": solver_force[solver_peak_index],
        "peak_abs_error_n": abs(solver_force[solver_peak_index] - official_force[official_peak_index]),
        "official_peak_time_s": valid_times[official_peak_index],
        "solver_peak_time_s": valid_times[solver_peak_index],
        "peak_time_error_s": abs(valid_times[solver_peak_index] - valid_times[official_peak_index]),
        "official_impulse_n_s": _trapezoid(valid_times, official_force),
        "solver_impulse_n_s": _trapezoid(valid_times, solver_force),
        "impulse_abs_error_n_s": abs(_trapezoid(valid_times, solver_force) - _trapezoid(valid_times, official_force)),
        "shape_correlation": _correlation(official_force, solver_force),
        "sign_agreement_fraction": _sign_agreement_fraction(official_force, solver_force),
        "validation_claim_allowed": False,
    }
    metrics["all_metrics_finite"] = _finite_metrics(metrics)
    return metrics


def _phase_lag_metrics(aligned: list[dict[str, Any]], force_metrics: dict[str, Any]) -> dict[str, Any]:
    if force_metrics.get("status") != "computed":
        return {"status": "force_metrics_unavailable", "validation_claim_allowed": False}
    times = [float(row["time_s"]) for row in aligned]
    solver_d = [float(row["solver_flap_tip_total_displacement_m"]) for row in aligned]
    official_d = [float(row["official_flap_tip_total_displacement_m"]) for row in aligned]
    solver_f = [_optional_float(row["solver_fluid_force_magnitude_n"]) for row in aligned]
    official_f = [_optional_float(row["official_fluid_force_magnitude_n"]) for row in aligned]
    solver_valid = [(time, force) for time, force in zip(times, solver_f) if math.isfinite(force)]
    official_valid = [(time, force) for time, force in zip(times, official_f) if math.isfinite(force)]
    if not solver_valid or not official_valid:
        return {"status": "force_values_missing", "validation_claim_allowed": False}
    solver_force_peak_time = max(solver_valid, key=lambda item: abs(item[1]))[0]
    official_force_peak_time = max(official_valid, key=lambda item: abs(item[1]))[0]
    solver_disp_peak_time = times[_peak_index(solver_d)]
    official_disp_peak_time = times[_peak_index(official_d)]
    return {
        "status": "computed",
        "official_force_displacement_peak_lag_s": official_force_peak_time - official_disp_peak_time,
        "solver_force_displacement_peak_lag_s": solver_force_peak_time - solver_disp_peak_time,
        "force_displacement_peak_lag_s": (solver_force_peak_time - solver_disp_peak_time)
        - (official_force_peak_time - official_disp_peak_time),
        "validation_claim_allowed": False,
    }


def _bug_hypotheses(
    displacement_metrics: dict[str, Any],
    force_metrics: dict[str, Any],
    phase_metrics: dict[str, Any],
) -> dict[str, Any]:
    hypotheses: list[dict[str, Any]] = []
    nrmse = float(displacement_metrics.get("normalized_rms_error", 0.0))
    peak_time = float(displacement_metrics.get("peak_time_error_s", 0.0))
    corr = float(displacement_metrics.get("shape_correlation", 0.0))

    if nrmse > 0.25:
        hypotheses.append(
            _hypothesis(
                "structural_model_error",
                min(1.0, nrmse),
                "solver displacement amplitude diverges from the official monitor",
                ["src/mpm_lbm/sim/mpm/solid.py", "src/mpm_lbm/sim/drivers/fsi_config.py"],
            )
        )
    if peak_time > 1.0e-12:
        hypotheses.append(
            _hypothesis(
                "time_integration_or_subcycling_error",
                min(1.0, peak_time / 5.0e-4),
                "official and solver peak displacement times differ inside the overlap window",
                ["src/mpm_lbm/sim/drivers/fsi_driver.py", "src/mpm_lbm/sim/drivers/fsi_config.py"],
            )
        )
    if corr < 0.25:
        hypotheses.append(
            _hypothesis(
                "solid_to_fluid_motion_error",
                min(1.0, 0.25 - corr + nrmse),
                "solver displacement shape has weak correlation with the official reference",
                ["src/mpm_lbm/sim/coupling/projection.py", "src/mpm_lbm/sim/drivers/fsi_driver.py"],
            )
        )

    if force_metrics.get("status") == "computed":
        force_nrmse = float(force_metrics.get("normalized_rms_error", 0.0))
        force_sign = float(force_metrics.get("sign_agreement_fraction", 1.0))
        if force_nrmse > 0.25 or force_sign < 0.75:
            hypotheses.append(
                _hypothesis(
                    "coupling_force_transfer_error",
                    min(1.0, force_nrmse + (1.0 - force_sign)),
                    "solver force monitor differs strongly from the official force reference",
                    ["src/mpm_lbm/sim/coupling/moving_boundary.py", "src/mpm_lbm/sim/lbm/fluid.py"],
                )
            )
    else:
        hypotheses.append(
            _hypothesis(
                "monitor_extraction_error",
                0.6,
                "force comparison could not be computed because force columns were missing",
                ["experiments/steps/step148_our_solver_fluent_official_case_reproduction.py"],
            )
        )

    if phase_metrics.get("status") == "computed" and abs(float(phase_metrics["force_displacement_peak_lag_s"])) > 0.0:
        hypotheses.append(
            _hypothesis(
                "coupling_force_transfer_error",
                min(1.0, abs(float(phase_metrics["force_displacement_peak_lag_s"])) / 5.0e-4),
                "force-displacement peak lag differs between official and solver monitors",
                ["src/mpm_lbm/sim/coupling/moving_boundary.py", "src/mpm_lbm/sim/drivers/fsi_driver.py"],
            )
        )

    if not hypotheses:
        hypotheses.append(
            _hypothesis(
                "fluid_boundary_error",
                0.2,
                "metrics are finite but no dominant error mode crossed the configured heuristic threshold",
                ["src/mpm_lbm/sim/lbm/fluid.py"],
            )
        )

    hypotheses.sort(key=lambda item: item["score"], reverse=True)
    return {
        "status": "hypotheses_generated",
        "categories": BUG_CATEGORIES,
        "hypotheses": hypotheses,
        "top_category": hypotheses[0]["category"],
        "next_fix_step_recommended": 150,
        "validation_claim_allowed": False,
        "fabricated_metrics_used": False,
    }


def _comparison_summary(
    official_monitor: Path,
    solver_monitor: Path,
    solver_force_monitor: Path,
    solver_summary_path: Path | None,
    aligned: list[dict[str, Any]],
    displacement_metrics: dict[str, Any],
    force_metrics: dict[str, Any],
    phase_metrics: dict[str, Any],
    hypotheses: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step": STEP,
        "status": "comparison_complete",
        "official_monitor": _display_path(official_monitor),
        "solver_monitor": _display_path(solver_monitor),
        "solver_force_monitor": _display_path(solver_force_monitor),
        "solver_summary": None if solver_summary_path is None else _display_path(solver_summary_path),
        "official_reference_loaded": True,
        "solver_monitor_loaded": True,
        "aligned_sample_count": len(aligned),
        "error_metrics_present": True,
        "solver_bug_hypotheses_present": True,
        "next_code_fix_step_identified": True,
        "recommended_next_step": 150,
        "top_bug_category": hypotheses.get("top_category"),
        "interpolation_method": "linear_time_overlap",
        "overlap_time_start_s": displacement_metrics.get("overlap_time_start_s"),
        "overlap_time_end_s": displacement_metrics.get("overlap_time_end_s"),
        "displacement_normalized_rms_error": displacement_metrics.get("normalized_rms_error"),
        "force_metrics_status": force_metrics.get("status"),
        "phase_lag_status": phase_metrics.get("status"),
        "fabricated_metrics_used": False,
        "validation_claim_allowed": False,
    }


def _hypothesis(category: str, score: float, evidence: str, suspect_modules: list[str]) -> dict[str, Any]:
    if category not in BUG_CATEGORIES:
        raise ValueError(f"unknown bug category: {category}")
    return {
        "category": category,
        "score": max(0.0, min(1.0, float(score))),
        "evidence": evidence,
        "suspect_modules": suspect_modules,
        "validation_claim_allowed": False,
    }


def _interpolate(series: list[dict[str, float]], column: str, time_s: float) -> float:
    if time_s <= series[0]["time_s"]:
        return float(series[0][column])
    if time_s >= series[-1]["time_s"]:
        return float(series[-1][column])
    for left, right in zip(series, series[1:]):
        left_t = left["time_s"]
        right_t = right["time_s"]
        if left_t <= time_s <= right_t:
            left_v = float(left[column])
            right_v = float(right[column])
            if not math.isfinite(left_v) or not math.isfinite(right_v):
                return math.nan
            if abs(right_t - left_t) <= 1.0e-30:
                return left_v
            alpha = (time_s - left_t) / (right_t - left_t)
            return left_v + alpha * (right_v - left_v)
    return math.nan


def _find_column(row: dict[str, Any], aliases: Sequence[str], required: bool = True) -> str | None:
    for name in aliases:
        if name in row:
            return name
    if required:
        raise ValueError("none of the required columns were present: " + ", ".join(aliases))
    return None


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_report(output_dir: Path, summary: dict[str, Any], hypotheses: dict[str, Any]) -> None:
    output_report = output_dir / "report.md"
    doc_report = REPO_ROOT / "docs" / "campaigns" / "fluent_duct_flap" / "steps" / "149" / "report.md"
    lines = [
        "# Step149 Fluent Official vs Our-Solver Error Localization",
        "",
        f"- Status: `{summary.get('status')}`",
        f"- Official reference loaded: `{summary.get('official_reference_loaded')}`",
        f"- Solver monitor loaded: `{summary.get('solver_monitor_loaded')}`",
        f"- Error metrics present: `{summary.get('error_metrics_present')}`",
        f"- Top bug category: `{summary.get('top_bug_category')}`",
        f"- Recommended next step: `{summary.get('recommended_next_step')}`",
        f"- Validation claim allowed: `{summary.get('validation_claim_allowed')}`",
        "",
        "This step compares monitors only when both official and solver time series are present.",
        "If the private official monitor is absent, it records a missing-reference state and does not fabricate metrics.",
        "",
    ]
    for item in hypotheses.get("hypotheses", [])[:3]:
        lines.append(f"- `{item['category']}` score `{item['score']}`: {item['evidence']}")
    text = "\n".join(lines) + "\n"
    output_report.write_text(text, encoding="utf-8")
    doc_report.parent.mkdir(parents=True, exist_ok=True)
    doc_report.write_text(text, encoding="utf-8")


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return math.sqrt(sum(float(value) * float(value) for value in values) / len(values))


def _peak_index(values: Sequence[float]) -> int:
    return max(range(len(values)), key=lambda index: abs(float(values[index])))


def _correlation(a_values: Sequence[float], b_values: Sequence[float]) -> float:
    if len(a_values) != len(b_values) or not a_values:
        return 0.0
    a_mean = sum(a_values) / len(a_values)
    b_mean = sum(b_values) / len(b_values)
    a_centered = [value - a_mean for value in a_values]
    b_centered = [value - b_mean for value in b_values]
    numerator = sum(a * b for a, b in zip(a_centered, b_centered))
    a_norm = math.sqrt(sum(value * value for value in a_centered))
    b_norm = math.sqrt(sum(value * value for value in b_centered))
    if a_norm <= 1.0e-30 or b_norm <= 1.0e-30:
        return 0.0
    return max(-1.0, min(1.0, numerator / (a_norm * b_norm)))


def _sign_agreement_fraction(a_values: Sequence[float], b_values: Sequence[float]) -> float:
    compared = 0
    matched = 0
    for a_value, b_value in zip(a_values, b_values):
        if abs(a_value) <= 1.0e-30 or abs(b_value) <= 1.0e-30:
            continue
        compared += 1
        if (a_value > 0.0) == (b_value > 0.0):
            matched += 1
    return 1.0 if compared == 0 else matched / compared


def _trapezoid(times: Sequence[float], values: Sequence[float]) -> float:
    if len(times) < 2:
        return 0.0
    area = 0.0
    for left_t, right_t, left_v, right_v in zip(times, times[1:], values, values[1:]):
        area += 0.5 * (right_v + left_v) * (right_t - left_t)
    return area


def _optional_float(value: Any) -> float:
    if value == "" or value is None:
        return math.nan
    try:
        return float(value)
    except Exception:
        return math.nan


def _finite_metrics(metrics: dict[str, Any]) -> bool:
    for value in metrics.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True


def _display_path(path: Path | str) -> str:
    path = Path(path)
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except Exception:
        return str(path)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-monitor", type=Path, default=DEFAULT_OFFICIAL_MONITOR)
    parser.add_argument("--solver-monitor", type=Path, default=DEFAULT_SOLVER_MONITOR)
    parser.add_argument("--solver-force-monitor", type=Path, default=DEFAULT_SOLVER_FORCE_MONITOR)
    parser.add_argument("--solver-summary", type=Path, default=DEFAULT_SOLVER_SUMMARY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    summary = run_step149_error_localization(
        official_monitor=args.official_monitor,
        solver_monitor=args.solver_monitor,
        solver_force_monitor=args.solver_force_monitor,
        solver_summary=args.solver_summary,
        output_dir=args.output_dir,
        force=args.force,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
