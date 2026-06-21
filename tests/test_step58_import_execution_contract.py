import importlib
import json
from pathlib import Path

from src.mpm_lbm.evidence.fsidriver_import_execution_audit import (
    build_fsidriver_import_execution_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step58_import_execution_audit_passes_current_runtime_imports():
    rows, summary = build_fsidriver_import_execution_audit(ROOT)
    assert summary["fsidriver_import_execution_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 6
    assert int(summary["symbol_pair_row_count"]) == 2
    assert int(summary["bridge_import_row_count"]) == 4
    assert int(summary["symbol_pair_pass_count"]) == 2
    assert int(summary["bridge_import_pass_count"]) == 4
    assert summary["output_snapshot_unchanged"] is True
    assert summary["solver_run"] is False
    assert summary["runtime_object_construction_required"] is False
    assert all(row["pass"] is True for row in rows)


def test_step58_import_execution_artifact_passes():
    payload = read_json("outputs/step58_import_execution_audit/import_execution_audit.json")
    summary = payload["summary"]
    assert summary["fsidriver_import_execution_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 6
    assert int(summary["symbol_pair_row_count"]) == 2
    assert int(summary["bridge_import_row_count"]) == 4
    assert all(row["pass"] is True for row in payload["rows"])


def test_step58_required_canonical_and_legacy_driver_imports_match():
    policy = read_json("configs/step58_driver_import_execution_policy.json")
    for pair in policy["symbol_pairs"]:
        canonical_module = importlib.import_module(pair["canonical_module"])
        legacy_module = importlib.import_module(pair["legacy_module"])
        canonical_obj = getattr(canonical_module, pair["symbol"])
        legacy_obj = getattr(legacy_module, pair["symbol"])
        if pair["comparison"] == "identity":
            assert legacy_obj is canonical_obj
        else:
            assert legacy_obj == canonical_obj


def test_step58_optional_bridge_imports_resolve():
    policy = read_json("configs/step58_driver_import_execution_policy.json")
    for item in policy["bridge_imports"]:
        module = importlib.import_module(item["canonical_module"])
        assert callable(getattr(module, item["symbol"]))


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
