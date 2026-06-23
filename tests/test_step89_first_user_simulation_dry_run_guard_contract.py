import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step89_first_user_simulation_dry_run_guard_passes():
    payload = read_json(
        "outputs/step89_first_user_simulation_dry_run_guard/first_user_simulation_dry_run_guard.json"
    )
    summary = payload["summary"]

    assert summary["step89_first_user_simulation_dry_run_guard_pass"] is True
    assert summary["guard_pass_count"] == summary["guard_row_count"]
    assert summary["step89_activation_feature_count"] == 0
    assert summary["planned_step90_activation_feature_count"] == 3
    assert summary["planned_step90_duration_lbm_steps"] == 5
    assert summary["squid_proxy_planned_for_step90"] is True
    assert summary["runtime_geometry_planned_for_step90"] is True
    assert summary["wall_velocity_planned_for_step90"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step90"] is True
    assert summary["geometry_motion_application_mode_planned_for_step90"] == "diagnostic_only"
    assert summary["wall_velocity_application_mode_planned_for_step90"] == "solid_vel_experimental"
    assert summary["target_lbm_field_planned_for_step90"] == "solid_vel"
    assert summary["target_u_lbm_planned_for_step90"] == [0.0, 0.0, 0.0]
    assert summary["real_geometry_planned_for_step90"] is False
    assert summary["real_geometry_candidate_data_planned_for_step90"] is False
    assert summary["link_area_planned_for_step90"] is False
    assert summary["write_vtk_planned_for_step90"] is False
    assert summary["write_particles_planned_for_step90"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
