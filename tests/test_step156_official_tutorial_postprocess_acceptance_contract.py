import csv
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STEP154_CASE = ROOT / "outputs/step154_official_solver_prepost_pipeline/compiled_case.json"
STEP155_ROOT = ROOT / "outputs/step155_official_tutorial_solver_v1"
STEP156_ROOT = ROOT / "outputs/step156_official_tutorial_postprocess_and_acceptance"


@pytest.fixture(scope="module")
def step156_temp_output(tmp_path_factory):
    from experiments.steps.step156_official_tutorial_postprocess_and_solver_acceptance import (
        run_step156_postprocess,
    )

    output_dir = tmp_path_factory.mktemp("step156-postprocess")
    summary = run_step156_postprocess(
        case_path=STEP154_CASE,
        solver_root=STEP155_ROOT,
        official_monitor_path=output_dir / "missing_official_monitor.csv",
        output_dir=output_dir,
        force=True,
        no_preview_open=True,
    )
    return output_dir, summary


def test_step156_runner_writes_required_artifacts(step156_temp_output):
    output_dir, summary = step156_temp_output
    required = [
        "velocity_magnitude_step050.png",
        "velocity_ux_step050.png",
        "velocity_uy_step050.png",
        "streamline_or_quiver_step050.png",
        "geometry_overlay_step050.png",
        "official_style_velocity_cloud_step050.png",
        "centerline_velocity_profile.csv",
        "x_plane_flux_profile.csv",
        "monitor_displacement_plot.png",
        "force_monitor_plot.png",
        "postprocess_summary.json",
        "solver_acceptance_report.json",
        "official_comparison_report.json",
        "report.md",
    ]

    for name in required:
        path = output_dir / name
        assert path.is_file(), name
        assert path.stat().st_size > 0, name

    assert summary["status"] == "official_tutorial_postprocess_complete"
    assert summary["postprocess_complete"] is True
    assert summary["validation_claim_allowed"] is False


def test_step156_source_excludes_solver_fluent_and_prior_step_execution():
    source = (
        ROOT / "experiments/steps/step156_official_tutorial_postprocess_and_solver_acceptance.py"
    ).read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_exact = [
        "FSIDriver3D(",
        "driver.run(",
        "step_once(",
        "run_official_tutorial_solver_v1",
        "run_step148",
        "run_step153",
        "step150_official_monitor_intake",
    ]
    for token in forbidden_exact:
        assert token not in source

    assert "fluent.exe" not in lowered
    assert "subprocess" not in lowered


def test_step156_velocity_snapshot_and_render_contract(step156_temp_output):
    output_dir, _summary = step156_temp_output
    data = np.load(STEP155_ROOT / "velocity_snapshots/velocity_snapshot_step050.npz")

    assert data["velocity"].shape == (48, 48, 48, 3)
    assert data["rho"].shape == (48, 48, 48)
    for name in ("speed", "ux", "uy", "uz"):
        assert name in data.files

    report = _read_json(output_dir / "velocity_render_report.json")
    assert report["status"] == "velocity_render_complete"
    assert report["velocity_magnitude_written"] is True
    assert report["velocity_ux_written"] is True
    assert report["velocity_uy_written"] is True
    assert report["streamline_or_quiver_written"] is True
    assert report["geometry_overlay_written"] is True
    assert report["official_style_velocity_cloud_written"] is True
    assert report["validation_claim_allowed"] is False


