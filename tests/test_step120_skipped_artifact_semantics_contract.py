import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _tmp(name: str) -> Path:
    path = ROOT / "outputs/tmp/step120_skipped_contract" / name
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_step120_large_row_placeholder_has_no_flux_balance_or_passed_physics_gates():
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import Step120RunSpec, run_step120_row

    row_dir = _tmp("large_placeholder") / "large_placeholder"
    spec = Step120RunSpec(
        name="large_placeholder",
        nx=48,
        ny=48,
        nz=48,
        n_steps=500,
        output_interval=25,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        requested_nx=48,
        requested_n_steps=500,
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
    )

    row = run_step120_row(spec, row_dir, allow_large_real_rows=False)

    assert row["steps_completed"] == 0
    assert row["simulation_backed_artifact"] is False
    assert row["flux_balance_reported"] is False
    assert row["density_gate_pass"] is False
    assert row["mass_drift_gate_pass"] is False
    assert row["population_gate_pass"] is False
    assert row["step120_validation_claimed"] is False
    assert row["first_failure_reason"] == "large_real_row_requires_explicit_allowance"
