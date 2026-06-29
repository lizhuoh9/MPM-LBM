import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step153_official_constants_and_config_are_encoded():
    import experiments.steps.step153_official_tutorial_setup_parity as step153

    setup = step153.OFFICIAL_TUTORIAL_SETUP
    material = step153.OFFICIAL_TUTORIAL_MATERIAL
    config = step153.create_official_tutorial_setup_fsi_config(grid=16, n_steps=50, dt_s=0.0005)

    assert setup["duct_length_m"] == 0.10
    assert setup["duct_height_m"] == 0.04
    assert setup["flap_height_m"] == 0.01
    assert setup["flap_thickness_m"] == 0.003
    assert setup["inlet_air_velocity_mps"] == 10.0
    assert setup["monitor_point_m"] == [0.0505, 0.0095]
    assert setup["official_tutorial_time_steps"] == 50
    assert setup["official_tutorial_dt_s"] == 0.0005
    assert setup["official_tutorial_total_time_s"] == 0.025
    assert setup["max_iterations_per_time_step"] == 40

    assert material["solid_density_kg_m3"] == 1600.0
    assert material["youngs_modulus_pa"] == 1.0e6
    assert material["poisson_ratio"] == 0.47
    assert material["material_name"] == "silicone-rubber"

    assert config.geometry_type == "duct_flap_proxy"
    assert config.coupling_mode == "moving_boundary"
    assert config.n_grid == 16
    assert config.n_lbm_steps == 50
    assert config.mpm_dt == 0.0005
    assert config.official_fsi_dt_s == 0.0005
    assert config.target_inlet_velocity_mps == 10.0
    assert config.physical_duct_length_m == 0.10
    assert list(config.fluent_like_monitor_physical_point_m) == [0.0505, 0.0095]


def test_step153_runner_writes_setup_parity_artifacts_with_solver_monitor(tmp_path, monkeypatch):
    import experiments.steps.step153_official_tutorial_setup_parity as step153

    class FakeDriver:
        material_reference_used_for_mpm_config = True
        flap_tip_monitor_rows = [
            {
                "step": 0,
                "time_s": 0.0,
                "flap_tip_total_displacement_m": 0.0,
                "flap_tip_x_displacement_m": 0.0,
                "flap_tip_y_displacement_m": 0.0,
            },
            {
                "step": 25,
                "time_s": 0.0125,
                "flap_tip_total_displacement_m": 4.0e-6,
                "flap_tip_x_displacement_m": 1.0e-6,
                "flap_tip_y_displacement_m": 3.0e-6,
            },
            {
                "step": 50,
                "time_s": 0.025,
                "flap_tip_total_displacement_m": 8.0e-6,
                "flap_tip_x_displacement_m": 2.0e-6,
                "flap_tip_y_displacement_m": 6.0e-6,
            },
        ]
        fluent_like_monitor_rows = []

    def fake_run_our_solver_fsi_case(config, output_dir, force=False, raw_output_dir=None):
        del output_dir, force, raw_output_dir
        assert config.n_lbm_steps == 50
        assert math.isclose(config.mpm_dt, 0.0005)
        diagnostics = [
            {"step": 0, "hydro_force_max_norm": 0.0},
            {"step": 25, "hydro_force_max_norm": 0.2},
            {"step": 50, "hydro_force_max_norm": 0.4},
        ]
        return FakeDriver(), diagnostics, {
            "driver_class": "FSIDriver3D",
            "raw_output_dir": "outputs/tmp/fake_step153_driver_raw",
            "diagnostics_rows": 3,
        }

    monkeypatch.setattr(step153, "run_our_solver_fsi_case", fake_run_our_solver_fsi_case)
    out_dir = tmp_path / "step153"
    summary = step153.run_step153_official_tutorial_setup_parity(
        official_private_root=tmp_path / "private_missing",
        output_dir=out_dir,
        grid=12,
        n_steps=50,
        dt_s=0.0005,
        force=True,
    )

    assert summary["step"] == 153
    assert summary["status"] == "official_tutorial_setup_parity_run_complete"
    assert summary["our_solver_run_executed"] is True
    assert summary["solver_monitor_found"] is True
    assert summary["solver_monitor_rows"] == 3
    assert math.isclose(summary["solver_time_end_s"], 0.025)
    assert summary["official_tutorial_time_steps"] == 50
    assert summary["official_tutorial_dt_s"] == 0.0005
    assert summary["official_tutorial_total_time_s"] == 0.025
    assert summary["monitor_point_m"] == [0.0505, 0.0095]
    assert summary["material_density_kg_m3"] == 1600.0
    assert summary["youngs_modulus_pa"] == 1.0e6
    assert summary["poisson_ratio"] == 0.47
    assert summary["official_monitor_required_for_error_metrics"] is True
    assert summary["official_monitor_loaded"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False
    assert summary["selected96_ready"] is False

    monitor_rows = _read_csv(out_dir / "solver_monitor.csv")
    assert len(monitor_rows) == 3
    assert math.isclose(float(monitor_rows[-1]["time_s"]), 0.025)

    for required in (
        "official_tutorial_setup_report.json",
        "official_tutorial_setup_report.md",
        "solver_run_manifest.json",
        "solver_monitor.csv",
        "solver_force_monitor.csv",
        "solver_reproduction_summary.json",
        "geometry_mapping_report.json",
        "material_mapping_report.json",
        "boundary_semantics_gap_report.json",
        "official_reference_gap_report.json",
    ):
        assert (out_dir / required).is_file()

    material_report = _read_json(out_dir / "material_mapping_report.json")
    assert material_report["official_structural_material_applied"] is True
    assert material_report["material_mapping_gap_blocks_physics_parity"] is False
    assert material_report["material_name"] == "silicone-rubber"

    boundary_report = _read_json(out_dir / "boundary_semantics_gap_report.json")
    assert boundary_report["official_velocity_inlet_present"] is True
    assert boundary_report["official_pressure_outlet_present"] is True
    assert boundary_report["official_intrinsic_fsi_wall_present"] is True
    assert boundary_report["our_solver_equivalent_moving_boundary_mode"] == "moving_boundary"
    assert any("Fluent intrinsic FSI" in item for item in boundary_report["semantic_gaps"])

    reference_gap = _read_json(out_dir / "official_reference_gap_report.json")
    assert reference_gap["official_monitor_required_for_error_metrics"] is True
    assert reference_gap["official_monitor_loaded"] is False
    assert reference_gap["validation_claim_allowed"] is False


def test_step153_source_uses_step148_solver_path_and_excludes_forbidden_shortcuts():
    source = (ROOT / "experiments/steps/step153_official_tutorial_setup_parity.py").read_text(encoding="utf-8")
    lowered = source.lower()

    assert "run_our_solver_fsi_case" in source
    assert "extract_solver_monitors" in source
    assert "FSIDriver3D" in source
    assert "step121_lbm_boundary_real_campaign_and_gate_correction" not in lowered
    assert "fluent.exe" not in lowered
    assert "selected96_ready\": true" not in lowered


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
