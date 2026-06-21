import json
from pathlib import Path

from src.mpm_lbm.evidence.batch_behavior_preservation_audit import build_batch_behavior_preservation_audit


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "configs/step67_squid_proxy_real_geometry_migration_policy.json"


def test_build_passes():
    rows, summary = build_batch_behavior_preservation_audit(ROOT, POLICY_PATH)
    assert rows
    assert summary["batch_behavior_preservation_audit_pass"] is True


def test_artifact_passes():
    payload = read_json("outputs/step67_behavior_preservation_audit/audit.json")
    assert payload["summary"]["step67_behavior_preservation_pass"] is True
    assert payload["rows"]


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
