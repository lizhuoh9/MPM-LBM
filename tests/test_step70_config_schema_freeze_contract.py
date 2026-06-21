import json
from pathlib import Path

from src.mpm_lbm.evidence.config_schema_freeze_audit import build_step70_config_schema_freeze_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step70_config_schema_freeze_audit(ROOT)
    assert rows
    assert summary["config_schema_freeze_audit_pass"] is True
    assert summary["missing_config_class_count"] == 0
    assert summary["schema_hash_count"] == summary["schema_row_count"]


def test_artifact_passes():
    payload = read_json("outputs/step70_config_schema_freeze_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["config_schema_freeze_audit_pass"] is True
    assert (ROOT / "outputs/step70_config_schema_freeze_audit/config_schema_freeze.json").is_file()
    assert (ROOT / "outputs/step70_config_schema_freeze_audit/config_schema_freeze.csv").is_file()


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
