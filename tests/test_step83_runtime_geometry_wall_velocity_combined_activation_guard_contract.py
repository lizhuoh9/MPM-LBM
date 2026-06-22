import json
from pathlib import Path

from src.mpm_lbm.evidence.step83_runtime_geometry_wall_velocity_combined_activation_guard import (
    build_step83_runtime_geometry_wall_velocity_combined_activation_guard,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step83_combined_activation_guard_passes():
    rows, summary = build_step83_runtime_geometry_wall_velocity_combined_activation_guard(ROOT)
    assert rows
    assert summary["step83_runtime_geometry_wall_velocity_combined_activation_guard_pass"] is True
    assert summary["guard_pass_count"] == summary["guard_row_count"]
    assert summary["step83_activation_feature_count"] == 0
    assert summary["planned_step84_activation_feature_count"] == 2
    assert summary["runtime_geometry_planned_for_step84"] is True
    assert summary["runtime_geometry_application_mode_planned_for_step84"] == "diagnostic_only"
    assert summary["geometry_mutation_allowed"] is False
    assert summary["wall_velocity_planned_for_step84"] is True
    assert summary["wall_velocity_application_mode_planned_for_step84"] == "solid_vel_experimental"
    assert summary["apply_to_lbm_solid_vel_planned_for_step84"] is True
    assert summary["apply_to_lbm_populations_planned_for_step84"] is False
    assert summary["apply_to_mpm_planned_for_step84"] is False
    assert summary["apply_to_projector_planned_for_step84"] is False
    assert summary["modify_bounceback_formula_planned_for_step84"] is False
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step84"] is True
    assert summary["real_geometry_planned_for_step84"] is False
    assert summary["squid_proxy_planned_for_step84"] is False
    assert summary["link_area_planned_for_step84"] is False
    assert summary["write_vtk_planned_for_step84"] is False
    assert summary["write_particles_planned_for_step84"] is False


def test_step83_combined_activation_guard_artifact_passes():
    payload = read_json(
        "outputs/step83_runtime_geometry_wall_velocity_combined_activation_guard/"
        "runtime_geometry_wall_velocity_combined_activation_guard.json"
    )
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step83_runtime_geometry_wall_velocity_combined_activation_guard_pass"] is True
    assert summary["guard_pass_count"] == summary["guard_row_count"]
    assert summary["step83_activation_feature_count"] == 0
    assert summary["planned_step84_activation_feature_count"] == 2
    assert summary["runtime_geometry_planned_for_step84"] is True
    assert summary["wall_velocity_planned_for_step84"] is True
    assert summary["combined_runtime_geometry_wall_velocity_planned_for_step84"] is True


def test_step83_guard_sources_do_not_run_driver():
    checked_paths = [
        "baseline_tests/step83_common.py",
        "baseline_tests/run_step83_runtime_geometry_wall_velocity_combined_activation_guard.py",
        "baseline_tests/run_step83_step82_regression_guard.py",
        "baseline_tests/run_step83_step80_regression_guard.py",
        "baseline_tests/run_step83_output_guard.py",
        "baseline_tests/run_step83_artifact_manifest.py",
        "src/mpm_lbm/evidence/step83_runtime_geometry_wall_velocity_combined_activation_guard.py",
        "src/mpm_lbm/evidence/step83_step82_regression_guard.py",
        "src/mpm_lbm/evidence/step83_step80_regression_guard.py",
        "src/mpm_lbm/evidence/step83_output_guard.py",
    ]
    forbidden_tokens = ["FSIDriver3D", "driver.run(", "ti.init(", "taichi.init("]
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
