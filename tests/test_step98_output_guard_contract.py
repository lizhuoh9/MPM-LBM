import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step98_output_guard_passes():
    payload = read_json("outputs/step98_output_guard/output_guard.json")
    summary = payload["summary"]

    assert summary["output_guard_pass"] is True
    assert summary["step98_required_driver_run_dir_count"] == 1
    assert summary["step98_optional_driver_run_dir_count"] == 0
    assert summary["step98_ggui_screenshot_count"] == 1
    assert summary["step98_ggui_video_count"] == 0
    assert summary["step98_vtr_count"] == 0
    assert summary["step98_particle_npy_count"] == 0
    assert summary["step98_raw_geometry_output_count"] == 0
    assert summary["step98_real_geometry_candidate_output_count"] == 0
    assert summary["step98_dense_wall_velocity_output_count"] == 0
    assert summary["step98_sparse_wall_velocity_output_count"] == 0
    assert summary["step98_dense_displacement_output_count"] == 0
    assert summary["step98_displaced_particle_output_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_sim_edit_count"] == 0
    assert summary["protected_diagnostics_edit_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0
    assert summary["step98_large_file_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
