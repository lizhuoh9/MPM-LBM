from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step111_error_comparison_uses_real_monitor_and_blocks_synthetic_success_claim():
    report = read_json(ROOT / "outputs" / "step111_error_comparison" / "error_report.json")
    summary = report["summary"]
    row = report["rows"][0]
    assert summary["step111_error_comparison_pass"] is False
    assert row["error_source"] == "real_solver_monitor_timeseries"
    assert row["solver_curve_loaded"] is True
    assert row["reference_loaded"] is True
    assert row["monitor_used"] == "nearest_public_monitor_point"
    assert row["monitor_equivalence"] is False
    assert row["sample_count"] == 51
    assert row["peak_solver_m"] > 1.0e-5
    assert row["normalized_rms_error"] >= 0.616126763475836
    assert row["shape_correlation"] <= 0.07866350821657236
    assert summary["normalized_rms_beats_step108"] is False
    assert summary["shape_correlation_beats_step108"] is False
    assert row["validation_claim_allowed"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
