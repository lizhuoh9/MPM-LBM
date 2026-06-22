import json
from pathlib import Path

from src.mpm_lbm.evidence.real_geometry_api_audit import build_step74_real_geometry_api_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step74_real_geometry_api_audit(ROOT)
    assert rows
    assert summary["real_geometry_api_audit_pass"] is True
    assert summary["missing_symbol_count"] == 0
    assert summary["output_snapshot_unchanged"] is True
    assert summary["projection_smoke_imported_but_not_executed"] is True
    assert summary["solver_run"] is False


def test_artifact_passes():
    payload = read_json("outputs/step74_real_geometry_api_audit/real_geometry_api.json")
    assert payload["rows"]
    assert payload["summary"]["real_geometry_api_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
