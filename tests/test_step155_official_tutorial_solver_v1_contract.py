import csv
import json
import math
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP154_CASE = ROOT / "outputs/step154_official_solver_prepost_pipeline/compiled_case.json"
STEP155_ROOT = ROOT / "outputs/step155_official_tutorial_solver_v1"


def test_step155_config_builder_consumes_compiled_case():
    from src.mpm_lbm.solvers.official_duct_flap_config import (
        build_step155_fsi_driver_config,
        load_compiled_case,
        validate_compiled_case_for_step155,
        write_generated_geometry_config,
    )

    compiled = load_compiled_case(STEP154_CASE)
    validate_compiled_case_for_step155(compiled)
    out_dir = ROOT / "outputs/tmp/test_step155_config_builder"
    geometry_path = write_generated_geometry_config(compiled, out_dir, n_particles=1024)
    config = build_step155_fsi_driver_config(compiled, geometry_path)

    assert config.n_grid == 48
    assert config.n_particles == 1024
    assert config.n_lbm_steps == 50
    assert math.isclose(config.mpm_dt, 0.0005)
    assert config.lbm_boundary_condition_mode == "duct_velocity_inlet_pressure_outlet"
    assert config.lbm_open_boundary_semantics == "regularized_velocity_pressure_limited"
    assert config.open_boundary_limiter_enabled is True
    assert config.target_inlet_velocity_mps == 10.0
    assert config.official_fsi_dt_s == 0.0005
    assert config.lbm_viscosity_semantics == "legacy_external"
    assert config.lbm_tau_stability_policy == "report_only"
    assert config.write_particles is False
    assert config.write_vtk is False


def test_step155_generated_geometry_config_contract(tmp_path):
    from src.mpm_lbm.solvers.official_duct_flap_config import (
        load_compiled_case,
        write_generated_geometry_config,
    )
    from src.mpm_lbm.sim.geometry.config import GeometryConfig

    compiled = load_compiled_case(STEP154_CASE)
    geometry_path = write_generated_geometry_config(compiled, tmp_path, n_particles=1024)
    payload = _read_json(geometry_path)
    geometry = GeometryConfig.from_json(str(geometry_path))

    duct = compiled["solver_geometry_mapping"]["duct_normalized"]
    flap = compiled["solver_geometry_mapping"]["flap_normalized"]
    material = compiled["official_material"]

    assert geometry.geometry_type == "duct_flap_proxy"
    assert geometry.n_particles == 1024
    assert payload["duct"] == duct
    assert payload["flap"]["normalized_height"] == flap["height"]
    assert payload["flap"]["normalized_thickness"] == flap["thickness"]
    assert payload["flap"]["height_over_duct_height"] == 0.25
    assert payload["flap"]["thickness_over_duct_height"] == 0.075
    assert payload["material_reference"]["used_for_mpm_config"] is True
    assert payload["material_reference"]["used_for_exact_structural_model"] is False
    assert payload["material_reference"]["density"] == material["solid_density_kg_m3"]
    assert payload["material_reference"]["youngs_modulus"] == material["youngs_modulus_pa"]
    assert payload["material_reference"]["poisson_ratio"] == material["poisson_ratio"]
    assert payload["dimensional_reference"]["official_transient_steps"] == 50
    assert payload["dimensional_reference"]["transient_dt_s"] == 0.0005
    assert payload["monitor_reference"]["monitor_point_m"] == [0.0505, 0.0095]


def test_step155_source_excludes_step148_step153_helpers_and_fluent_shortcuts():
    source = (ROOT / "experiments/steps/step155_official_tutorial_solver_v1.py").read_text(
        encoding="utf-8"
    )
    lowered = source.lower()

    forbidden = [
        "create_fluent_official_proxy_fsi_config",
        "run_our_solver_fsi_case",
        "extract_solver_monitors",
        "run_step148_reproduction",
        "run_step153_official_tutorial_setup_parity",
    ]
    for name in forbidden:
        assert name not in source
    assert "FSIDriver3D" in source
    assert "fluent.exe" not in lowered
    assert "step150_official_monitor_intake" not in lowered


def test_step155_boundary_report_treats_limited_regularized_as_unknown_reconstruction(tmp_path):
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    config = FSIDriverConfig(
        lbm_boundary_condition_mode="duct_velocity_inlet_pressure_outlet",
        lbm_open_boundary_semantics="regularized_velocity_pressure_limited",
        open_boundary_limiter_enabled=True,
        geometry_type="duct_flap_proxy",
    )
    driver = object.__new__(FSIDriver3D)
    driver.config = config
    driver.out_dir = str(tmp_path)
    driver.duct_static_geometry_report = {
        "inlet_fluid_cell_count": 80,
        "pressure_outlet_fluid_cell_count": 80,
        "duct_wall_cell_count": 106752,
    }
    report = FSIDriver3D._write_lbm_boundary_condition_report(
        driver,
        config.make_unified_sim_config().make_lbm_config(),
    )

    assert report["lbm_open_boundary_semantics"] == "regularized_velocity_pressure_limited"
    assert report["all_population_equilibrium_reset_used"] is False
    assert report["unknown_population_reconstruction_used"] is True
    assert report["open_boundary_limiter_enabled"] is True
    assert "with limiter" in report["lbm_open_boundary_scope_note"]
    assert report["validation_claim_allowed"] is False


