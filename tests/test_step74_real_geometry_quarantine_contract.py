import json
from pathlib import Path

from src.mpm_lbm.evidence.real_geometry_quarantine_audit import build_step74_real_geometry_quarantine_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step74_real_geometry_quarantine_audit(ROOT)
    assert rows
    assert summary["real_geometry_quarantine_audit_pass"] is True
    assert summary["quarantined_experiment_path_exists"] is True
    assert summary["under_sim_package"] is False
    assert summary["driver_helper_detected"] is True
    assert summary["driver_helper_executed"] is False
    assert summary["solver_run"] is False


def test_artifact_passes():
    payload = read_json("outputs/step74_real_geometry_quarantine_audit/real_geometry_quarantine.json")
    assert payload["rows"]
    assert payload["summary"]["real_geometry_quarantine_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
