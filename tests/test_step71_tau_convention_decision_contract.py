import json
from pathlib import Path

from src.mpm_lbm.evidence.tau_convention_decision_audit import build_step71_tau_convention_decision_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step71_tau_convention_decision_audit(ROOT)
    assert rows
    assert summary["tau_convention_decision_audit_pass"] is True
    assert summary["tau_convention_decision"] == "preserve_legacy_external_solver_parameter_for_now"
    assert summary["default_solver_tau_formula"] == "tau_from_legacy_external_solver_parameter"
    assert summary["legacy_tau_for_0_1"] == 0.5333333333333333
    assert summary["standard_tau_for_0_1"] == 0.8
    assert summary["standard_lattice_viscosity_is_default"] is False
    assert summary["physical_viscosity_validation_claim"] is False


def test_artifact_passes():
    payload = read_json("outputs/step71_tau_convention_decision_audit/tau_convention_decision.json")
    assert payload["rows"]
    assert payload["summary"]["tau_convention_decision_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