def test_step155_committed_artifact_schema():
    required = [
        "compiled_case_consumed.json",
        "generated_geometry_config.json",
        "solver_driver_config.json",
        "solver_run_manifest.json",
        "case_to_driver_geometry_report.json",
        "boundary_semantics_runtime_report.json",
        "unit_mapping_report.json",
        "solver_timeseries.csv",
        "solver_monitor.csv",
        "solver_force_monitor.csv",
        "stability_timeseries.csv",
        "mass_flux_timeseries.csv",
        "solver_v1_summary.json",
        "physics_gap_report.json",
        "report.md",
    ]
    for name in required:
        path = STEP155_ROOT / name
        assert path.is_file(), name
        assert path.stat().st_size > 0, name

    snapshot_dir = STEP155_ROOT / "velocity_snapshots"
    expected_steps = list(range(0, 51, 5))
    for step in expected_steps:
        path = snapshot_dir / f"velocity_snapshot_step{step:03d}.npz"
        assert path.is_file(), path.name
        assert path.stat().st_size > 0, path.name

    summary = _read_json(STEP155_ROOT / "solver_v1_summary.json")
    manifest = _read_json(STEP155_ROOT / "solver_run_manifest.json")
    boundary = _read_json(STEP155_ROOT / "boundary_semantics_runtime_report.json")
    physics = _read_json(STEP155_ROOT / "physics_gap_report.json")

    assert manifest["step148_helper_used"] is False
    assert manifest["step153_helper_used"] is False
    assert boundary["unknown_population_reconstruction_used"] is True
    assert physics["validation_claim_allowed"] is False
    assert summary["validation_claim_allowed"] is False

    csv_expectations = {
        "solver_timeseries.csv": 51,
        "solver_monitor.csv": 51,
        "solver_force_monitor.csv": 51,
        "stability_timeseries.csv": 51,
        "mass_flux_timeseries.csv": 51,
    }
    for name, expected_count in csv_expectations.items():
        rows = _read_csv(STEP155_ROOT / name)
        assert len(rows) == expected_count, name

    data = np.load(snapshot_dir / "velocity_snapshot_step050.npz")
    for name in ("velocity", "rho", "solid", "speed", "ux", "uy", "uz"):
        assert name in data.files
    assert data["velocity"].shape == (48, 48, 48, 3)
    assert data["rho"].shape == (48, 48, 48)
    assert bool(data["validation_claim_allowed"]) is False


def test_step155_real_run_summary_contract():
    summary = _read_json(STEP155_ROOT / "solver_v1_summary.json")

    assert summary["step"] == 155
    assert summary["status"] == "official_tutorial_solver_v1_run_complete"
    assert summary["solver_v1_run_executed"] is True
    assert summary["compiled_case_consumed"] is True
    assert summary["compiled_case_ready_for_step155"] is True
    assert summary["step148_helper_used"] is False
    assert summary["step153_helper_used"] is False
    assert summary["driver_class"] == "FSIDriver3D"
    assert summary["n_steps_requested"] == 50
    assert summary["n_steps_completed"] == 50
    assert math.isclose(summary["time_end_s"], 0.025, rel_tol=0.0, abs_tol=1.0e-12)
    assert summary["time_window_matches_official_tutorial"] is True
    assert summary["velocity_inlet_active"] is True
    assert summary["pressure_outlet_active"] is True
    assert summary["legacy_all_population_reset_used"] is False
    assert summary["unknown_population_reconstruction_used"] is True
    assert summary["open_boundary_limiter_enabled"] is True
    assert summary["lbm_open_boundary_semantics"] == "regularized_velocity_pressure_limited"
    assert summary["solver_monitor_rows"] == 51
    assert summary["solver_force_monitor_rows"] == 51
    assert summary["stability_rows"] == 51
    assert summary["mass_flux_rows"] == 51
    assert summary["velocity_snapshot_count"] == 11
    assert summary["final_velocity_snapshot_written"] is True
    assert summary["monitor_displacement_finite"] is True
    assert summary["force_monitor_finite"] is True
    assert summary["density_gate_pass"] is True
    assert summary["finite_gate_pass"] is True
    assert summary["mpm_j_gate_pass"] is True
    assert summary["mass_flux_reported"] is True
    assert summary["official_monitor_loaded"] is False
    assert summary["official_error_metrics_available"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["figure_29_3_parity_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
