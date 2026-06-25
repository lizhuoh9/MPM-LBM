import csv
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _runner_tmp(name: str) -> Path:
    path = ROOT / "outputs/tmp/step117_runner_contract" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_step117_tiny_long_window_runner_writes_schema_and_resume_rows():
    from experiments.steps.step117_regularized_lbm_long_window_fluid_validation import (
        Step117RunSpec,
        run_step117_matrix,
    )

    output_dir = _runner_tmp("tiny_long_window_resume")
    spec = Step117RunSpec(
        name="tiny_step117_regularized_10step_full",
        nx=8,
        ny=6,
        nz=6,
        n_steps=10,
        output_interval=5,
        open_boundary_semantics="regularized_velocity_pressure",
        geometry_mode="duct_only",
    )

    first = run_step117_matrix(output_dir, specs=[spec], force=True)
    row = first["runs"][0]
    row_dir = output_dir / row["name"]
    finite = _read_json(row_dir / "finite_stability_report.json")
    metadata = _read_json(row_dir / "run_metadata.json")

    assert first["step"] == 117
    assert row["requested_window_completed"] is True
    assert row["steps_completed"] == 10
    assert row["long_window_schema_version"] == 1
    assert finite["step117_gate_pass"] in (True, False)
    assert "timeseries_trend_summary" in finite
    assert "long_window_gates" in finite
    assert metadata["step"] == 117
    assert metadata["full_fsi_rerun_done"] is False
    assert metadata["fluent_validation_claim_allowed"] is False

    with (row_dir / "fluid_diagnostics_timeseries.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert [int(item["step"]) for item in rows] == [0, 5, 10]

    resumed = run_step117_matrix(output_dir, specs=[spec], resume=True)
    assert resumed["runs"][0]["row_source"] == "resumed"


def test_step117_runner_skips_strict_physical_nu_tau_failure_before_stepping():
    from experiments.steps.step117_regularized_lbm_long_window_fluid_validation import (
        Step117RunSpec,
        run_step117_matrix,
    )

    output_dir = _runner_tmp("strict_tau_skip")
    spec = Step117RunSpec(
        name="tiny_step117_strict_physical_nu_skip",
        nx=8,
        ny=6,
        nz=6,
        n_steps=10,
        output_interval=5,
        open_boundary_semantics="regularized_velocity_pressure",
        geometry_mode="duct_only",
        lbm_viscosity_semantics="physical_nu_mapping",
        lbm_tau_stability_policy="strict",
        lbm_min_tau_margin=1.0e-4,
        lbm_dt_phys_override_s=2.0833333333333334e-6,
        physical_duct_length_m=0.1,
        target_inlet_velocity_mps=10.0,
        target_reynolds_number=26666.666666666668,
        requested_nx=96,
        requested_n_steps=100,
    )

    summary = run_step117_matrix(output_dir, specs=[spec], force=True)
    row = summary["runs"][0]
    finite = _read_json(output_dir / "tiny_step117_strict_physical_nu_skip" / "finite_stability_report.json")

    assert row["skipped_due_to_tau_margin"] is True
    assert row["steps_completed"] == 0
    assert finite["tau_feasibility_report"]["tau_margin_pass"] is False
    assert finite["physical_reynolds_direct_simulation_feasible_with_current_lbm"] is False
    assert finite["not_used_for_validation"] is True


def test_step117_profile_only_writes_planning_metadata_without_validation_claim():
    from experiments.steps.step117_regularized_lbm_long_window_fluid_validation import (
        Step117RunSpec,
        run_step117_matrix,
    )

    output_dir = _runner_tmp("profile_only")
    spec = Step117RunSpec(
        name="tiny_step117_profile_only",
        nx=8,
        ny=6,
        nz=6,
        n_steps=10,
        output_interval=5,
        open_boundary_semantics="regularized_velocity_pressure",
        geometry_mode="static_two_flap",
    )

    summary = run_step117_matrix(output_dir, specs=[spec], force=True, profile_only=True)
    row = summary["runs"][0]
    finite = _read_json(output_dir / "tiny_step117_profile_only" / "finite_stability_report.json")
    metadata = _read_json(output_dir / "tiny_step117_profile_only" / "run_metadata.json")

    assert row["profile_only"] is True
    assert row["steps_completed"] == 0
    assert row["requested_window_completed"] is False
    assert finite["step117_gate_pass"] is False
    assert metadata["simulation_backed_artifact"] is False
    assert metadata["fluent_validation_claim_allowed"] is False
