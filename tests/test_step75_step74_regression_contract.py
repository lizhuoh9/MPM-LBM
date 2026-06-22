import json
from pathlib import Path

from src.mpm_lbm.evidence.step75_regression_guard import build_step75_step74_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step75_step74_regression_guard(ROOT)
    assert rows
    assert summary["step75_step74_regression_guard_pass"] is True
    assert summary["step74_artifact_check_count"] == 10
    assert summary["step74_artifact_pass_count"] == summary["step74_artifact_check_count"]
    assert summary["closed_gate_pass_count"] == summary["required_closed_gate_count"]


def test_artifact_passes():
    payload = read_json("outputs/step75_step74_regression_guard/step74_regression_guard.json")
    assert payload["rows"]
    assert payload["summary"]["step75_step74_regression_guard_pass"] is True
    assert payload["summary"]["step74_artifact_pass_count"] == 10


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
