import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step93_output_guard_passes():
    payload = read_json("outputs/step93_output_guard/output_guard.json")
    summary = payload["summary"]

    assert summary["output_guard_pass"] is True
    assert summary["step93_driver_run_dir_count"] == 0
    assert summary["vtr_file_count"] == 0
    assert summary["step93_particle_npy_count"] == 0
    assert summary["step93_ggui_screenshot_count"] == 0
    assert summary["step93_raw_geometry_output_count"] == 0
    assert summary["step93_real_geometry_candidate_output_count"] == 0
    assert summary["step93_dense_wall_velocity_output_count"] == 0
    assert summary["step93_sparse_wall_velocity_output_count"] == 0
    assert summary["step93_dense_displacement_output_count"] == 0
    assert summary["step93_displaced_particle_output_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_sim_edit_count"] == 0
    assert summary["protected_diagnostics_edit_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0
    assert summary["step93_large_file_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
