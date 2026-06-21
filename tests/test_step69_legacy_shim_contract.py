import json
from pathlib import Path

from src.mpm_lbm.evidence.step69_legacy_shim_audit import build_step69_legacy_shim_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step69_legacy_shim_audit(ROOT)
    assert len(rows) == 6
    assert summary["step69_legacy_shim_audit_pass"] is True
    assert summary["legacy_shim_count_for_six_support_rows"] == 6
    assert summary["legacy_implementation_body_count_for_six_support_rows"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step69_legacy_shim_audit/audit.json")
    assert len(payload["rows"]) == 6
    assert payload["summary"]["step69_legacy_shim_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
