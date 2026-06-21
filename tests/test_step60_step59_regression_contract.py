import json
from pathlib import Path

from src.mpm_lbm.evidence.step60_regression_guard import build_step60_step59_regression_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step60_step59_regression_guard_passes_current_artifacts():
    rows, summary = build_step60_step59_regression_guard(ROOT)
    assert summary["step59_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["step59_required_row_count"]) == 3
    assert int(summary["step59_canonical_module_count"]) == 3
    assert int(summary["step59_legacy_driver_module_used_count"]) == 0
    assert summary["step59_missing_required_rows"] == []
    assert all(row["pass"] is True for row in rows)


def test_step60_step59_regression_guard_artifact_passes():
    payload = read_json("outputs/step60_step59_regression_guard/step59_regression_guard.json")
    summary = payload["summary"]
    assert summary["step59_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["step59_required_row_count"]) == 3
    assert int(summary["step59_canonical_module_count"]) == 3
    assert int(summary["step59_legacy_driver_module_used_count"]) == 0
    assert summary["step59_missing_required_rows"] == []
    assert all(row["pass"] is True for row in payload["rows"])


def test_step60_preserves_step59_required_smoke_artifacts():
    payload = read_json("outputs/step59_canonical_driver_smoke_matrix/smoke_matrix.json")
    rows = {row["row_name"]: row for row in payload["rows"]}
    assert set(rows) == {
        "canonical_driver_none_16_1step",
        "canonical_driver_penalty_16_1step",
        "canonical_driver_moving_boundary_engineering_16_1step",
    }
    assert all(row["driver_run_called"] is True for row in rows.values())
    assert all(row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver" for row in rows.values())
    assert all(row["legacy_driver_module_used_as_implementation"] is False for row in rows.values())


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
