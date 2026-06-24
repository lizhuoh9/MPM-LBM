import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step95_step93_regression_guard_passes():
    payload = read_json("outputs/step95_step93_regression_guard/step93_regression_guard.json")
    summary = payload["summary"]

    assert summary["step95_step93_regression_guard_pass"] is True
    assert summary["step93_taichi_ggui_visualization_enablement_plan_pass"] is True
    assert summary["step93_taichi_ggui_visualization_enablement_guard_pass"] is True
    assert summary["step93_step92_regression_guard_pass"] is True
    assert summary["step93_step91_regression_guard_pass"] is True
    assert summary["step93_step90_regression_guard_pass"] is True
    assert summary["step93_output_guard_pass"] is True
    assert summary["step93_artifact_budget_pass"] is True
    assert summary["step93_activation_feature_count"] == 0
    assert summary["planned_step94_activation_feature_count"] == 4
    assert summary["step93_driver_run_dir_count"] == 0
    assert summary["step93_ggui_screenshot_count"] == 0
    assert summary["step93_particle_npy_count"] == 0
    assert summary["vtr_file_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
