import json
from pathlib import Path

from src.mpm_lbm.evidence.runtime_geometry_output_policy_audit import build_step72_runtime_geometry_output_policy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step72_runtime_geometry_output_policy_audit(ROOT)
    assert rows
    assert summary["runtime_geometry_output_policy_audit_pass"] is True
    assert summary["json_controlled_true_count"] == 0
    assert summary["step72_vtr_count"] == 0
    assert summary["step72_particle_npy_count"] == 0
    assert summary["protected_step72_file_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step72_runtime_geometry_output_policy_audit/runtime_geometry_output_policy.json")
    assert payload["rows"]
    assert payload["summary"]["runtime_geometry_output_policy_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
