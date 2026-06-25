from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_csv_rows, read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step112_candidate_matrix_uses_real_solver_only():
    report = read_json(ROOT / "outputs" / "step112_real_candidate_matrix" / "candidate_matrix_report.json")
    summary = report["summary"]
    rows = report["rows"]
    assert summary["candidate_matrix_row_count"] >= 10
    assert summary["successful_real_rows"] >= 8
    assert summary["all_candidate_curves_real_solver"] is True
    assert summary["synthetic_candidate_curve_count"] == 0
    assert summary["proxy_curve_replay_evidence_mode_count"] == 0
    assert summary["solver_curve_generated_from_reference_count"] == 0
    assert all(row["evidence_mode"] == "real_solver_particles" for row in rows)
    assert all(row["driver_run_called"] for row in rows if row["stable"])
    assert all(row["restart_loaded"] for row in rows if row["stable"])
    assert all(row["monitor_source"] == "real_solver_particles" for row in rows if row["stable"])


def test_step112_best_real_candidate_beats_step111_or_records_failure():
    report = read_json(ROOT / "outputs" / "step112_real_candidate_matrix" / "candidate_matrix_report.json")
    summary = report["summary"]
    best = report["rows"][0]
    assert best["row_name"] == summary["best_candidate_row_name"]
    assert best["normalized_rms_error"] < 0.7131889376595728
    assert best["peak_relative_error"] < 1.0202873032239297
    assert best["peak_time_error_s"] <= 0.021
    assert summary["hard_gate_pass"] == (
        best["normalized_rms_error"] < 0.616126763475836
        and best["peak_relative_error"] < 0.75
        and best["shape_correlation"] > 0.10
        and best["peak_time_error_s"] <= 0.021
    )
    assert summary["validation_claim_allowed"] is False
    assert summary["direct_quantitative_equivalence_allowed"] is False


def test_step112_candidate_curves_have_real_rows():
    report = read_json(ROOT / "outputs" / "step112_real_candidate_matrix" / "candidate_matrix_report.json")
    best_name = report["summary"]["best_candidate_row_name"]
    rows = read_csv_rows(ROOT / "outputs" / "step112_real_candidate_matrix" / "curves" / f"{best_name}_nearest_public_monitor_point.csv")
    assert len(rows) == 51
    assert float(rows[0]["time_s"]) == 0.0
    assert float(rows[-1]["time_s"]) == 0.025
