import importlib
import json
from pathlib import Path

from src.mpm_lbm.evidence.driver_support_import_execution_audit import (
    build_driver_support_import_execution_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_step57_import_execution_audit_passes_current_runtime_imports():
    rows, summary = build_driver_support_import_execution_audit(ROOT)
    assert summary["driver_support_import_execution_audit_pass"] is True
    assert int(summary["row_count"]) == 14
    assert int(summary["row_count"]) == int(summary["pass_count"])
    assert int(summary["same_object_count"]) == 14
    assert summary["output_snapshot_unchanged"] is True
    assert summary["solver_run"] is False
    assert summary["runtime_object_construction_required"] is False
    assert all(row["same_object"] is True for row in rows)


def test_step57_import_execution_artifact_passes():
    payload = read_json("outputs/step57_import_execution_audit/import_execution_audit.json")
    summary = payload["summary"]
    assert summary["driver_support_import_execution_audit_pass"] is True
    assert int(summary["row_count"]) == int(summary["pass_count"]) == 14
    assert int(summary["same_object_count"]) == 14
    assert all(row["pass"] is True for row in payload["rows"])


def test_step57_required_canonical_and_legacy_imports_resolve_to_same_objects():
    policy = read_json("configs/step57_import_execution_policy.json")
    for pair in policy["symbol_pairs"]:
        canonical_module = importlib.import_module(pair["canonical_module"])
        legacy_module = importlib.import_module(pair["legacy_module"])
        assert getattr(legacy_module, pair["symbol"]) is getattr(canonical_module, pair["symbol"])


def read_json(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)
