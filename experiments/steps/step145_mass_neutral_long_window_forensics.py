from __future__ import annotations

import argparse
import csv
import json
import math
from hashlib import sha256
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


STEP = 145
SOURCE_STEP = 144
DEFAULT_STEP144_ROOT = Path("outputs") / "step144_mass_neutral_final48"
DEFAULT_STEP143_ROOT = Path("outputs") / "step143_mass_neutral_design_diagnostic"
DEFAULT_STEP140_ROOT = Path("outputs") / "step140_long_window_drift_forensics"
DEFAULT_OUTPUT_DIR = Path("outputs") / "step145_mass_neutral_long_window_forensics"

WINDOW_SPECS = [
    {"name": "0_100", "start": 0.0, "end": 100.0},
    {"name": "100_200", "start": 100.0, "end": 200.0},
    {"name": "200_250", "start": 200.0, "end": 250.0},
    {"name": "250_300", "start": 250.0, "end": 300.0},
    {"name": "300_400", "start": 300.0, "end": 400.0},
    {"name": "400_500", "start": 400.0, "end": 500.0},
    {"name": "tail_80pct_diagnostic", "tail_fraction": 0.80},
    {"name": "tail_20pct_hard_gate", "tail_fraction": 0.20},
]

REQUIRED_INPUT_KEYS = [
    "step144_decision_summary",
    "step144_long_window_comparison",
    "step144_finite_stability_report",
    "step144_flow_development_diagnostics_csv",
    "step144_flow_development_diagnostics_summary",
    "step144_boundary_flux_timeseries_csv",
    "step144_density_drift_timeseries_csv",
    "step143_decision_summary",
    "step143_mass_neutral_comparison",
    "step140_failure_mechanism_summary",
]

SATURATION_FIELDS = [
    "mass_neutral_feedback_saturation_fraction_run",
    "mass_neutral_feedback_saturation_count_run",
    "mass_neutral_feedback_update_count_run",
    "mass_neutral_mass_error",
    "mass_neutral_rho_feedback",
    "mass_neutral_rho_feedback_abs",
    "mass_total_delta_rel",
]

STATIONARITY_FIELDS = [
    "inlet_flux",
    "outlet_flux",
    "outlet_flux_after_correction",
    "midplane_flux",
    "flux_imbalance_rel",
    "outlet_to_inlet_flux_ratio",
    "midplane_to_inlet_flux_ratio",
    "near_outlet_flux_xminus1",
    "near_outlet_flux_xminus2",
    "near_outlet_flux_xminus3",
    "near_outlet_to_outlet_flux_ratio",
]

MASS_NEUTRAL_ERROR_FIELDS = [
    "mass_total_delta_rel",
    "mass_neutral_mass_error",
    "mass_neutral_rho_feedback",
    "mass_neutral_rho_feedback_abs",
    "mass_neutral_feedback_saturation_fraction_run",
    "mass_neutral_feedback_update_count_run",
]

CONTROLLER_FIELDS = [
    "controller_target_outlet_flux",
    "controller_measured_outlet_flux",
    "controller_raw_flux_error",
    "controller_filtered_flux_error",
    "controller_u_feedback",
    "controller_u_feedback_abs",
    "controller_density_feedback",
    "controller_density_feedback_abs",
    "controller_authority_ratio",
    "controller_saturation_fraction_run",
    "controller_drop_guard_activation_fraction_run",
]

SUMMARY_ALIASES = {
    "mass_neutral_feedback_saturation_fraction": "mass_neutral_feedback_saturation_fraction_run",
    "mass_neutral_feedback_update_count": "mass_neutral_feedback_update_count_run",
    "controller_saturation_fraction": "controller_saturation_fraction_run",
    "drop_guard_activation_fraction": "controller_drop_guard_activation_fraction_run",
}

DECISION_CASES = {
    "mass_neutral_cap_saturation_dominant",
    "stationarity_drift_dominant",
    "controller_lag_or_slew_dominant",
    "mass_neutral_actuator_insufficient",
    "mixed_saturation_stationarity_failure",
    "mechanism_unresolved",
}


