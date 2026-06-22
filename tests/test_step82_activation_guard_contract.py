import json
from pathlib import Path

from src.mpm_lbm.evidence.step82_wall_velocity_solid_vel_activation_guard import (
    build_step82_wall_velocity_solid_vel_activation_guard,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step82_activation_guard_passes():
    rows, summary = build_step82_wall_velocity_solid_vel_activation_guard(ROOT)
    assert rows
    assert summary["step82_activation_guard_pass"] is True
    assert summary["pass_count"] == summary["row_count"]
    assert summary["activation_feature_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 0
    assert summary["planned_step82_activation_feature_count"] == 1


def test_step82_activation_guard_artifact_passes():
    payload = read_json("outputs/step82_activation_guard/activation_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step82_activation_guard_pass"] is True
    assert summary["pass_count"] == summary["row_count"]
    assert summary["activation_feature_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 0


def test_step82_guard_sources_do_not_run_driver():
    checked_paths = [
        "baseline_tests/step82_common.py",
        "baseline_tests/run_step82_wall_velocity_solid_vel_quality.py",
        "baseline_tests/run_step82_activation_guard.py",
        "baseline_tests/run_step82_step81_regression_guard.py",
        "baseline_tests/run_step82_output_guard.py",
        "baseline_tests/run_step82_artifact_manifest.py",
        "src/mpm_lbm/evidence/step82_wall_velocity_solid_vel_quality_audit.py",
        "src/mpm_lbm/evidence/step82_wall_velocity_solid_vel_activation_guard.py",
        "src/mpm_lbm/evidence/step82_step81_regression_guard.py",
        "src/mpm_lbm/evidence/step82_output_guard.py",
    ]
    forbidden_tokens = ["FSIDriver3D", "driver.run(", "ti.init(", "taichi.init("]
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
