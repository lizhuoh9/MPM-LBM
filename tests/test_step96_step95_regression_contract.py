import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step96_step95_regression_guard_passes():
    payload = read_json("outputs/step96_step95_regression_guard/step95_regression_guard.json")
    summary = payload["summary"]

    assert summary["step96_step95_regression_guard_pass"] is True
    assert summary["step95_taichi_ggui_10step_visualization_plan_guard_matrix_pass"] is True
    assert summary["step95_taichi_ggui_10step_visualization_plan_guard_quality_pass"] is True
    assert summary["step95_activation_guard_pass"] is True
    assert summary["step95_output_guard_pass"] is True
    assert summary["step95_step94_regression_guard_pass"] is True
    assert summary["step95_step92_regression_guard_pass"] is True
    assert summary["step95_artifact_budget_pass"] is True
    assert summary["step95_activation_feature_count"] == 0
    assert summary["planned_step96_activation_feature_count"] == 4
    assert summary["step95_driver_run_dir_count"] == 0
    assert summary["step95_ggui_screenshot_count"] == 0
    assert summary["step95_ggui_video_count"] == 0
    assert summary["step95_vtr_count"] == 0
    assert summary["step95_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
