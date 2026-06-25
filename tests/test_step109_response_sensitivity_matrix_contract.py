import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_ROWS = {
    "base",
    "cap_1e-4_scale_1",
    "cap_1e-3_scale_1",
    "cap_1e-2_scale_1",
    "cap_1e-1_scale_1",
    "cap_1e-2_scale_10",
    "cap_1e-1_scale_10",
}


def test_step109_response_matrix_contains_required_cap_scale_rows():
    policy = read_json("configs/step109_response_matrix_policy.json")
    assert policy["required_step_name"] == "Step109 Fluent Duct-Flap FSI Response Amplitude Sensitivity Matrix"
    assert policy["step108_peak_solver_m"] == 1.2332112646618043e-6
    assert policy["min_successful_rows"] == 5
    assert policy["min_peak_solver_m"] == 1.0e-5
    assert policy["validation_claim_allowed"] is False
    assert policy["direct_quantitative_equivalence_allowed"] is False
    assert REQUIRED_ROWS.issubset(set(policy["required_cap_scale_rows"]))

    for row_name in REQUIRED_ROWS:
        config = read_json(f"configs/step109_response_matrix_{row_name}.json")
        assert config["row_name"] == row_name
        assert config["fsi_exchange_mode"] == "lbm_subcycled_per_fsi_step"
        assert config["n_lbm_steps"] == 50
        assert config["lbm_substeps_per_fsi_step"] == 120
        assert config["lbm_dt_phys_override_s"] == 4.166666666666667e-6
        assert config["target_u_lbm"] == [0.02, 0.0, 0.0]
        assert config["wall_velocity_application_mode"] == "disabled"


def test_step109_response_matrix_runs_step108_baseline_and_variants():
    payload = read_json("outputs/step109_response_sensitivity_matrix/response_matrix_report.json")
    rows = payload["rows"]
    summary = payload["summary"]
    by_name = {row["row_name"]: row for row in rows}

    assert summary["response_matrix_pass"] is True
    assert summary["response_matrix_row_count"] >= 6
    assert summary["successful_response_matrix_rows"] >= 5
    assert summary["best_candidate_selected"] is True
    assert summary["best_candidate_validation_claim_allowed"] is False
    assert summary["best_candidate_direct_quantitative_equivalence_allowed"] is False
    assert summary["best_peak_solver_m"] > summary["step108_peak_solver_m"]
    assert summary["best_peak_solver_m"] > 1.0e-5
    assert REQUIRED_ROWS.issubset(by_name.keys())

    for row in rows:
        if not row["stable"]:
            continue
        assert row["completed_official_fsi_steps"] == 50
        assert row["completed_lbm_substeps"] == 6000
        assert row["flap_tip_timeseries_row_count"] == 51
        assert row["solver_curve_time_end_s"] == 0.025
        assert row["all_metrics_finite"] is True
        assert row["validation_claim_allowed"] is False
        assert row["direct_quantitative_equivalence_allowed"] is False
        assert row["has_nan"] is False
        assert row["has_inf"] is False
        assert finite_numeric_row(row)


def test_step109_reports_peak_ratio_and_best_candidate_artifacts():
    payload = read_json("outputs/step109_response_sensitivity_matrix/response_matrix_report.json")
    rows = payload["rows"]
    summary = payload["summary"]
    best = read_json("outputs/step109_response_sensitivity_matrix/best_candidate_error_report.json")
    curve = read_csv("outputs/step109_response_sensitivity_matrix/best_candidate_flap_tip_displacement_timeseries.csv")

    best_row = max((row for row in rows if row["stable"]), key=lambda row: row["peak_solver_m"])
    assert summary["best_candidate_row_name"] == best_row["row_name"]
    assert best["row"]["row_name"] == best_row["row_name"]
    assert best["row"]["peak_solver_m"] == best_row["peak_solver_m"]
    assert best_row["peak_reference_m"] > 3.0e-4
    assert best_row["peak_ratio"] > 0.0
    assert best_row["normalized_rms_error"] >= 0.0
    assert -1.0 <= best_row["shape_correlation"] <= 1.0
    assert len(curve) == 51
    assert math.isclose(float(curve[0]["time_s"]), 0.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(float(curve[-1]["time_s"]), 0.025, rel_tol=0.0, abs_tol=1.0e-15)


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
