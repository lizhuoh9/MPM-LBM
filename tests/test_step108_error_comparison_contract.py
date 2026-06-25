import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step108_error_report_uses_step107_reference_and_step108_solver_curve():
    policy = read_json("configs/step108_low_mach_subcycling_policy.json")
    payload = read_json("outputs/step108_error_comparison/error_report.json")
    row = payload["rows"][0]
    summary = payload["summary"]

    assert policy["reference_curve_path"] == "benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv"
    assert policy["solver_curve_path"] == "outputs/step108_low_mach_fsi_candidate/flap_tip_displacement_timeseries.csv"
    assert policy["solver_time_column"] == "time_s"
    assert policy["solver_displacement_column"] == "flap_tip_total_displacement_m"
    assert policy["monitor_used"] == "free_tip_proxy_mean"
    assert policy["monitor_equivalence"] is False
    assert policy["validation_claim_allowed"] is False
    assert policy["direct_quantitative_equivalence_allowed"] is False

    assert summary["step108_error_comparison_pass"] is True
    assert summary["row_count"] == 1
    assert row["reference_loaded"] is True
    assert row["solver_curve_loaded"] is True
    assert row["monitor_used"] == "free_tip_proxy_mean"
    assert row["monitor_equivalence"] is False
    assert row["sample_count"] == 51
    assert row["solver_curve_time_end_s"] == 0.025
    assert row["peak_reference_m"] > 3.0e-4
    assert row["peak_solver_m"] >= 0.0
    assert row["normalized_rms_error"] >= 0.0
    assert -1.0 <= row["shape_correlation"] <= 1.0
    assert row["all_metrics_finite"] is True
    assert row["validation_claim_allowed"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert finite_numeric_row(row)

    csv_rows = read_csv("outputs/step108_error_comparison/error_report.csv")
    assert len(csv_rows) == 1
    md_text = (ROOT / "outputs/step108_error_comparison/error_report.md").read_text(encoding="utf-8")
    assert "Step108 Low-Mach Subcycling Error Comparison" in md_text
    assert "not Fluent validation" in md_text


def test_step108_reports_soft_goal_comparison_without_faking_pass():
    payload = read_json("outputs/step108_error_comparison/error_report.json")
    summary = payload["summary"]

    assert "step107_peak_solver_m" in summary
    assert "step108_peak_solver_improved" in summary
    assert "step107_normalized_rms_error" in summary
    assert "step108_normalized_rms_improved" in summary
    assert "step107_shape_correlation" in summary
    assert "step108_shape_correlation_improved" in summary
    assert isinstance(summary["step108_peak_solver_improved"], bool)
    assert isinstance(summary["step108_normalized_rms_improved"], bool)
    assert isinstance(summary["step108_shape_correlation_improved"], bool)
    assert summary["soft_goals_are_hard_gates"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def finite_numeric_row(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True
