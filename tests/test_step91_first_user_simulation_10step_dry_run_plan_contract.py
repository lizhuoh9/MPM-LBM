import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step91_first_user_simulation_10step_dry_run_plan_passes():
    payload = read_json(
        "outputs/step91_first_user_simulation_10step_dry_run_plan/"
        "first_user_simulation_10step_dry_run_plan.json"
    )
    summary = payload["summary"]

    assert summary["step91_first_user_simulation_10step_dry_run_plan_pass"] is True
    assert summary["previous_step"] == "Step90"
    assert summary["previous_commit"] == "72503260933df8919826ef8fa7ed7cab12b96297"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["step92_allowed"] is True
    assert summary["step92_allowed_row_name"] == (
        "first_user_squid_proxy_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_10step_dry_run"
    )
    assert summary["step92_allowed_n_grid"] == 32
    assert summary["step92_allowed_n_particles"] == 1024
    assert summary["step92_allowed_n_lbm_steps"] == 10
    assert summary["only_duration_expansion_from_step90"] is True
    assert summary["previous_step90_n_lbm_steps"] == 5
    assert summary["planned_step92_n_lbm_steps"] == 10
    assert summary["squid_proxy_planned_for_step92"] is True
    assert summary["runtime_geometry_planned_for_step92"] is True
    assert summary["wall_velocity_planned_for_step92"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step92"] is True
    assert summary["step91_activation_feature_count"] == 0
    assert summary["planned_step92_activation_feature_count"] == 3
    assert summary["target_u_lbm_allowed_for_step92"] == [0.0, 0.0, 0.0]
    assert summary["real_geometry_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
