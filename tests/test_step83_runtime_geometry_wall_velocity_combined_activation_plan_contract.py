import json
from pathlib import Path

from src.mpm_lbm.evidence.step83_runtime_geometry_wall_velocity_combined_activation_plan import (
    build_step83_runtime_geometry_wall_velocity_combined_activation_plan,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step83_combined_activation_plan_passes():
    rows, summary = build_step83_runtime_geometry_wall_velocity_combined_activation_plan(ROOT)
    assert rows
    assert summary["step83_runtime_geometry_wall_velocity_combined_activation_plan_pass"] is True
    assert summary["previous_step"] == "Step82"
    assert summary["previous_commit"] == "3df6bb25b32d74f16300b8ba603c843eecc725c2"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["runtime_geometry_planned_for_step84"] is True
    assert summary["geometry_motion_application_mode_allowed_for_step84"] == "diagnostic_only"
    assert summary["geometry_mutation_allowed"] is False
    assert summary["wall_velocity_planned_for_step84"] is True
    assert summary["wall_velocity_application_mode_allowed_for_step84"] == "solid_vel_experimental"
    assert summary["target_lbm_field_planned_for_step84"] == "solid_vel"
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step84"] is True
    assert summary["step83_activation_feature_count"] == 0
    assert summary["planned_step84_activation_feature_count"] == 2
    assert summary["real_geometry_allowed"] is False
    assert summary["squid_proxy_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["step84_allowed_row_name"] == (
        "canonical_driver_runtime_geometry_diagnostic_only_wall_velocity_solid_vel_32_3step_smoke"
    )


def test_step83_combined_activation_plan_artifact_passes():
    payload = read_json(
        "outputs/step83_runtime_geometry_wall_velocity_combined_activation_plan/"
        "runtime_geometry_wall_velocity_combined_activation_plan.json"
    )
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step83_runtime_geometry_wall_velocity_combined_activation_plan_pass"] is True
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["runtime_geometry_planned_for_step84"] is True
    assert summary["wall_velocity_planned_for_step84"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step84"] is True
    assert summary["step83_activation_feature_count"] == 0
    assert summary["planned_step84_activation_feature_count"] == 2


def test_step83_activation_plan_sources_do_not_run_driver():
    checked_paths = [
        "baseline_tests/run_step83_runtime_geometry_wall_velocity_combined_activation_plan.py",
        "src/mpm_lbm/evidence/step83_runtime_geometry_wall_velocity_combined_activation_plan.py",
    ]
    forbidden_tokens = ["FSIDriver3D", "driver.run(", "ti.init(", "taichi.init("]
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
