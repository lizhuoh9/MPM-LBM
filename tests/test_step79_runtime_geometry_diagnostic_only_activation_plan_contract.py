import json
from pathlib import Path

from src.mpm_lbm.evidence.step79_runtime_geometry_diagnostic_only_activation_plan import (
    build_step79_runtime_geometry_diagnostic_only_activation_plan,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step79_runtime_geometry_diagnostic_only_activation_plan_passes():
    rows, summary = build_step79_runtime_geometry_diagnostic_only_activation_plan(ROOT)
    assert rows
    assert summary["step79_runtime_geometry_diagnostic_only_activation_plan_pass"] is True
    assert summary["previous_step"] == "Step78"
    assert summary["previous_commit"] == "d226b1fc679f7d5592629a359c56f0b83372a393"
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["runtime_geometry_activation_planned"] is True
    assert summary["runtime_geometry_application_mode_planned_for_step80"] == "diagnostic_only"
    assert summary["geometry_mutation_allowed"] is False
    assert summary["solver_formula_change_allowed"] is False
    assert summary["wall_velocity_allowed"] is False
    assert summary["real_geometry_allowed"] is False
    assert summary["squid_proxy_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["grid_48_allowed"] is False
    assert summary["grid_64_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False
    assert summary["step80_allowed_row_count"] == 1
    assert summary["step80_allowed_row_name"] == "canonical_driver_runtime_geometry_diagnostic_only_32_3step_smoke"


def test_step79_runtime_geometry_diagnostic_only_activation_plan_artifact_passes():
    payload = read_json("outputs/step79_runtime_geometry_diagnostic_only_activation_plan/runtime_geometry_diagnostic_only_activation_plan.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["step79_runtime_geometry_diagnostic_only_activation_plan_pass"] is True
    assert summary["driver_run_required"] is False
    assert summary["fsidriver_run_allowed"] is False
    assert summary["simulation_run_allowed"] is False
    assert summary["runtime_geometry_activation_planned"] is True
    assert summary["runtime_geometry_application_mode_planned_for_step80"] == "diagnostic_only"
    assert summary["geometry_mutation_allowed"] is False
    assert summary["solver_formula_change_allowed"] is False
    assert summary["wall_velocity_allowed"] is False
    assert summary["real_geometry_allowed"] is False
    assert summary["squid_proxy_allowed"] is False
    assert summary["link_area_allowed"] is False
    assert summary["vtr_output_allowed"] is False
    assert summary["particle_npy_output_allowed"] is False


def test_step79_activation_plan_sources_do_not_run_driver():
    checked_paths = [
        "baseline_tests/run_step79_runtime_geometry_diagnostic_only_activation_plan.py",
        "src/mpm_lbm/evidence/step79_runtime_geometry_diagnostic_only_activation_plan.py",
    ]
    forbidden_tokens = ["FSIDriver3D", "driver.run(", "ti.init(", "taichi.init("]
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
