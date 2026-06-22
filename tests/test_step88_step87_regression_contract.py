import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step88_step87_regression_guard_passes():
    payload = read_json("outputs/step88_step87_regression_guard/step87_regression_guard.json")
    summary = payload["summary"]

    assert summary["step88_step87_regression_guard_pass"] is True
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["step87_activation_feature_count"] == 0
    assert summary["planned_step88_activation_feature_count"] == 3
    assert summary["step87_driver_run_dir_count"] == 0
    assert summary["step87_particle_npy_count"] == 0
    assert summary["step87_vtr_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
