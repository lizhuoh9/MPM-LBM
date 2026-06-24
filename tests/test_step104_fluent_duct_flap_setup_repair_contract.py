import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
from src.mpm_lbm.sim.geometry.config import GeometryConfig
from src.mpm_lbm.sim.geometry.sampler import GeometrySampler3D


STEP104_ROW = "fluent_duct_flap_setup_repair_48_5step_smoke"


def test_fsidriver_config_separates_target_u_from_initial_solid_velocity():
    config = FSIDriverConfig(target_u_lbm=[0.02, 0.0, 0.0])

    assert config.target_u_lbm == (0.02, 0.0, 0.0)
    assert config.initial_solid_velocity_norm == (0.0, 0.0, 0.0)


def test_step104_config_represents_official_problem_setup_repair():
    config = read_json("configs/step104_fluent_duct_flap_setup_repair_48_5step_smoke.json")

    assert config["geometry_type"] == "duct_flap_proxy"
    assert config["geometry_config_path"] == "configs/step104_fluent_duct_flap_geometry_1024.json"
    assert config["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert config["initial_solid_velocity_norm"] == [0.0, 0.0, 0.0]
    assert config["lbm_boundary_condition_mode"] == "duct_velocity_inlet_pressure_outlet"
    assert config["wall_velocity_application_mode"] == "disabled"
    assert config["wall_velocity_application_config_path"] is None
    assert "step36_wall_velocity_application_solid_vel_experimental" not in json.dumps(config)


def test_step104_geometry_sampler_exposes_fixed_base_and_tip_masks():
    geometry = GeometryConfig.from_json(str(ROOT / "configs/step104_fluent_duct_flap_geometry_1024.json"))
    cloud = GeometrySampler3D(geometry).sample_particles()

    assert cloud["x"].shape == (1024, 3)
    assert cloud["fixed_base_mask"].shape == (1024,)
    assert cloud["free_tip_proxy_mask"].shape == (1024,)
    assert int(np.count_nonzero(cloud["fixed_base_mask"])) > 0
    assert int(np.count_nonzero(cloud["free_tip_proxy_mask"])) > 0
    assert geometry.material_reference["used_for_mpm_config"] is True
    assert geometry.material_reference["density"] == 1600.0
    assert geometry.material_reference["youngs_modulus"] == 1000000.0
    assert geometry.material_reference["poisson_ratio"] == 0.47


def test_step104_setup_repair_report_passes_and_is_gap_only():
    payload = read_json("outputs/step104_fluent_duct_flap_setup_repair/setup_repair_report.json")
    summary = payload["summary"]
    row = payload["rows"][0]

    assert summary["step104_setup_repair_pass"] is True
    assert row["row_name"] == STEP104_ROW
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["target_u_lbm_applied_to_solid_initial_velocity"] is False
    assert row["initial_solid_velocity_norm"] == [0.0, 0.0, 0.0]
    assert row["target_u_lbm_applied_to_inlet"] is True
    assert row["lbm_boundary_condition_mode"] == "duct_velocity_inlet_pressure_outlet"
    assert row["all_fluid_geometry_used"] is False
    assert row["geo_path_name"] == "geo_duct_flap_proxy_48.dat"
    assert row["fixed_base_particle_count"] > 0
    assert row["fixed_base_constraint_applied"] is True
    assert row["fixed_base_max_displacement_norm"] <= 1.0e-7
    assert row["fixed_base_max_velocity_norm"] <= 1.0e-7
    assert row["material_reference_used_for_mpm_config"] is True
    assert row["mpm_p_rho"] == 1600.0
    assert row["mpm_young_modulus"] == 1000000.0
    assert row["mpm_poisson_ratio"] == 0.47
    assert row["step36_squid_wall_velocity_config_used"] is False
    assert row["proxy_flap_tip_displacement_available"] is True
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert row["validation_claim_allowed"] is False
    assert row["stable"] is True


def test_step104_boundary_and_static_geometry_reports_are_not_all_fluid():
    boundary = read_json("outputs/step104_fluent_duct_flap_setup_repair/duct_boundary_condition_report.json")
    geometry = read_json("outputs/step104_fluent_duct_flap_setup_repair/duct_static_geometry_report.json")

    assert boundary["target_u_lbm_applied_to_inlet"] is True
    assert boundary["bc_x_left"] == 2
    assert boundary["bc_x_right"] == 1
    assert boundary["velocity_inlet_cell_count"] > 0
    assert boundary["pressure_outlet_cell_count"] > 0
    assert boundary["periodic_boundary_used"] is False
    assert geometry["all_fluid_geometry_used"] is False
    assert geometry["duct_wall_cell_count"] > 0
    assert geometry["fluid_cell_count"] > 0
    assert geometry["solid_cell_count"] > 0


def test_step104_flap_tip_timeseries_schema_is_committed():
    rows = read_csv("outputs/step104_fluent_duct_flap_setup_repair/flap_tip_displacement_timeseries.csv")

    assert rows
    assert list(rows[0].keys()) == [
        "step",
        "time_s",
        "flap_tip_total_displacement_m",
        "flap_tip_x_displacement_m",
        "flap_tip_y_displacement_m",
    ]
    assert rows[0]["step"] == "0"
    assert rows[-1]["step"] == "5"


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