def test_step156_profile_csv_contracts(step156_temp_output):
    output_dir, _summary = step156_temp_output
    centerline_rows = _read_csv(output_dir / "centerline_velocity_profile.csv")
    flux_rows = _read_csv(output_dir / "x_plane_flux_profile.csv")

    assert centerline_rows
    assert flux_rows
    assert set(centerline_rows[0]) >= {
        "x_index",
        "x_norm",
        "x_m",
        "rho",
        "ux_lbm",
        "uy_lbm",
        "uz_lbm",
        "speed_lbm",
        "ux_mps_proxy",
        "uy_mps_proxy",
        "uz_mps_proxy",
        "speed_mps_proxy",
        "solid",
        "fluid_mask",
    }
    assert set(flux_rows[0]) >= {
        "x_index",
        "x_norm",
        "x_m",
        "fluid_cell_count_static_mask",
        "fluid_cell_count_dynamic_solver",
        "mass_flux_lbm",
        "mean_ux_lbm",
        "mean_speed_lbm",
        "max_speed_lbm",
        "mass_flux_mps_proxy_sum",
        "outlet_plane",
        "inlet_plane",
        "midplane",
    }


def test_step156_monitor_plots_and_summary_contract(step156_temp_output):
    output_dir, _summary = step156_temp_output
    report = _read_json(output_dir / "monitor_plot_report.json")

    assert report["solver_monitor_rows"] == 51
    assert report["solver_force_monitor_rows"] == 51
    assert report["monitor_displacement_plot_written"] is True
    assert report["force_monitor_plot_written"] is True
    assert report["force_is_direct_fluent_wall_integral"] is False


def test_step156_solver_acceptance_report_contract(step156_temp_output):
    output_dir, _summary = step156_temp_output
    report = _read_json(output_dir / "solver_acceptance_report.json")

    assert report["status"] == "solver_acceptance_report_written"
    assert report["postprocess_acceptance_pass"] is True
    assert report["solver_numerical_sanity_pass"] is True
    assert report["validation_claim_allowed"] is False
    assert report["figure_29_3_parity_claim_allowed"] is False
    assert report["official_error_metrics_available"] is False
    for field in [
        "flow_development_gate_pass",
        "flow_development_gate_policy",
        "inlet_flux_tail_mean",
        "outlet_flux_tail_mean",
        "flux_imbalance_rel_tail_mean",
        "outlet_to_inlet_flux_ratio_tail_mean",
    ]:
        assert field in report
    assert report["flow_development_gate_policy"] == "report_only_for_step156"


def test_step156_missing_official_monitor_behavior(step156_temp_output):
    output_dir, _summary = step156_temp_output
    report = _read_json(output_dir / "official_comparison_report.json")

    assert report["status"] == "official_monitor_missing"
    assert report["official_monitor_loaded"] is False
    assert report["official_error_metrics_available"] is False
    assert report["validation_claim_allowed"] is False


def test_step156_synthetic_official_monitor_comparison(tmp_path):
    from src.mpm_lbm.postprocessing.fluent_duct_flap_official_comparison import (
        build_official_comparison_report,
    )

    official = tmp_path / "official_monitor.csv"
    official.write_text(
        "time_s,flap_tip_total_displacement_m\n0.0,0.0\n0.025,0.0\n",
        encoding="utf-8",
    )
    report = build_official_comparison_report(
        official,
        STEP155_ROOT / "solver_monitor.csv",
        tmp_path / "official_comparison_report.json",
    )

    assert report["official_monitor_loaded"] is True
    assert report["official_error_metrics_available"] is True
    assert math.isfinite(report["rmse_m"])
    assert math.isfinite(report["max_abs_error_m"])
    assert report["validation_claim_allowed"] is False


def test_step156_committed_artifact_schema():
    summary = _read_json(STEP156_ROOT / "postprocess_summary.json")

    assert summary["status"] == "official_tutorial_postprocess_complete"
    assert summary["preprocess_complete"] is True
    assert summary["solver_complete"] is True
    assert summary["postprocess_complete"] is True
    assert summary["solver_pipeline_complete"] is True
    assert summary["flow_development_gate_reported"] is True
    assert summary["validation_claim_allowed"] is False
    assert summary["figure_29_3_parity_claim_allowed"] is False
    assert summary["selected96_execution_allowed"] is False


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _read_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))
