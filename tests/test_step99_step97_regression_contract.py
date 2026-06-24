import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step99_step97_regression_guard_passes():
    payload = read_json("outputs/step99_step97_regression_guard/step97_regression_guard.json")
    summary = payload["summary"]

    assert summary["step99_step97_regression_guard_pass"] is True
    assert summary["step97_48cube_taichi_ggui_visualization_expansion_plan_pass"] is True
    assert summary["step97_48cube_taichi_ggui_visualization_expansion_guard_pass"] is True
    assert summary["step97_step96_regression_guard_pass"] is True
    assert summary["step97_step94_regression_guard_pass"] is True
    assert summary["step97_step92_regression_guard_pass"] is True
    assert summary["step97_output_guard_pass"] is True
    assert summary["step97_artifact_budget_pass"] is True
    assert summary["step97_activation_feature_count"] == 0
    assert summary["planned_step98_activation_feature_count"] == 5
    assert summary["step97_driver_run_dir_count"] == 0
    assert summary["step97_ggui_screenshot_count"] == 0
    assert summary["step97_ggui_video_count"] == 0
    assert summary["step97_vtr_count"] == 0
    assert summary["step97_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
