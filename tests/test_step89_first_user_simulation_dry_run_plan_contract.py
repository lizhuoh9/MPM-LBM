import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step89_first_user_simulation_dry_run_plan_passes():
    payload = read_json(
        "outputs/step89_first_user_simulation_dry_run_plan/first_user_simulation_dry_run_plan.json"
    )
    summary = payload["summary"]

    assert summary["step89_first_user_simulation_dry_run_plan_pass"] is True
    assert summary["previous_step"] == "Step88"
    assert summary["previous_commit"] == "f83ddcd1a0979ed6dbe41c6a9763d891e9c66b9f"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["step90_allowed"] is True
    assert summary["step90_allowed_row_name"] == (
        "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_5step_dry_run"
    )
    assert summary["step90_allowed_n_grid"] == 32
    assert summary["step90_allowed_n_particles"] == 1024
    assert summary["step90_allowed_n_lbm_steps"] == 5
    assert summary["squid_proxy_planned_for_step90"] is True
    assert summary["runtime_geometry_planned_for_step90"] is True
    assert summary["wall_velocity_planned_for_step90"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step90"] is True
    assert summary["target_u_lbm_allowed_for_step90"] == [0.0, 0.0, 0.0]
    assert summary["step89_activation_feature_count"] == 0
    assert summary["planned_step90_activation_feature_count"] == 3
    assert summary["real_geometry_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
