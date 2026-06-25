import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step119_limiter_summary_reports_required_fields_and_blocks_high_activation():
    from experiments.steps.step119_lbm_boundary_repair_real_run_validation import (
        Step119RunSpec,
        summarize_limiter_activation,
    )

    spec = Step119RunSpec(
        name="limiter_summary_contract",
        nx=8,
        ny=6,
        nz=6,
        n_steps=10,
        output_interval=5,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        open_boundary_limiter_enabled=True,
        open_boundary_population_floor=-1.0e-8,
    )
    records = [
        {
            "rho_below_low_count": 20,
            "rho_above_high_count": 15,
            "velocity_outlier_count": 10,
            "negative_population_count": 40,
            "population_entry_count": 120,
        },
        {
            "rho_below_low_count": 5,
            "rho_above_high_count": 2,
            "velocity_outlier_count": 3,
            "negative_population_count": 12,
            "population_entry_count": 120,
        },
    ]

    summary = summarize_limiter_activation(records, spec)

    assert summary["open_boundary_limiter_enabled"] is True
    assert summary["rho_clip_used"] is True
    assert summary["velocity_clip_used"] is True
    assert summary["noneq_limiter_used"] is True
    assert summary["population_floor_used"] is True
    assert summary["limiter_activation_count"] > 0
    assert summary["limiter_activation_fraction"] > 0.05
    assert summary["validation_blocked_by_limiter_activation"] is True
    assert summary["validation_claim_allowed"] is False


def test_step119_limiter_summary_allows_zero_activation_but_never_claims_validation_by_itself():
    from experiments.steps.step119_lbm_boundary_repair_real_run_validation import (
        Step119RunSpec,
        summarize_limiter_activation,
    )

    spec = Step119RunSpec(
        name="limiter_summary_zero",
        nx=8,
        ny=6,
        nz=6,
        n_steps=4,
        output_interval=2,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        geometry_mode="duct_only",
        open_boundary_limiter_enabled=True,
    )
    summary = summarize_limiter_activation(
        [{"rho_below_low_count": 0, "rho_above_high_count": 0, "velocity_outlier_count": 0, "negative_population_count": 0}],
        spec,
    )

    assert summary["limiter_activation_count"] == 0
    assert summary["limiter_activation_fraction"] == 0.0
    assert summary["validation_blocked_by_limiter_activation"] is False
    assert summary["validation_claim_allowed"] is False
