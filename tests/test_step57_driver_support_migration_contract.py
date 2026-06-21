import json
from pathlib import Path

from src.mpm_lbm.evidence.driver_support_migration_audit import build_driver_support_migration_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step57_driver_support_migration_audit_passes_current_source():
    rows, summary = build_driver_support_migration_audit(ROOT)
    assert summary["driver_support_migration_audit_pass"] is True
    assert int(summary["row_count"]) == 16
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["canonical_missing_count"]) == 0
    assert int(summary["legacy_missing_count"]) == 0
    assert int(summary["canonical_legacy_getattr_count"]) == 0
    assert int(summary["canonical_legacy_root_import_count"]) == 0
    assert int(summary["forbidden_reverse_dependency_count"]) == 0
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False
    assert all(row["canonical_contains_real_implementation"] is True for row in rows)
    assert all(row["legacy_is_shim"] is True for row in rows)


def test_step57_driver_support_migration_artifact_passes():
    payload = read_json("outputs/step57_driver_support_migration_audit/driver_support_migration_audit.json")
    summary = payload["summary"]
    assert summary["driver_support_migration_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 16
    assert all(row["pass"] is True for row in payload["rows"])


def test_step57_geometry_sampler_is_canonical_real_implementation_not_legacy_wrapper():
    canonical = read_text("src/mpm_lbm/sim/geometry/sampler.py")
    legacy = read_text("src/geometry.py")
    assert "class GeometrySampler3D" in canonical
    assert "def sample_particles" in canonical
    assert "_LEGACY_MODULE" not in canonical
    assert "legacy_getattr" not in canonical
    assert "from src.mpm_lbm.sim.geometry.sampler import *" in legacy
    assert "class GeometrySampler3D" not in legacy


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
