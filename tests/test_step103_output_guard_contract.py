import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step103_output_guard_passes():
    payload = read_json("outputs/step103_output_guard/output_guard.json")
    summary = payload["summary"]

    assert summary["output_guard_pass"] is True
    assert summary["step103_required_driver_run_dir_count"] == 1
    assert summary["step103_ggui_screenshot_count"] == 1
    assert summary["step103_ggui_video_count"] == 0
    assert summary["step103_vtr_count"] == 0
    assert summary["step103_particle_npy_count"] == 0
    assert summary["step103_ansys_proprietary_file_count"] == 0
    assert summary["step103_fluent_run_output_count"] == 0
    assert summary["step103_large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
