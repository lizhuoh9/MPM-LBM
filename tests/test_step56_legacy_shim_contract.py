import json
from pathlib import Path

from src.mpm_lbm.evidence.legacy_shim_audit import build_legacy_shim_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step56_legacy_shim_audit_passes_current_source():
    rows, summary = build_legacy_shim_audit(ROOT)
    assert summary["legacy_shim_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 9
    assert int(summary["legacy_implementation_body_count"]) == 0
    assert all(row["legacy_is_shim"] is True for row in rows)
    assert all(row["legacy_contains_implementation_body"] is False for row in rows)


def test_step56_legacy_shim_artifact_passes():
    payload = read_json("outputs/step56_legacy_shim_audit/legacy_shim_audit.json")
    summary = payload["summary"]
    assert summary["legacy_shim_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 9
    assert all(row["pass"] is True for row in payload["rows"])


def test_step56_all_legacy_files_are_thin_canonical_shims():
    policy = read_json("configs/step56_canonical_runtime_migration_policy.json")
    for migration in policy["migrations"]:
        text = read_text(migration["legacy_path"])
        nonblank_lines = [line for line in text.splitlines() if line.strip()]
        assert "Compatibility shim. Canonical implementation lives in " in text
        assert migration["legacy_import"] in text
        assert len(nonblank_lines) <= 4
        assert "class " not in text
        assert "def " not in text
        assert "_LEGACY_MODULE" not in text
        assert "legacy_getattr" not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
