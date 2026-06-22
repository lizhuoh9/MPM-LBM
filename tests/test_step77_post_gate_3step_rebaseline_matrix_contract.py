import json
from pathlib import Path

from src.mpm_lbm.evidence.post_gate_3step_rebaseline_audit import build_step77_post_gate_3step_rebaseline_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step77_3step_rebaseline_audit_passes_committed_artifacts():
    rows, summary = build_step77_post_gate_3step_rebaseline_audit(ROOT)
    assert rows
    assert summary["post_gate_3step_rebaseline_audit_pass"] is True
    assert summary["required_row_count"] == 1
    assert summary["row_count"] == summary["pass_count"] == 1
    assert summary["driver_run_called_count"] == 1
    assert summary["stable_count"] == 1
    assert summary["legacy_driver_module_used_count"] == 0
    assert summary["activation_feature_count"] == 0
    assert summary["missing_required_rows"] == []


def test_step77_3step_rebaseline_matrix_artifact_passes():
    payload = read_json("outputs/step77_post_gate_3step_rebaseline_matrix/post_gate_3step_rebaseline_matrix.json")
    summary = payload["summary"]
    assert summary["post_gate_3step_rebaseline_matrix_pass"] is True
    assert summary["gate_status"] == "ready_for_step77_3step_rebaseline_only"
    assert summary["post_gate_simulation_allowed"] is True
    assert summary["allowed_next_step"] == "Step77"
    assert summary["allowed_next_step_scope"] == "minimal post-gate canonical driver 3-step rebaseline only"
    assert summary["previous_rebaseline_step"] == "Step76"
    assert summary["required_row_count"] == 1
    assert summary["row_count"] == 1
    assert summary["stable_count"] == 1
    assert summary["optional_row_count"] == 0
    assert summary["activation_feature_count"] == 0
    assert summary["runtime_hard_fail_count"] == 0

    row = payload["rows"][0]
    assert row["row_name"] == "canonical_driver_moving_boundary_engineering_32_3step_rebaseline"
    assert row["n_grid"] == 32
    assert row["n_particles"] == 1024
    assert row["n_lbm_steps"] == 3
    assert row["completed_lbm_steps"] == 3
    assert row["total_mpm_substeps"] >= 3
    assert row["diagnostics_row_count"] >= 4
    assert row["previous_rebaseline_step"] == "Step76"
    assert row["runtime_hard_fail"] is False
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["legacy_driver_module_used_as_implementation"] is False
    assert row["geo_path_name"] == "geo_all_fluid_32.dat"


def test_step77_required_driver_run_outputs_exist_and_are_lightweight():
    run_dir = ROOT / "outputs" / "step77_driver_runs" / "canonical_driver_moving_boundary_engineering_32_3step_rebaseline"
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


def test_step77_matrix_runner_uses_real_canonical_driver_run():
    source = (ROOT / "baseline_tests/run_step77_post_gate_3step_rebaseline_matrix.py").read_text(encoding="utf-8")
    runner = (ROOT / "src/mpm_lbm/evidence/post_gate_3step_rebaseline_runner.py").read_text(encoding="utf-8")
    assert "build_step77_post_gate_3step_rebaseline_matrix" in source
    assert "from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D" in runner
    assert "driver.run()" in runner
    assert "src.fsi_driver" not in runner


def test_step77_has_no_optional_rows():
    policy = read_json("configs/step77_minimal_post_gate_canonical_driver_3step_rebaseline.json")
    acceptance = read_json("configs/step77_rebaseline_acceptance_policy.json")
    assert policy["required_rebaseline_configs"] == [
        "configs/step77_canonical_driver_moving_boundary_engineering_32_3step_rebaseline.json"
    ]
    assert acceptance["optional_row_names"] == []
    run_root = ROOT / "outputs" / "step77_driver_runs"
    optional_dirs = [
        path.name
        for path in run_root.iterdir()
        if path.is_dir() and path.name != "canonical_driver_moving_boundary_engineering_32_3step_rebaseline"
    ]
    assert optional_dirs == []


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
