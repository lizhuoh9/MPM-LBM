import json
from pathlib import Path

from src.mpm_lbm.evidence.src_init_export_refresh_audit import build_step69_src_init_export_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step69_src_init_export_audit(ROOT)
    assert rows
    assert summary["src_init_export_audit_pass"] is True
    assert summary["no_stale_export_count"] == 0
    assert summary["heavy_import_during_src_import"] is False


def test_artifact_passes():
    payload = read_json("outputs/step69_src_init_export_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["src_init_export_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
