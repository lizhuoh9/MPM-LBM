import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DUCT_ROW = "duct_only_lbm_outlet_boundary_flow_48"
FSI_ROW = "fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke"


def test_step106_configs_pin_outlet_repair_scope():
    policy = read_json("configs/step106_outlet_boundary_flow_policy.json")
    duct_config = read_json("configs/step106_duct_only_lbm_outlet_boundary_flow_48.json")
    fsi_config = read_json("configs/step106_fluent_duct_flap_proxy_48_20step_outlet_repair_regression_smoke.json")

    assert policy["required_duct_row_name"] == DUCT_ROW
    assert policy["pressure_outlet_policy"] == "interior_neighbor_velocity_extrapolation"
    assert policy["min_outlet_plane_mean_ux"] == 1.0e-5
    assert policy["min_outlet_plane_max_ux"] == 1.0e-5
    assert policy["min_mid_duct_plane_mean_ux"] == 1.0e-4
    assert policy["inlet_plane_mean_ux_range"] == [0.015, 0.025]
    assert policy["rho_min_lower_bound"] == 0.95
    assert policy["rho_max_upper_bound"] == 1.10
    assert policy["direct_quantitative_equivalence_allowed"] is False
    assert policy["validation_claim_allowed"] is False

    assert duct_config["row_name"] == DUCT_ROW
    assert duct_config["n_grid"] == 48
    assert duct_config["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert duct_config["bc_x_left"] == 2
    assert duct_config["bc_x_right"] == 1
    assert duct_config["rho_bc_x_right"] == 1.0
    assert duct_config["geometry_config_path"] == "configs/step104_fluent_duct_flap_geometry_1024.json"
    assert duct_config["geometry_type"] == "duct_flap_proxy"
    assert duct_config["include_flap_in_lbm_static_geometry"] is False
    assert duct_config["pressure_outlet_velocity_policy"] == "interior_neighbor_velocity_extrapolation"
    assert duct_config["write_vtk"] is False
    assert duct_config["write_particles"] is False

    assert fsi_config["geometry_type"] == "duct_flap_proxy"
    assert fsi_config["geometry_config_path"] == "configs/step104_fluent_duct_flap_geometry_1024.json"
    assert fsi_config["n_grid"] == 48
    assert fsi_config["n_particles"] == 1024
    assert fsi_config["n_lbm_steps"] == 20
    assert fsi_config["mpm_dt"] == 0.0005
    assert fsi_config["mpm_substeps_per_lbm_step"] == 1
    assert fsi_config["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert fsi_config["initial_solid_velocity_norm"] == [0.0, 0.0, 0.0]
    assert fsi_config["lbm_boundary_condition_mode"] == "duct_velocity_inlet_pressure_outlet"
    assert fsi_config["wall_velocity_application_mode"] == "disabled"
    assert fsi_config["wall_velocity_application_config_path"] is None
    assert fsi_config["write_vtk"] is False
    assert fsi_config["write_particles"] is False


def test_step106_source_uses_interior_neighbor_for_x_right_pressure_outlet():
    source = (ROOT / "src/mpm_lbm/sim/lbm/fluid.py").read_text(encoding="utf-8")
    branch = source.split("if ti.static(self.bc_x_right==1):", 1)[1].split(
        "if ti.static(self.bc_x_right==2):", 1
    )[0]

    assert "self.feq(s, self.rho_bcxr, self.v[self.nx-2,j,k])" in branch
    assert "self.feq(s, self.rho_bcxr, self.v[self.nx-1,j,k])" not in branch


def test_step106_duct_only_report_proves_outlet_flow_without_fluent_claims():
    payload = read_json("outputs/step106_outlet_boundary_flow_propagation/flow_plane_report.json")
    row = payload["rows"][0]
    summary = payload["summary"]

    assert summary["duct_only_outlet_boundary_flow_pass"] is True
    assert row["row_name"] == DUCT_ROW
    assert row["n_grid"] == 48
    assert row["bc_x_left"] == 2
    assert row["bc_x_right"] == 1
    assert row["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert row["pressure_outlet_policy"] == "interior_neighbor_velocity_extrapolation"
    assert row["completed_lbm_steps"] == row["n_lbm_steps"]
    assert row["outlet_plane_mean_ux_final"] > 1.0e-5
    assert row["outlet_plane_max_ux_final"] > 1.0e-5
    assert row["mid_duct_plane_mean_ux_final"] > 1.0e-4
    assert 0.015 <= row["inlet_plane_mean_ux_final"] <= 0.025
    assert row["rho_min_final"] > 0.95
    assert row["rho_max_final"] < 1.10
    assert row["has_nan"] is False
    assert row["has_inf"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert row["validation_claim_allowed"] is False
    assert finite_numeric_row(row)

    timeseries = read_csv("outputs/step106_outlet_boundary_flow_propagation/flow_plane_timeseries.csv")
    assert len(timeseries) == row["n_lbm_steps"] + 1
    assert timeseries[-1]["step"] == str(row["n_lbm_steps"])


def test_step106_boundary_semantics_report_records_repaired_outlet_policy():
    semantics = read_json("outputs/step106_outlet_boundary_flow_propagation/boundary_condition_semantics_report.json")

    assert semantics["bc_x_left"] == 2
    assert semantics["bc_x_right"] == 1
    assert semantics["velocity_inlet_policy"] == "fixed_equilibrium_velocity"
    assert semantics["pressure_outlet_policy"] == "interior_neighbor_velocity_extrapolation"
    assert semantics["pressure_outlet_uses_boundary_self_velocity"] is False
    assert semantics["pressure_outlet_uses_interior_neighbor_velocity"] is True
    assert semantics["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert semantics["rho_bc_x_right"] == 1.0
    assert semantics["direct_quantitative_equivalence_allowed"] is False
    assert semantics["validation_claim_allowed"] is False


def test_step106_fsi_regression_smoke_preserves_step105_boundaries():
    payload = read_json("outputs/step106_fsi_outlet_repair_regression/fsi_outlet_repair_regression_report.json")
    row = payload["rows"][0]
    summary = payload["summary"]

    assert summary["step106_fsi_outlet_repair_regression_pass"] is True
    assert row["row_name"] == FSI_ROW
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["completed_lbm_steps"] == 20
    assert row["n_grid"] == 48
    assert row["n_particles"] == 1024
    assert row["diagnostics_row_count"] >= 21
    assert row["flap_tip_timeseries_row_count"] >= 21
    assert row["target_u_lbm_applied_to_inlet"] is True
    assert row["target_u_lbm_applied_to_solid_initial_velocity"] is False
    assert row["fixed_base_constraint_applied"] is True
    assert row["fixed_base_max_displacement_norm"] <= 1.0e-7
    assert row["fixed_base_max_velocity_norm"] <= 1.0e-7
    assert row["step36_squid_wall_velocity_config_used"] is False
    assert row["has_nan"] is False
    assert row["has_inf"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert row["validation_claim_allowed"] is False
    assert row["gap_count"] >= 8
    assert row["stable"] is True

    tip_rows = read_csv("outputs/step106_fsi_outlet_repair_regression/flap_tip_displacement_timeseries.csv")
    assert tip_rows[0]["step"] == "0"
    assert tip_rows[-1]["step"] == "20"


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
