import json
from pathlib import Path

from src.mpm_lbm.evidence.step_specific_proxy_import_execution_audit import build_step68_import_execution_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step68_import_execution_audit(ROOT)
    assert rows
    assert summary["step68_import_execution_audit_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step68_import_execution_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["step68_import_execution_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
