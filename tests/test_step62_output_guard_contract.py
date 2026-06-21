import json
from pathlib import Path

from src.mpm_lbm.evidence.canonical_driver_32_duration_output_guard import (
    build_canonical_driver_32_duration_output_guard,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step62_output_guard_passes_current_artifacts():
    rows, summary = build_canonical_driver_32_duration_output_guard(ROOT)
    assert summary["output_guard_pass"] is True
    assert int(summary["step62_required_driver_run_dir_count"]) == 1
    assert int(summary["step62_optional_driver_run_dir_count"]) == 0
    assert int(summary["step62_vtr_count"]) == 0
    assert int(summary["step62_particle_npy_count"]) == 0
    assert int(summary["step62_large_file_count"]) == 0
    assert int(summary["step62_forbidden_file_count"]) == 0
    assert int(summary["external_edit_count"]) == 0
    assert int(summary["real_geometry_candidates_edit_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert all(row["pass"] is True for row in rows)


def test_step62_output_guard_artifact_passes():
    payload = read_json("outputs/step62_output_guard/output_guard.json")
    summary = payload["summary"]
    assert summary["output_guard_pass"] is True
    assert int(summary["step62_required_driver_run_dir_count"]) == 1
    assert int(summary["step62_optional_driver_run_dir_count"]) == 0
    assert int(summary["step62_vtr_count"]) == 0
    assert int(summary["step62_particle_npy_count"]) == 0
    assert int(summary["step62_large_file_count"]) == 0
    assert int(summary["external_edit_count"]) == 0
    assert int(summary["real_geometry_candidates_edit_count"]) == 0
    assert int(summary["private_absolute_path_count"]) == 0
    assert all(row["pass"] is True for row in payload["rows"])


def test_step62_artifact_manifest_passes():
    manifest = read_json("outputs/step62_artifact_manifest/artifact_summary.json")
    assert manifest["artifact_budget_pass"] is True
    assert int(manifest["protected_external_taichi_lbm3d_step62_file_count"]) == 0
    assert int(manifest["protected_real_geometry_candidates_step62_file_count"]) == 0
    assert int(manifest["large_file_count"]) == 0
    assert int(manifest["step62_vtr_count"]) == 0
    assert int(manifest["step62_particle_npy_count"]) == 0
    assert float(manifest["step62_total_size_mb"]) < 20.0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
