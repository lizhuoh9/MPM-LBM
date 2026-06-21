import json
from pathlib import Path

from src.mpm_lbm.evidence.current_root_inventory_audit import build_step69_current_root_inventory_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step69_current_root_inventory_audit(ROOT)
    assert rows
    assert summary["current_root_inventory_audit_pass"] is True
    assert summary["current_step_specific_proxy_remaining_count"] == 0
    assert summary["current_root_step_specific_implementation_count"] == 0
    assert summary["current_unknown_requires_review_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step69_current_root_inventory_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["current_root_inventory_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
