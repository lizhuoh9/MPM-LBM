import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step110_curve_shape_diagnostics_reports_windows():
    payload = read_json("outputs/step110_curve_shape_diagnostics/curve_shape_diagnostics_report.json")
    rows = payload["rows"]
    summary = payload["summary"]

    assert summary["curve_shape_diagnostics_pass"] is True
    assert summary["diagnostic_row_count"] >= 8
    for row in rows:
        assert "early_window_rms_error_0_to_0p008" in row
        assert "mid_window_rms_error_0p008_to_0p017" in row
        assert "late_window_rms_error_0p017_to_0p025" in row
        assert row["validation_claim_allowed"] is False
        assert row["direct_quantitative_equivalence_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)

