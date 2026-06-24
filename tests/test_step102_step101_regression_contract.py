import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step102_step101_regression_guard_passes():
    payload = read_json("outputs/step102_step101_regression_guard/step101_regression_guard.json")
    summary = payload["summary"]

    assert summary["step102_step101_regression_guard_pass"] is True
    assert summary["step101_48cube_10step_taichi_ggui_visualization_plan_pass"] is True
    assert summary["step101_48cube_10step_taichi_ggui_visualization_guard_pass"] is True
    assert summary["step101_output_guard_pass"] is True
    assert summary["step101_artifact_budget_pass"] is True
    assert summary["step101_driver_run_dir_count"] == 0
    assert summary["step101_ggui_screenshot_count"] == 0
    assert summary["step101_vtr_count"] == 0
    assert summary["step101_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
