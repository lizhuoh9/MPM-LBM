import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step94_output_guard_passes():
    payload = read_json("outputs/step94_output_guard/output_guard.json")
    summary = payload["summary"]

    assert summary["output_guard_pass"] is True
    assert summary["step94_required_driver_run_dir_count"] == 1
    assert summary["step94_optional_driver_run_dir_count"] == 0
    assert summary["step94_ggui_screenshot_count"] == 1
    assert summary["step94_ggui_video_count"] == 0
    assert summary["step94_vtr_count"] == 0
    assert summary["step94_particle_npy_count"] == 0
    assert summary["step94_raw_geometry_output_count"] == 0
    assert summary["step94_real_geometry_candidate_output_count"] == 0
    assert summary["step94_dense_wall_velocity_output_count"] == 0
    assert summary["step94_dense_displacement_output_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_sim_edit_count"] == 0
    assert summary["protected_diagnostics_edit_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
