import json
from pathlib import Path

from src.mpm_lbm.evidence.step77_regression_guard import build_step77_step76_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step77_step76_regression_guard_passes():
    rows, summary = build_step77_step76_regression_guard(ROOT)
    assert rows
    assert summary["step77_step76_regression_guard_pass"] is True
    assert summary["artifact_check_count"] == 13
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]


def test_step77_step76_regression_artifact_passes():
    payload = read_json("outputs/step77_step76_regression_guard/step76_regression_guard.json")
    assert payload["rows"]
    assert payload["summary"]["step77_step76_regression_guard_pass"] is True
    assert payload["summary"]["artifact_pass_count"] == 13


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
