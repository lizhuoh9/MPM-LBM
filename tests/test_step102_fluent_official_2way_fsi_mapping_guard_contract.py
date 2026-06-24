import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step102_fluent_mapping_guard_passes():
    payload = read_json(
        "outputs/step102_fluent_official_2way_fsi_mapping_guard/"
        "fluent_official_2way_fsi_mapping_guard.json"
    )
    summary = payload["summary"]

    assert summary["step102_fluent_official_2way_fsi_mapping_guard_pass"] is True
    assert summary["mapping_status"] == "intake_only"
    assert summary["direct_equivalence_claim_allowed"] is False
    assert summary["validation_claim_allowed"] is False
    assert summary["official_case_dimensionality"] == "2D"
    assert summary["current_solver_dimensionality"] == "3D"
    assert summary["official_structure_model"] == "linear_elasticity_intrinsic_fsi"
    assert summary["current_structure_proxy"] == "mpm_particles_or_future_duct_flap_proxy"
    assert summary["comparison_level_allowed_initially"] == "qualitative_and_diagnostic_only"
    assert summary["quantitative_match_claim_allowed"] is False
    assert summary["recommended_future_solver_proxy"] == "procedural_duct_flap_proxy_not_official_mesh_import"


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
