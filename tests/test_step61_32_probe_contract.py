import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_32_probe_audit import build_canonical_driver_32_probe_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step61_32_probe_audit_passes_committed_artifacts():
    rows, summary = build_canonical_driver_32_probe_audit(ROOT)
    assert summary["probe_32_audit_pass"] is True
    assert int(summary["required_row_count"]) == 1
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert int(summary["driver_run_called_count"]) == 1
    assert int(summary["stable_count"]) == 1
    assert int(summary["legacy_driver_module_used_count"]) == 0
    assert summary["missing_required_rows"] == []
    assert all(row["pass"] is True for row in rows)


def test_step61_32_probe_matrix_artifact_passes():
    payload = read_json("outputs/step61_32_probe_matrix/probe_32_matrix.json")
    summary = payload["summary"]
    assert summary["probe_32_matrix_pass"] is True
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
    assert row["row_name"] == "canonical_driver_moving_boundary_engineering_32_1step"
    assert row["n_grid"] == 32
    assert row["n_particles"] == 1024
    assert row["n_lbm_steps"] == 1
    assert row["driver_run_called"] is True
    assert row["stable"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geo_path_name"] == "geo_all_fluid_32.dat"


def test_step61_required_driver_run_outputs_exist_and_are_lightweight():
    run_dir = ROOT / "outputs" / "step61_driver_runs" / "canonical_driver_moving_boundary_engineering_32_1step"
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


def test_step61_matrix_runner_uses_real_canonical_driver_run():
    source = (ROOT / "baseline_tests/run_step61_32_probe_matrix.py").read_text(encoding="utf-8")
    runner = (ROOT / "src/mpm_lbm/evidence/canonical_driver_32_probe_runner.py").read_text(encoding="utf-8")
    assert "build_canonical_driver_32_probe_matrix" in source
    assert "from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D" in runner
    assert "driver.run()" in runner
    assert "src.fsi_driver" not in runner


def test_step61_optional_rows_are_defined_but_disabled_by_default():
    matrix_policy = read_json("configs/step61_controlled_canonical_32_moving_boundary_single_step.json")
    assert matrix_policy["run_optional_penalty_32_probe"] is False
    assert matrix_policy["run_optional_32_3step_probe"] is False
    assert matrix_policy["optional_penalty_32_configs"] == [
        "configs/step61_canonical_driver_penalty_32_1step_optional.json"
    ]
    assert matrix_policy["optional_32_3step_configs"] == [
        "configs/step61_canonical_driver_moving_boundary_engineering_32_3step_optional.json"
    ]
    assert not (ROOT / "outputs/step61_driver_runs/canonical_driver_penalty_32_1step_optional").exists()
    assert not (ROOT / "outputs/step61_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_optional").exists()


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
