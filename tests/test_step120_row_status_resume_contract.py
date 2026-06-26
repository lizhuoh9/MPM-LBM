import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _tmp(name: str) -> Path:
    path = ROOT / "outputs/tmp/step120_row_status_contract" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_finite(row_dir: Path, summary_row: dict, skipped_reason: str | None = None):
    row_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        **summary_row,
        "skipped_reason": skipped_reason,
        "summary_row": summary_row,
    }
    with (row_dir / "finite_stability_report.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f)


def test_step120_placeholder_is_not_resume_complete_when_large_rows_later_allowed():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        ROW_STATUS_INCOMPLETE_PLACEHOLDER,
        Step120RunSpec,
        classify_step120_row_status,
        run_step120_matrix,
        step120_row_complete_for_resume,
    )

    output_dir = _tmp("placeholder_then_real")
    row_dir = output_dir / "placeholder_then_real"
    _write_finite(
        row_dir,
        {
            "name": "placeholder_then_real",
            "requested_window_completed": False,
            "steps_completed": 0,
            "step120_validation_claimed": False,
            "simulation_backed_artifact": False,
            "first_failure_reason": "large_real_row_requires_explicit_allowance",
        },
        skipped_reason="large_real_row_requires_explicit_allowance",
    )

    assert classify_step120_row_status(row_dir)["status"] == ROW_STATUS_INCOMPLETE_PLACEHOLDER
    assert step120_row_complete_for_resume(row_dir) is False

    spec = Step120RunSpec(
        name="placeholder_then_real",
        nx=5,
        ny=4,
        nz=4,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=1,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )
    summary = run_step120_matrix(output_dir, specs=[spec], resume=True, allow_large_real_rows=True)
    row = summary["runs"][0]
    assert row["row_source"] != "resumed"
    assert row["steps_completed"] == 1
    assert row["simulation_backed_artifact"] is True


def test_step120_tau_skip_is_expected_policy_completion_but_not_validation_pass():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        ROW_STATUS_EXPECTED_POLICY_SKIP,
        classify_step120_row_status,
        step120_row_complete_for_resume,
    )

    row_dir = _tmp("tau_policy") / "tau_policy"
    _write_finite(
        row_dir,
        {
            "name": "tau_policy",
            "requested_window_completed": False,
            "steps_completed": 0,
            "step120_validation_claimed": False,
            "simulation_backed_artifact": False,
            "skipped_due_to_tau_margin": True,
            "first_failure_reason": "tau_margin",
        },
        skipped_reason="tau_margin",
    )

    status = classify_step120_row_status(row_dir)
    assert status["status"] == ROW_STATUS_EXPECTED_POLICY_SKIP
    assert status["validation_pass"] is False
    assert step120_row_complete_for_resume(row_dir) is True


def test_step120_completed_real_row_resumes_normally():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        ROW_STATUS_COMPLETED,
        Step120RunSpec,
        classify_step120_row_status,
        run_step120_matrix,
    )

    output_dir = _tmp("completed_resume")
    spec = Step120RunSpec(
        name="completed_resume",
        nx=5,
        ny=4,
        nz=4,
        n_steps=1,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=1,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )

    first = run_step120_matrix(output_dir, specs=[spec], force=True)
    row_dir = output_dir / first["runs"][0]["name"]
    assert classify_step120_row_status(row_dir)["status"] == ROW_STATUS_COMPLETED

    resumed = run_step120_matrix(output_dir, specs=[spec], resume=True)
    assert resumed["runs"][0]["row_source"] == "resumed"
