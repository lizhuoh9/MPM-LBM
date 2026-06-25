import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _synthetic_snapshot():
    rho = np.ones((4, 3, 2), dtype=float)
    velocity = np.zeros((4, 3, 2, 3), dtype=float)
    solid = np.zeros((4, 3, 2), dtype=np.int8)
    f = np.full((4, 3, 2, 19), 1.0 / 19.0, dtype=float)
    F = np.full((4, 3, 2, 19), 1.0 / 19.0, dtype=float)

    rho[0, 1, 1] = -0.05
    rho[3, 1, 1] = 1.35
    velocity[3, 1, 1, 0] = 0.35
    velocity[2, 1, 1, 1] = -0.25
    f[0, 1, 1, 1] = -1.0e-4
    F[3, 1, 1, 2] = -2.0e-4
    solid[1, 1, 0] = 1
    return {"rho": rho, "v": velocity, "solid": solid, "f": f, "F": F}


def test_step118_population_and_boundary_stats_find_negative_populations():
    from src.mpm_lbm.sim.diagnostics.lbm_stability_diagnostics import (
        boundary_population_stats,
        negative_population_stats,
        population_stats,
    )

    snapshot = _synthetic_snapshot()
    pop = population_stats(snapshot)
    neg = negative_population_stats(snapshot)
    inlet = boundary_population_stats(snapshot, side="x_min")
    outlet = boundary_population_stats(snapshot, side="x_max")

    assert pop["f_min"] < 0.0
    assert pop["F_min"] < 0.0
    assert pop["all_finite"] is True
    assert neg["negative_population_count"] == 2
    assert 0.0 < neg["negative_population_fraction"] < 1.0
    assert inlet["side"] == "x_min"
    assert inlet["negative_population_count"] == 1
    assert outlet["side"] == "x_max"
    assert outlet["negative_population_count"] == 1


def test_step118_density_velocity_and_first_failure_diagnostics_are_schema_stable():
    from src.mpm_lbm.sim.diagnostics.lbm_stability_diagnostics import (
        classify_first_failure_location,
        density_outlier_stats,
        first_gate_failure_detector,
        mass_source_sink_by_step,
        velocity_outlier_stats,
    )

    snapshot = _synthetic_snapshot()
    density = density_outlier_stats(snapshot, low=0.0, high=1.2)
    velocity = velocity_outlier_stats(snapshot, max_v_threshold=0.2)
    location = classify_first_failure_location(snapshot)

    assert density["rho_below_low_count"] == 1
    assert density["rho_above_high_count"] == 1
    assert density["first_negative_density_location"] == [0, 1, 1]
    assert density["first_high_density_location"] == [3, 1, 1]
    assert velocity["velocity_outlier_count"] == 2
    assert math.isclose(velocity["max_v"], 0.35, rel_tol=0.0, abs_tol=1.0e-12)
    assert location["first_failure_location"] in {"inlet", "outlet", "wall_or_open_boundary_corner", "interior"}

    records = [
        {"step": 0, "rho_min": 1.0, "rho_max": 1.0, "mass_total_delta_rel": 0.0, "max_v": 0.02},
        {"step": 5, "rho_min": 0.98, "rho_max": 1.05, "mass_total_delta_rel": 0.02, "max_v": 0.05},
        {"step": 10, "rho_min": -0.01, "rho_max": 1.35, "mass_total_delta_rel": 0.07, "max_v": 0.3},
    ]
    first = first_gate_failure_detector(records)
    mass = mass_source_sink_by_step(records)

    assert first["first_failure_step"] == 10
    assert first["first_negative_density_step"] == 10
    assert first["first_high_density_step"] == 10
    assert first["first_mass_drift_step"] == 10
    assert first["first_max_v_step"] == 10
    assert mass["record_count"] == 3
    assert math.isclose(mass["mass_drift_delta_final"], 0.07, rel_tol=0.0, abs_tol=1.0e-12)


def test_step118_diagnostics_reject_bad_boundary_side_and_nonfinite_records():
    from src.mpm_lbm.sim.diagnostics.lbm_stability_diagnostics import (
        boundary_population_stats,
        first_gate_failure_detector,
    )

    snapshot = _synthetic_snapshot()
    try:
        boundary_population_stats(snapshot, side="y_min")
    except ValueError as exc:
        assert "side" in str(exc)
    else:
        raise AssertionError("boundary_population_stats accepted a non-x side")

    records = [{"step": 0, "rho_min": float("nan"), "rho_max": 1.0, "mass_total_delta_rel": 0.0, "max_v": 0.0}]
    failure = first_gate_failure_detector(records)
    assert failure["all_records_finite"] is False
    assert failure["first_nonfinite_step"] == 0
