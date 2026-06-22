import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step84_output_guard_passes():
    payload = read_json("outputs/step84_output_guard/output_guard.json")
    summary = payload["summary"]

    assert payload["rows"]
    assert summary["output_guard_pass"] is True
    assert summary["step84_required_driver_run_dir_count"] == 1
    assert summary["step84_optional_driver_run_dir_count"] == 0
    assert summary["step84_vtr_count"] == 0
    assert summary["step84_particle_npy_count"] == 0
    assert summary["step84_dense_wall_velocity_output_count"] == 0
    assert summary["step84_sparse_wall_velocity_output_count"] == 0
    assert summary["step84_dense_displacement_output_count"] == 0
    assert summary["step84_displaced_particle_output_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def test_step84_artifact_manifest_passes():
    summary = read_json("outputs/step84_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert summary["step84_required_driver_run_dir_count"] == 1
    assert summary["step84_optional_driver_run_dir_count"] == 0
    assert summary["step84_vtr_count"] == 0
    assert summary["step84_particle_npy_count"] == 0
    assert summary["large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_taichi_lbm3d_step84_file_count"] == 0
    assert summary["protected_real_geometry_candidates_step84_file_count"] == 0
    assert summary["raw_geometry_file_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
