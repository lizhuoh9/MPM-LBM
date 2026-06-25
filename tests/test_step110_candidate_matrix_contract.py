import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step110_candidate_matrix_scores_by_error_not_peak():
    policy = read_json("configs/step110_candidate_matrix_policy.json")
    payload = read_json("outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.json")
    rows = payload["rows"]
    summary = payload["summary"]

    assert len(policy["candidate_rows"]) == 12
    for row_name in policy["candidate_rows"]:
        cfg = read_json(f"configs/step110_candidates/{row_name}.json")
        assert cfg["row_name"] == row_name
        assert cfg["validation_claim_allowed"] is False

    assert summary["candidate_matrix_pass"] is True
    assert summary["candidate_matrix_row_count"] >= 8
    assert summary["successful_candidate_rows"] >= 6
    assert summary["best_candidate_selected"] is True
    assert summary["validation_claim_allowed"] is False
    assert summary["direct_quantitative_equivalence_allowed"] is False

    best_by_score = min(rows, key=lambda row: float(row["composite_error_score"]))
    best_by_peak = max(rows, key=lambda row: abs(float(row["peak_solver_m"])))
    assert summary["best_candidate_row_name"] == best_by_score["row_name"]
    assert summary["best_candidate_row_name"] != best_by_peak["row_name"]


def test_step110_best_candidate_improves_rms_peak_time_and_correlation():
    summary = read_json("outputs/step110_error_minimized_candidate_matrix/candidate_matrix_report.json")["summary"]
    best_curve = read_csv("outputs/step110_error_minimized_candidate_matrix/best_candidate_monitor_timeseries.csv")

    assert summary["best_candidate_normalized_rms_error"] < 0.460371
    assert summary["best_candidate_peak_time_error_s"] < 0.021
    assert summary["best_candidate_peak_relative_error"] < 0.5
    assert summary["best_candidate_shape_correlation"] > 0.10
    assert len(best_curve) == 51
    assert float(best_curve[0]["time_s"]) == 0.0
    assert float(best_curve[-1]["time_s"]) == 0.025


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

