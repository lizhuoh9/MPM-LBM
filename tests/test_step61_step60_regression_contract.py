import json
from pathlib import Path

from src.mpm_lbm.evidence.step61_regression_guard import build_step61_step60_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step61_step60_regression_guard_passes_current_artifacts():
    rows, summary = build_step61_step60_regression_guard(ROOT)
    assert summary["step60_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["step60_required_row_count"]) == 3
    assert int(summary["step60_legacy_driver_module_used_count"]) == 0
    assert summary["step60_missing_required_rows"] == []
    assert summary["step60_runtime_code_changed"] is False
    assert summary["step60_solver_behavior_changed"] is False
    assert summary["step60_physics_feature_expansion"] is False
    assert all(row["pass"] is True for row in rows)


def test_step61_step60_regression_guard_artifact_passes():
    payload = read_json("outputs/step61_step60_regression_guard/step60_regression_guard.json")
    summary = payload["summary"]
    assert summary["step60_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["step60_required_row_count"]) == 3
    assert int(summary["step60_legacy_driver_module_used_count"]) == 0
    assert summary["step60_missing_required_rows"] == []
    assert summary["step60_runtime_code_changed"] is False
    assert summary["step60_solver_behavior_changed"] is False
    assert summary["step60_physics_feature_expansion"] is False
    assert all(row["pass"] is True for row in payload["rows"])


def test_step61_preserves_step60_required_duration_ramp_artifacts():
    payload = read_json("outputs/step60_duration_ramp_matrix/duration_ramp_matrix.json")
    rows = {row["row_name"]: row for row in payload["rows"]}
    assert set(rows) == {
        "canonical_driver_moving_boundary_engineering_16_3step",
        "canonical_driver_moving_boundary_engineering_16_5step",
        "canonical_driver_penalty_16_5step",
    }
    assert all(row["driver_run_called"] is True for row in rows.values())
    assert all(row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver" for row in rows.values())
    assert all(row["legacy_driver_module_used_as_implementation"] is False for row in rows.values())


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
