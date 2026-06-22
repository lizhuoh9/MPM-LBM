import json
from pathlib import Path

from src.mpm_lbm.evidence.post_gate_rebaseline_audit import build_step76_post_gate_rebaseline_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step76_rebaseline_audit_passes_committed_artifacts():
    rows, summary = build_step76_post_gate_rebaseline_audit(ROOT)
    assert rows
    assert summary["post_gate_rebaseline_audit_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["row_count"] == summary["pass_count"] == 1
    assert summary["driver_run_called_count"] == 1
    assert summary["stable_count"] == 1
    assert summary["legacy_driver_module_used_count"] == 0
    assert summary["activation_feature_count"] == 0
    assert summary["missing_required_rows"] == []


def test_step76_rebaseline_matrix_artifact_passes():
    payload = read_json("outputs/step76_post_gate_rebaseline_matrix/post_gate_rebaseline_matrix.json")
    summary = payload["summary"]
    assert summary["post_gate_rebaseline_matrix_pass"] is True
    assert summary["gate_status"] == "ready_for_step76_rebaseline_only"
    assert summary["post_gate_simulation_allowed"] is True
    assert summary["allowed_next_step"] == "Step76"
    assert summary["allowed_next_step_scope"] == "minimal safe rebaseline only"
    assert summary["required_row_count"] == 1
    assert summary["row_count"] == 1
    assert summary["stable_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["activation_feature_count"] == 0
    row = payload["rows"][0]
    assert row["row_name"] == "canonical_driver_moving_boundary_engineering_32_1step_rebaseline"
    assert row["n_grid"] == 32
    assert row["n_particles"] == 1024
    assert row["n_lbm_steps"] == 1
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geo_path_name"] == "geo_all_fluid_32.dat"


def test_step76_required_driver_run_outputs_exist_and_are_lightweight():
    run_dir = ROOT / "outputs" / "step76_driver_runs" / "canonical_driver_moving_boundary_engineering_32_1step_rebaseline"
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


def test_step76_matrix_runner_uses_real_canonical_driver_run():
    source = (ROOT / "baseline_tests/run_step76_post_gate_rebaseline_matrix.py").read_text(encoding="utf-8")
    runner = (ROOT / "src/mpm_lbm/evidence/post_gate_rebaseline_runner.py").read_text(encoding="utf-8")
    assert "build_step76_post_gate_rebaseline_matrix" in source
    assert "from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D" in runner
    assert "driver.run()" in runner
    assert "src.fsi_driver" not in runner


def test_step76_optional_row_is_defined_but_disabled_by_default():
    policy = read_json("configs/step76_minimal_post_gate_canonical_driver_rebaseline.json")
    assert policy["run_optional_32_3step"] is False
    assert policy["optional_32_3step_configs"] == [
        "configs/step76_canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional.json"
    ]
    optional_dir = ROOT / "outputs/step76_driver_runs/canonical_driver_moving_boundary_engineering_32_3step_rebaseline_optional"
    assert not optional_dir.exists()


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
