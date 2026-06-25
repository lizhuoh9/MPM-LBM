import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _snapshot():
    rho = np.ones((4, 3, 2), dtype=float)
    velocity = np.zeros((4, 3, 2, 3), dtype=float)
    solid = np.zeros((4, 3, 2), dtype=np.int8)
    velocity[..., 0] = 0.1
    solid[1, 1, 0] = 1
    rho[2, 2, 1] = 1.2
    return {"rho": rho, "v": velocity, "solid": solid}


def test_step116_fluid_mask_and_flux_ignore_solid_cells():
    from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import fluid_mask, plane_flux_x

    snapshot = _snapshot()
    mask = fluid_mask(snapshot)

    assert mask.shape == (4, 3, 2)
    assert mask[1, 1, 0] is np.False_
    assert mask[0, 0, 0] is np.True_
    assert math.isclose(plane_flux_x(snapshot, 1), 0.5, rel_tol=0.0, abs_tol=1.0e-12)


def test_step116_density_mass_centerline_and_outlet_proxy_schema():
    from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import (
        centerline_profile_x,
        density_stats,
        mass_total,
        outlet_reflection_proxy,
        summarize_lbm_boundary_diagnostics,
    )

    snapshot = _snapshot()

    density = density_stats(snapshot)
    assert density["fluid_cell_count"] == 23
    assert math.isclose(density["rho_min"], 1.0, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isclose(density["rho_max"], 1.2, rel_tol=0.0, abs_tol=1.0e-12)
    assert math.isfinite(density["rho_mean"])
    assert math.isclose(mass_total(snapshot), 23.2, rel_tol=0.0, abs_tol=1.0e-12)

    profile = centerline_profile_x(snapshot)
    assert profile["axis"] == "x"
    assert len(profile["ux"]) == 4
    assert all(math.isfinite(value) for value in profile["ux"])

    outlet = outlet_reflection_proxy(snapshot)
    assert outlet["proxy_name"] == "outlet_near_plane_ux_density_variation"
    assert 0.0 <= outlet["negative_ux_fraction"] <= 1.0
    assert math.isfinite(outlet["ux_std"])

    summary = summarize_lbm_boundary_diagnostics(snapshot, step=7, mass_initial=24.0)
    assert summary["step"] == 7
    assert math.isclose(summary["mass_total_delta_from_initial"], -0.8, rel_tol=0.0, abs_tol=1.0e-12)
    assert summary["flux_balance_reported"] is True
    assert "centerline_ux_profile" in summary
    assert "outlet_reflection_proxy" in summary
