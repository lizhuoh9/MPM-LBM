import json
from pathlib import Path

from src.mpm_lbm.evidence.step69_code_placement_audit import build_step69_code_placement_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step69_code_placement_audit(ROOT)
    assert rows
    assert summary["code_placement_audit_pass"] is True
    assert summary["protected_step69_file_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step69_code_placement_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["code_placement_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
