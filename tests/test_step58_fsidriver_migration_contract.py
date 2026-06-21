import json
from pathlib import Path

from src.mpm_lbm.evidence.fsidriver_migration_audit import build_fsidriver_migration_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step58_fsidriver_migration_audit_passes_current_source():
    rows, summary = build_fsidriver_migration_audit(ROOT)
    assert summary["fsidriver_migration_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert int(summary["canonical_missing_count"]) == 0
    assert int(summary["legacy_missing_count"]) == 0
    assert int(summary["canonical_forbidden_token_count"]) == 0
    assert int(summary["canonical_legacy_root_import_count"]) == 0
    assert int(summary["forbidden_reverse_dependency_count"]) == 0
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False
    assert rows[0]["canonical_contains_real_implementation"] is True
    assert rows[0]["legacy_is_shim"] is True


def test_step58_fsidriver_migration_artifact_passes():
    payload = read_json("outputs/step58_fsidriver_migration_audit/fsidriver_migration_audit.json")
    summary = payload["summary"]
    assert summary["fsidriver_migration_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert payload["rows"][0]["pass"] is True


def test_step58_fsidriver_real_implementation_lives_in_canonical_module():
    canonical = read_text("src/mpm_lbm/sim/drivers/fsi_driver.py")
    legacy = read_text("src/fsi_driver.py")
    assert "class FSIDriver3D" in canonical
    assert "DIAGNOSTIC_FIELDS" in canonical
    assert "def initialize" in canonical
    assert "def step_once" in canonical
    assert "def run" in canonical
    assert "_LEGACY_MODULE" not in canonical
    assert "legacy_getattr" not in canonical
    assert "from src.mpm_lbm.sim.drivers.fsi_driver import *" in legacy
    assert "class FSIDriver3D" not in legacy


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
