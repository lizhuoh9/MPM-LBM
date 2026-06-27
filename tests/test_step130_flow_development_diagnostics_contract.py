import csv
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_step130_boundary_diagnostics_expose_outlet_plane_and_midplane_flux_fields():
    from src.mpm_lbm.sim.diagnostics.lbm_boundary_diagnostics import summarize_lbm_boundary_diagnostics

    rho = np.ones((5, 4, 4), dtype=float)
    v = np.zeros((5, 4, 4, 3), dtype=float)
    solid = np.zeros((5, 4, 4), dtype=np.int8)
    v[0, :, :, 0] = 0.031
    v[2, :, :, 0] = 0.030
    v[4, :, :, 0] = np.array(
        [
            [0.020, 0.021, 0.022, 0.023],
            [0.024, -0.010, 0.025, 0.026],
            [0.027, 0.028, 0.029, 0.030],
            [0.031, 0.032, 0.033, 0.034],
        ],
        dtype=float,
    )

    summary = summarize_lbm_boundary_diagnostics({"rho": rho, "v": v, "solid": solid}, step=25)

    assert "midplane_flux" in summary
    assert "outlet_plane_ux_min" in summary
    assert "outlet_plane_ux_max" in summary
    assert "outlet_plane_ux_mean" in summary
    assert "outlet_plane_negative_ux_fraction" in summary
    assert summary["outlet_plane_ux_min"] < 0.0
    assert summary["outlet_plane_negative_ux_fraction"] > 0.0


def test_step130_flow_development_diagnostic_record_and_csv_are_bounded(tmp_path):
    from experiments.steps.step120_lbm_boundary_repair_large_real_execution import (
        FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS,
        Step120RunSpec,
        _flow_development_diagnostic_record,
        _write_flow_development_diagnostics,
    )

    spec = Step120RunSpec(
        name="diag",
        nx=5,
        ny=4,
        nz=4,
        n_steps=3,
        output_interval=1,
        failure_check_interval=1,
        open_boundary_semantics="regularized_flux_matched_pressure_outlet",
        geometry_mode="duct_only",
        requested_nx=5,
        requested_n_steps=3,
        allow_large_real_run_without_flag=True,
        row_role="flow_repair_candidate_48",
        open_boundary_flux_feedback_gain_u=0.01,
        open_boundary_flux_feedback_gain_rho=0.005,
        open_boundary_flux_filter_alpha=0.05,
        open_boundary_flux_correction_cap_u=0.005,
    )
    record = {
        "step": 25,
        "inlet_flux": 42.0,
        "outlet_flux": 52.0,
        "midplane_flux": 48.0,
        "outlet_plane_ux_min": -0.01,
        "outlet_plane_ux_max": 0.08,
        "outlet_plane_ux_mean": 0.04,
        "outlet_plane_negative_ux_fraction": 0.0625,
        "mass_total_delta_rel": 0.001,
        "sampled_x_profile_flux": "0:42.0;2:48.0;4:52.0",
    }
    stats = {
        "flow_outlet_flux_error_filtered_run": -8.0,
        "flow_correction_delta_abs_sum_step": 0.125,
        "flow_correction_delta_abs_sum_run": 0.25,
    }

    diagnostic = _flow_development_diagnostic_record(record, spec, stats)
    _write_flow_development_diagnostics(tmp_path, [diagnostic])

    csv_path = tmp_path / "flow_development_diagnostics.csv"
    summary_path = tmp_path / "flow_development_diagnostics_summary.json"
    assert csv_path.is_file()
    assert summary_path.is_file()
    assert csv_path.stat().st_size < 4096

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert set(FLOW_DEVELOPMENT_DIAGNOSTIC_FIELDS).issubset(rows[0].keys())
    assert rows[0]["target_outlet_flux"] == "42.0"
    assert rows[0]["outlet_flux_error"] == "-10.0"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["row_count"] == 1
    assert summary["bounded_size_artifact"] is True
    assert summary["validation_claim_allowed"] is False
    assert summary["selected96_claim_allowed"] is False


def test_step130_flow_development_diagnostics_are_written_for_tiny_real_row(tmp_path):
    from experiments.steps import step120_lbm_boundary_repair_large_real_execution as step120

    spec = step120.Step120RunSpec(
        name="tiny_step130_flow_diag",
        nx=4,
        ny=3,
        nz=3,
        n_steps=1,
        output_interval=1,
        failure_check_interval=1,
        checkpoint_every=0,
        open_boundary_semantics="convective_flux_matched_damped_outlet",
        geometry_mode="duct_only",
        requested_nx=4,
        requested_n_steps=1,
        allow_large_real_run_without_flag=True,
        row_role="flow_repair_candidate_48",
        open_boundary_convective_blend_weight=0.05,
    )

    row = step120.run_step120_row(spec, tmp_path / spec.name, checkpoint_root=tmp_path / "checkpoints")
    csv_path = tmp_path / spec.name / "flow_development_diagnostics.csv"
    summary_path = tmp_path / spec.name / "flow_development_diagnostics_summary.json"

    assert row["simulation_backed_artifact"] is True
    assert csv_path.is_file()
    assert summary_path.is_file()
    assert csv_path.stat().st_size < 8192
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["validation_claim_allowed"] is False
    assert payload["selected96_claim_allowed"] is False
