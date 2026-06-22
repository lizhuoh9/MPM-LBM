import json
from pathlib import Path

from src.mpm_lbm.evidence.step81_wall_velocity_single_feature_activation_plan import (
    build_step81_wall_velocity_single_feature_activation_plan,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step81_wall_velocity_activation_plan_passes():
    rows, summary = build_step81_wall_velocity_single_feature_activation_plan(ROOT)
    assert rows
    assert summary["step81_wall_velocity_single_feature_activation_plan_pass"] is True
    assert summary["previous_step"] == "Step80"
    assert summary["previous_commit"] == "a2fbdfa6a9af0f02901e16e92b276c2055755fe1"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["wall_velocity_activation_planned"] is True
    assert summary["wall_velocity_application_mode_planned_for_step82"] == "solid_vel_experimental"
    assert summary["target_lbm_field_planned_for_step82"] == "solid_vel"
    assert summary["step81_activation_feature_count"] == 0
    assert summary["planned_step82_activation_feature_count"] == 1
    assert summary["runtime_geometry_allowed"] is False
    assert summary["combined_runtime_geometry_wall_velocity_allowed"] is False
    assert summary["real_geometry_allowed"] is False
    assert summary["squid_proxy_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["grid_48_allowed"] is False
    assert summary["grid_64_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["step82_allowed_row_name"] == "canonical_driver_wall_velocity_solid_vel_32_3step_smoke"


def test_step81_wall_velocity_activation_plan_artifact_passes():
    payload = read_json(
        "outputs/step81_wall_velocity_single_feature_activation_plan/wall_velocity_single_feature_activation_plan.json"
    )
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step81_wall_velocity_single_feature_activation_plan_pass"] is True
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["wall_velocity_activation_planned"] is True
    assert summary["wall_velocity_application_mode_planned_for_step82"] == "solid_vel_experimental"
    assert summary["target_lbm_field_planned_for_step82"] == "solid_vel"
    assert summary["runtime_geometry_allowed"] is False
    assert summary["combined_runtime_geometry_wall_velocity_allowed"] is False
    assert summary["real_geometry_allowed"] is False
    assert summary["squid_proxy_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False


def test_step81_activation_plan_sources_do_not_run_driver():
    checked_paths = [
        "baseline_tests/run_step81_wall_velocity_single_feature_activation_plan.py",
        "src/mpm_lbm/evidence/step81_wall_velocity_single_feature_activation_plan.py",
    ]
    forbidden_tokens = ["FSIDriver3D", "driver.run(", "ti.init(", "taichi.init("]
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
