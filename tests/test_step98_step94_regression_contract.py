import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step98_step94_regression_guard_passes():
    payload = read_json("outputs/step98_step94_regression_guard/step94_regression_guard.json")
    summary = payload["summary"]

    assert summary["step98_step94_regression_guard_pass"] is True
    assert summary["step94_taichi_ggui_visualization_smoke_matrix_pass"] is True
    assert summary["step94_taichi_ggui_visualization_quality_pass"] is True
    assert summary["step94_activation_guard_pass"] is True
    assert summary["step94_output_guard_pass"] is True
    assert summary["step94_artifact_budget_pass"] is True
    assert summary["step94_activation_feature_count"] == 4
    assert summary["step94_completed_lbm_steps"] == 1
    assert summary["step94_ggui_screenshot_count"] == 1
    assert summary["step94_ggui_video_count"] == 0
    assert summary["step94_vtr_count"] == 0
    assert summary["step94_particle_npy_count"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
