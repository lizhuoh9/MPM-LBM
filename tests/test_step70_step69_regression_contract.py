import json
from pathlib import Path

from src.mpm_lbm.evidence.step70_regression_guard import build_step70_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step70_regression_guard(ROOT)
    assert rows
    assert summary["step70_step69_regression_guard_pass"] is True
    assert summary["step69_pass_count"] == summary["step69_required_check_count"]
    assert summary["missing_artifact_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step70_step69_regression_guard/audit.json")
    assert payload["rows"]
    assert payload["summary"]["step70_step69_regression_guard_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
