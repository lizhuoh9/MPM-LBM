import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step103_step100_regression_guard_passes():
    payload = read_json("outputs/step103_step100_regression_guard/step100_regression_guard.json")
    summary = payload["summary"]

    assert summary["step103_step100_regression_guard_pass"] is True
    assert summary["step100_48cube_5step_taichi_ggui_visualization_run_matrix_pass"] is True
    assert summary["step100_activation_guard_pass"] is True
    assert summary["step100_output_guard_pass"] is True
    assert summary["step100_artifact_budget_pass"] is True
    assert summary["step100_completed_lbm_steps"] == 5
    assert summary["step100_grid_48_enabled_count"] == 1
    assert summary["step100_ggui_screenshot_count"] == 1
    assert summary["step100_vtr_count"] == 0
    assert summary["step100_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
