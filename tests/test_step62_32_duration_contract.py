import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_32_duration_audit import build_canonical_driver_32_duration_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step62_32_duration_audit_passes_committed_artifacts():
    rows, summary = build_canonical_driver_32_duration_audit(ROOT)
    assert summary["duration_32_audit_pass"] is True
    assert int(summary["required_row_count"]) == 1
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert int(summary["driver_run_called_count"]) == 1
    assert int(summary["stable_count"]) == 1
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert all(row["pass"] is True for row in rows)


def test_step62_32_duration_matrix_artifact_passes():
    payload = read_json("outputs/step62_32_duration_matrix/duration_32_matrix.json")
    summary = payload["summary"]
    assert summary["duration_32_matrix_pass"] is True
    assert int(summary["required_row_count"]) == 1
    assert int(summary["row_count"]) == 1
    assert int(summary["stable_count"]) == 1
    assert int(summary["driver_run_called_count"]) == 1
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert int(summary["optional_row_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert summary["runtime_code_changed"] is False
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False
    row = payload["rows"][0]
    assert row["row_name"] == "canonical_driver_moving_boundary_engineering_32_3step"
    assert row["n_grid"] == 32
    assert row["n_particles"] == 1024
    assert row["n_lbm_steps"] == 3
    assert row["completed_lbm_steps"] == 3
    assert row["total_mpm_substeps"] >= 3
    assert row["diagnostics_row_count"] >= 4
    assert row["driver_run_called"] is True
    assert row["runtime_hard_limit_exceeded"] is False
    assert row["stable"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geo_path_name"] == "geo_all_fluid_32.dat"


def test_step62_required_driver_run_outputs_exist_and_are_lightweight():
    run_dir = ROOT / "outputs" / "step62_driver_runs" / "canonical_driver_moving_boundary_engineering_32_3step"
    assert run_dir.is_dir()
    actual = {path.name for path in run_dir.iterdir() if path.is_file()}
    assert actual == {
        "diagnostics_timeseries.csv",
        "diagnostics_timeseries.npz",
        "driver_config.json",
        "geo_all_fluid_32.dat",
    }
    assert not any(path.suffix.lower() == ".vtr" for path in run_dir.rglob("*"))
    assert not any(path.suffix.lower() == ".npy" and "particle" in path.name.lower() for path in run_dir.rglob("*"))


def test_step62_matrix_runner_uses_real_canonical_driver_run():
    source = (ROOT / "baseline_tests/run_step62_32_duration_matrix.py").read_text(encoding="utf-8")
    runner = (ROOT / "src/mpm_lbm/evidence/canonical_driver_32_duration_runner.py").read_text(encoding="utf-8")
    assert "build_canonical_driver_32_duration_matrix" in source
    assert "from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D" in runner
    assert "driver.run()" in runner
    assert "src.fsi_driver" not in runner


def test_step62_optional_rows_are_defined_but_disabled_by_default():
    matrix_policy = read_json("configs/step62_controlled_canonical_32_moving_boundary_3step_duration.json")
    assert matrix_policy["run_optional_penalty_32_3step"] is False
    assert matrix_policy["run_optional_32_5step"] is False
    assert matrix_policy["optional_penalty_32_3step_configs"] == [
        "configs/step62_canonical_driver_penalty_32_3step_optional.json"
    ]
    assert matrix_policy["optional_32_5step_configs"] == [
        "configs/step62_canonical_driver_moving_boundary_engineering_32_5step_optional.json"
    ]
    assert not (ROOT / "outputs/step62_driver_runs/canonical_driver_penalty_32_3step_optional").exists()
    assert not (ROOT / "outputs/step62_driver_runs/canonical_driver_moving_boundary_engineering_32_5step_optional").exists()


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
