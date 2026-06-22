import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step87_combined_activation_guard_passes():
    payload = read_json(
        "outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard/"
        "runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard.json"
    )
    summary = payload["summary"]

    assert summary["step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_guard_pass"] is True
    assert summary["guard_pass_count"] == summary["guard_row_count"]
    assert summary["step87_activation_feature_count"] == 0
    assert summary["planned_step88_activation_feature_count"] == 3
    assert summary["squid_proxy_planned_for_step88"] is True
    assert summary["runtime_geometry_planned_for_step88"] is True
    assert summary["wall_velocity_planned_for_step88"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step88"] is True
    assert summary["runtime_geometry_application_mode_planned_for_step88"] == "diagnostic_only"
    assert summary["wall_velocity_application_mode_planned_for_step88"] == "solid_vel_experimental"
    assert summary["apply_to_lbm_solid_vel_planned_for_step88"] is True
    assert summary["apply_to_lbm_populations_planned_for_step88"] is False
    assert summary["modify_bounceback_formula_planned_for_step88"] is False
    assert summary["real_geometry_planned_for_step88"] is False
    assert summary["real_geometry_candidate_data_planned_for_step88"] is False
    assert summary["write_vtk_planned_for_step88"] is False
    assert summary["write_particles_planned_for_step88"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
