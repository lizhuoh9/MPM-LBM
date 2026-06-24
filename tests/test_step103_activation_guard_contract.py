import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEP103_ROW = "fluent_inspired_duct_flap_proxy_48_5step_ggui_comparison_smoke"


def test_step103_activation_guard_passes():
    payload = read_json("outputs/step103_activation_guard/activation_guard.json")
    summary = payload["summary"]

    assert summary["step103_activation_guard_pass"] is True
    assert summary["required_row_name"] == STEP103_ROW
    assert summary["geometry_type"] == "duct_flap_proxy"
    assert summary["duct_flap_proxy_enabled_count"] == 1
    assert summary["runtime_geometry_enabled_count"] == 1
    assert summary["wall_velocity_enabled_count"] == 1
    assert summary["ggui_visualization_enabled_count"] == 1
    assert summary["grid_48_enabled_count"] == 1
    assert summary["grid_64_enabled_count"] == 0
    assert summary["real_geometry_candidate_enabled_count"] == 0
    assert summary["real_geometry_enabled_count"] == 0
    assert summary["link_area_enabled_count"] == 0
    assert summary["write_vtk_count"] == 0
    assert summary["write_particles_count"] == 0
    assert summary["validation_claim_allowed"] is False
    assert summary["direct_quantitative_equivalence_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
