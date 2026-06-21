import importlib
import json
from pathlib import Path

from src.mpm_lbm.evidence.optional_bridge_audit import build_optional_bridge_audit


ROOT = Path(__file__).resolve().parents[1]


def test_step58_optional_bridge_audit_passes_current_source():
    rows, summary = build_optional_bridge_audit(ROOT)
    assert summary["optional_bridge_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 3
    assert int(summary["symbol_count"]) == 4
    assert int(summary["same_object_symbol_count"]) == 4
    assert summary["bridge_is_temporary_until_step59"] is True
    assert summary["output_snapshot_unchanged"] is True
    assert summary["solver_run"] is False
    assert int(summary["bridge_retired_count"]) == 3
    assert int(summary["active_temporary_bridge_count"]) == 0
    assert all(row["bridge_retired"] is True for row in rows)
    assert all(row["uses_legacy_getattr"] is False for row in rows)


def test_step58_optional_bridge_artifact_passes():
    payload = read_json("outputs/step58_optional_bridge_audit/optional_bridge_audit.json")
    summary = payload["summary"]
    assert summary["optional_bridge_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 3
    assert int(summary["same_object_symbol_count"]) == int(summary["symbol_count"]) == 4
    assert int(summary["bridge_retired_count"]) == 3
    assert all(row["pass"] is True for row in payload["rows"])


def test_step58_optional_bridges_are_retired_by_step64_batch_a():
    policy = read_json("configs/step58_optional_bridge_policy.json")
    assert policy["bridge_is_temporary_until_step59"] is True
    for bridge in policy["bridges"]:
        text = read_text(bridge["canonical_path"])
        assert "Implementation remains legacy until Step 59" not in text
        assert "BRIDGE_IS_TEMPORARY_UNTIL_STEP59 = True" not in text
        assert "_LEGACY_MODULE" not in text
        assert "legacy_getattr" not in text
        canonical_module = importlib.import_module(bridge["canonical_module"])
        legacy_module = importlib.import_module(bridge["legacy_module"])
        for symbol in bridge["symbols"]:
            assert getattr(canonical_module, symbol) is getattr(legacy_module, symbol)


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")
