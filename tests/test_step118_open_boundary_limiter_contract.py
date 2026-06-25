import math
import sys
from pathlib import Path

import taichi as ti


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step118_lbm_config_accepts_opt_in_boundary_variants_and_validates_limiters():
    from src.mpm_lbm.sim.lbm.config import LBMConfig, VALID_LBM_OPEN_BOUNDARY_SEMANTICS

    assert "regularized_velocity_pressure_limited" in VALID_LBM_OPEN_BOUNDARY_SEMANTICS
    assert "convective_pressure_outlet_experimental" in VALID_LBM_OPEN_BOUNDARY_SEMANTICS

    default = LBMConfig(nx=4, ny=4, nz=4)
    assert default.open_boundary_limiter_enabled is False
    assert default.open_boundary_semantics == "equilibrium_all_population_reset"

    limited = LBMConfig(
        nx=4,
        ny=4,
        nz=4,
        open_boundary_semantics="regularized_velocity_pressure_limited",
        open_boundary_limiter_enabled=True,
        open_boundary_rho_min=0.8,
        open_boundary_rho_max=1.2,
        open_boundary_u_max=0.1,
        open_boundary_noneq_cap=0.05,
        open_boundary_population_floor=-1.0e-8,
    )
    assert limited.open_boundary_limiter_enabled is True
    assert math.isclose(limited.open_boundary_rho_min, 0.8)

    try:
        LBMConfig(
            nx=4,
            ny=4,
            nz=4,
            open_boundary_semantics="regularized_velocity_pressure_limited",
            open_boundary_limiter_enabled=True,
            open_boundary_rho_min=1.2,
            open_boundary_rho_max=0.8,
        )
    except ValueError as exc:
        assert "open_boundary_rho_min" in str(exc)
    else:
        raise AssertionError("invalid limiter rho range was accepted")


def test_step118_fsi_config_passes_boundary_variant_and_limiter_fields_to_lbm_config():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    cfg = FSIDriverConfig(
        lbm_open_boundary_semantics="regularized_velocity_pressure_limited",
        open_boundary_limiter_enabled=True,
        open_boundary_rho_min=0.75,
        open_boundary_rho_max=1.25,
        open_boundary_u_max=0.12,
        open_boundary_noneq_cap=0.04,
        open_boundary_population_floor=0.0,
    )
    unified = cfg.make_unified_sim_config()
    lbm = unified.make_lbm_config()

    assert unified.lbm_open_boundary_semantics == "regularized_velocity_pressure_limited"
    assert lbm.open_boundary_semantics == "regularized_velocity_pressure_limited"
    assert lbm.open_boundary_limiter_enabled is True
    assert math.isclose(lbm.open_boundary_rho_min, 0.75)
    assert math.isclose(lbm.open_boundary_population_floor, 0.0)


def test_step118_fluid_source_contains_limited_and_convective_x_boundary_branches():
    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")

    assert "REGULARIZED_VELOCITY_PRESSURE_LIMITED" in source
    assert "CONVECTIVE_PRESSURE_OUTLET_EXPERIMENTAL" in source
    assert "def _limit_open_boundary_rho" in source
    assert "def _limit_open_boundary_velocity" in source
    assert "def _limited_regularized_population" in source
    assert "def apply_regularized_limited_x_open_boundaries" in source
    assert "def apply_convective_pressure_outlet_x_open_boundaries" in source

    regularized_start = source.index("def apply_regularized_x_open_boundaries")
    limited_start = source.index("def apply_regularized_limited_x_open_boundaries")
    regularized_body = source[regularized_start:limited_start]
    assert "open_boundary_population_floor" not in regularized_body


def test_step118_limited_and_convective_boundary_dispatch_is_explicit_without_touching_legacy_runtime():
    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    boundary_start = source.index("def Boundary_condition")
    boundary_end = source.index("def Boundary_condition_legacy")
    dispatch_body = source[boundary_start:boundary_end]

    assert "REGULARIZED_VELOCITY_PRESSURE_LIMITED" in dispatch_body
    assert "CONVECTIVE_PRESSURE_OUTLET_EXPERIMENTAL" in dispatch_body
    assert "self.apply_regularized_limited_x_open_boundaries()" in dispatch_body
    assert "self.apply_convective_pressure_outlet_x_open_boundaries()" in dispatch_body
    assert "self.Boundary_condition_legacy()" in dispatch_body
