import json
from pathlib import Path

from src.mpm_lbm.evidence.wall_velocity_readiness_audit import build_step73_wall_velocity_readiness_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step73_wall_velocity_readiness_audit(ROOT)
    assert rows
    assert summary["wall_velocity_readiness_audit_pass"] is True
    assert summary["required_audit_pass_count"] == summary["required_audit_count"]
    assert summary["activation_allowed_after_step73"] is False


def test_artifact_passes():
    payload = read_json("outputs/step73_wall_velocity_readiness_audit/wall_velocity_readiness.json")
    assert payload["rows"]
    assert payload["summary"]["wall_velocity_readiness_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
