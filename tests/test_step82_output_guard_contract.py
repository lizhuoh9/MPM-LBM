import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step82_output_guard_artifact_passes():
    payload = read_json("outputs/step82_output_guard/output_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["output_guard_pass"] is True
    assert summary["step82_required_driver_run_dir_count"] == 1
    assert summary["step82_optional_driver_run_dir_count"] == 0
    assert summary["step82_vtr_count"] == 0
    assert summary["step82_particle_npy_count"] == 0
    assert summary["step82_dense_wall_velocity_output_count"] == 0
    assert summary["step82_sparse_wall_velocity_output_count"] == 0
    assert summary["step82_raw_geometry_output_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def test_step82_artifact_manifest_passes():
    summary = read_json("outputs/step82_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert summary["step82_required_driver_run_dir_count"] == 1
    assert summary["step82_optional_driver_run_dir_count"] == 0
    assert summary["step82_vtr_count"] == 0
    assert summary["step82_particle_npy_count"] == 0
    assert summary["large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_taichi_lbm3d_step82_file_count"] == 0
    assert summary["protected_real_geometry_candidates_step82_file_count"] == 0
    assert summary["raw_geometry_file_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
