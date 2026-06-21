import json
from pathlib import Path

from src.mpm_lbm.evidence.simulation_freeze_audit import build_simulation_freeze_audit


ROOT = Path(__file__).resolve().parents[1]



def test_build_passes():
    rows, summary = build_simulation_freeze_audit(ROOT)
    assert rows
    assert summary["simulation_freeze_audit_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step63_simulation_freeze_audit/audit.json")
    assert payload["summary"]["simulation_freeze_audit_pass"] is True
    assert payload["rows"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
