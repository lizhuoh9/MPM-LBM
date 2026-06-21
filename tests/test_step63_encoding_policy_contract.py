import json
from pathlib import Path

from src.mpm_lbm.evidence.encoding_policy_audit import build_encoding_policy_audit


ROOT = Path(__file__).resolve().parents[1]



def test_build_passes():
    rows, summary = build_encoding_policy_audit(ROOT)
    assert rows
    assert summary["encoding_policy_audit_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step63_encoding_policy_audit/audit.json")
    assert payload["summary"]["encoding_policy_audit_pass"] is True
    assert payload["rows"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
