import json
from pathlib import Path

from src.mpm_lbm.evidence.step69_regression_guard import build_step69_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step69_regression_guard(ROOT)
    assert rows
    assert summary["step69_step68_regression_guard_pass"] is True
    assert summary["step68_pass_count"] == summary["step68_required_artifact_count"]


def test_artifact_passes():
    payload = read_json("outputs/step69_step68_regression_guard/audit.json")
    assert payload["rows"]
    assert payload["summary"]["step69_step68_regression_guard_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
