import json
from pathlib import Path

from src.mpm_lbm.evidence.wall_velocity_output_policy_audit import build_step73_wall_velocity_output_policy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step73_wall_velocity_output_policy_audit(ROOT)
    assert rows
    assert summary["wall_velocity_output_policy_audit_pass"] is True
    assert summary["json_controlled_true_count"] == 0
    assert summary["step73_vtr_count"] == 0
    assert summary["step73_particle_npy_count"] == 0
    assert summary["step73_dense_wall_velocity_count"] == 0
    assert summary["step73_sparse_wall_velocity_count"] == 0
    assert summary["protected_step73_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step73_wall_velocity_output_policy_audit/wall_velocity_output_policy.json")
    assert payload["rows"]
    assert payload["summary"]["wall_velocity_output_policy_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
