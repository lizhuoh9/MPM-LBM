import json
from pathlib import Path

from src.mpm_lbm.evidence.wall_velocity_api_audit import build_step73_wall_velocity_api_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step73_wall_velocity_api_audit(ROOT)
    assert rows
    assert summary["wall_velocity_api_audit_pass"] is True
    assert summary["missing_symbol_count"] == 0
    assert summary["output_snapshot_unchanged"] is True
    assert summary["solver_run"] is False


def test_artifact_passes():
    payload = read_json("outputs/step73_wall_velocity_api_audit/wall_velocity_api.json")
    assert payload["rows"]
    assert payload["summary"]["wall_velocity_api_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
