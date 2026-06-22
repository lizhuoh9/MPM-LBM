import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step87_combined_activation_plan_passes():
    payload = read_json(
        "outputs/step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan/"
        "runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan.json"
    )
    summary = payload["summary"]

    assert summary["step87_runtime_geometry_wall_velocity_squid_proxy_combined_activation_plan_pass"] is True
    assert summary["previous_step"] == "Step86"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["squid_proxy_planned_for_step88"] is True
    assert summary["geometry_type_allowed_for_step88"] == "squid_proxy"
    assert summary["runtime_geometry_planned_for_step88"] is True
    assert summary["geometry_motion_application_mode_allowed_for_step88"] == "diagnostic_only"
    assert summary["geometry_mutation_allowed"] is False
    assert summary["wall_velocity_planned_for_step88"] is True
    assert summary["wall_velocity_application_mode_allowed_for_step88"] == "solid_vel_experimental"
    assert summary["target_lbm_field_planned_for_step88"] == "solid_vel"
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step88"] is True
    assert summary["step87_activation_feature_count"] == 0
    assert summary["planned_step88_activation_feature_count"] == 3
    assert summary["real_geometry_allowed"] is False
    assert summary["real_geometry_candidate_data_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