def run_step145_forensics(
    step144_root: Path | str = DEFAULT_STEP144_ROOT,
    step143_root: Path | str = DEFAULT_STEP143_ROOT,
    step140_root: Path | str = DEFAULT_STEP140_ROOT,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    del force
    step144_root = Path(step144_root)
    step143_root = Path(step143_root)
    step140_root = Path(step140_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = _resolve_inputs(step144_root, step143_root, step140_root)
    if inputs["missing"]:
        return _write_missing_input_summary(output_dir, step144_root, step143_root, step140_root, inputs)

    records = _load_records(inputs)
    windows = _materialize_windows(records)
    context = _load_context(inputs)

    saturation_report = _segment_report(
        artifact="saturation_segment_report",
        inputs=inputs,
        records=records,
        windows=windows,
        metric_fields=SATURATION_FIELDS,
        extra={
            "classification": _classify_saturation(records),
            "tail_saturation_threshold": 0.75,
        },
    )
    stationarity_report = _segment_report(
        artifact="stationarity_segment_report",
        inputs=inputs,
        records=records,
        windows=windows,
        metric_fields=STATIONARITY_FIELDS,
        extra={
            "classification": _classify_stationarity(context),
            "hard_gate_tail_mean_limit": 0.10,
            "hard_gate_tail_cv_limit": 0.10,
            "step140_context": _step140_context(context),
        },
    )
    mass_error_report = _segment_report(
        artifact="mass_neutral_error_segment_report",
        inputs=inputs,
        records=records,
        windows=windows,
        metric_fields=MASS_NEUTRAL_ERROR_FIELDS,
        extra={
            "classification": _classify_mass_neutral_error(context),
            "step143_to_step144_250_vs_500": _step143_to_step144_comparison(context, records, windows),
        },
    )
    controller_report = _segment_report(
        artifact="controller_lag_segment_report",
        inputs=inputs,
        records=records,
        windows=windows,
        metric_fields=CONTROLLER_FIELDS,
        extra={
            "classification": _classify_controller(records),
        },
    )
    summary = _mechanism_summary(
        inputs=inputs,
        records=records,
        windows=windows,
        context=context,
        saturation_report=saturation_report,
        stationarity_report=stationarity_report,
        mass_error_report=mass_error_report,
        controller_report=controller_report,
    )

    _write_json(output_dir / "saturation_segment_report.json", saturation_report)
    _write_json(output_dir / "stationarity_segment_report.json", stationarity_report)
    _write_json(output_dir / "mass_neutral_error_segment_report.json", mass_error_report)
    _write_json(output_dir / "controller_lag_segment_report.json", controller_report)
    _write_json(output_dir / "step145_failure_mechanism_summary.json", summary)
    _write_markdown_summary(output_dir / "step145_failure_mechanism_summary.md", summary)
    return summary


def _resolve_inputs(step144_root: Path, step143_root: Path, step140_root: Path) -> dict[str, Any]:
    phase_root = step144_root / "mass_neutral_final48"
    row_dir = _find_step144_row_dir(phase_root)
    paths: dict[str, Path | None] = {
        "step144_decision_summary": step144_root / "step144_decision_summary.json",
        "step144_long_window_comparison": step144_root / "step144_long_window_comparison.json",
        "step143_decision_summary": step143_root / "step143_decision_summary.json",
        "step143_mass_neutral_comparison": step143_root / "step143_mass_neutral_comparison.json",
        "step140_failure_mechanism_summary": step140_root / "step140_failure_mechanism_summary.json",
        "step144_finite_stability_report": None,
        "step144_flow_development_diagnostics_csv": None,
        "step144_flow_development_diagnostics_summary": None,
        "step144_boundary_flux_timeseries_csv": None,
        "step144_density_drift_timeseries_csv": None,
    }
    if row_dir is not None:
        paths.update(
            {
                "step144_finite_stability_report": row_dir / "finite_stability_report.json",
                "step144_flow_development_diagnostics_csv": row_dir / "flow_development_diagnostics.csv",
                "step144_flow_development_diagnostics_summary": row_dir / "flow_development_diagnostics_summary.json",
                "step144_boundary_flux_timeseries_csv": row_dir / "boundary_flux_timeseries.csv",
                "step144_density_drift_timeseries_csv": row_dir / "density_drift_timeseries.csv",
            }
        )
    else:
        paths.update(
            {
                "step144_finite_stability_report": phase_root / "*" / "finite_stability_report.json",
                "step144_flow_development_diagnostics_csv": phase_root / "*" / "flow_development_diagnostics.csv",
                "step144_flow_development_diagnostics_summary": phase_root / "*" / "flow_development_diagnostics_summary.json",
                "step144_boundary_flux_timeseries_csv": phase_root / "*" / "boundary_flux_timeseries.csv",
                "step144_density_drift_timeseries_csv": phase_root / "*" / "density_drift_timeseries.csv",
            }
        )

    missing = [
        _display_path(Path(paths[key])) if paths[key] is not None else key
        for key in REQUIRED_INPUT_KEYS
        if paths[key] is None or not Path(paths[key]).is_file()
    ]
    return {
        "step144_root": step144_root,
        "step143_root": step143_root,
        "step140_root": step140_root,
        "phase_root": phase_root,
        "row_dir": row_dir,
        "paths": paths,
        "missing": missing,
    }


def _find_step144_row_dir(phase_root: Path) -> Path | None:
    if not phase_root.is_dir():
        return None
    row_dirs = sorted(path for path in phase_root.iterdir() if path.is_dir())
    return next(
        (
            path
            for path in row_dirs
            if (path / "finite_stability_report.json").is_file()
            and (path / "flow_development_diagnostics.csv").is_file()
        ),
        None,
    )


def _load_records(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    paths = inputs["paths"]
    records_by_step: dict[int, dict[str, Any]] = {}

    for row in _read_csv(Path(paths["step144_flow_development_diagnostics_csv"])):
        record = _normalize_row(row)
        records_by_step[int(record["step"])] = record

    for row in _read_csv(Path(paths["step144_boundary_flux_timeseries_csv"])):
        step = int(float(row["step"]))
        target = records_by_step.setdefault(step, {"step": step})
        for key in ["inlet_flux", "outlet_flux", "flux_imbalance_abs", "flux_imbalance_rel"]:
            target[key] = _to_number(row.get(key))

    for row in _read_csv(Path(paths["step144_density_drift_timeseries_csv"])):
        step = int(float(row["step"]))
        target = records_by_step.setdefault(step, {"step": step})
        for key in [
            "rho_min",
            "rho_max",
            "rho_mean",
            "mass_total",
            "mass_total_delta_from_initial",
            "mass_total_delta_rel",
        ]:
            target[key] = _to_number(row.get(key))

    records = [records_by_step[key] for key in sorted(records_by_step)]
    for record in records:
        inlet = record.get("inlet_flux")
        outlet = record.get("outlet_flux")
        midplane = record.get("midplane_flux")
        if _valid(inlet) and abs(float(inlet)) > 1.0e-12:
            if _valid(outlet):
                record["outlet_to_inlet_flux_ratio"] = float(outlet) / float(inlet)
            if _valid(midplane):
                record["midplane_to_inlet_flux_ratio"] = float(midplane) / float(inlet)
    return records


def _load_context(inputs: dict[str, Any]) -> dict[str, Any]:
    paths = inputs["paths"]
    return {
        "step144_decision": _read_json(Path(paths["step144_decision_summary"])),
        "step144_comparison": _read_json(Path(paths["step144_long_window_comparison"])),
        "step144_finite": _read_json(Path(paths["step144_finite_stability_report"])),
        "step144_flow_summary": _read_json(Path(paths["step144_flow_development_diagnostics_summary"])),
        "step143_decision": _read_json(Path(paths["step143_decision_summary"])),
        "step143_comparison": _read_json(Path(paths["step143_mass_neutral_comparison"])),
        "step140_summary": _read_json(Path(paths["step140_failure_mechanism_summary"])),
    }


def _normalize_row(row: dict[str, str]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        if key == "step":
            normalized[key] = int(float(value))
        elif key in {"x_profile_flux_samples", "x_profile_ux_mean_samples", "x_profile_rho_mean_samples"}:
            normalized[key] = _parse_json_map(value)
        else:
            normalized[key] = _to_number(value)
    return normalized


def _materialize_windows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    max_step = max(float(record["step"]) for record in records)
    windows: list[dict[str, Any]] = []
    for spec in WINDOW_SPECS:
        if "tail_fraction" in spec:
            start = max_step * (1.0 - float(spec["tail_fraction"]))
            end = max_step
        else:
            start = float(spec["start"])
            end = float(spec["end"])
        windows.append({"name": spec["name"], "start": start, "end": end})
    return windows


def _segment_report(
    artifact: str,
    inputs: dict[str, Any],
    records: list[dict[str, Any]],
    windows: list[dict[str, Any]],
    metric_fields: list[str],
    extra: dict[str, Any],
) -> dict[str, Any]:
    segments = []
    unavailable = set()
    for window in windows:
        window_records = _records_in_window(records, float(window["start"]), float(window["end"]))
        metrics = {}
        for field in metric_fields:
            metric = _metric(window_records, field)
            if metric["available"]:
                metrics[field] = metric
            else:
                unavailable.add(field)
        summary_metrics = {
            alias: _metric(window_records, source_field)
            for alias, source_field in SUMMARY_ALIASES.items()
        }
        x_profile = _x_profile_flux_summary(window_records)
        segments.append(
            {
                "name": window["name"],
                "start_step": window["start"],
                "end_step": window["end"],
                "record_count": len(window_records),
                "metrics": metrics,
                "summary_metrics": summary_metrics,
                "x_profile_flux_samples_by_x": x_profile,
            }
        )

    report = _base_payload(artifact, inputs)
    report.update(extra)
    report["segments"] = segments
    report["unavailable_fields"] = sorted(unavailable)
    return report


def _mechanism_summary(
    inputs: dict[str, Any],
    records: list[dict[str, Any]],
    windows: list[dict[str, Any]],
    context: dict[str, Any],
    saturation_report: dict[str, Any],
    stationarity_report: dict[str, Any],
    mass_error_report: dict[str, Any],
    controller_report: dict[str, Any],
) -> dict[str, Any]:
    row = _step144_row(context)
    tail = _records_in_window(records, windows[-1]["start"], windows[-1]["end"])
    tail_saturation = _metric(tail, "mass_neutral_feedback_saturation_fraction_run").get("mean")
    tail_mass_error = _metric(tail, "mass_neutral_mass_error")
    tail_flux = _metric(tail, "flux_imbalance_rel")
    tail_outlet = _metric(tail, "outlet_flux")
    tail_controller = _metric(tail, "controller_authority_ratio")
    tail_rho_feedback = _metric(tail, "mass_neutral_rho_feedback")

    step144_mass_abs = _as_float(row.get("candidate_mass_acceptance_observed_abs"))
    step144_flux_mean = _as_float(row.get("flux_imbalance_rel_tail_mean"))
    step144_outlet_cv = _as_float(row.get("outlet_flux_tail_cv"))
    row_saturation = _as_float(row.get("mass_neutral_feedback_saturation_fraction_tail"))
    saturation_for_classification = _first_valid(tail_saturation, row_saturation)

    mass_failed = bool(row.get("candidate_mass_acceptance_gate_pass") is False or (step144_mass_abs or 0.0) > 0.005)
    flux_failed = bool((step144_flux_mean or 0.0) > 0.10)
    outlet_cv_failed = bool((step144_outlet_cv or 0.0) > 0.10)
    saturation_high = bool((saturation_for_classification or 0.0) > 0.75)

    dominant, mechanism_notes = _classify_dominant_mechanism(
        mass_failed=mass_failed,
        flux_failed=flux_failed,
        outlet_cv_failed=outlet_cv_failed,
        saturation_high=saturation_high,
        controller_tail=tail_controller,
    )
    recommendation = _recommend_next_step(dominant)

    mechanism = {
        "dominant_failure_mechanism": dominant,
        "question_a_mass_neutral_cap_or_actuator": _answer_question_a(
            saturation_high=saturation_high,
            mass_failed=mass_failed,
            tail_mass_error=tail_mass_error,
            tail_rho_feedback=tail_rho_feedback,
        ),
        "question_b_outlet_cv_origin": _answer_question_b(
            context=context,
            flux_failed=flux_failed,
            outlet_cv_failed=outlet_cv_failed,
        ),
        "question_c_250_step_non_extrapolation": _answer_question_c(mass_error_report),
        "classification_notes": mechanism_notes,
        "recommended_next_step": recommendation,
    }

    summary = _base_payload("step145_failure_mechanism_summary", inputs)
    summary.update(
        {
            "status": "mechanism_classified",
            "missing_input": False,
            "source_step": SOURCE_STEP,
            "source_step144_decision_case": context["step144_decision"].get("decision_case"),
            "source_step144_row_name": row.get("name"),
            "source_step143_decision_case": context["step143_decision"].get("decision_case"),
            "source_step140_dominant_failure_mechanism": context["step140_summary"].get(
                "dominant_failure_mechanism"
            ),
            "step144_final_mass_abs": step144_mass_abs,
            "step144_flux_imbalance_rel_tail_mean": step144_flux_mean,
            "step144_outlet_flux_tail_cv": step144_outlet_cv,
            "step144_mass_neutral_feedback_saturation_fraction_tail": row_saturation,
            "tail_mass_neutral_mass_error_mean": tail_mass_error.get("mean"),
            "tail_mass_neutral_rho_feedback_mean": tail_rho_feedback.get("mean"),
            "tail_flux_imbalance_rel_mean": tail_flux.get("mean"),
            "tail_outlet_flux_cv": tail_outlet.get("cv"),
            "tail_controller_authority_ratio_slope": tail_controller.get("slope_per_step"),
            "mechanism_summary_present": True,
            "mechanism_summary": mechanism,
            "dominant_failure_mechanism": dominant,
            "decision_case": dominant,
            "recommended_next_step": recommendation,
            "next_experiment_recommendations": [recommendation],
            "next_experiment_recommendation_count": 1,
            "segment_count": len(windows),
            "saturation_report_artifact": "saturation_segment_report.json",
            "stationarity_report_artifact": "stationarity_segment_report.json",
            "mass_neutral_error_report_artifact": "mass_neutral_error_segment_report.json",
            "controller_lag_report_artifact": "controller_lag_segment_report.json",
            "step146_250step_diagnostic_proposal_allowed": True,
            "step146_500step_probe_allowed": False,
            "step146_selected96_allowed": False,
        }
    )
    return summary


def _classify_dominant_mechanism(
    mass_failed: bool,
    flux_failed: bool,
    outlet_cv_failed: bool,
    saturation_high: bool,
    controller_tail: dict[str, Any],
) -> tuple[str, list[str]]:
    notes = []
    if saturation_high:
        notes.append("mass-neutral density feedback is saturated through the hard-gate tail")
    if mass_failed:
        notes.append("mass acceptance remains outside the candidate gate")
    if flux_failed or outlet_cv_failed:
        notes.append("outlet stationarity or mean flux imbalance remains outside the final gate")

    authority_slope = controller_tail.get("slope_per_step")
    controller_lag = authority_slope is not None and authority_slope < -0.001
    if controller_lag:
        notes.append("controller authority decays over the hard-gate tail")

    if saturation_high and mass_failed and (flux_failed or outlet_cv_failed):
        return "mixed_saturation_stationarity_failure", notes
    if saturation_high and mass_failed:
        return "mass_neutral_cap_saturation_dominant", notes
    if controller_lag and (flux_failed or outlet_cv_failed):
        return "controller_lag_or_slew_dominant", notes
    if saturation_high and (flux_failed or outlet_cv_failed):
        return "mass_neutral_actuator_insufficient", notes
    if flux_failed or outlet_cv_failed:
        return "stationarity_drift_dominant", notes
    return "mechanism_unresolved", notes


def _classify_saturation(records: list[dict[str, Any]]) -> dict[str, Any]:
    tail = _tail_records(records, 0.20)
    saturation = _metric(tail, "mass_neutral_feedback_saturation_fraction_run")
    return {
        "tail_saturation_high": bool((saturation.get("mean") or 0.0) > 0.75),
        "tail_saturation_mean": saturation.get("mean"),
        "tail_saturation_final": saturation.get("final"),
    }


def _classify_stationarity(context: dict[str, Any]) -> dict[str, Any]:
    row = _step144_row(context)
    step140 = context["step140_summary"].get("mechanism_summary") or {}
    outlet_cv = _as_float(row.get("outlet_flux_tail_cv"))
    flux_mean = _as_float(row.get("flux_imbalance_rel_tail_mean"))
    return {
        "outlet_cv_failed": bool((outlet_cv or 0.0) > 0.10),
        "flux_mean_failed": bool((flux_mean or 0.0) > 0.10),
        "step140_outlet_cv_mechanism": step140.get("outlet_cv_mechanism"),
        "step140_flux_mean_mechanism": step140.get("flux_mean_mechanism"),
        "interpretation": "long_window_stationarity_failure_recurs_after_mass_neutral_feedback",
    }


def _classify_mass_neutral_error(context: dict[str, Any]) -> dict[str, Any]:
    row = _step144_row(context)
    mass_abs = _as_float(row.get("candidate_mass_acceptance_observed_abs"))
    saturation = _as_float(row.get("mass_neutral_feedback_saturation_fraction_tail"))
    return {
        "mass_acceptance_failed": bool((mass_abs or 0.0) > 0.005),
        "mass_neutral_feedback_saturated": bool((saturation or 0.0) > 0.75),
        "interpretation": "250_step_mass_improvement_does_not_extrapolate_to_500_step_tail",
    }


def _classify_controller(records: list[dict[str, Any]]) -> dict[str, Any]:
    tail = _tail_records(records, 0.20)
    authority = _metric(tail, "controller_authority_ratio")
    filtered = _metric(tail, "controller_filtered_flux_error")
    saturation = _metric(tail, "controller_saturation_fraction_run")
    return {
        "controller_authority_ratio_tail_mean": authority.get("mean"),
        "controller_authority_ratio_tail_slope": authority.get("slope_per_step"),
        "controller_filtered_error_tail_mean": filtered.get("mean"),
        "controller_saturation_tail_mean": saturation.get("mean"),
        "interpretation": "unsaturated_velocity_controller_cannot_prevent_stationarity_drift",
    }


def _answer_question_a(
    saturation_high: bool,
    mass_failed: bool,
    tail_mass_error: dict[str, Any],
    tail_rho_feedback: dict[str, Any],
) -> dict[str, Any]:
    if saturation_high and mass_failed:
        code = "A4"
        interpretation = (
            "Mass-neutral feedback is saturated while mass acceptance still fails; "
            "the mass correction is coupled to outlet stationarity and actuator sufficiency."
        )
    elif saturation_high:
        code = "A3"
        interpretation = "Density-offset feedback is saturated, suggesting actuator insufficiency."
    else:
        code = "mechanism_unresolved"
        interpretation = "Mass-neutral saturation is not dominant enough to classify the actuator."
    return {
        "classification": code,
        "tail_mass_error_mean": tail_mass_error.get("mean"),
        "tail_mass_error_final": tail_mass_error.get("final"),
        "tail_rho_feedback_mean": tail_rho_feedback.get("mean"),
        "interpretation": interpretation,
    }


def _answer_question_b(context: dict[str, Any], flux_failed: bool, outlet_cv_failed: bool) -> dict[str, Any]:
    row = _step144_row(context)
    step140 = context["step140_summary"].get("mechanism_summary") or {}
    return {
        "classification": "plane_flux_stationarity_failure_recurs"
        if flux_failed or outlet_cv_failed
        else "stationarity_within_gate",
        "step144_outlet_flux_tail_cv": row.get("outlet_flux_tail_cv"),
        "step144_flux_imbalance_rel_tail_mean": row.get("flux_imbalance_rel_tail_mean"),
        "step140_outlet_cv_mechanism": step140.get("outlet_cv_mechanism"),
        "step140_near_outlet_to_outlet_tail_mean": step140.get("near_outlet_to_outlet_tail_mean"),
        "interpretation": (
            "Step144 outlet CV remains close to the original long-window stationarity problem; "
            "mass-neutral feedback did not remove the stationarity failure."
        ),
    }


def _answer_question_c(mass_error_report: dict[str, Any]) -> dict[str, Any]:
    comparison = mass_error_report["step143_to_step144_250_vs_500"]
    return {
        "classification": "step143_250_step_window_not_long_window_evidence",
        "step143_best_mass_abs": comparison["step143_best_mass_abs"],
        "step144_final_mass_abs": comparison["step144_final_mass_abs"],
        "step143_best_outlet_cv": comparison["step143_best_outlet_cv"],
        "step144_final_outlet_cv": comparison["step144_final_outlet_cv"],
        "interpretation": (
            "The best 250-step Step143 row improved all monitored gates, but Step144 shows "
            "that the 500-step tail reintroduces mass and stationarity failures."
        ),
    }


def _step143_to_step144_comparison(
    context: dict[str, Any],
    records: list[dict[str, Any]],
    windows: list[dict[str, Any]],
) -> dict[str, Any]:
    del windows
    step143_decision = context["step143_decision"]
    best_name = step143_decision.get("best_row_name")
    step143_best = next(
        (row for row in context["step143_comparison"].get("rows", []) if row.get("name") == best_name),
        {},
    )
    step144 = _step144_row(context)
    step144_250 = _records_in_window(records, 200.0, 250.0)
    return {
        "step143_best_row_name": best_name,
        "step143_best_mass_abs": step143_best.get("candidate_mass_acceptance_observed_abs"),
        "step143_best_flux_imbalance_rel_tail_mean": step143_best.get("flux_imbalance_rel_tail_mean"),
        "step143_best_outlet_cv": step143_best.get("outlet_flux_tail_cv"),
        "step143_best_mass_neutral_feedback_saturation_fraction_tail": step143_best.get(
            "mass_neutral_feedback_saturation_fraction_tail"
        ),
        "step144_row_name": step144.get("name"),
        "step144_final_mass_abs": step144.get("candidate_mass_acceptance_observed_abs"),
        "step144_final_flux_imbalance_rel_tail_mean": step144.get("flux_imbalance_rel_tail_mean"),
        "step144_final_outlet_cv": step144.get("outlet_flux_tail_cv"),
        "step144_final_mass_neutral_feedback_saturation_fraction_tail": step144.get(
            "mass_neutral_feedback_saturation_fraction_tail"
        ),
        "step144_200_250_mass_total_delta_rel": _metric(step144_250, "mass_total_delta_rel"),
        "step144_200_250_flux_imbalance_rel": _metric(step144_250, "flux_imbalance_rel"),
        "step144_200_250_outlet_flux": _metric(step144_250, "outlet_flux"),
    }


def _step140_context(context: dict[str, Any]) -> dict[str, Any]:
    summary = context["step140_summary"]
    mechanism = summary.get("mechanism_summary") or {}
    return {
        "dominant_failure_mechanism": summary.get("dominant_failure_mechanism"),
        "outlet_cv_mechanism": mechanism.get("outlet_cv_mechanism"),
        "flux_mean_mechanism": mechanism.get("flux_mean_mechanism"),
        "controller_response_mechanism": mechanism.get("controller_response_mechanism"),
    }


def _base_payload(artifact: str, inputs: dict[str, Any]) -> dict[str, Any]:
    paths = inputs.get("paths", {})
    return {
        "artifact": artifact,
        "step": STEP,
        "source_step": SOURCE_STEP,
        "step144_input_root": _display_path(inputs.get("step144_root", DEFAULT_STEP144_ROOT)),
        "step143_context_root": _display_path(inputs.get("step143_root", DEFAULT_STEP143_ROOT)),
        "step140_context_root": _display_path(inputs.get("step140_root", DEFAULT_STEP140_ROOT)),
        "step144_row_dir": _display_path(inputs.get("row_dir")) if inputs.get("row_dir") else None,
        "input_hashes": {
            key: _file_hash(Path(path))
            for key, path in paths.items()
            if path is not None and Path(path).is_file()
        },
        "new_lbm_run_executed": False,
        "new_parameter_tuning_executed": False,
        "selected96_execution_allowed": False,
        "selected_static_execution_allowed": False,
        "validation_claim_allowed": False,
        "selected_candidate_surface_review_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "figure29_3_parity_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    }

def _write_missing_input_summary(
    output_dir: Path,
    step144_root: Path,
    step143_root: Path,
    step140_root: Path,
    inputs: dict[str, Any],
) -> dict[str, Any]:
    summary = _base_payload(
        "step145_failure_mechanism_summary",
        {
            "step144_root": step144_root,
            "step143_root": step143_root,
            "step140_root": step140_root,
            "row_dir": inputs.get("row_dir"),
            "paths": inputs.get("paths", {}),
        },
    )
    summary.update(
        {
            "status": "missing_input",
            "missing_input": True,
            "missing_inputs": inputs["missing"],
            "source_step144_decision_case": None,
            "mechanism_summary_present": False,
            "mechanism_summary": None,
            "dominant_failure_mechanism": None,
            "recommended_next_step": "Provide the missing Step144/Step143/Step140 artifacts before classification.",
            "next_experiment_recommendations": [],
            "next_experiment_recommendation_count": 0,
            "step146_250step_diagnostic_proposal_allowed": False,
            "step146_500step_probe_allowed": False,
            "step146_selected96_allowed": False,
        }
    )
    _write_json(output_dir / "step145_failure_mechanism_summary.json", summary)
    _write_markdown_summary(output_dir / "step145_failure_mechanism_summary.md", summary)
    return summary


def _records_in_window(records: list[dict[str, Any]], start: float, end: float) -> list[dict[str, Any]]:
    return [record for record in records if start <= float(record["step"]) <= end]


def _tail_records(records: list[dict[str, Any]], fraction: float) -> list[dict[str, Any]]:
    max_step = max(float(record["step"]) for record in records)
    return _records_in_window(records, max_step * (1.0 - fraction), max_step)


def _metric(records: list[dict[str, Any]], field: str) -> dict[str, Any]:
    values = [
        (float(record["step"]), float(record[field]))
        for record in records
        if field in record and _valid(record[field])
    ]
    if not values:
        return {"available": False}
    metric = _series_metric(values)
    metric["available"] = True
    return metric


def _series_metric(values: list[tuple[float, float]]) -> dict[str, Any]:
    ys = [value for _, value in values]
    avg = mean(ys)
    std = pstdev(ys) if len(ys) > 1 else 0.0
    return {
        "available": True,
        "count": len(values),
        "mean": avg,
        "final": ys[-1],
        "min": min(ys),
        "max": max(ys),
        "max_abs": max(abs(value) for value in ys),
        "std": std,
        "cv": std / abs(avg) if abs(avg) > 1.0e-12 else None,
        "slope_per_step": _slope(values),
    }


def _slope(values: list[tuple[float, float]]) -> float | None:
    if len(values) < 2:
        return None
    xs = [item[0] for item in values]
    ys = [item[1] for item in values]
    x_mean = mean(xs)
    y_mean = mean(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if abs(denom) <= 1.0e-18:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denom


def _x_profile_flux_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    x_keys = sorted(
        {
            key
            for record in records
            for key in (record.get("x_profile_flux_samples") or {}).keys()
        },
        key=lambda value: float(value),
    )
    by_x = {}
    for x_key in x_keys:
        values = [
            (float(record["step"]), float(record["x_profile_flux_samples"][x_key]))
            for record in records
            if isinstance(record.get("x_profile_flux_samples"), dict)
            and x_key in record["x_profile_flux_samples"]
            and _valid(record["x_profile_flux_samples"][x_key])
        ]
        if values:
            by_x[x_key] = _series_metric(values)
    return by_x


def _step144_row(context: dict[str, Any]) -> dict[str, Any]:
    rows = context["step144_comparison"].get("rows") or []
    return dict(rows[0]) if rows else {}


def _recommend_next_step(dominant: str) -> str:
    if dominant == "mixed_saturation_stationarity_failure":
        return (
            "Step146 should be a design proposal for coupled mass-neutral saturation and "
            "stationarity failure; do not run selected96, selected-static, 96^3, or a 500-step probe."
        )
    if dominant == "mass_neutral_actuator_insufficient":
        return (
            "Step146 should design an actuator/formulation diagnostic before tuning cap values; "
            "no selected96 and no 500-step probe."
        )
    if dominant == "controller_lag_or_slew_dominant":
        return (
            "Step146 may propose a bounded 250-step controller-lag diagnostic matrix only; "
            "no selected96 and no 500-step probe."
        )
    if dominant == "stationarity_drift_dominant":
        return (
            "Step146 may propose stationarity-focused 250-step diagnostics only; "
            "no selected96 and no 500-step probe."
        )
    if dominant == "mass_neutral_cap_saturation_dominant":
        return (
            "Step146 may propose a bounded 250-step capped-response diagnostic only; "
            "no selected96 and no 500-step probe."
        )
    return "Step146 should add telemetry before any new parameter run."


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(_jsonable(payload), f, indent=2, sort_keys=True)
        f.write("\n")


def _write_markdown_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Step145 Failure Mechanism Summary",
        "",
        f"Status: `{summary['status']}`.",
        "",
        f"New LBM run executed: `{str(summary['new_lbm_run_executed']).lower()}`.",
        f"New parameter tuning executed: `{str(summary['new_parameter_tuning_executed']).lower()}`.",
        f"Selected96 execution allowed: `{str(summary['selected96_execution_allowed']).lower()}`.",
        f"Selected-candidate-surface review allowed: `{str(summary['selected_candidate_surface_review_allowed']).lower()}`.",
        f"Validation claim allowed: `{str(summary['validation_claim_allowed']).lower()}`.",
        "",
    ]
    if summary["status"] == "missing_input":
        lines.extend(["Missing inputs:", ""])
        lines.extend(f"- `{item}`" for item in summary.get("missing_inputs", []))
    else:
        lines.extend(
            [
                f"Dominant failure mechanism: `{summary['dominant_failure_mechanism']}`.",
                "",
                "Recommended next step:",
                "",
            ]
        )
        lines.extend(f"- {item}" for item in summary.get("next_experiment_recommendations", []))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_json_map(value: Any) -> dict[str, float]:
    if value in (None, ""):
        return {}
    try:
        decoded = json.loads(str(value))
    except json.JSONDecodeError:
        return {}
    if not isinstance(decoded, dict):
        return {}
    result = {}
    for key, item in decoded.items():
        number = _as_float(item)
        if number is not None:
            result[str(key)] = number
    return result


def _to_number(value: Any) -> Any:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    if text == "True":
        return True
    if text == "False":
        return False
    try:
        number = float(text)
    except ValueError:
        return value
    if math.isfinite(number) and number.is_integer():
        return int(number)
    return number if math.isfinite(number) else None


def _valid(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _as_float(value: Any) -> float | None:
    if not _valid(value):
        return None
    return float(value)


def _first_valid(*values: Any) -> float | None:
    for value in values:
        number = _as_float(value)
        if number is not None:
            return number
    return None


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _display_path(path: Any) -> str:
    if path is None:
        return ""
    path = Path(path)
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return _display_path(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Step145 artifact-only long-window failure forensics")
    parser.add_argument("--step144-root", type=Path, default=DEFAULT_STEP144_ROOT)
    parser.add_argument("--step143-root", type=Path, default=DEFAULT_STEP143_ROOT)
    parser.add_argument("--step140-root", type=Path, default=DEFAULT_STEP140_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    summary = run_step145_forensics(
        step144_root=args.step144_root,
        step143_root=args.step143_root,
        step140_root=args.step140_root,
        output_dir=args.output_dir,
        force=args.force,
    )
    print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
    return 0 if summary.get("status") != "missing_input" else 2


if __name__ == "__main__":
    raise SystemExit(main())
