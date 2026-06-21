import json
from pathlib import Path

from src.mpm_lbm.evidence.report_consistency_freeze_audit import build_step70_report_consistency_audit


ROOT = Path(__file__).resolve().parents[1]


def test_goal_report_docs_exist():
    required = [
        "STEP70_API_CONFIG_FREEZE_BEFORE_ACTIVATION_GOAL.md",
        "STEP70_API_CONFIG_FREEZE_BEFORE_ACTIVATION_REPORT.md",
        "docs/70_api_config_freeze_before_activation.md",
        "docs/PUBLIC_API_SURFACE.md",
        "docs/CONFIG_SCHEMA_FREEZE.md",
        "docs/COMPATIBILITY_AND_DEPRECATION_POLICY.md",
        "docs/ACTIVATION_PRECONDITIONS.md",
    ]
    for path in required:
        assert (ROOT / path).is_file(), path


def test_build_passes():
    rows, summary = build_step70_report_consistency_audit(ROOT)
    assert rows
    assert summary["report_consistency_freeze_audit_pass"] is True
    assert summary["step69_report_consistency_fixed"] is True
    assert summary["fail_count"] == 0
    assert summary["deferred_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step70_report_consistency_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["report_consistency_freeze_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
