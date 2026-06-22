import json
from pathlib import Path

from src.mpm_lbm.evidence.step82_step81_regression_guard import build_step82_step81_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step82_step81_regression_guard_passes():
    rows, summary = build_step82_step81_regression_guard(ROOT)
    assert rows
    assert summary["step82_step81_regression_guard_pass"] is True
    assert summary["artifact_check_count"] == 10
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["step81_activation_feature_count"] == 0
    assert summary["planned_step82_activation_feature_count"] == 1
    assert summary["step81_driver_run_dir_count"] == 0
    assert summary["step81_vtr_count"] == 0
    assert summary["step81_particle_npy_count"] == 0


def test_step82_step81_regression_guard_artifact_passes():
    payload = read_json("outputs/step82_step81_regression_guard/step81_regression_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step82_step81_regression_guard_pass"] is True
    assert summary["artifact_check_count"] == 10
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
