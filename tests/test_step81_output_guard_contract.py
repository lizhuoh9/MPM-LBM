import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step81_output_guard_artifact_passes():
    payload = read_json("outputs/step81_output_guard/output_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["output_guard_pass"] is True
    assert summary["step81_driver_run_dir_count"] == 0
    assert summary["step81_vtr_count"] == 0
    assert summary["step81_particle_npy_count"] == 0
    assert summary["step81_dense_wall_velocity_output_count"] == 0
    assert summary["step81_sparse_wall_velocity_output_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def test_step81_artifact_manifest_passes():
    summary = read_json("outputs/step81_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert summary["step81_driver_run_dir_count"] == 0
    assert summary["step81_vtr_count"] == 0
    assert summary["step81_particle_npy_count"] == 0
    assert summary["large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_taichi_lbm3d_step81_file_count"] == 0
    assert summary["protected_real_geometry_candidates_step81_file_count"] == 0
    assert summary["raw_geometry_file_count"] == 0


def test_step81_plan_guard_sources_do_not_run_driver():
    checked_paths = [
        "baseline_tests/step81_common.py",
        "baseline_tests/run_step81_wall_velocity_single_feature_activation_plan.py",
        "baseline_tests/run_step81_wall_velocity_single_feature_activation_guard.py",
        "baseline_tests/run_step81_step80_regression_guard.py",
        "baseline_tests/run_step81_output_guard.py",
        "baseline_tests/run_step81_artifact_manifest.py",
        "src/mpm_lbm/evidence/step81_wall_velocity_single_feature_activation_plan.py",
        "src/mpm_lbm/evidence/step81_wall_velocity_single_feature_activation_guard.py",
        "src/mpm_lbm/evidence/step81_step80_regression_guard.py",
        "src/mpm_lbm/evidence/step81_output_guard.py",
    ]
    forbidden_tokens = ["FSIDriver3D", "driver.run(", "ti.init(", "taichi.init("]
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
