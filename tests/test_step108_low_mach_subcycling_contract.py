import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step108_mapping_reports_10mps_with_ulbm_0p02():
    policy = read_json("configs/step108_low_mach_subcycling_policy.json")
    mapping = read_json("outputs/step108_dimensional_mapping/low_mach_subcycling_mapping_report.json")

    assert policy["required_step_name"] == "Step108 Fluent Duct-Flap Official-Speed Low-Mach Subcycling Smoke"
    assert policy["reference_source_url"].startswith("https://ansyshelp.ansys.com/")
    assert policy["low_mach_mapping_enabled"] is True
    assert policy["physical_duct_length_m"] == 0.1
    assert policy["n_grid"] == 48
    assert policy["target_inlet_velocity_mps"] == 10.0
    assert policy["target_u_lbm"] == 0.02
    assert policy["official_fsi_dt_s"] == 0.0005
    assert policy["lbm_substeps_per_fsi_step"] == 120
    assert math.isclose(policy["lbm_dt_phys_s"], 4.166666666666667e-6, rel_tol=0.0, abs_tol=1.0e-18)

    assert mapping["low_mach_mapping_enabled"] is True
    assert mapping["n_grid"] == 48
    assert math.isclose(mapping["dx_phys_m"], 0.1 / 48.0, rel_tol=0.0, abs_tol=1.0e-18)
    assert mapping["target_inlet_velocity_mps"] == 10.0
    assert mapping["target_u_lbm"] == 0.02
    assert mapping["lbm_substeps_per_fsi_step"] == 120
    assert math.isclose(mapping["lbm_dt_phys_s"], 4.166666666666667e-6, rel_tol=0.0, abs_tol=1.0e-18)
    assert 9.99 <= mapping["mapped_inlet_velocity_mps"] <= 10.01
    assert abs(mapping["mapped_velocity_error_mps"]) <= 1.0e-9
    assert mapping["mapping_pass"] is True


def test_step108_driver_config_requires_subcycling_120_and_preserves_default_path():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.sim_config import UnifiedSimConfig

    default_config = FSIDriverConfig()
    assert default_config.fsi_exchange_mode == "one_lbm_step_per_fsi_step"
    assert default_config.lbm_substeps_per_fsi_step == 1
    assert default_config.official_fsi_dt_s is None
    assert default_config.lbm_dt_phys_override_s is None
    assert math.isclose(default_config.make_unified_sim_config().lbm_dt_phys, 0.004, rel_tol=0.0, abs_tol=1.0e-15)

    sim_config = UnifiedSimConfig(mpm_dt=0.0005, mpm_substeps_per_lbm_step=1, lbm_dt_phys_override_s=4.166666666666667e-6)
    assert math.isclose(sim_config.lbm_dt_phys, 4.166666666666667e-6, rel_tol=0.0, abs_tol=1.0e-18)

    candidate = FSIDriverConfig.from_json(ROOT / "configs/step108_fluent_duct_flap_low_mach_subcycling_48_50step_candidate.json")
    assert candidate.fsi_exchange_mode == "lbm_subcycled_per_fsi_step"
    assert candidate.physical_duct_length_m == 0.1
    assert candidate.target_inlet_velocity_mps == 10.0
    assert candidate.official_fsi_dt_s == 0.0005
    assert candidate.target_u_lbm_for_dimensional_mapping == 0.02
    assert candidate.lbm_substeps_per_fsi_step == 120
    assert math.isclose(candidate.lbm_dt_phys_override_s, 4.166666666666667e-6, rel_tol=0.0, abs_tol=1.0e-18)
    assert candidate.make_unified_sim_config().lbm_dt_phys == candidate.lbm_dt_phys_override_s


def test_step108_duct_only_low_mach_precheck_is_finite():
    config = read_json("configs/step108_duct_only_low_mach_subcycling_48_50official_steps.json")
    payload = read_json("outputs/step108_duct_only_low_mach_subcycling/flow_plane_report.json")
    summary = payload["summary"]
    row = payload["rows"][0]

    assert config["official_steps"] == 50
    assert config["lbm_substeps_per_fsi_step"] == 120
    assert config["total_lbm_substeps"] == 6000
    assert config["target_u_lbm"] == [0.02, 0.0, 0.0]

    assert summary["duct_only_low_mach_subcycling_pass"] is True
    assert row["completed_official_steps"] == 50
    assert row["completed_lbm_substeps"] == 6000
    assert row["low_mach_mapping_enabled"] is True
    assert 0.019 <= row["inlet_plane_mean_ux_final"] <= 0.021
    assert row["mid_duct_plane_mean_ux_final"] > 1.0e-4
    assert row["outlet_plane_mean_ux_final"] > 1.0e-4
    assert row["rho_min_final"] > 0.90
    assert row["rho_max_final"] < 1.20
    assert row["has_nan"] is False
    assert row["has_inf"] is False
    assert finite_numeric_row(row)


def test_step108_solver_curve_covers_0p025s_without_endpoint_hold():
    report = read_json("outputs/step108_low_mach_fsi_candidate/low_mach_fsi_report.json")
    row = report["rows"][0]
    summary = report["summary"]
    curve = read_csv("outputs/step108_low_mach_fsi_candidate/flap_tip_displacement_timeseries.csv")

    assert summary["step108_low_mach_fsi_candidate_pass"] is True
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["completed_official_fsi_steps"] == 50
    assert row["completed_lbm_substeps"] == 6000
    assert row["flap_tip_timeseries_row_count"] == 51
    assert row["solver_curve_time_start_s"] == 0.0
    assert row["solver_curve_time_end_s"] == 0.025
    assert row["fixed_base_max_displacement_norm"] <= 1.0e-7
    assert row["fixed_base_max_velocity_norm"] <= 1.0e-7
    assert row["step36_squid_wall_velocity_config_used"] is False
    assert row["has_nan"] is False
    assert row["has_inf"] is False
    assert row["validation_claim_allowed"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert finite_numeric_row(row)

    assert len(curve) == 51
    assert math.isclose(float(curve[0]["time_s"]), 0.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(float(curve[-1]["time_s"]), 0.025, rel_tol=0.0, abs_tol=1.0e-15)
    assert sorted(float(row["time_s"]) for row in curve) == [float(row["time_s"]) for row in curve]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def finite_numeric_row(row: dict) -> bool:
    for value in row.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        if not math.isfinite(float(value)):
            return False
    return True
