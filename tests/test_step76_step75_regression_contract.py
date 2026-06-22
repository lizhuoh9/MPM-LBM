import json
from pathlib import Path

from src.mpm_lbm.evidence.step76_regression_guard import build_step76_step75_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step76_step75_regression_guard_passes():
    rows, summary = build_step76_step75_regression_guard(ROOT)
    assert rows
    assert summary["step76_step75_regression_guard_pass"] is True
    assert summary["artifact_check_count"] == 8
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["gate_pass_count"] == summary["gate_check_count"]


def test_step76_step75_regression_artifact_passes():
    payload = read_json("outputs/step76_step75_regression_guard/step75_regression_guard.json")
    assert payload["rows"]
    assert payload["summary"]["step76_step75_regression_guard_pass"] is True
    assert payload["summary"]["artifact_pass_count"] == 8


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
