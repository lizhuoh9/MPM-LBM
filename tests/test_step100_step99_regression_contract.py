import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step100_step99_regression_guard_passes():
    payload = read_json("outputs/step100_step99_regression_guard/step99_regression_guard.json")
    summary = payload["summary"]

    assert summary["step100_step99_regression_guard_pass"] is True
    assert summary["step99_48cube_5step_taichi_ggui_visualization_plan_pass"] is True
    assert summary["step99_48cube_5step_taichi_ggui_visualization_guard_pass"] is True
    assert summary["step99_step98_regression_guard_pass"] is True
    assert summary["step99_step97_regression_guard_pass"] is True
    assert summary["step99_step96_regression_guard_pass"] is True
    assert summary["step99_output_guard_pass"] is True
    assert summary["step99_artifact_budget_pass"] is True
    assert summary["step99_activation_feature_count"] == 0
    assert summary["planned_step100_activation_feature_count"] == 5
    assert summary["step99_driver_run_dir_count"] == 0
    assert summary["step99_ggui_screenshot_count"] == 0
    assert summary["step99_ggui_video_count"] == 0
    assert summary["step99_vtr_count"] == 0
    assert summary["step99_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
