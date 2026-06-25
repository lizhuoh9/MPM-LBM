import json
from pathlib import Path

from src.mpm_lbm.evidence.config_schema_delta_audit import build_step71_config_schema_delta_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step71_config_schema_delta_audit(ROOT)
    assert rows
    assert summary["config_schema_delta_audit_pass"] is True
    assert summary["changed_schema_classes"] == ["FSIDriverConfig", "GeometryConfig", "UnifiedSimConfig"]
    assert summary["fsidriver_write_vtk_default_previous"] == "True"
    assert summary["fsidriver_write_vtk_default_current"] == "False"
    assert summary["fsidriver_write_particles_default_previous"] == "True"
    assert summary["fsidriver_write_particles_default_current"] == "False"
    unchanged_rows = [row for row in rows if row["class_name"] not in {"FSIDriverConfig", "GeometryConfig", "UnifiedSimConfig"}]
    assert unchanged_rows
    assert all(row["schema_hash_changed"] is False for row in unchanged_rows)


def test_artifact_passes():
    payload = read_json("outputs/step71_config_schema_delta_audit/config_schema_delta.json")
    assert payload["rows"]
    assert payload["summary"]["config_schema_delta_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
