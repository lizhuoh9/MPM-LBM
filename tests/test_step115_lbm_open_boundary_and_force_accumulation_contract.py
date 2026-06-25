import json
import math
import sys
from pathlib import Path

import numpy as np
import taichi as ti


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _read_json(path: str):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


@ti.kernel
def _write_hydro_force_sample(lbm: ti.template(), i: ti.i32, j: ti.i32, k: ti.i32, fx: ti.f32, fy: ti.f32, fz: ti.f32):
    lbm.hydro_force[i, j, k] = ti.Vector([fx, fy, fz])


def test_step115_runtime_force_accumulator_averages_real_kernel_samples():
    from src.mpm_lbm.sim.lbm.config import LBMConfig
    from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D

    ti.init(arch=ti.cpu, cpu_max_num_threads=1)
    lbm = LBMFluid3D(LBMConfig(nx=4, ny=4, nz=4))

    lbm.clear_moving_boundary_force_accumulator()
    _write_hydro_force_sample(lbm, 1, 1, 1, 1.0, 0.0, 0.0)
    lbm.accumulate_moving_boundary_force_sample()
    _write_hydro_force_sample(lbm, 1, 1, 1, 3.0, 0.0, 0.0)
    lbm.accumulate_moving_boundary_force_sample()
    lbm.finalize_moving_boundary_force_accumulator()

    hydro = lbm.hydro_force.to_numpy()
    stats = lbm.get_moving_boundary_accumulation_stats()

    assert np.allclose(hydro[1, 1, 1], [2.0, 0.0, 0.0], rtol=0.0, atol=1.0e-6)
    assert stats["mb_subcycle_force_sample_count"] == 2
    assert math.isclose(stats["mb_subcycle_force_accum_norm_max"], 4.0, rel_tol=0.0, abs_tol=1.0e-6)
    assert math.isclose(stats["mb_subcycle_force_mean_norm_max"], 2.0, rel_tol=0.0, abs_tol=1.0e-6)


def test_step115_non_subcycled_moving_boundary_path_does_not_use_accumulator():
    source = (ROOT / "src/mpm_lbm/sim/drivers/fsi_driver.py").read_text(encoding="utf-8")
    start = source.index("def _step_moving_boundary(self):")
    end = source.index("def _step_moving_boundary_subcycled(self):")
    body = source[start:end]

    assert "clear_moving_boundary_force_accumulator" not in body
    assert "accumulate_moving_boundary_force_sample" not in body
    assert "finalize_moving_boundary_force_accumulator" not in body


def test_step115_regularized_open_boundary_is_opt_in_and_legacy_default_is_preserved():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    legacy = FSIDriverConfig()
    assert legacy.lbm_open_boundary_semantics == "equilibrium_all_population_reset"
    assert legacy.make_unified_sim_config().make_lbm_config().open_boundary_semantics == "equilibrium_all_population_reset"

    regularized = FSIDriverConfig(lbm_open_boundary_semantics="regularized_velocity_pressure")
    assert regularized.lbm_open_boundary_semantics == "regularized_velocity_pressure"
    assert regularized.make_unified_sim_config().lbm_open_boundary_semantics == "regularized_velocity_pressure"
    assert regularized.make_unified_sim_config().make_lbm_config().open_boundary_semantics == "regularized_velocity_pressure"

    try:
        FSIDriverConfig(lbm_open_boundary_semantics="zou_he_reconstruct_unknowns")
    except ValueError as exc:
        assert "not implemented" in str(exc)
    else:
        raise AssertionError("zou_he_reconstruct_unknowns should remain fail-fast in Step115")


def test_step115_regularized_x_boundary_reconstructs_unknown_populations_only():
    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")

    assert "self.open_boundary_semantics" in source
    assert "regularized_velocity_pressure" in source
    assert "apply_regularized_x_open_boundaries" in source
    assert "UNKNOWN_X_MIN_POPULATIONS" in source
    assert "UNKNOWN_X_MAX_POPULATIONS" in source

    regularized_start = source.index("def apply_regularized_x_open_boundaries")
    regularized_end = source.index("def streaming3")
    regularized_body = source[regularized_start:regularized_end]

    assert "for s in ti.static(UNKNOWN_X_MIN_POPULATIONS)" in regularized_body
    assert "for s in ti.static(UNKNOWN_X_MAX_POPULATIONS)" in regularized_body
    assert "for s in ti.static(range(19))" not in regularized_body
    assert "self.feq(s, self.rho_bcxl" not in regularized_body
    assert "self.feq(s,1.0,ti.Vector(self.bc_vel_x_left))" not in regularized_body


