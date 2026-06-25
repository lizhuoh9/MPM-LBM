import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step114_physical_viscosity_mapping_uses_standard_lattice_formula():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.lbm.relaxation_semantics import STANDARD_LATTICE_KINEMATIC_VISCOSITY

    config = FSIDriverConfig(
        coupling_mode="moving_boundary",
        lbm_boundary_condition_mode="duct_velocity_inlet_pressure_outlet",
        geometry_type="duct_flap_proxy",
        geometry_config_path="outputs/step113_full_fsi_mirrored_duct_flap_96_stabilized/mirrored_duct_flap_geometry_96_8192.json",
        n_grid=96,
        n_particles=8192,
        physical_duct_length_m=0.1,
        target_inlet_velocity_mps=10.0,
        official_fsi_dt_s=0.0005,
        target_u_lbm_for_dimensional_mapping=0.02,
        target_u_lbm=[0.02, 0.0, 0.0],
        fsi_exchange_mode="lbm_subcycled_per_fsi_step",
        lbm_substeps_per_fsi_step=240,
        lbm_dt_phys_override_s=2.0833333333333334e-06,
        lbm_viscosity_semantics="physical_nu_mapping",
        fluid_kinematic_viscosity_m2_s=1.5e-5,
        fluid_density_kg_m3=1.225,
    )

    mapping = config.lbm_viscosity_mapping_report()
    dx_phys = 0.1 / 96.0
    expected_nu_lbm = 1.5e-5 * 2.0833333333333334e-06 / (dx_phys * dx_phys)
    expected_tau = 3.0 * expected_nu_lbm + 0.5

    assert math.isclose(mapping["nu_lbm"], expected_nu_lbm, rel_tol=1.0e-12)
    assert math.isclose(mapping["tau"], expected_tau, rel_tol=1.0e-12)
    assert mapping["lbm_relaxation_semantics"] == STANDARD_LATTICE_KINEMATIC_VISCOSITY
    assert config.make_unified_sim_config().lbm_niu == mapping["nu_lbm"]


def test_step114_legacy_viscosity_mapping_preserves_default_semantics():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.lbm.relaxation_semantics import LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER

    config = FSIDriverConfig()
    mapping = config.lbm_viscosity_mapping_report()

    assert mapping["lbm_viscosity_semantics"] == "legacy_external"
    assert mapping["lbm_relaxation_semantics"] == LEGACY_EXTERNAL_SOLVER_RELAXATION_PARAMETER
    assert mapping["legacy_lbm_niu"] == 0.1
    assert config.make_unified_sim_config().lbm_niu == 0.1


def test_step114_physical_viscosity_mapping_rejects_invalid_values():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    for kwargs in (
        {"lbm_viscosity_semantics": "physical_nu_mapping", "fluid_kinematic_viscosity_m2_s": 0.0},
        {"lbm_viscosity_semantics": "physical_nu_mapping", "fluid_density_kg_m3": -1.0},
        {"lbm_viscosity_semantics": "not_a_semantics"},
    ):
        try:
            FSIDriverConfig(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid viscosity mapping accepted: {kwargs}")


def test_step114_subcycled_driver_uses_accumulated_mean_force_before_mpm_reaction():
    driver_source = (ROOT / "src" / "mpm_lbm" / "sim" / "drivers" / "fsi_driver.py").read_text(encoding="utf-8")
    fluid_source = (ROOT / "src" / "mpm_lbm" / "sim" / "lbm" / "fluid.py").read_text(encoding="utf-8")

    assert "clear_moving_boundary_force_accumulator" in fluid_source
    assert "accumulate_moving_boundary_force_sample" in fluid_source
    assert "finalize_moving_boundary_force_accumulator" in fluid_source
    assert "get_moving_boundary_accumulation_stats" in fluid_source

    subcycled_start = driver_source.index("def _step_moving_boundary_subcycled")
    subcycled_end = driver_source.index("def _advance_mpm_with_moving_boundary_reaction")
    subcycled_body = driver_source[subcycled_start:subcycled_end]

    assert subcycled_body.index("clear_moving_boundary_force_accumulator") < subcycled_body.index(
        "step_moving_bounceback"
    )
    assert subcycled_body.index("accumulate_moving_boundary_force_sample") > subcycled_body.index(
        "step_moving_bounceback"
    )
    assert subcycled_body.index("finalize_moving_boundary_force_accumulator") < subcycled_body.index(
        "_advance_mpm_with_moving_boundary_reaction"
    )
    assert "mb_subcycle_force_sample_count" in driver_source
    assert "mb_subcycle_force_mean_norm_max" in driver_source


def test_step114_fluent_like_monitor_helper_selects_nearest_particles():
    from src.mpm_lbm.sim.monitoring.fluent_like import official_point_like_displacement

    initial = np.array(
        [
            [0.50, 0.40, 0.50],
            [0.51, 0.40, 0.50],
            [0.70, 0.40, 0.50],
        ],
        dtype=np.float64,
    )
    current = initial.copy()
    current[0] += np.array([0.01, 0.00, 0.00])
    current[1] += np.array([0.03, 0.04, 0.00])
    current[2] += np.array([0.50, 0.00, 0.00])

    result = official_point_like_displacement(
        initial,
        current,
        target_point_norm=np.array([0.505, 0.40, 0.50], dtype=np.float64),
        nearest_count=2,
        scale_m=0.1,
    )

    assert result["selected_particle_count"] == 2
    assert result["selected_particle_indices"] == [0, 1]
    assert math.isclose(result["official_point_like_x_displacement_m"], 0.002, rel_tol=1.0e-12)
    assert math.isclose(result["official_point_like_y_displacement_m"], 0.002, rel_tol=1.0e-12)
    assert result["monitor_is_direct_fluent_equivalent"] is False


def test_step114_guard_fields_make_unimplemented_fluent_parity_modes_fail_fast():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    accepted = FSIDriverConfig(
        lbm_open_boundary_semantics="equilibrium_all_population_reset",
        solid_model="finite_deformation_mpm",
        solid_dimensionality="three_dimensional",
        flow_dimensionality_mode="three_dimensional",
        reaction_transfer_mode="engineering",
    )
    assert accepted.lbm_open_boundary_semantics == "equilibrium_all_population_reset"

    for kwargs in (
        {"lbm_open_boundary_semantics": "zou_he_reconstruct_unknowns"},
        {"solid_model": "small_strain_linear_elastic"},
        {"solid_dimensionality": "plane_strain_2d"},
        {"reaction_transfer_mode": "interface_traction_conservative"},
        {"flow_dimensionality_mode": "d2q9_planar"},
    ):
        try:
            FSIDriverConfig(**kwargs)
        except ValueError:
            pass
        else:
            raise AssertionError(f"unimplemented Fluent-parity mode did not fail fast: {kwargs}")
