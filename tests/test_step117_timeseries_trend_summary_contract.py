import math
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _record(step, rho_min, rho_max, mass_drift, flux_imbalance, outlet_flux, mid_ux, max_v, neg_ux, rho_std):
    return {
        "step": step,
        "rho_min": rho_min,
        "rho_max": rho_max,
        "rho_mean": 1.0,
        "rho_std": rho_std / 2.0,
        "mass_total_delta_rel": mass_drift,
        "flux_imbalance_rel": flux_imbalance,
        "outlet_flux": outlet_flux,
        "midplane_mean_ux": mid_ux,
        "max_v": max_v,
        "mach_proxy_observed": max_v / math.sqrt(1.0 / 3.0),
        "outlet_reflection_proxy": {
            "negative_ux_fraction": neg_ux,
            "rho_std": rho_std,
            "ux_std": rho_std * 0.1,
        },
    }


def test_step117_timeseries_trend_summary_reports_tail_and_global_values():
    from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import summarize_timeseries_trends

    records = [
        _record(0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.02, 0.00, 0.001),
        _record(25, 0.98, 1.03, 0.01, 0.8, 0.1, 0.02, 0.04, 0.02, 0.002),
        _record(50, 0.96, 1.06, -0.02, 0.6, 0.3, 0.04, 0.06, 0.04, 0.003),
        _record(75, 0.94, 1.09, 0.03, 0.4, 0.5, 0.06, 0.08, 0.06, 0.004),
        _record(100, 0.93, 1.10, 0.04, 0.2, 0.7, 0.08, 0.10, 0.08, 0.006),
    ]

    summary = summarize_timeseries_trends(records, tail_fraction=0.4)

    assert summary["record_count"] == 5
    assert summary["tail_record_count"] == 2
    assert summary["rho_min_global"] == 0.93
    assert summary["rho_max_global"] == 1.10
    assert summary["mass_drift_final"] == 0.04
    assert summary["mass_drift_abs_max"] == 0.04
    assert summary["flux_imbalance_rel_final"] == 0.2
    assert math.isclose(summary["flux_imbalance_rel_tail_mean"], 0.3, rel_tol=0.0, abs_tol=1.0e-12)
    assert summary["outlet_flux_final"] == 0.7
    assert math.isclose(summary["outlet_flux_tail_mean"], 0.6, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(summary["midplane_mean_ux_tail_mean"], 0.07, rel_tol=0.0, abs_tol=1.0e-12)
    assert summary["max_v_global"] == 0.10
    assert summary["mach_proxy_observed_max"] > 0.0
    assert math.isclose(summary["negative_ux_fraction_tail_mean"], 0.07, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(summary["rho_std_outlet_tail_mean"], 0.005, rel_tol=0.0, abs_tol=1.0e-12)


def test_step117_timeseries_trend_summary_rejects_empty_records():
    from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import summarize_timeseries_trends

    with pytest.raises(ValueError, match="records"):
        summarize_timeseries_trends([])