def test_step115_regularized_open_boundary_runtime_smoke_is_finite():
    from src.mpm_lbm.sim.lbm.config import LBMConfig
    from src.mpm_lbm.sim.lbm.fluid import LBMFluid3D

    ti.init(arch=ti.cpu, cpu_max_num_threads=1)
    lbm = LBMFluid3D(
        LBMConfig(
            nx=6,
            ny=4,
            nz=4,
            open_boundary_semantics="regularized_velocity_pressure",
            bc_x_left=2,
            bc_x_right=1,
            vel_bc_x_left=(0.02, 0.0, 0.0),
            rho_bc_x_right=1.0,
        )
    )
    lbm.init_simulation()

    for _ in range(3):
        lbm.step()

    stats = lbm.get_stats()
    assert math.isfinite(stats["rho_min"])
    assert math.isfinite(stats["rho_max"])
    assert math.isfinite(stats["max_v"])
    assert 0.8 < stats["rho_min"] < 1.2
    assert 0.8 < stats["rho_max"] < 1.2


def test_step115_tau_feasibility_guard_reports_near_half_tau_and_strict_rejects():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig

    risky = FSIDriverConfig(
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
        lbm_min_tau_margin=1.0e-4,
        lbm_tau_stability_policy="report_only",
        fluid_kinematic_viscosity_m2_s=1.5e-5,
        fluid_density_kg_m3=1.225,
        target_reynolds_number=26666.666666666668,
    )

    mapping = risky.lbm_viscosity_mapping_report()
    assert mapping["tau"] > 0.5
    assert mapping["tau_minus_half"] < mapping["lbm_min_tau_margin"]
    assert mapping["tau_margin_pass"] is False
    assert mapping["lbm_tau_stability_policy"] == "report_only"
    assert mapping["physical_reynolds_direct_simulation_feasible_with_current_lbm"] is False
    assert math.isclose(mapping["reynolds_from_config"], 26666.666666666668, rel_tol=1.0e-12)
    assert mapping["target_reynolds_match"] is True

    try:
        FSIDriverConfig(
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
            lbm_min_tau_margin=1.0e-4,
            lbm_tau_stability_policy="strict",
            fluid_kinematic_viscosity_m2_s=1.5e-5,
            fluid_density_kg_m3=1.225,
            target_reynolds_number=26666.666666666668,
        )
    except ValueError as exc:
        assert "tau stability margin" in str(exc)
    else:
        raise AssertionError("strict tau stability policy accepted a near-half tau mapping")


def test_step115_boundary_report_fields_are_emitted_by_driver():
    report = _read_json("outputs/step115_lbm_open_boundary_repair/boundary_condition_semantics_report.json")

    assert report["lbm_open_boundary_semantics"] == "regularized_velocity_pressure"
    assert report["unknown_population_reconstruction_used"] is True
    assert report["all_population_equilibrium_reset_used"] is False
    assert report["implemented_axis"] == "x"
    assert report["boundary_condition_equivalence_claim_allowed"] is False
    assert report["validation_claim_allowed"] is False


def test_step115_solver_report_records_scope_and_no_fluent_claim():
    report = _read_json("outputs/step115_lbm_open_boundary_repair/solver_report.json")
    tau = _read_json("outputs/step115_lbm_open_boundary_repair/tau_feasibility_report.json")

    assert report["step"] == 115
    assert report["fluent_validation_claim_allowed"] is False
    assert report["regularized_velocity_pressure_implemented"] is True
    assert report["runtime_accumulator_test_added"] is True
    assert report["full_fsi_rerun_done"] is False
    assert tau["tau_margin_pass"] is False
    assert tau["physical_reynolds_direct_simulation_feasible_with_current_lbm"] is False
