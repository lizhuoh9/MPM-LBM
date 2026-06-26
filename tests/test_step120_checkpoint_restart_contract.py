import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _tmp(name: str) -> Path:
    path = ROOT / "outputs/tmp/step120_checkpoint_contract" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_step120_tiny_checkpoint_resume_matches_uninterrupted_result():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        ROW_STATUS_CHECKPOINT_AVAILABLE,
        Step120RunSpec,
        classify_step120_row_status,
        run_step120_row,
    )

    interrupted_dir = _tmp("interrupted") / "row"
    uninterrupted_dir = _tmp("uninterrupted") / "row"
    checkpoint_root = ROOT / "outputs/tmp/step120_checkpoints_test"
    if checkpoint_root.exists():
        shutil.rmtree(checkpoint_root)

    spec = Step120RunSpec(
        name="checkpoint_resume_tiny",
        nx=5,
        ny=4,
        nz=4,
        n_steps=3,
        output_interval=1,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=3,
        checkpoint_every=1,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
        allow_large_real_run_without_flag=True,
    )

    interrupted = run_step120_row(
        spec,
        interrupted_dir,
        checkpoint_root=checkpoint_root,
        stop_after_steps=1,
    )
    assert interrupted["steps_completed"] == 1
    assert classify_step120_row_status(interrupted_dir)["status"] == ROW_STATUS_CHECKPOINT_AVAILABLE

    resumed = run_step120_row(
        spec,
        interrupted_dir,
        checkpoint_root=checkpoint_root,
        resume_from_checkpoint=True,
    )
    uninterrupted = run_step120_row(spec, uninterrupted_dir, checkpoint_root=checkpoint_root / "fresh")

    assert resumed["requested_window_completed"] is True
    assert resumed["steps_completed"] == 3
    assert abs(resumed["mass_total_delta_rel_final"] - uninterrupted["mass_total_delta_rel_final"]) < 1.0e-7
    assert abs(resumed["flux_imbalance_rel_final"] - uninterrupted["flux_imbalance_rel_final"]) < 1.0e-7
    assert resumed["limiter_activation_count"] == uninterrupted["limiter_activation_count"]
    assert resumed["limiter_activation_denominator"] == uninterrupted["limiter_activation_denominator"]
