import json
from pathlib import Path

from src.mpm_lbm.evidence.step73_regression_guard import build_step73_step72_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_goal_report_docs_exist():
    required = [
        "STEP73_WALL_VELOCITY_ACTIVATION_READINESS_AUDIT_GOAL.md",
        "STEP73_WALL_VELOCITY_ACTIVATION_READINESS_AUDIT_REPORT.md",
        "docs/73_wall_velocity_activation_readiness_audit.md",
        "docs/WALL_VELOCITY_ACTIVATION_READINESS.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
    ]
    for path in required:
        assert (ROOT / path).is_file(), path


def test_build_passes():
    rows, summary = build_step73_step72_regression_guard(ROOT)
    assert rows
    assert summary["step73_step72_regression_guard_pass"] is True
    assert summary["step72_artifact_pass_count"] == summary["step72_artifact_check_count"]
    assert summary["closed_gate_pass_count"] == summary["required_closed_gate_count"]


def test_artifact_passes():
    payload = read_json("outputs/step73_step72_regression_guard/step72_regression_guard.json")
    assert payload["rows"]
    assert payload["summary"]["step73_step72_regression_guard_pass"] is True
    manifest = read_json("outputs/step73_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert manifest["step73_vtr_count"] == 0
    assert manifest["step73_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
