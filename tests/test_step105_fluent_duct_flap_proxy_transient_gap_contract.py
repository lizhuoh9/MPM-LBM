import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP105_ROW = "fluent_duct_flap_proxy_48_50step_transient_gap_smoke"
REQUIRED_GAPS = {
    "dimensionality_2D_vs_3D",
    "conformal_mesh_equivalence",
    "linear_elasticity_equivalence",
    "dynamic_mesh_equivalence",
    "exact_fluent_monitor_equivalence",
    "dimensional_velocity_mapping",
    "turbulence_or_fluid_model_equivalence",
    "steady_preflow_initial_condition",
}


def test_step105_config_preserves_step104_setup_and_extends_to_50_steps():
    config = read_json("configs/step105_fluent_duct_flap_proxy_48_50step_transient_gap_smoke.json")

    assert config["geometry_type"] == "duct_flap_proxy"
    assert config["geometry_config_path"] == "configs/step104_fluent_duct_flap_geometry_1024.json"
    assert config["n_grid"] == 48
    assert config["n_particles"] == 1024
    assert config["n_lbm_steps"] == 50
    assert config["mpm_dt"] == 0.0005
    assert config["output_interval"] == 1
    assert config["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert config["initial_solid_velocity_norm"] == [0.0, 0.0, 0.0]
    assert config["lbm_boundary_condition_mode"] == "duct_velocity_inlet_pressure_outlet"
    assert config["wall_velocity_application_mode"] == "disabled"
    assert config["wall_velocity_application_config_path"] is None
    assert config["write_vtk"] is False
    assert config["write_particles"] is False


def test_step105_dimensional_mapping_report_records_velocity_gap():
    payload = read_json("outputs/step105_dimensional_mapping/velocity_mapping_report.json")
    row = payload["rows"][0]
    summary = payload["summary"]

    assert summary["dimensional_mapping_report_pass"] is True
    assert row["row_name"] == STEP105_ROW
    assert row["n_grid"] == 48
    assert row["dx_norm"] == 1.0 / 48.0
    assert row["mpm_dt"] == 0.0005
    assert row["lbm_dt_phys"] == 0.0005
    assert row["duct_length_m"] == 0.1
    assert row["target_u_lbm"] == [0.02, 0.0, 0.0]
    assert math.isclose(row["proxy_inlet_velocity_mps"], 0.08333333333333334, rel_tol=1.0e-12)
    assert row["official_inlet_velocity_mps"] == 10.0
    assert math.isclose(row["velocity_ratio"], 0.008333333333333333, rel_tol=1.0e-12)
    assert row["dimensional_velocity_mapping_gap_present"] is True
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert row["validation_claim_allowed"] is False


def test_step105_transient_report_passes_as_gap_only_50_step_smoke():
    payload = read_json("outputs/step105_transient_gap_smoke/transient_gap_smoke_report.json")
    row = payload["rows"][0]
    summary = payload["summary"]

    assert summary["step105_transient_gap_smoke_pass"] is True
    assert row["row_name"] == STEP105_ROW
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["completed_lbm_steps"] == 50
    assert row["diagnostics_row_count"] == 51
    assert row["flap_tip_timeseries_row_count"] == 51
    assert row["target_u_lbm_applied_to_inlet"] is True
    assert row["target_u_lbm_applied_to_solid_initial_velocity"] is False
    assert row["all_fluid_geometry_used"] is False
    assert row["fixed_base_constraint_applied"] is True
    assert row["fixed_base_max_displacement_norm"] <= 1.0e-7
    assert row["fixed_base_max_velocity_norm"] <= 1.0e-7
    assert row["step36_squid_wall_velocity_config_used"] is False
    assert row["has_nan"] is False
    assert row["has_inf"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert row["validation_claim_allowed"] is False
    assert row["stable"] is True

    tip_rows = read_csv("outputs/step105_transient_gap_smoke/flap_tip_displacement_timeseries.csv")
    assert tip_rows[0]["step"] == "0"
    assert tip_rows[-1]["step"] == "50"


def test_step105_flow_development_report_has_plane_diagnostics_without_fluent_claims():
    payload = read_json("outputs/step105_flow_development/flow_development_report.json")
    row = payload["rows"][0]
    summary = payload["summary"]

    assert summary["flow_development_report_pass"] is True
    assert row["row_name"] == STEP105_ROW
    for key in (
        "inlet_plane_mean_ux",
        "inlet_plane_max_ux",
        "mid_duct_plane_mean_ux",
        "mid_duct_plane_max_ux",
        "outlet_plane_mean_ux",
        "outlet_plane_max_ux",
        "final_fluid_mean_ux",
        "final_far_field_fluid_mean_ux",
    ):
        assert key in row
        assert math.isfinite(float(row[key]))
    assert row["inlet_plane_flow_present"] is True
    assert row["flow_development_not_fluent_equivalent"] is True
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert row["validation_claim_allowed"] is False


def test_step105_gap_taxonomy_restores_required_gap_set():
    payload = read_json("outputs/step105_gap_taxonomy/gap_taxonomy_report.json")
    rows = payload["rows"]
    summary = payload["summary"]
    gap_names = {row["gap_name"] for row in rows}

    assert summary["gap_taxonomy_report_pass"] is True
    assert REQUIRED_GAPS.issubset(gap_names)
    assert int(summary["gap_count"]) >= 8
    assert summary["direct_quantitative_equivalence_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert all(row["gap_present"] is True for row in rows if row["gap_name"] in REQUIRED_GAPS)


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path):
    with (ROOT / path).open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
