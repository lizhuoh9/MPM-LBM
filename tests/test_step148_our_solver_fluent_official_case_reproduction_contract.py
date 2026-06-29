import csv
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


EXPECTED_MONITOR_FIELDS = [
    "time_s",
    "step",
    "flap_tip_total_displacement_m",
    "flap_tip_x_displacement_m",
    "flap_tip_y_displacement_m",
    "flap_tip_velocity_m_per_s",
    "fluid_force_x_n",
    "fluid_force_y_n",
    "fluid_force_magnitude_n",
]


def test_step148_module_exports_required_runner_functions():
    import experiments.steps.step148_our_solver_fluent_official_case_reproduction as step148

    for name in (
        "create_fluent_official_proxy_fsi_config",
        "run_our_solver_fsi_case",
        "extract_solver_monitors",
        "write_solver_case_mapping_report",
    ):
        assert callable(getattr(step148, name))


def test_step148_config_uses_real_fsi_driver_and_fluent_proxy_mapping():
    import experiments.steps.step148_our_solver_fluent_official_case_reproduction as step148

    config = step148.create_fluent_official_proxy_fsi_config(grid=16, n_steps=3)

    assert config.geometry_type == "duct_flap_proxy"
    assert config.coupling_mode == "moving_boundary"
    assert config.lbm_boundary_condition_mode == "duct_velocity_inlet_pressure_outlet"
    assert config.n_grid == 16
    assert config.n_lbm_steps == 3
    assert config.fluent_like_monitor_enabled is True
    assert config.write_vtk is False
    assert config.write_particles is False
    assert "step121" not in json.dumps(config.to_dict()).lower()


def test_step148_runner_writes_required_schema_from_solver_outputs(tmp_path, monkeypatch):
    import experiments.steps.step148_our_solver_fluent_official_case_reproduction as step148

    class FakeDriver:
        flap_tip_monitor_rows = [
            {
                "step": 0,
                "time_s": 0.0,
                "flap_tip_total_displacement_m": 0.0,
                "flap_tip_x_displacement_m": 0.0,
                "flap_tip_y_displacement_m": 0.0,
            },
            {
                "step": 2,
                "time_s": 0.001,
                "flap_tip_total_displacement_m": 1.0e-5,
                "flap_tip_x_displacement_m": 1.0e-6,
                "flap_tip_y_displacement_m": 9.0e-6,
            },
        ]
        fluent_like_monitor_rows = []

    def fake_run_our_solver_fsi_case(config, output_dir, force=False, raw_output_dir=None):
        del config, output_dir, force, raw_output_dir
        diagnostics = [
            {
                "step": 0,
                "hydro_force_max_norm": 0.0,
                "cell_force_max_norm": 0.0,
                "max_grid_reaction_norm": 0.0,
            },
            {
                "step": 2,
                "hydro_force_max_norm": 3.0,
                "cell_force_max_norm": 2.0,
                "max_grid_reaction_norm": 1.0,
            },
        ]
        return FakeDriver(), diagnostics, {
            "driver_class": "FSIDriver3D",
            "raw_output_dir": "outputs/tmp/fake_step148_driver_raw",
            "diagnostics_rows": 2,
        }

    monkeypatch.setattr(step148, "run_our_solver_fsi_case", fake_run_our_solver_fsi_case)
    out_dir = tmp_path / "step148"
    summary = step148.run_step148_reproduction(
        official_private_root=tmp_path / "private_missing",
        output_dir=out_dir,
        grid=12,
        n_steps=2,
        force=True,
    )

    assert summary["step"] == 148
    assert summary["our_solver_run_executed"] is True
    assert summary["solver_monitor_found"] is True
    assert summary["solver_monitor_rows"] > 0
    assert summary["fsi_coupling_mode"] == "moving_boundary"
    assert summary["fluid_solver"] == "LBM"
    assert summary["solid_solver"] == "MPM"
    assert summary["two_way_coupling_attempted"] is True
    assert summary["official_payload_committed"] is False
    assert summary["official_monitor_committed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False

    rows = read_csv(out_dir / "solver_monitor.csv")
    assert list(rows[0].keys()) == EXPECTED_MONITOR_FIELDS
    assert rows[0]["step"] == "0"
    assert int(rows[-1]["step"]) == 2
    for row in rows:
        for key in EXPECTED_MONITOR_FIELDS:
            if key == "step":
                continue
            assert math.isfinite(float(row[key]))

    force_rows = read_csv(out_dir / "solver_force_monitor.csv")
    assert len(force_rows) == len(rows)
    assert list(force_rows[0].keys()) == [
        "time_s",
        "step",
        "fluid_force_x_n",
        "fluid_force_y_n",
        "fluid_force_magnitude_n",
    ]

    for required in (
        "solver_run_manifest.json",
        "solver_case_mapping_report.json",
        "geometry_mapping_report.json",
        "unit_mapping_report.json",
        "coupling_diagnostics_summary.json",
        "solver_reproduction_summary.json",
    ):
        assert (out_dir / required).is_file()


def test_step148_source_excludes_forbidden_shortcuts():
    source = (ROOT / "experiments/steps/step148_our_solver_fluent_official_case_reproduction.py").read_text(
        encoding="utf-8"
    )
    forbidden_tokens = [
        "step121_lbm_boundary_real_campaign_and_gate_correction",
        "lbm-only",
        "fluent.exe",
    ]
    lowered = source.lower()
    for token in forbidden_tokens:
        assert token.lower() not in lowered
    assert "FSIDriver3D" in source
    assert ".run(" in source


def read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
