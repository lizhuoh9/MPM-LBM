import json
from pathlib import Path

from src.mpm_lbm.evidence.wall_velocity_config_schema_audit import build_step73_wall_velocity_config_schema_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step73_wall_velocity_config_schema_audit(ROOT)
    assert rows
    assert summary["wall_velocity_config_schema_audit_pass"] is True
    assert summary["schema_hash_matches_step70_count"] == summary["required_schema_hash_count"]
    assert summary["unsafe_execution_flag_count"] == 0
    assert summary["unsafe_application_flag_count"] == 0
    assert summary["missing_required_field_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step73_wall_velocity_config_schema_audit/wall_velocity_config_schema.json")
    assert payload["rows"]
    assert payload["summary"]["wall_velocity_config_schema_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
