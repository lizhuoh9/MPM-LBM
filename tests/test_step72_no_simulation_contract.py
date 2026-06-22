import json
from pathlib import Path

from src.mpm_lbm.evidence.step72_no_simulation_audit import build_step72_no_simulation_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step72_no_simulation_audit(ROOT)
    assert rows
    assert summary["no_simulation_audit_pass"] is True
    assert summary["forbidden_python_call_count"] == 0
    assert summary["forbidden_output_directory_count"] == 0
    assert summary["step72_vtr_count"] == 0
    assert summary["step72_particle_npy_count"] == 0
    assert summary["protected_step72_file_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step72_no_simulation_audit/no_simulation.json")
    assert payload["rows"]
    assert payload["summary"]["no_simulation_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
