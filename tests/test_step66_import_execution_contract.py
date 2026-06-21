import json
from pathlib import Path

from src.mpm_lbm.evidence.batch_import_execution_audit import build_batch_import_execution_audit


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "configs/step66_diagnostic_geometry_displacement_migration_policy.json"


def test_build_passes():
    rows, summary = build_batch_import_execution_audit(ROOT, POLICY_PATH)
    assert rows
    assert summary["batch_import_execution_audit_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step66_import_execution_audit/audit.json")
    assert payload["summary"]["step66_import_execution_pass"] is True
    assert payload["rows"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
