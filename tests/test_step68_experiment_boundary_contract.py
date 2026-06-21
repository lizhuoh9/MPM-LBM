import json
from pathlib import Path

from src.mpm_lbm.evidence.experiment_boundary_audit import build_step68_experiment_boundary_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step68_experiment_boundary_audit(ROOT)
    assert rows
    assert summary["experiment_boundary_audit_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step68_experiment_boundary_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["experiment_boundary_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
