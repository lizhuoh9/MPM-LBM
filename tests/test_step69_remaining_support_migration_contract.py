import json
from pathlib import Path

from src.mpm_lbm.evidence.remaining_support_migration_audit import build_step69_remaining_support_migration_audit


ROOT = Path(__file__).resolve().parents[1]


def test_build_passes():
    rows, summary = build_step69_remaining_support_migration_audit(ROOT)
    assert len(rows) == 6
    assert summary["remaining_support_migration_audit_pass"] is True
    assert summary["migration_required_count_from_step63"] == 6
    assert summary["migrated_support_count"] == 6
    assert summary["remaining_migration_required_count"] == 0


def test_artifact_passes():
    payload = read_json("outputs/step69_remaining_support_migration_audit/audit.json")
    assert len(payload["rows"]) == 6
    assert payload["summary"]["remaining_support_migration_audit_pass"] is True


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
