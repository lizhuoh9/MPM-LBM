import json
from pathlib import Path

from src.mpm_lbm.evidence.batch_legacy_shim_audit import build_batch_legacy_shim_audit


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "configs/step64_motion_wall_velocity_migration_policy.json"


def test_build_passes():
    rows, summary = build_batch_legacy_shim_audit(ROOT, POLICY_PATH)
    assert rows
    assert summary["batch_legacy_shim_audit_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step64_legacy_shim_audit/audit.json")
    assert payload["summary"]["step64_legacy_shim_pass"] is True
    assert payload["rows"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
