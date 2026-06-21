import json
from pathlib import Path

from src.mpm_lbm.evidence.fsidriver_behavior_preservation_audit import (
    build_fsidriver_behavior_preservation_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step58_behavior_preservation_audit_passes_current_source():
    rows, summary = build_fsidriver_behavior_preservation_audit(ROOT)
    assert summary["fsidriver_behavior_preservation_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 5
    assert summary["solver_behavior_changed"] is False
    assert summary["physics_feature_expansion"] is False
    assert summary["solver_run"] is False
    assert summary["output_dir_created_by_constructor"] is False
    assert all(row["pass"] is True for row in rows)


def test_step58_behavior_preservation_artifact_passes():
    payload = read_json("outputs/step58_behavior_preservation_audit/behavior_preservation_audit.json")
    summary = payload["summary"]
    assert summary["fsidriver_behavior_preservation_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 5
    assert summary["output_dir_created_by_constructor"] is False
    assert all(row["pass"] is True for row in payload["rows"])


def test_step58_constructor_probe_does_not_initialize_or_write_outputs():
    from src.mpm_lbm.sim.drivers.fsi_config import FSIDriverConfig
    from src.mpm_lbm.sim.drivers.fsi_driver import FSIDriver3D

    policy = read_json("configs/step58_behavior_preservation_policy.json")
    out_dir = ROOT / policy["constructor_probe_out_dir"]
    assert not out_dir.exists()
    driver = FSIDriver3D(
        FSIDriverConfig(n_lbm_steps=1, write_vtk=False, write_particles=False),
        out_dir=str(out_dir),
    )
    assert driver.initialized is False
    assert driver.current_lbm_step == 0
    assert driver.total_mpm_substeps == 0
    assert list(driver.timing.keys()) == policy["expected_timing_keys"]
    assert driver.lbm is None
    assert driver.solid is None
    assert driver.projector is None
    assert not out_dir.exists()


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
