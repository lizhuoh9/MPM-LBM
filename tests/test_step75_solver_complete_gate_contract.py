import json
from pathlib import Path

from src.mpm_lbm.evidence.solver_complete_gate_audit import build_step75_solver_complete_gate_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step75_solver_complete_gate_audit(ROOT)
    assert rows
    assert summary["solver_complete_gate_audit_pass"] is True
    assert summary["gate_status"] == "ready_for_step76_rebaseline_only"
    assert summary["post_gate_simulation_allowed"] is True
    assert summary["allowed_next_step"] == "Step76"
    assert summary["allowed_next_step_scope"] == "minimal safe rebaseline only"
    assert summary["activation_features_allowed_in_next_step"] == []
    assert summary["runtime_geometry_activation_allowed"] is False
    assert summary["wall_velocity_activation_allowed"] is False
    assert summary["real_geometry_activation_allowed"] is False
    assert summary["squid_proxy_activation_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["production_readiness_claim"] is False
    assert summary["physical_validation_claim"] is False


def test_artifact_passes():
    payload = read_json("outputs/step75_solver_complete_gate_audit/solver_complete_gate.json")
    assert payload["rows"]
    assert payload["summary"]["solver_complete_gate_audit_pass"] is True
    assert payload["summary"]["gate_status"] == "ready_for_step76_rebaseline_only"


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
