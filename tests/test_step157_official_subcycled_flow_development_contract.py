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
STEP156_ROOT = ROOT / "outputs/step156_official_tutorial_postprocess_and_acceptance"
STEP157_ROOT = ROOT / "outputs/step157_official_subcycled_flow_development_repair"


def test_step157_substep_calculation_from_compiled_case():
    from src.mpm_lbm.solvers.official_subcycled_flow_config import load_compiled_case_for_step157
    from src.mpm_lbm.solvers.official_subcycled_flow_diagnostics import (
        compute_required_lbm_substeps,
    )

    compiled = load_compiled_case_for_step157(STEP154_CASE)
    report = compute_required_lbm_substeps(compiled, (0.02, 0.0, 0.0))

    assert math.isclose(report["dx_phys_m"], 0.1 / 48, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(report["target_u_lbm"], 0.02, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(report["target_inlet_velocity_mps"], 10.0, rel_tol=0.0, abs_tol=1.0e-15)
    assert math.isclose(report["lbm_dt_phys_s"], 4.166666666666667e-6, rel_tol=1.0e-12)
    assert report["required_lbm_substeps_per_fsi_step"] == 120
    assert report["required_total_lbm_substeps_for_50_official_steps"] == 6000
    assert report["validation_claim_allowed"] is False


def test_step157_config_builder_uses_subcycled_exchange(tmp_path):
    from src.mpm_lbm.solvers.official_subcycled_flow_config import (
        build_step157_subcycled_fsi_config,
        build_step157_subcycled_geometry_config,
        load_compiled_case_for_step157,
    )

    compiled = load_compiled_case_for_step157(STEP154_CASE)
    geometry_path = build_step157_subcycled_geometry_config(compiled, tmp_path, n_particles=1024)
    config = build_step157_subcycled_fsi_config(compiled, geometry_path)

    assert config.fsi_exchange_mode == "lbm_subcycled_per_fsi_step"
    assert config.lbm_substeps_per_fsi_step == 120
    assert math.isclose(config.lbm_dt_phys_override_s, 4.166666666666667e-6, rel_tol=1.0e-12)
    assert math.isclose(config.official_fsi_dt_s, 0.0005, rel_tol=0.0, abs_tol=1.0e-15)
    assert config.n_lbm_steps == 50
    assert math.isclose(config.mpm_dt, 0.0005)
    assert config.target_u_lbm == (0.02, 0.0, 0.0)
    assert math.isclose(config.target_u_lbm_for_dimensional_mapping, 0.02)
    assert math.isclose(config.target_inlet_velocity_mps, 10.0)
    assert config.lbm_open_boundary_semantics == "regularized_velocity_pressure_limited"
    assert config.lbm_viscosity_semantics == "legacy_external"
    assert config.write_particles is False
    assert config.write_vtk is False


def test_step157_source_excludes_prior_experiment_runners_and_fluent_shortcuts():
    source = (
        ROOT / "experiments/steps/step157_official_subcycled_flow_development_repair.py"
    ).read_text(encoding="utf-8")
    lowered = source.lower()
    forbidden = [
        "run_step148",
        "run_step153",
        "run_official_tutorial_solver_v1",
        "run_step156_postprocess",
        "step150_official_monitor_intake",
        "subprocess",
    ]
    for token in forbidden:
        assert token not in source
    assert "fluent.exe" not in lowered
    assert "FSIDriver3D" in source


def test_step157_time_scale_diagnosis_artifact_schema():
    report = _read_json(STEP157_ROOT / "step157_time_scale_diagnosis.json")

    assert report["status"] == "time_scale_mismatch_diagnosed"
    assert report["step155_subcycling_deficit_factor"] == 120
    assert report["required_lbm_substeps_per_fsi_step"] == 120
    assert report["required_total_lbm_substeps_for_50_official_steps"] == 6000
    assert report["step156_flow_development_gate_pass"] is False
    assert report["validation_claim_allowed"] is False


def test_step157_real_run_artifact_schema():
    required = [
        "step157_time_scale_diagnosis.json",
        "step157_subcycle_config_report.json",
        "generated_geometry_config.json",
        "solver_driver_config.json",
        "solver_run_manifest.json",
        "subcycled_solver_timeseries.csv",
        "subcycled_solver_monitor.csv",
        "subcycled_solver_force_monitor.csv",
        "subcycled_stability_timeseries.csv",
        "subcycled_mass_flux_timeseries.csv",
        "velocity_snapshots/velocity_snapshot_step050.npz",
        "x_plane_flux_profile_step050.csv",
        "flow_development_comparison_report.json",
        "solver_acceptance_report.json",
        "official_comparison_status_report.json",
        "step157_summary.json",
        "report.md",
    ]
    for name in required:
        path = STEP157_ROOT / name
        assert path.is_file(), name
        assert path.stat().st_size > 0, name


def test_step157_summary_contract():
    summary = _read_json(STEP157_ROOT / "step157_summary.json")

    assert summary["time_scale_mismatch_diagnosed"] is True
    assert summary["compiled_case_consumed"] is True
    assert summary["step155_baseline_consumed"] is True
    assert summary["step156_acceptance_consumed"] is True
    assert summary["subcycled_solver_run_executed"] is True
    assert summary["fsi_exchange_mode"] == "lbm_subcycled_per_fsi_step"
    assert summary["lbm_substeps_per_fsi_step"] == 120
    assert math.isclose(summary["lbm_dt_phys_override_s"], 4.166666666666667e-6, rel_tol=1.0e-12)
    assert summary["n_official_steps_completed"] == 50
    assert math.isclose(summary["official_time_end_s"], 0.025, rel_tol=0.0, abs_tol=1.0e-12)
    assert summary["total_lbm_substeps_completed"] == 6000
    assert summary["source_step156_flow_development_gate_pass"] is False
    assert summary["step157_flow_development_gate_reported"] is True
    assert "step157_flow_development_gate_pass" in summary
    assert summary["flow_metrics_valid_for_gate"] is False
    assert summary["flow_metrics_invalid_reason"] == "density_gate_failed_before_tail_window"
    assert summary["first_density_gate_failure_step"] == 9
    assert summary["validation_claim_allowed"] is False
    assert summary["figure_29_3_parity_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False


def test_step157_flow_comparison_contract():
    report = _read_json(STEP157_ROOT / "flow_development_comparison_report.json")

    assert report["status"] == "flow_development_comparison_written"
    assert "baseline_step155_step156" in report
    assert "subcycled_step157" in report
    assert "outlet_flux_ratio_improved" in report
    assert "flux_imbalance_improved" in report
    assert report["flow_metrics_valid_for_gate"] is False
    assert report["flow_metrics_invalid_reason"] == "density_gate_failed_before_tail_window"
    assert report["first_density_gate_failure_step"] == 9
    assert report["raw_outlet_flux_ratio_improved"] is True
    assert report["outlet_flux_ratio_improved"] is False
    assert "subcycling_repair_success" in report
    assert report["subcycling_repair_success_policy"].startswith("flow gate requires")
    assert report["validation_claim_allowed"] is False


def test_step157_final_snapshot_schema_and_finite_fields():
    data = np.load(STEP157_ROOT / "velocity_snapshots/velocity_snapshot_step050.npz")
    for name in [
        "velocity",
        "rho",
        "solid",
        "speed",
        "ux",
        "uy",
        "uz",
        "official_step",
        "time_s",
        "total_lbm_substeps",
        "lbm_substeps_per_fsi_step",
        "validation_claim_allowed",
    ]:
        assert name in data.files, name

    solid = data["solid"] != 0
    fluid = ~solid
    assert data["velocity"].shape == (48, 48, 48, 3)
    assert data["rho"].shape == (48, 48, 48)
    assert np.isfinite(data["velocity"][fluid]).all()
    assert np.isfinite(data["rho"][fluid]).all()
    assert int(data["official_step"]) == 50
    assert int(data["total_lbm_substeps"]) == 6000
    assert int(data["lbm_substeps_per_fsi_step"]) == 120
    assert bool(data["validation_claim_allowed"]) is False


def test_step157_csv_contracts():
    expectations = {
        "subcycled_solver_timeseries.csv": 51,
        "subcycled_solver_monitor.csv": 51,
        "subcycled_solver_force_monitor.csv": 51,
        "subcycled_stability_timeseries.csv": 51,
        "subcycled_mass_flux_timeseries.csv": 51,
        "x_plane_flux_profile_step050.csv": 48,
    }
    for name, expected_rows in expectations.items():
        rows = _read_csv(STEP157_ROOT / name)
        assert len(rows) == expected_rows, name
        assert "time_s" in rows[0]

    mass = _read_csv(STEP157_ROOT / "subcycled_mass_flux_timeseries.csv")
    assert set(mass[0]) >= {
        "official_step",
        "time_s",
        "total_lbm_substeps",
        "total_fluid_mass",
        "mass_delta_rel",
        "inlet_flux",
        "outlet_flux",
        "midplane_flux",
        "flux_imbalance_rel",
        "outlet_to_inlet_flux_ratio",
        "midplane_to_inlet_flux_ratio",
    }


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
