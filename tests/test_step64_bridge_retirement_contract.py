import json
from pathlib import Path

from src.mpm_lbm.evidence.batch_migration_audit import build_batch_migration_audit


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "configs/step64_motion_wall_velocity_migration_policy.json"


def test_step64_bridge_tokens_are_retired_from_canonical_files():
    rows, summary = build_batch_migration_audit(ROOT, POLICY_PATH)
    assert rows
    assert summary["batch_migration_audit_pass"] is True
    assert summary["canonical_forbidden_bridge_token_count"] == 0
    assert all(row["canonical_forbidden_bridge_token_count"] == 0 for row in rows)


def test_step64_bridge_retirement_artifact_passes():
    payload = read_json("outputs/step64_bridge_retirement_audit/audit.json")
    assert payload["summary"]["step64_bridge_retirement_pass"] is True
    assert payload["summary"]["temporary_bridge_count_for_step64_files"] == 0


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
