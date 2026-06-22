import json
from pathlib import Path

from src.mpm_lbm.evidence.step74_regression_guard import build_step74_step73_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_goal_report_docs_exist():
    required = [
        "STEP74_REAL_GEOMETRY_DATA_BOUNDARY_AUDIT_GOAL.md",
        "STEP74_REAL_GEOMETRY_DATA_BOUNDARY_AUDIT_REPORT.md",
        "docs/74_real_geometry_data_boundary_audit.md",
        "docs/REAL_GEOMETRY_DATA_BOUNDARY.md",
        "docs/REAL_GEOMETRY_CANDIDATE_POLICY.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
    ]
    for path in required:
        assert (ROOT / path).is_file(), path


def test_build_passes():
    rows, summary = build_step74_step73_regression_guard(ROOT)
    assert rows
    assert summary["step74_step73_regression_guard_pass"] is True
    assert summary["step73_artifact_pass_count"] == summary["step73_artifact_check_count"]
    assert summary["closed_gate_pass_count"] == summary["required_closed_gate_count"]


def test_artifact_passes():
    payload = read_json("outputs/step74_step73_regression_guard/step73_regression_guard.json")
    assert payload["rows"]
    assert payload["summary"]["step74_step73_regression_guard_pass"] is True
    manifest = read_json("outputs/step74_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert manifest["step74_vtr_count"] == 0
    assert manifest["step74_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
