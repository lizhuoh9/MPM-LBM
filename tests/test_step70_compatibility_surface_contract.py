import json
from pathlib import Path

from src.mpm_lbm.evidence.compatibility_surface_audit import build_step70_compatibility_surface_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step70_compatibility_surface_audit(ROOT)
    assert rows
    assert summary["compatibility_surface_audit_pass"] is True
    assert summary["src_init_export_audit_pass"] is True
    assert summary["stale_export_count"] == 0
    assert summary["forbidden_target_count"] == 0
    assert summary["heavy_import_during_src_import"] is False
    assert summary["legacy_shim_targets_are_shims"] is True


def test_artifact_passes():
    payload = read_json("outputs/step70_compatibility_surface_audit/audit.json")
    assert payload["rows"]
    assert payload["summary"]["compatibility_surface_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
