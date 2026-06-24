import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_step102_fluent_data_guard_passes():
    payload = read_json(
        "outputs/step102_fluent_official_2way_fsi_data_guard/"
        "fluent_official_2way_fsi_data_guard.json"
    )
    summary = payload["summary"]

    assert summary["step102_fluent_official_2way_fsi_data_guard_pass"] is True
    assert summary["official_archive_committed_count"] == 0
    assert summary["official_mesh_committed_count"] == 0
    assert summary["official_journal_committed_count"] == 0
    assert summary["fluent_case_data_committed_count"] == 0
    assert summary["private_benchmark_path_committed_count"] == 0
    assert summary["ansys_proprietary_file_committed_count"] == 0
    assert summary["ansys_large_verbatim_excerpt_count"] == 0
    assert summary["private_absolute_path_count"] == 0
    assert summary["artifact_budget_pass"] is True
    assert summary["local_data_required"] is True
    assert summary["local_data_committed"] is False


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
