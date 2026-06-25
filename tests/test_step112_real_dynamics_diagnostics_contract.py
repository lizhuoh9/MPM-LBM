from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step112_diagnostics_reports_z_component_and_monotonicity():
    report = read_json(ROOT / "outputs" / "step112_real_dynamics_diagnostics" / "component_monitor_report.json")
    summary = report["summary"]
    row = report["rows"][0]
    assert summary["real_dynamics_diagnostics_pass"] is True
    assert row["diagnostics_source"] == "real_solver_particles"
    assert row["nearest_monitor_peak_total_m"] > 0.0
    assert row["z_to_total_peak_ratio"] >= 0.0
    assert row["y_to_total_peak_ratio"] >= 0.0
    assert row["monotonic_increasing_fraction"] >= 0.0
    assert row["all_metrics_finite"] is True
    assert row["validation_claim_allowed"] is False
    assert row["direct_quantitative_equivalence_allowed"] is False


def test_step112_force_and_structural_reports_are_real_and_finite():
    force = read_json(ROOT / "outputs" / "step112_real_dynamics_diagnostics" / "force_displacement_phase_report.json")
    structural = read_json(ROOT / "outputs" / "step112_real_dynamics_diagnostics" / "structural_state_report.json")
    force_row = force["rows"][0]
    structural_row = structural["rows"][0]
    assert force["summary"]["force_displacement_phase_pass"] is True
    assert structural["summary"]["structural_state_pass"] is True
    assert force_row["diagnostics_source"] == "real_solver_particles"
    assert structural_row["diagnostics_source"] == "real_solver_particles"
    assert force_row["hydro_force_max_norm_max"] > 0.0
    assert force_row["max_grid_reaction_norm_max"] > 0.0
    assert structural_row["mpm_min_J_min"] > 0.0
    assert structural_row["mpm_max_speed_max"] > 0.0
