import json
from pathlib import Path

from src.mpm_lbm.evidence.post_gate_output_guard import build_step76_post_gate_output_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step76_output_guard_passes():
    rows, summary = build_step76_post_gate_output_guard(ROOT)
    assert rows
    assert summary["output_guard_pass"] is True
    assert summary["step76_required_driver_run_dir_count"] == 1
    assert summary["step76_optional_driver_run_dir_count"] == 0
    assert summary["step76_vtr_count"] == 0
    assert summary["step76_particle_npy_count"] == 0
    assert summary["step76_large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def test_step76_output_guard_artifact_passes():
    payload = read_json("outputs/step76_output_guard/output_guard.json")
    assert payload["rows"]
    assert payload["summary"]["output_guard_pass"] is True
    assert payload["summary"]["step76_total_size_mb"] < 20.0


def test_step76_artifact_manifest_passes():
    summary = read_json("outputs/step76_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert summary["step76_required_driver_run_dir_count"] == 1
    assert summary["step76_optional_driver_run_dir_count"] == 0
    assert summary["step76_vtr_count"] == 0
    assert summary["step76_particle_npy_count"] == 0
    assert summary["large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
