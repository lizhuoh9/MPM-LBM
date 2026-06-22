import json
from pathlib import Path

from src.mpm_lbm.evidence.wall_velocity_application_safety_audit import build_step73_wall_velocity_application_safety_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step73_wall_velocity_application_safety_audit(ROOT)
    assert rows
    assert summary["wall_velocity_application_safety_audit_pass"] is True
    assert summary["lbm_population_update_allowed"] is False
    assert summary["mpm_update_allowed"] is False
    assert summary["projector_update_allowed"] is False
    assert summary["bounceback_formula_modification_allowed"] is False
    assert summary["jet_model_allowed"] is False
    assert summary["actuation_claim_allowed"] is False


def test_artifact_passes():
    payload = read_json("outputs/step73_wall_velocity_application_safety_audit/wall_velocity_application_safety.json")
    assert payload["rows"]
    assert payload["summary"]["wall_velocity_application_safety_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
