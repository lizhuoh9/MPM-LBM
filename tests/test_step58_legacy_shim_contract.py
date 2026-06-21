import json
from pathlib import Path

from src.mpm_lbm.evidence.fsidriver_legacy_shim_audit import build_fsidriver_legacy_shim_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step58_legacy_shim_audit_passes_current_source():
    rows, summary = build_fsidriver_legacy_shim_audit(ROOT)
    assert summary["fsidriver_legacy_shim_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert int(summary["legacy_implementation_body_count"]) == 0
    assert rows[0]["legacy_is_shim"] is True
    assert rows[0]["legacy_contains_implementation_body"] is False


def test_step58_legacy_shim_artifact_passes():
    payload = read_json("outputs/step58_legacy_shim_audit/legacy_shim_audit.json")
    summary = payload["summary"]
    assert summary["fsidriver_legacy_shim_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 1
    assert payload["rows"][0]["pass"] is True


def test_step58_legacy_fsidriver_is_thin_canonical_shim():
    policy = read_json("configs/step58_legacy_shim_policy.json")
    text = read_text(policy["legacy_file"])
    nonblank_lines = [line for line in text.splitlines() if line.strip()]
    assert "Compatibility shim. Canonical implementation lives in " in text
    assert policy["canonical_import"] in text
    assert len(nonblank_lines) <= int(policy["max_nonblank_lines_per_shim"])
    assert "class FSIDriver3D" not in text
    assert "DIAGNOSTIC_FIELDS = [" not in text
    assert "_LEGACY_MODULE" not in text
    assert "legacy_getattr" not in text


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
