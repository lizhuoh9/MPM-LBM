import json
from pathlib import Path

from src.mpm_lbm.evidence.public_api_surface_audit import build_step70_public_api_surface_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step70_public_api_surface_audit(ROOT)
    assert rows
    assert summary["public_api_surface_audit_pass"] is True
    assert summary["canonical_import_pass_count"] == summary["expected_count"]
    assert summary["solver_run"] is False
    assert summary["output_snapshot_unchanged"] is True


def test_artifact_passes():
    payload = read_json("outputs/step70_public_api_surface_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["public_api_surface_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
