from pathlib import Path

from src.mpm_lbm.evidence.step109_common import read_json


ROOT = Path(__file__).resolve().parents[1]


def test_step111_artifact_manifest_contract():
    report = read_json(ROOT / "outputs" / "step111_artifact_manifest" / "artifact_manifest.json")
    summary = report["summary"]
    assert summary["artifact_manifest_pass"] is True
    assert summary["artifact_budget_pass"] is True
    assert summary["step111_file_count"] <= 90
    assert summary["step111_total_size_mb"] < 20.0
    assert summary["large_file_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["step111_proprietary_file_count"] == 0
    assert summary["step111_official_image_count"] == 0
