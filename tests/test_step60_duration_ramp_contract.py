import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_duration_ramp_audit import (
    build_canonical_driver_duration_ramp_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step60_duration_ramp_audit_passes_committed_artifacts():
    rows, summary = build_canonical_driver_duration_ramp_audit(ROOT)
    assert summary["duration_ramp_audit_pass"] is True
    assert int(summary["required_row_count"]) == 3
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 3
    assert int(summary["driver_run_called_count"]) == 3
    assert int(summary["stable_count"]) == 3
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert all(row["pass"] is True for row in rows)


def test_step60_duration_ramp_matrix_artifact_passes():
    payload = read_json("outputs/step60_duration_ramp_matrix/duration_ramp_matrix.json")
    summary = payload["summary"]
    assert summary["duration_ramp_matrix_pass"] is True
    assert int(summary["required_row_count"]) == 3
    assert int(summary["row_count"]) == 3
    assert int(summary["stable_count"]) == 3
    assert int(summary["driver_run_called_count"]) == 3
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert summary["runtime_code_changed"] is False
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False
    assert all(row["driver_run_called"] is True for row in payload["rows"])
    assert all(row["stable"] is True for row in payload["rows"])
    assert all(row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver" for row in payload["rows"])
    assert all(row["legacy_driver_module_used_as_implementation"] is False for row in payload["rows"])


def test_step60_required_driver_run_outputs_exist_and_are_lightweight():
    policy = read_json("configs/step60_duration_ramp_acceptance_policy.json")
    allowed = set(policy["allowed_driver_run_files"])
    for row_name in policy["required_row_names"]:
        run_dir = ROOT / "outputs" / "step60_driver_runs" / row_name
        assert run_dir.is_dir()
        actual = {path.name for path in run_dir.iterdir() if path.is_file()}
        assert actual <= allowed
        assert actual == {
            "diagnostics_timeseries.csv",
            "diagnostics_timeseries.npz",
            "driver_config.json",
            "geo_all_fluid_16.dat",
        }
        assert not any(path.suffix.lower() == ".vtr" for path in run_dir.rglob("*"))
        assert not any(path.suffix.lower() == ".npy" and "particle" in path.name.lower() for path in run_dir.rglob("*"))


def test_step60_matrix_runner_uses_real_canonical_driver_run():
    source = (ROOT / "baseline_tests/run_step60_duration_ramp_matrix.py").read_text(encoding="utf-8")
    runner = (ROOT / "src/mpm_lbm/evidence/canonical_driver_duration_ramp_runner.py").read_text(encoding="utf-8")
    assert "build_canonical_driver_duration_ramp_matrix" in source
    assert "from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D" in runner
    assert "driver.run()" in runner
    assert "src.fsi_driver" not in runner


def test_step60_optional_32_probe_is_defined_but_disabled_by_default():
    matrix_policy = read_json("configs/step60_controlled_canonical_moving_boundary_duration_ramp.json")
    assert matrix_policy["run_optional_32_probe"] is False
    assert matrix_policy["optional_duration_configs"] == [
        "configs/step60_canonical_driver_moving_boundary_engineering_32_1step_optional.json"
    ]
    assert not (ROOT / "outputs/step60_driver_runs/canonical_driver_moving_boundary_engineering_32_1step_optional").exists()


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
