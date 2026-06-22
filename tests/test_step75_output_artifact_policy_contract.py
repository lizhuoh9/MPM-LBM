import json
from pathlib import Path

from src.mpm_lbm.evidence.step75_output_artifact_policy_audit import build_step75_output_artifact_policy_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step75_output_artifact_policy_audit(ROOT)
    assert rows
    assert summary["output_artifact_policy_audit_pass"] is True
    assert summary["large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0
    assert summary["report_missing_count"] == 0
    assert summary["step75_driver_run_output_dir_count"] == 0
    assert summary["step75_vtr_count"] == 0
    assert summary["step75_particle_npy_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step75_output_artifact_policy_audit/output_artifact_policy.json")
    assert payload["rows"]
    assert payload["summary"]["output_artifact_policy_audit_pass"] is True
    assert payload["summary"]["report_missing_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
