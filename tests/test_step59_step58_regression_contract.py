import json
from pathlib import Path

from src.mpm_lbm.evidence.fsidriver_behavior_preservation_audit import (
    build_fsidriver_behavior_preservation_audit,
)
from src.mpm_lbm.evidence.fsidriver_import_execution_audit import build_fsidriver_import_execution_audit
from src.mpm_lbm.evidence.fsidriver_legacy_shim_audit import build_fsidriver_legacy_shim_audit
from src.mpm_lbm.evidence.fsidriver_migration_audit import build_fsidriver_migration_audit
from src.mpm_lbm.evidence.optional_bridge_audit import build_optional_bridge_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step59_step58_regression_guard_passes_current_source():
    _, migration_summary = build_fsidriver_migration_audit(ROOT)
    _, import_summary = build_fsidriver_import_execution_audit(ROOT)
    _, shim_summary = build_fsidriver_legacy_shim_audit(ROOT)
    _, bridge_summary = build_optional_bridge_audit(ROOT)
    _, behavior_summary = build_fsidriver_behavior_preservation_audit(ROOT)
    assert migration_summary["fsidriver_migration_audit_pass"] is True
    assert import_summary["fsidriver_import_execution_audit_pass"] is True
    assert shim_summary["fsidriver_legacy_shim_audit_pass"] is True
    assert bridge_summary["optional_bridge_audit_pass"] is True
    assert behavior_summary["fsidriver_behavior_preservation_audit_pass"] is True


def test_step59_step58_regression_guard_artifact_passes():
    payload = read_json("outputs/step59_step58_regression_guard/step58_regression_guard.json")
    summary = payload["summary"]
    assert summary["step58_regression_guard_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert "geo_path filename now follows n_grid" in summary["step59_geo_path_naming_supersession"]
    assert all(row["pass"] is True for row in payload["rows"])


def test_step59_keeps_legacy_fsidriver_as_thin_shim_and_bridges_temporary():
    legacy_driver = (ROOT / "src/fsi_driver.py").read_text(encoding="utf-8")
    assert "from src.mpm_lbm.sim.drivers.fsi_driver import *" in legacy_driver
    assert "class FSIDriver3D" not in legacy_driver
    for path in [
        "src/mpm_lbm/sim/motion/boundary_motion_interface.py",
        "src/mpm_lbm/sim/motion/geometry_motion_interface.py",
        "src/mpm_lbm/sim/wall_velocity/application.py",
    ]:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "Implementation remains legacy until Step 59" in text
        assert "legacy_getattr" in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
