import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step107_error_metric_policy_is_comparison_only():
    policy = read_json("configs/step107_error_metric_policy.json")

    assert policy["reference_curve_path"] == "benchmarks/public/fluent_fsi_2way_digitized/figure_29_4_structural_point_flap_digitized.csv"
    assert policy["solver_curve_path"] == "outputs/step106_fsi_outlet_repair_regression/flap_tip_displacement_timeseries.csv"
    assert policy["solver_time_column"] == "time_s"
    assert policy["solver_displacement_column"] == "flap_tip_total_displacement_m"
    assert policy["monitor_used"] == "free_tip_proxy_mean"
    assert policy["monitor_equivalence"] is False
    assert policy["min_sample_count"] == 10
    assert policy["expected_sample_count"] == 51
    assert policy["validation_claim_allowed"] is False
    assert policy["direct_quantitative_equivalence_allowed"] is False


def test_step107_error_metrics_compute_against_solver_timeseries():
    payload = read_json("outputs/step107_error_comparison/error_report.json")
    row = payload["rows"][0]
    summary = payload["summary"]

    assert summary["step107_error_comparison_pass"] is True
    assert summary["row_count"] == 1
    assert row["reference_loaded"] is True
    assert row["solver_curve_loaded"] is True
    assert row["monitor_used"] == "free_tip_proxy_mean"
    assert row["monitor_equivalence"] is False
    assert row["sample_count"] == 51
    assert row["peak_reference_m"] > 3.0e-4
    assert row["peak_solver_m"] >= 0.0
    assert row["peak_abs_error_m"] >= 0.0
    assert row["rms_abs_error_m"] >= 0.0
    assert row["normalized_rms_error"] >= 0.0
    assert row["final_abs_error_m"] >= 0.0
    assert -1.0 <= row["shape_correlation"] <= 1.0
    assert row["sign_consistency"] is True
    assert row["all_metrics_finite"] is True
    assert row["validation_claim_allowed"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert finite_numeric_row(row)

    csv_rows = read_csv("outputs/step107_error_comparison/error_report.csv")
    assert len(csv_rows) == 1
    md_text = (ROOT / "outputs/step107_error_comparison/error_report.md").read_text(encoding="utf-8")
    assert "Step107 Public Fluent Plot Error Comparison" in md_text
    assert "not Fluent validation" in md_text


def test_step107_pure_error_metric_helpers_are_finite():
    from src.mpm_lbm.validation.error_metrics import compute_displacement_error_metrics

    reference = [
        {"time_s": 0.0, "fluent_public_digitized_total_displacement_m": 0.0},
        {"time_s": 0.5, "fluent_public_digitized_total_displacement_m": 2.0},
        {"time_s": 1.0, "fluent_public_digitized_total_displacement_m": 0.0},
    ]
    solver = [
        {"time_s": 0.0, "solver_total_displacement_m": 0.0},
        {"time_s": 0.5, "solver_total_displacement_m": 1.0},
        {"time_s": 1.0, "solver_total_displacement_m": 0.0},
    ]
    metrics = compute_displacement_error_metrics(
        reference,
        solver,
        {
            "monitor_used": "unit_fixture",
            "monitor_equivalence": False,
            "min_sample_count": 3,
            "direct_quantitative_equivalence_allowed": False,
            "validation_claim_allowed": False,
        },
    )

    assert metrics["reference_loaded"] is True
    assert metrics["solver_curve_loaded"] is True
    assert metrics["sample_count"] == 3
    assert metrics["peak_reference_m"] == 2.0
    assert metrics["peak_solver_m"] == 1.0
    assert metrics["peak_abs_error_m"] == 1.0
    assert metrics["all_metrics_finite"] is True


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
