import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step104_output_guard_passes():
    payload = read_json("outputs/step104_output_guard/output_guard_report.json")
    summary = payload["summary"]
    paths = [row["path"] for row in payload["rows"]]

    assert summary["output_guard_pass"] is True
    assert summary["step104_ansys_proprietary_file_count"] == 0
    assert summary["step104_private_fluent_csv_count"] == 0
    assert summary["step104_fluent_run_output_count"] == 0
    assert summary["step104_vtr_count"] == 0
    assert summary["step104_particle_npy_count"] == 0
    assert summary["step104_video_count"] == 0
    assert summary["step104_step36_wall_velocity_reference_count"] == 0
    assert summary["protected_external_edit_count"] == 0
    assert summary["protected_real_geometry_candidate_edit_count"] == 0
    assert summary["forbidden_validation_claim_count"] == 0
    assert all(not path.startswith("outputs/step104_artifact_manifest/") for path in paths)
    assert all(not path.startswith("outputs/step104_output_guard/") for path in paths)


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
