from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


STEP = 140
SOURCE_STEP = 139
DEFAULT_STEP139_ROOT = Path("outputs/step139_planeflux_final48")
DEFAULT_OUTPUT_DIR = Path("outputs/step140_long_window_drift_forensics")

DEFAULT_WINDOWS = [
    {"name": "0_100", "start": 0.0, "end": 100.0},
    {"name": "100_200", "start": 100.0, "end": 200.0},
    {"name": "200_250", "start": 200.0, "end": 250.0},
    {"name": "250_300", "start": 250.0, "end": 300.0},
    {"name": "300_400", "start": 300.0, "end": 400.0},
    {"name": "400_500", "start": 400.0, "end": 500.0},
    {"name": "tail_80pct_diagnostic", "tail_fraction": 0.80},
    {"name": "tail_20pct_hard_gate", "tail_fraction": 0.20},
]

MASS_FIELDS = ["mass_total_delta_rel"]
FLUX_FIELDS = [
    "inlet_flux",
    "outlet_flux",
    "outlet_flux_after_correction",
    "midplane_flux",
    "outlet_to_inlet_flux_ratio",
    "midplane_to_inlet_flux_ratio",
    "flux_imbalance_rel",
    "near_outlet_to_outlet_flux_ratio",
]
CONTROLLER_FIELDS = [
    "controller_target_outlet_flux",
    "controller_measured_outlet_flux",
    "controller_filtered_flux_error",
    "controller_raw_flux_error",
    "controller_u_feedback",
    "controller_u_feedback_abs",
    "controller_authority_ratio",
    "controller_saturation_fraction_run",
    "controller_drop_guard_activation_fraction_run",
]


