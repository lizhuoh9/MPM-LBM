import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step102_fluent_benchmark_intake_passes():
    payload = read_json(
        "outputs/step102_fluent_official_2way_fsi_benchmark_intake/"
        "fluent_official_2way_fsi_benchmark_intake.json"
    )
    summary = payload["summary"]

    assert summary["step102_fluent_official_2way_fsi_benchmark_intake_pass"] is True
    assert summary["source_url_recorded"] is True
    assert summary["problem_family"] == "two_way_intrinsic_fsi"
    assert summary["official_case_dimensionality"] == "2D"
    assert summary["official_archive_name"] == "fsi_2way.zip"
    assert summary["official_mesh_name"] == "flap.msh"
    assert summary["official_journal_name"] == "steady_fluid_flow.jou"
    assert summary["official_files_expected"] == "flap.msh, steady_fluid_flow.jou"
    assert summary["duct_length_m"] == 0.10
    assert summary["duct_height_m"] == 0.04
    assert summary["flap_height_m"] == 0.01
    assert summary["flap_thickness_m"] == 0.003
    assert summary["inlet_velocity_m_per_s"] == 10.0
    assert summary["solid_density"] == 1600.0
    assert summary["solid_youngs_modulus"] == 1000000.0
    assert summary["solid_poisson_ratio"] == 0.47
    assert summary["number_of_time_steps"] == 50
    assert summary["time_step_size_s"] == 0.0005
    assert summary["max_iterations_per_time_step"] == 40
    assert summary["step102_driver_run_required"] is False
    assert summary["step102_simulation_run_allowed"] is False
    assert summary["step102_fluent_run_allowed"] is False
    assert summary["step102_benchmark_comparison_allowed"] is False
    assert summary["step102_validation_claim_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
