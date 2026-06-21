import json
from pathlib import Path

from src.mpm_lbm.evidence.remaining_solver_inventory_audit import build_remaining_solver_inventory_audit


ROOT = Path(__file__).resolve().parents[1]



def test_build_passes():
    rows, summary = build_remaining_solver_inventory_audit(ROOT)
    assert rows
    assert summary["remaining_solver_inventory_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step63_remaining_solver_inventory_audit/audit.json")
    assert payload["summary"]["remaining_solver_inventory_pass"] is True
    assert payload["rows"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
