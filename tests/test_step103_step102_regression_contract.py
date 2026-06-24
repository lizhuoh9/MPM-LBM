import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step103_step102_regression_guard_passes():
    payload = read_json("outputs/step103_step102_regression_guard/step102_regression_guard.json")
    summary = payload["summary"]

    assert summary["step103_step102_regression_guard_pass"] is True
    assert summary["step102_fluent_official_2way_fsi_benchmark_intake_pass"] is True
    assert summary["step102_output_guard_pass"] is True
    assert summary["step102_artifact_budget_pass"] is True
    assert summary["step102_driver_run_dir_count"] == 0
    assert summary["step102_validation_claim_allowed"] is False
    assert summary["step102_benchmark_comparison_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
