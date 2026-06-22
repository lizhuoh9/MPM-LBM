import json
from pathlib import Path

from src.mpm_lbm.evidence.post_gate_5step_activation_guard import build_step78_post_gate_5step_activation_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step78_activation_guard_passes():
    rows, summary = build_step78_post_gate_5step_activation_guard(ROOT)
    assert rows
    assert summary["post_gate_5step_activation_guard_pass"] is True
    assert summary["activation_feature_count"] == 0
    assert summary["previous_activation_feature_count"] == 0
    assert summary["optional_row_count"] == 0


def test_step78_activation_guard_artifact_passes():
    payload = read_json("outputs/step78_activation_guard/activation_guard.json")
    assert payload["rows"]
    assert payload["summary"]["post_gate_5step_activation_guard_pass"] is True
    assert payload["summary"]["activation_feature_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
