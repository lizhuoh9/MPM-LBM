import json
from pathlib import Path

from src.mpm_lbm.evidence.step79_output_guard import build_step79_output_guard


ROOT = Path(__file__).resolve().parents[1]


def test_step79_output_guard_passes():
    rows, summary = build_step79_output_guard(ROOT)
    assert rows
    assert summary["output_guard_pass"] is True
    assert summary["step79_driver_run_dir_count"] == 0
    assert summary["step79_vtr_count"] == 0
    assert summary["step79_particle_npy_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def test_step79_output_guard_artifact_passes():
    payload = read_json("outputs/step79_output_guard/output_guard.json")
    summary = payload["summary"]
    assert payload["rows"]
    assert summary["output_guard_pass"] is True
    assert summary["step79_driver_run_dir_count"] == 0
    assert summary["step79_vtr_count"] == 0
    assert summary["step79_particle_npy_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0


def test_step79_artifact_manifest_passes():
    summary = read_json("outputs/step79_artifact_manifest/artifact_summary.json")
    assert summary["artifact_budget_pass"] is True
    assert summary["step79_file_count"] <= 50
    assert summary["step79_total_size_mb"] < 5.0
    assert summary["step79_driver_run_dir_count"] == 0
    assert summary["step79_vtr_count"] == 0
    assert summary["step79_particle_npy_count"] == 0
    assert summary["large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["protected_external_taichi_lbm3d_step79_file_count"] == 0
    assert summary["protected_real_geometry_candidates_step79_file_count"] == 0
    assert summary["raw_geometry_file_count"] == 0


def test_step79_output_guard_sources_do_not_run_driver():
    checked_paths = [
        "baseline_tests/run_step79_output_guard.py",
        "baseline_tests/run_step79_artifact_manifest.py",
        "src/mpm_lbm/evidence/step79_output_guard.py",
    ]
    forbidden_tokens = ["FSIDriver3D", "driver.run(", "ti.init(", "taichi.init("]
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden_tokens:
            assert token not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
