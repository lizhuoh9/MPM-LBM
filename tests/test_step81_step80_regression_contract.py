import json
from pathlib import Path

from src.mpm_lbm.evidence.step81_step80_regression_guard import build_step81_step80_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step81_step80_regression_guard_passes():
    rows, summary = build_step81_step80_regression_guard(ROOT)
    assert rows
    assert summary["step81_step80_regression_guard_pass"] is True
    assert summary["artifact_check_count"] == 15
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]
    assert summary["step80_activation_feature_count"] == 1
    assert summary["step80_runtime_geometry_enabled_count"] == 1
    assert summary["step80_wall_velocity_enabled_count"] == 0
    assert summary["step80_real_geometry_enabled_count"] == 0
    assert summary["step80_squid_proxy_enabled_count"] == 0
    assert summary["step80_link_area_enabled_count"] == 0
    assert summary["step80_vtr_count"] == 0
    assert summary["step80_particle_npy_count"] == 0


def test_step81_step80_regression_guard_artifact_passes():
    payload = read_json("outputs/step81_step80_regression_guard/step80_regression_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step81_step80_regression_guard_pass"] is True
    assert summary["artifact_check_count"] == 15
    assert summary["artifact_pass_count"] == summary["artifact_check_count"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
