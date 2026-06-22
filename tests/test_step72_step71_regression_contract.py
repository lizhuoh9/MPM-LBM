import json
from pathlib import Path

from src.mpm_lbm.evidence.step72_regression_guard import build_step72_step71_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_goal_report_docs_exist():
    required = [
        "STEP72_RUNTIME_GEOMETRY_ACTIVATION_READINESS_AUDIT_GOAL.md",
        "STEP72_RUNTIME_GEOMETRY_ACTIVATION_READINESS_AUDIT_REPORT.md",
        "docs/72_runtime_geometry_activation_readiness_audit.md",
        "docs/RUNTIME_GEOMETRY_ACTIVATION_READINESS.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
    ]
    for path in required:
        assert (ROOT / path).is_file(), path


def test_build_passes():
    rows, summary = build_step72_step71_regression_guard(ROOT)
    assert rows
    assert summary["step72_step71_regression_guard_pass"] is True
    assert summary["current_fsidriver_default_write_vtk"] is False
    assert summary["current_fsidriver_default_write_particles"] is False


def test_artifact_passes():
    payload = read_json("outputs/step72_step71_regression_guard/step71_regression_guard.json")
    assert payload["rows"]
    assert payload["summary"]["step72_step71_regression_guard_pass"] is True
    manifest = read_json("outputs/step72_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert manifest["step72_vtr_count"] == 0
    assert manifest["step72_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
