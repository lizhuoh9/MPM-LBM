import json
from pathlib import Path

from src.mpm_lbm.evidence.output_default_alignment_audit import build_step71_output_default_alignment_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step71_output_default_alignment_audit(ROOT)
    assert rows
    assert summary["output_default_alignment_audit_pass"] is True
    assert summary["fsidriver_default_write_vtk"] is False
    assert summary["fsidriver_default_write_particles"] is False
    assert summary["explicit_true_write_vtk"] is True
    assert summary["explicit_true_write_particles"] is True
    assert summary["step70_default_write_vtk_allowed"] is False
    assert summary["step70_default_write_particles_allowed"] is False


def test_artifact_passes():
    payload = read_json("outputs/step71_output_default_alignment_audit/output_default_alignment.json")
    assert payload["rows"]
    assert payload["summary"]["output_default_alignment_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
