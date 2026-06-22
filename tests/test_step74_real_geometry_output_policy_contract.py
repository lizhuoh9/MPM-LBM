import json
from pathlib import Path

from src.mpm_lbm.evidence.real_geometry_output_policy_audit import build_step74_real_geometry_output_policy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step74_real_geometry_output_policy_audit(ROOT)
    assert rows
    assert summary["real_geometry_output_policy_audit_pass"] is True
    assert summary["protected_real_geometry_candidate_edit_count"] == 0
    assert summary["external_taichi_lbm3d_edit_count"] == 0
    assert summary["raw_geometry_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["large_file_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step74_real_geometry_output_policy_audit/real_geometry_output_policy.json")
    assert payload["rows"]
    assert payload["summary"]["real_geometry_output_policy_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
