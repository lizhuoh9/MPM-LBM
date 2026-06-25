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
    path = ROOT / "outputs/tmp/step118_runner_contract" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_step118_tiny_runner_writes_stability_artifacts_and_resume_rows():
    from experiments.steps.step118_lbm_open_boundary_stability_repair import (
        Step118RunSpec,
        run_step118_matrix,
    )

    output_dir = _runner_tmp("tiny_limited_resume")
    spec = Step118RunSpec(
        name="tiny_step118_limited_10step",
        nx=8,
        ny=6,
        nz=6,
        n_steps=10,
        output_interval=5,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        open_boundary_limiter_enabled=True,
        synthetic_diagnostic_mode=True,
    )

    first = run_step118_matrix(output_dir, specs=[spec], force=True)
    row = first["runs"][0]
    row_dir = output_dir / row["name"]
    finite = _read_json(row_dir / "finite_stability_report.json")
    first_failure = _read_json(row_dir / "first_failure_diagnostics.json")
    metadata = _read_json(row_dir / "run_metadata.json")

    assert first["step"] == 118
    assert row["requested_window_completed"] is True
    assert row["steps_completed"] == 10
    assert row["stability_diagnostics_reported"] is True
    assert finite["step118_gate_pass"] in (True, False)
    assert "stability_timeseries_trend_summary" in finite
    assert "population_stats_final" in finite
    assert first_failure["first_failure_detector"]["record_count"] >= 1
    assert metadata["step"] == 118
    assert metadata["fluent_validation_claim_allowed"] is False
    assert metadata["full_fsi_rerun_done"] is False
    assert metadata["validation_claim_allowed"] is False
    assert metadata["synthetic_diagnostic_mode"] is True

    with (row_dir / "stability_diagnostics_timeseries.csv").open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert [int(item["step"]) for item in rows] == [0, 5, 10]
    assert "negative_population_count" in rows[0]

    resumed = run_step118_matrix(output_dir, specs=[spec], resume=True)
    assert resumed["runs"][0]["row_source"] == "resumed"


def test_step118_runner_skips_strict_physical_nu_tau_failure_before_stepping():
    from experiments.steps.step118_lbm_open_boundary_stability_repair import (
        Step118RunSpec,
        run_step118_matrix,
    )

    output_dir = _runner_tmp("strict_tau_skip")
    spec = Step118RunSpec(
        name="tiny_step118_strict_physical_nu_skip",
        nx=8,
        ny=6,
        nz=6,
        n_steps=10,
        output_interval=5,
        open_boundary_semantics="regularized_velocity_pressure_limited",
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

    summary = run_step118_matrix(output_dir, specs=[spec], force=True)
    row = summary["runs"][0]
    finite = _read_json(output_dir / "tiny_step118_strict_physical_nu_skip" / "finite_stability_report.json")

    assert row["skipped_due_to_tau_margin"] is True
    assert row["steps_completed"] == 0
    assert finite["tau_feasibility_report"]["tau_margin_pass"] is False
    assert finite["not_used_for_validation"] is True
    assert finite["step118_gate_pass"] is False


def test_step118_profile_only_writes_planning_metadata_without_validation_claim():
    from experiments.steps.step118_lbm_open_boundary_stability_repair import (
        Step118RunSpec,
        run_step118_matrix,
    )

    output_dir = _runner_tmp("profile_only")
    spec = Step118RunSpec(
        name="tiny_step118_profile_only",
        nx=8,
        ny=6,
        nz=6,
        n_steps=10,
        output_interval=5,
        open_boundary_semantics="convective_pressure_outlet_experimental",
        geometry_mode="static_two_flap",
    )

    summary = run_step118_matrix(output_dir, specs=[spec], force=True, profile_only=True)
    row = summary["runs"][0]
    finite = _read_json(output_dir / "tiny_step118_profile_only" / "finite_stability_report.json")
    metadata = _read_json(output_dir / "tiny_step118_profile_only" / "run_metadata.json")

    assert row["profile_only"] is True
    assert row["steps_completed"] == 0
    assert row["requested_window_completed"] is False
    assert finite["step118_gate_pass"] is False
    assert metadata["simulation_backed_artifact"] is False
    assert metadata["validation_claim_allowed"] is False
