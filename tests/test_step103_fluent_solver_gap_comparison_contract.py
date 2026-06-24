import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step103_fluent_solver_gap_comparison_report_is_gap_only():
    payload = read_json("outputs/step103_fluent_comparison/fluent_solver_gap_report.json")
    summary = payload["summary"]

    assert summary["step103_fluent_solver_gap_comparison_pass"] is True
    assert summary["comparison_status"] == "capability_gap_detected"
    assert summary["official_case_dimensionality"] == "2D"
    assert summary["our_solver_dimensionality"] == "3D"
    assert summary["direct_quantitative_equivalence_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["official_structural_model"] == "linear_elasticity_intrinsic_fsi"
    assert summary["our_structural_model_equivalent"] is False
    assert summary["official_dynamic_mesh"] is True
    assert summary["our_geometry_mutation_enabled"] is False
    assert summary["official_monitor_quantity"] == "total_displacement"
    assert summary["our_equivalent_flap_tip_displacement_available"] is False
    assert summary["capability_gap_count"] >= 1
    assert summary["gap_dynamic_mesh_equivalence"] is True
    assert summary["gap_linear_elasticity_equivalence"] is True
    assert summary["gap_exact_flap_tip_displacement"] is True
    assert summary["our_solver_run_stable"] is True
    assert summary["our_solver_has_nan"] is False
    assert summary["our_solver_has_inf"] is False
    assert summary["official_fluent_files_used_as_runtime_input"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