def run_step140_forensics(
    step139_root: Path | str = DEFAULT_STEP139_ROOT,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    force: bool = False,
) -> dict[str, Any]:
    step139_root = Path(step139_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = _resolve_inputs(step139_root)
    if inputs["missing"]:
        return _write_missing_input_summary(output_dir, step139_root, inputs["missing"])

    records = _load_records(inputs)
    context = _load_context(inputs)
    windows = _materialize_windows(records)

    mass_report = _segment_report(
        artifact="mass_drift_segment_report",
        step139_root=step139_root,
        records=records,
        windows=windows,
        metric_fields=MASS_FIELDS,
        extra={
            "classification": _classify_mass(records),
            "input_final_mass_abs": abs(_final_value(records, "mass_total_delta_rel") or 0.0),
        },
    )
    flux_report = _segment_report(
        artifact="flux_stationarity_segment_report",
        step139_root=step139_root,
        records=records,
        windows=windows,
        metric_fields=FLUX_FIELDS,
        extra={
            "classification": _classify_flux(records),
            "hard_gate_tail_mean_limit": 0.10,
            "hard_gate_tail_cv_limit": 0.10,
        },
    )
    controller_report = _segment_report(
        artifact="controller_response_segment_report",
        step139_root=step139_root,
        records=records,
        windows=windows,
        metric_fields=CONTROLLER_FIELDS,
        extra={"classification": _classify_controller(records)},
    )
    x_profile_report = _x_profile_report(step139_root, records, windows)
    summary = _mechanism_summary(
        step139_root=step139_root,
        records=records,
        windows=windows,
        context=context,
        mass_report=mass_report,
        flux_report=flux_report,
        controller_report=controller_report,
    )

    _write_json(output_dir / "mass_drift_segment_report.json", mass_report)
    _write_json(output_dir / "flux_stationarity_segment_report.json", flux_report)
    _write_json(output_dir / "controller_response_segment_report.json", controller_report)
    _write_json(output_dir / "x_profile_evolution_report.json", x_profile_report)
    _write_json(output_dir / "step140_failure_mechanism_summary.json", summary)
    _write_markdown_summary(output_dir / "step140_failure_mechanism_summary.md", summary)
    return summary


def _resolve_inputs(step139_root: Path) -> dict[str, Any]:
    phase_root = step139_root / "planeflux_final48"
    row_dirs = (
        sorted(path for path in phase_root.iterdir() if path.is_dir())
        if phase_root.is_dir()
        else []
    )
    row_dir = next(
        (path for path in row_dirs if (path / "flow_development_diagnostics.csv").is_file()),
        None,
    )

    paths = {
        "phase_root": phase_root,
        "row_dir": row_dir,
        "campaign_manifest": phase_root / "campaign_manifest.json",
        "summary": phase_root / "step121_summary.json",
        "gate_report": phase_root / "step121_gate_report.json",
        "best_selection": phase_root / "step121_best_boundary_selection.json",
        "long_window_comparison": step139_root / "step139_long_window_comparison.json",
        "failure_forensics": step139_root / "step139_failure_forensics.json",
    }
    if row_dir is not None:
        paths.update(
            {
                "finite": row_dir / "finite_stability_report.json",
                "flow_csv": row_dir / "flow_development_diagnostics.csv",
                "flow_summary": row_dir / "flow_development_diagnostics_summary.json",
                "boundary_csv": row_dir / "boundary_flux_timeseries.csv",
                "density_csv": row_dir / "density_drift_timeseries.csv",
            }
        )
    else:
        paths.update(
            {
                "finite": phase_root / "<missing-row>" / "finite_stability_report.json",
                "flow_csv": phase_root / "<missing-row>" / "flow_development_diagnostics.csv",
                "flow_summary": phase_root / "<missing-row>" / "flow_development_diagnostics_summary.json",
                "boundary_csv": phase_root / "<missing-row>" / "boundary_flux_timeseries.csv",
                "density_csv": phase_root / "<missing-row>" / "density_drift_timeseries.csv",
            }
        )

    required = [
        "campaign_manifest",
        "summary",
        "gate_report",
        "best_selection",
        "long_window_comparison",
        "failure_forensics",
        "finite",
        "flow_csv",
        "flow_summary",
        "boundary_csv",
        "density_csv",
    ]
    missing = [str(paths[key]) for key in required if not Path(paths[key]).is_file()]
    return {"paths": paths, "missing": missing}


def _load_records(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    paths = inputs["paths"]
    records_by_step: dict[int, dict[str, Any]] = {}

    for row in _read_csv(paths["flow_csv"]):
        step = int(float(row["step"]))
        records_by_step[step] = _normalize_row(row)

    for row in _read_csv(paths["boundary_csv"]):
        step = int(float(row["step"]))
        target = records_by_step.setdefault(step, {"step": step})
        target["inlet_flux"] = _to_number(row.get("inlet_flux"))
        target["outlet_flux"] = _to_number(row.get("outlet_flux"))
        target["flux_imbalance_abs"] = _to_number(row.get("flux_imbalance_abs"))
        target["flux_imbalance_rel"] = _to_number(row.get("flux_imbalance_rel"))

    for row in _read_csv(paths["density_csv"]):
        step = int(float(row["step"]))
        target = records_by_step.setdefault(step, {"step": step})
        target["rho_min"] = _to_number(row.get("rho_min"))
        target["rho_max"] = _to_number(row.get("rho_max"))
        target["rho_mean"] = _to_number(row.get("rho_mean"))
        target["mass_total"] = _to_number(row.get("mass_total"))
        target["mass_total_delta_rel"] = _to_number(row.get("mass_total_delta_rel"))

    records = [records_by_step[key] for key in sorted(records_by_step)]
    for record in records:
        inlet = record.get("inlet_flux")
        outlet = record.get("outlet_flux")
        midplane = record.get("midplane_flux")
        if _valid(inlet) and abs(inlet) > 1.0e-12:
            if _valid(outlet):
                record["outlet_to_inlet_flux_ratio"] = float(outlet) / float(inlet)
            if _valid(midplane):
                record["midplane_to_inlet_flux_ratio"] = float(midplane) / float(inlet)
    return records


def _load_context(inputs: dict[str, Any]) -> dict[str, Any]:
    paths = inputs["paths"]
    return {
        "finite": _read_json(paths["finite"]),
        "flow_summary": _read_json(paths["flow_summary"]),
        "long_window_comparison": _read_json(paths["long_window_comparison"]),
        "failure_forensics": _read_json(paths["failure_forensics"]),
        "gate_report": _read_json(paths["gate_report"]),
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
    for spec in DEFAULT_WINDOWS:
        if "tail_fraction" in spec:
            fraction = float(spec["tail_fraction"])
            start = max_step * (1.0 - fraction)
            end = max_step
        else:
            start = float(spec["start"])
            end = float(spec["end"])
        windows.append({"name": spec["name"], "start": start, "end": end})
    return windows


def _segment_report(
    artifact: str,
    step139_root: Path,
    records: list[dict[str, Any]],
    windows: list[dict[str, Any]],
    metric_fields: list[str],
    extra: dict[str, Any],
) -> dict[str, Any]:
    segments = []
    unavailable = set()
    for window in windows:
        window_records = _records_in_window(records, window["start"], window["end"])
        metrics = {}
        for field in metric_fields:
            metric = _metric(window_records, field)
            if metric["available"]:
                metrics[field] = metric
            else:
                unavailable.add(field)
        segments.append(
            {
                "name": window["name"],
                "start_step": window["start"],
                "end_step": window["end"],
                "record_count": len(window_records),
                "metrics": metrics,
            }
        )

    report = _base_payload(artifact, step139_root)
    report.update(extra)
    report["segments"] = segments
    report["unavailable_fields"] = sorted(unavailable)
    return report


def _x_profile_report(step139_root: Path, records: list[dict[str, Any]], windows: list[dict[str, Any]]) -> dict[str, Any]:
    segments = []
    for window in windows:
        window_records = _records_in_window(records, window["start"], window["end"])
        x_keys = sorted(
            {
                key
                for record in window_records
                for key in (record.get("x_profile_flux_samples") or {}).keys()
            },
            key=lambda value: float(value),
        )
        by_x = {}
        for x_key in x_keys:
            values = [
                (float(record["step"]), float(record["x_profile_flux_samples"][x_key]))
                for record in window_records
                if isinstance(record.get("x_profile_flux_samples"), dict)
                and x_key in record["x_profile_flux_samples"]
                and _valid(record["x_profile_flux_samples"][x_key])
            ]
            if values:
                by_x[x_key] = _series_metric(values)
        segments.append(
            {
                "name": window["name"],
                "start_step": window["start"],
                "end_step": window["end"],
                "record_count": len(window_records),
                "x_profile_flux_by_x": by_x,
            }
        )

    report = _base_payload("x_profile_evolution_report", step139_root)
    report["x_profile_source_field"] = "x_profile_flux_samples"
    report["segments"] = segments
    report["unavailable_fields"] = []
    return report


def _mechanism_summary(
    step139_root: Path,
    records: list[dict[str, Any]],
    windows: list[dict[str, Any]],
    context: dict[str, Any],
    mass_report: dict[str, Any],
    flux_report: dict[str, Any],
    controller_report: dict[str, Any],
) -> dict[str, Any]:
    tail = _records_in_window(records, windows[-1]["start"], windows[-1]["end"])
    final_mass_abs = abs(_final_value(records, "mass_total_delta_rel") or 0.0)
    flux_tail = _metric(tail, "flux_imbalance_rel")
    outlet_tail = _metric(tail, "outlet_flux")
    near_tail = _metric(tail, "near_outlet_to_outlet_flux_ratio")
    controller_tail = _metric(tail, "controller_authority_ratio")

    mass_failed = final_mass_abs > 0.005
    outlet_cv_failed = outlet_tail.get("cv") is not None and outlet_tail["cv"] > 0.10
    flux_failed = flux_tail.get("mean") is not None and flux_tail["mean"] > 0.10

    mechanism_summary = {
        "mass_drift_mechanism": mass_report["classification"],
        "outlet_cv_mechanism": flux_report["classification"]["outlet_cv_mechanism"],
        "flux_mean_mechanism": flux_report["classification"]["flux_mean_mechanism"],
        "controller_response_mechanism": controller_report["classification"],
        "near_outlet_to_outlet_tail_mean": near_tail.get("mean"),
        "controller_authority_ratio_tail_slope": controller_tail.get("slope_per_step"),
    }
    dominant = "mixed_long_window_drift"
    recommendation = "Step141 should add diagnostics before tuning; no selected96 and no 500-step final evidence."
    if mass_failed and outlet_cv_failed:
        dominant = "mass_accumulation_with_outlet_stationarity_drift"
        recommendation = (
            "Step141 may propose one bounded 48^3 / 250-step diagnostic design focused on "
            "mass-neutral plane-flux or density-feedback isolation; no selected96 and no 500-step run."
        )
    mechanism_summary["dominant_failure_mechanism"] = dominant
    mechanism_summary["recommended_next_step"] = recommendation

    summary = _base_payload("step140_failure_mechanism_summary", step139_root)
    summary.update(
        {
            "status": "mechanism_classified",
            "missing_input": False,
            "input_step": SOURCE_STEP,
            "input_row_completed_500": True,
            "input_final_hard_gate_pass": bool(context["long_window_comparison"].get("final_hard_gate_pass")),
            "segment_count": len(windows),
            "mass_drift_failure_classified": mass_failed,
            "outlet_cv_failure_classified": outlet_cv_failed,
            "flux_mean_failure_classified": flux_failed,
            "mechanism_summary_present": True,
            "mechanism_summary": mechanism_summary,
            "dominant_failure_mechanism": dominant,
            "next_experiment_recommendations": [recommendation],
            "next_experiment_recommendation_count": 1,
            "step141_branch_policy": {
                "mass_drift_dominates": "mass-neutral plane-flux or outlet density feedback design proposal only",
                "outlet_cv_dominates": "stationarity-focused 48^3 / 250-step diagnostic sweep only",
                "controller_lag_dominates": "filter_alpha / slew / delta_cap bounded diagnostic, no more than 6 rows",
                "profile_mismatch_dominates": "measurement-plane / x-profile forensics, no more than 250 steps",
                "unclear": "add diagnostics before tuning",
            },
        }
    )
    return summary


def _classify_mass(records: list[dict[str, Any]]) -> str:
    after_250 = [record for record in records if float(record["step"]) >= 250.0]
    slope = _metric(after_250, "mass_total_delta_rel").get("slope_per_step")
    final_abs = abs(_final_value(records, "mass_total_delta_rel") or 0.0)
    if final_abs > 0.005 and slope is not None and slope > 0.0:
        return "post_250_mass_accumulation"
    if final_abs > 0.005:
        return "tail_mass_acceptance_failure"
    return "mass_drift_not_dominant"


def _classify_flux(records: list[dict[str, Any]]) -> dict[str, str]:
    max_step = max(float(record["step"]) for record in records)
    tail = _records_in_window(records, max_step * 0.8, max_step)
    flux_mean = _metric(tail, "flux_imbalance_rel").get("mean")
    outlet_cv = _metric(tail, "outlet_flux").get("cv")
    near_mean = _metric(tail, "near_outlet_to_outlet_flux_ratio").get("mean")
    return {
        "flux_mean_mechanism": "mean_flux_imbalance_tail_drift"
        if flux_mean is not None and flux_mean > 0.10
        else "flux_mean_within_gate",
        "outlet_cv_mechanism": "true_outlet_stationarity_oscillation"
        if outlet_cv is not None and outlet_cv > 0.10 and near_mean is not None and 0.98 <= near_mean <= 1.01
        else "outlet_cv_or_measurement_plane_unresolved",
    }


def _classify_controller(records: list[dict[str, Any]]) -> str:
    max_step = max(float(record["step"]) for record in records)
    tail = _records_in_window(records, max_step * 0.8, max_step)
    saturation = _metric(tail, "controller_saturation_fraction_run").get("max")
    authority_slope = _metric(tail, "controller_authority_ratio").get("slope_per_step")
    if saturation == 0.0 and authority_slope is not None and authority_slope < 0.0:
        return "unsaturated_controller_authority_decay"
    if saturation == 0.0:
        return "unsaturated_controller_response"
    return "controller_saturation_involved"


def _base_payload(artifact: str, step139_root: Path) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "step": STEP,
        "source_step": SOURCE_STEP,
        "step139_input_root": _display_path(step139_root),
        "new_lbm_run_executed": False,
        "new_parameter_tuning_executed": False,
        "selected96_execution_allowed": False,
        "validation_claim_allowed": False,
        "quasi2d_validation_claim_allowed": False,
        "fsi_validation_claim_allowed": False,
        "fluent_validation_claim_allowed": False,
        "figure29_3_parity_claim_allowed": False,
        "production_readiness_claim_allowed": False,
    }


def _write_missing_input_summary(output_dir: Path, step139_root: Path, missing: list[str]) -> dict[str, Any]:
    summary = _base_payload("step140_failure_mechanism_summary", step139_root)
    summary.update(
        {
            "status": "missing_input",
            "missing_input": True,
            "missing_inputs": missing,
            "input_step": SOURCE_STEP,
            "input_row_completed_500": False,
            "input_final_hard_gate_pass": False,
            "segment_count": 0,
            "mass_drift_failure_classified": False,
            "outlet_cv_failure_classified": False,
            "flux_mean_failure_classified": False,
            "mechanism_summary_present": False,
            "mechanism_summary": None,
            "dominant_failure_mechanism": None,
            "next_experiment_recommendations": [],
            "next_experiment_recommendation_count": 0,
        }
    )
    _write_json(output_dir / "step140_failure_mechanism_summary.json", summary)
    _write_markdown_summary(output_dir / "step140_failure_mechanism_summary.md", summary)
    return summary


def _records_in_window(records: list[dict[str, Any]], start: float, end: float) -> list[dict[str, Any]]:
    return [record for record in records if start <= float(record["step"]) <= end]


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


def _final_value(records: list[dict[str, Any]], field: str) -> float | None:
    for record in reversed(records):
        if field in record and _valid(record[field]):
            return float(record[field])
    return None


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_markdown_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Step140 Failure Mechanism Summary",
        "",
        f"Status: `{summary['status']}`.",
        "",
        f"New LBM run executed: `{str(summary['new_lbm_run_executed']).lower()}`.",
        f"New parameter tuning executed: `{str(summary['new_parameter_tuning_executed']).lower()}`.",
        f"Selected96 execution allowed: `{str(summary['selected96_execution_allowed']).lower()}`.",
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


def _to_number(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (int, float, bool)):
        return value
    text = str(value).strip()
    if text == "":
        return None
    if text in {"True", "False"}:
        return text == "True"
    try:
        return float(text)
    except ValueError:
        return value


def _parse_json_map(value: str) -> dict[str, float]:
    try:
        payload = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}
    return {str(key): float(item) for key, item in payload.items() if _valid(_to_number(item))}


def _valid(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(numeric)


def _display_path(path: Path) -> str:
    try:
        rel = path.resolve().relative_to(Path.cwd().resolve())
        return rel.as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build Step140 long-window drift forensics from Step139 artifacts."
    )
    parser.add_argument("--step139-root", type=Path, default=DEFAULT_STEP139_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    summary = run_step140_forensics(args.step139_root, args.output_dir, force=args.force)
    print(json.dumps({"status": summary["status"], "output_dir": _display_path(args.output_dir)}, sort_keys=True))
    return 2 if summary["status"] == "missing_input" else 0


if __name__ == "__main__":
    raise SystemExit(main())
