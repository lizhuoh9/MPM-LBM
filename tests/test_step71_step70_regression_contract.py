import json
from pathlib import Path

from src.mpm_lbm.evidence.step71_regression_guard import build_step71_step70_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_goal_report_docs_exist():
    required = [
        "STEP71_OUTPUT_DEFAULT_SAFETY_ALIGNMENT_AND_TAU_CONVENTION_GOAL.md",
        "STEP71_OUTPUT_DEFAULT_SAFETY_ALIGNMENT_AND_TAU_CONVENTION_REPORT.md",
        "docs/71_output_default_safety_alignment_and_tau_convention.md",
        "docs/OUTPUT_DEFAULT_SAFETY_POLICY.md",
        "docs/LBM_TAU_CONVENTION_DECISION.md",
        "docs/LBM_RELAXATION_SEMANTICS.md",
        "docs/CONFIG_SCHEMA_FREEZE.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
    ]
    for path in required:
        assert (ROOT / path).is_file(), path


def test_build_passes():
    rows, summary = build_step71_step70_regression_guard(ROOT)
    assert rows
    assert summary["step71_step70_regression_guard_pass"] is True
    assert summary["schema_freeze_superseded_by_step71_delta"] is True


def test_artifact_passes():
    payload = read_json("outputs/step71_step70_regression_guard/step70_regression_guard.json")
    assert payload["rows"]
    assert payload["summary"]["step71_step70_regression_guard_pass"] is True
    manifest = read_json("outputs/step71_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert manifest["step71_vtr_count"] == 0
    assert manifest["step71_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
