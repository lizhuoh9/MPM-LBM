import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step80_step79_regression_guard_artifact_passes():
    payload = read_json("outputs/step80_step79_regression_guard/step79_regression_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step80_step79_regression_guard_pass"] is True
    assert summary["artifact_check_count"] == 10
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
