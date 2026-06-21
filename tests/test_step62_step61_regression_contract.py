import json
from pathlib import Path

from src.mpm_lbm.evidence.step62_regression_guard import build_step62_step61_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step62_step61_regression_guard_passes_current_artifacts():
    rows, summary = build_step62_step61_regression_guard(ROOT)
    assert summary["step61_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert summary["step61_missing_required_rows"] == []
    assert int(summary["step61_optional_row_count"]) == 0
    assert int(summary["step61_legacy_driver_module_used_count"]) == 0
    assert summary["step61_runtime_code_changed"] is False
    assert summary["step61_solver_behavior_changed"] is False
    assert summary["step61_physics_feature_expansion"] is False
    assert summary["step61_report_consistency_issue_fixed"] is True
    assert all(row["pass"] is True for row in rows)


def test_step62_step61_regression_artifact_passes():
    payload = read_json("outputs/step62_step61_regression_guard/step61_regression_guard.json")
    summary = payload["summary"]
    assert summary["step61_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert summary["step61_report_consistency_issue_fixed"] is True
    assert all(row["pass"] is True for row in payload["rows"])


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
