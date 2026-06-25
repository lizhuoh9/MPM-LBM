from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_csv_rows, read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step111_real_solver_candidate_report_contract():
    report = read_json(ROOT / "outputs" / "step111_real_solver_candidate" / "real_solver_candidate_report.json")
    summary = report["summary"]
    row = report["rows"][0]
    assert summary["real_solver_candidate_pass"] is True
    assert row["row_name"] == "cap_2e-2_E_2e4"
    assert row["driver_run_called"] is True
    assert row["canonical_driver_module"] == "src.mpm_lbm.sim.drivers.fsi_driver"
    assert row["restart_loaded"] is True
    assert row["preflow_source"] == "real_lbm_simulation"
    assert row["completed_official_fsi_steps"] == 50
    assert row["completed_lbm_substeps"] == 6000
    assert row["diagnostics_row_count"] == 51
    assert row["flap_tip_timeseries_row_count"] == 51
    assert row["nearest_monitor_timeseries_row_count"] == 51
    assert row["fixed_base_particle_count"] > 0
    assert row["fixed_base_constraint_applied"] is True
    assert row["fixed_base_max_displacement_norm"] <= 1.0e-7
    assert row["fixed_base_max_velocity_norm"] <= 1.0e-7
    assert row["step36_squid_wall_velocity_config_used"] is False
    assert row["validation_claim_allowed"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False
    assert row["has_nan"] is False
    assert row["has_inf"] is False


def test_step111_real_monitor_timeseries_are_real_solver_rows():
    for name in ("nearest_public_monitor_point", "top_5_nearest_public_monitor_mean", "radius_public_monitor_mean"):
        rows = read_csv_rows(ROOT / "outputs" / "step111_real_solver_candidate" / f"monitor_timeseries_{name}.csv")
        assert len(rows) == 51
        assert float(rows[0]["time_s"]) == 0.0
        assert float(rows[-1]["time_s"]) == 0.025
